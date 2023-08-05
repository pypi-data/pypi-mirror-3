#
# SNMP Devices Simulator
#
# Written by Ilya Etingof <ilya@glas.net>, 2010-2011
#
import os
import sys
import getopt
if sys.version_info[0] < 3 and sys.version_info[1] < 5:
    from md5 import md5
else:
    from hashlib import md5
import time
if sys.version_info[0] < 3:
    import anydbm as dbm
    from whichdb import whichdb
else:
    import dbm
    whichdb = dbm.whichdb
import bisect
from pyasn1.type import univ
from pyasn1.codec.ber import encoder, decoder
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.carrier.asynsock.dgram import udp
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.smi import exval, indices
from pysnmp.proto import rfc1902, api
from pysnmp import debug

# Process command-line options

# Defaults
forceIndexBuild = False
validateData = False
v2cArch = False
v3Only = False
v3User = 'simulator'
v3AuthKey = 'auctoritas'
v3PrivKey = 'privatus'
v3PrivProto = config.usmDESPrivProtocol
agentAddress = ('127.0.0.1', 161)
deviceDir = '.'
deviceExt = os.path.extsep + 'snmpwalk'

helpMessage = 'Usage: %s [--help] [--debug=<category>] [--device-dir=<dir>] [--force-index-rebuild] [--validate-device-data] [--agent-address=<X.X.X.X>] [--agent-port=<port>] [--v2c-arch ] [--v3-only] [--v3-user=<username>] [--v3-auth-key=<key>] [--v3-priv-key=<key>] [--v3-priv-proto=<DES|AES>]' % sys.argv[0]

try:
    opts, params = getopt.getopt(sys.argv[1:], 'h',
        ['help', 'debug=', 'device-dir=', 'force-index-rebuild', 'validate-device-data', 'agent-address=', 'agent-port=', 'v2c-arch', 'v3-only', 'v3-user=', 'v3-auth-key=', 'v3-priv-key=', 'v3-priv-proto=']
        )
except Exception:
    sys.stdout.write('%s\r\n%s\r\n' % (sys.exc_info()[1], helpMessage))
    sys.exit(-1)

if params:
    sys.stdout.write('extra arguments supplied %s%s\r\n' % (params, helpMessage))
    sys.exit(-1)

for opt in opts:
    if opt[0] == '-h' or opt[0] == '--help':
        sys.stdout.write('%s\r\n' % helpMessage)
        sys.exit(-1)
    elif opt[0] == '--debug':
        debug.setLogger(debug.Debug(opt[1]))
    elif opt[0] == '--device-dir':
        deviceDir = opt[1]
    elif opt[0] == '--force-index-rebuild':
        forceIndexBuild = True
    elif opt[0] == '--validate-device-data':
        validateData = True
    elif opt[0] == '--agent-address':
        agentAddress = (opt[1], agentAddress[1])
    elif opt[0] == '--agent-port':
        agentAddress = (agentAddress[0], int(opt[1]))
    elif opt[0] == '--v2c-arch':
        v2cArch = True
    elif opt[0] == '--v3-only':
        v3Only = True
    elif opt[0] == '--v3-user':
        v3User = opt[1]
    elif opt[0] == '--v3-auth-key':
        v3AuthKey = opt[1]
    elif opt[0] == '--v3-priv-key':
        v3PrivKey = opt[1]
    elif opt[0] == '--v3-priv-proto':
        if opt[1].upper() == 'DES':
            v3PrivProto = config.usmDESPrivProtocol
        elif opt[1].upper() == 'AES':
            v3PrivProto = config.usmAesCfb128Protocol
        else:
            sys.stdout.write('bad v3 privacy protocol\r\n')
            sys.exit(-1)

# Device file entry parsers

class DumpParser:
    ext = os.path.extsep + 'dump'
    tagMap = {
        '0': rfc1902.Counter32,
        '1': rfc1902.Gauge32,
        '2': rfc1902.Integer32,
        '3': rfc1902.IpAddress,
        '4': univ.Null,
        '5': univ.ObjectIdentifier,
        '6': rfc1902.OctetString,
        '7': rfc1902.TimeTicks,
        '8': rfc1902.Counter32,  # an alias
        '9': rfc1902.Counter64,
        }

    def __nullFilter(value):
        return '' # simply drop whatever value is there when it's a Null
    
    def __unhexFilter(value):
        if value[:5].lower() == 'hex: ':
            value = [ int(x, 16) for x in value[5:].split('.') ]
        elif value[0] == '"' and value[-1] == '"':
            value = value[1:-1]
        return value

    filterMap = {
        '4': __nullFilter,
        '6': __unhexFilter
        }

    def parse(self, line): return line.split('|', 2)

    def evaluateOid(self, oid):
        return univ.ObjectIdentifier(oid)

    def evaluateValue(self, tag, value):
        return tag, self.tagMap[tag](
            self.filterMap.get(tag, lambda x: x)(value.strip())
            )
    
    def evaluate(self, line, oidOnly=False, muteValueError=True):
        oid, tag, value = self.parse(line)
        if oidOnly:
            value = None
        else:
            try:
                tag, value = self.evaluateValue(tag, value)
            except:
                if muteValueError:
                    value = rfc1902.OctetString(
                        'SIMULATOR VALUE ERROR %s' % repr(value)
                        )
                else:
                    raise
        return self.evaluateOid(oid), value

class MvcParser(DumpParser):
    ext = os.path.extsep + 'MVC'  # just an alias

class SnmprecParser:
    ext = os.path.extsep + 'snmprec'
    tagMap = {}
    for t in ( rfc1902.Gauge32,
               rfc1902.Integer32,
               rfc1902.IpAddress,
               univ.Null,
               univ.ObjectIdentifier,
               rfc1902.OctetString,
               rfc1902.TimeTicks,
               rfc1902.Opaque,
               rfc1902.Counter32,
               rfc1902.Counter64 ):
        tagMap[str(sum([ x for x in t.tagSet[0] ]))] = t

    def parse(self, line): return line.strip().split('|', 2)

    def evaluateOid(self, oid):
        return univ.ObjectIdentifier(oid)
    
    def evaluateValue(self, tag, value):
        # Unhexify
        if tag[-1] == 'x':
            tag = tag[:-1]
            value = [int(value[x:x+2], 16) for x in  range(0, len(value), 2)]
        return tag, self.tagMap[tag](value)

    def evaluate(self, line, oidOnly=False, muteValueError=True):
        oid, tag, value = self.parse(line)
        if oidOnly:
            value = None
        else:
            try:
                tag, value = self.evaluateValue(tag, value)                
            except:
                if muteValueError:
                    value = rfc1902.OctetString(
                        'SIMULATOR VALUE ERROR %s' % repr(value)
                        )
                else:
                    raise
        return self.evaluateOid(oid), value

parserSet = {
    DumpParser.ext: DumpParser(),
    MvcParser.ext: MvcParser(),
    SnmprecParser.ext: SnmprecParser()
    }

# Device text file and OID index

class DeviceFile:
    openedQueue = []
    maxQueueEntries = 31  # max number of open text and index files
    def __init__(self, textFile):
        self.__textFile = textFile
        try:
            self.__dbFile = textFile[:textFile.rindex(os.path.extsep)]
        except ValueError:
            self.__dbFile = textFile

        self.__dbFile = self.__dbFile + os.path.extsep + 'dbm'
    
        self.__db = self.__text = None
        self.__dbType = '?'
        
    def indexText(self, textParser, forceIndexBuild=False):
        textFileStamp = os.stat(self.__textFile)[8]

        # gdbm on OS X seems to voluntarily append .db, trying to catch that
        
        indexNeeded = forceIndexBuild
        
        for dbFile in (
            self.__dbFile + os.path.extsep + 'db',
            self.__dbFile
            ):
            if os.path.exists(dbFile):
                if textFileStamp < os.stat(dbFile)[8]:
                    if indexNeeded:
                        sys.stdout.write('Forced index rebuild %s\r\n' % dbFile)
                else:
                    indexNeeded = True
                    sys.stdout.write('Index %s out of date\r\n' % dbFile)
                break
        else:
            indexNeeded = True
            sys.stdout.write('Index does not exist for %s\r\n' % self.__textFile)
            
        if indexNeeded:
            sys.stdout.write('Indexing device file %s...' % self.__textFile)
            sys.stdout.flush()

            text = open(self.__textFile)
            
            db = dbm.open(self.__dbFile, 'n')
        
            lineNo = 0
            offset = 0
            while 1:
                line = text.readline()
                if not line:
                    break
            
                lineNo = lineNo + 1

                try:
                    oid, tag, val = textParser.parse(line)
                except Exception:
                    db.close()
                    os.remove(self.__dbFile)
                    raise Exception(
                        'Data error at %s:%d: %s' % (
                            self.__textFile, lineNo, sys.exc_info()[1]
                            )
                        )

                if validateData:
                    try:
                        textParser.evaluateOid(oid)
                    except Exception:
                        db.close()
                        os.remove(self.__dbFile)
                        raise Exception(
                            'OID error at %s:%d: %s' % (
                                self.__textFile, lineNo, sys.exc_info()[1]
                                )
                            )
                    try:
                        textParser.evaluateValue(tag, val)
                    except Exception:
                        sys.stdout.write(
                            '*** Error at line %s, value %r: %s\r\n' % \
                            (lineNo, val, sys.exc_info()[1])
                            )
                        
                db[oid] = str(offset)

                offset = text.tell()

            text.close()
            db.close()
        
            sys.stdout.write('...%d entries indexed\r\n' % (lineNo - 1,))

        self.__dbType = whichdb(self.__dbFile)

        return self

    def close(self):
        self.__text.close()
        self.__db.close()
        self.__db = self.__text = None
    
    def getHandles(self):
        if self.__db is None:
            if len(DeviceFile.openedQueue) > self.maxQueueEntries:
                DeviceFile.openedQueue[0].close()
                del DeviceFile.openedQueue[0]

            DeviceFile.openedQueue.append(self)

            self.__text = open(self.__textFile)
            
            self.__db = dbm.open(self.__dbFile)

        return self.__text, self.__db

    def __str__(self):
        return 'file %s, %s-indexed, %s' % (
            self.__textFile, self.__dbType, self.__db and 'opened' or 'closed'
            )

# Collect device files

def getDevices(tgtDir, topLen=None):
    if topLen is None:
        topLen = len(tgtDir.split(os.path.sep))
    dirContent = []
    for dFile in os.listdir(tgtDir):
        fullPath = tgtDir + os.path.sep + dFile
        inode = os.stat(fullPath)
        if inode[0] & 0x4000:
            dirContent = dirContent + getDevices(fullPath, topLen)
            continue            
        if not (inode[0] & 0x8000):
            continue
        try:
            dExt = dFile[dFile.rindex(os.path.extsep):]
        except ValueError:
            continue
        if dExt not in parserSet:
            continue
        fullPath = tgtDir + os.path.sep + dFile
        relPath = fullPath.split(os.path.sep)[topLen:]
        dirContent.append(
            (fullPath, parserSet[dExt], os.path.sep.join(relPath)[:-len(dExt)])
            )
    return dirContent

# Lightweignt MIB instrumentation (API-compatible with pysnmp's)

class MibInstrumController:
    def __init__(self, deviceFile, textParser):
        self.__deviceFile = deviceFile
        self.__textParser = textParser

    def __str__(self): return str(self.__deviceFile)

    # In-place, by-OID binary search

    def __searchOid(self, text, oid):
        lo = mid = 0
        text.seek(0, 2)
        hi = sz = text.tell()
        while lo < hi:
            mid = (lo+hi)//2
            while mid:
                text.seek(mid)
                c = text.read(1)
                if c == '\n':
                    mid = mid + 1
                    break
                mid = mid - 1
            if not mid:
                text.seek(mid)
            line = text.readline()
            try:
                midval, _ = self.__textParser.evaluate(line, oidOnly=True)
            except Exception:
                raise Exception(
                    'Data error at %s for %s: %s' % (self,oid,sys.exc_info()[1])
                    )                
            if midval < oid:
                lo = mid + len(line)
            elif midval > oid:
                hi = mid
            else:
                return mid
            if mid >= sz:
                return sz
        if lo == mid:
            return lo
        else:
            return hi

    def __doVars(self, varBinds, nextFlag=False, writeMode=False):
        rspVarBinds = []

        if nextFlag:
            errorStatus = exval.endOfMib
        else:
            errorStatus = exval.noSuchInstance

        text, db = self.__deviceFile.getHandles()
        
        for oid, val in varBinds:
            textOid = univ.OctetString(
                '.'.join([ '%s' % x for x in oid ])
                ).asOctets()
            try:
                offset = db[textOid]
                exactMatch = True
            except KeyError:
                if nextFlag:
                    offset = self.__searchOid(text, oid)
                    exactMatch = False
                else:
                    rspVarBinds.append((oid, errorStatus))
                    continue

            offset = int(offset)

            text.seek(offset)

            line = text.readline()

            if nextFlag and exactMatch:
                line = text.readline()

            if not line:
                rspVarBinds.append((oid, errorStatus))
                continue

            try:
                oid, val = self.__textParser.evaluate(line)
            except Exception:
                raise Exception(
                    'Data error at %s for %s: %s' % (self, textOid, sys.exc_info()[1])
                    )

            rspVarBinds.append((oid, val))

        return rspVarBinds
    
    def readVars(self, varBinds, acInfo=None):
        return self.__doVars(varBinds, False)

    def readNextVars(self, varBinds, acInfo=None):
        return self.__doVars(varBinds, True)

    def writeVars(self, varBinds, acInfo=None):
        return self.__doVars(varBinds, False, True)

# Devices index as a MIB instrumentaion at a dedicated SNMP context

class DevicesIndexInstrumController:
    indexSubOid = (1,)
    def __init__(self, baseOid=(1, 3, 6, 1, 4, 1, 20408, 999)):
        self.__db = indices.OidOrderedDict()
        self.__indexOid = baseOid + self.indexSubOid
        self.__idx = 1

    def readVars(self, varBinds, acInfo=None):
        return [ (vb[0], self.__db.get(vb[0], exval.noSuchInstance)) for vb in varBinds ]

    def __getNextVal(self, key, default):
        try:
            key = self.__db.nextKey(key)
        except KeyError:
            return key, default
        else:
            return key, self.__db[key]
                                                            
    def readNextVars(self, varBinds, acInfo=None):
        return [ (vb[0], self.__getNextVal(vb[0], exval.endOfMib)) for vb in varBinds ]        

    def writeVars(self, varBinds, acInfo=None):
        return [ (vb[0], exval.noSuchInstance) for vb in varBinds ]        
    
    def addDevice(self, *args):
        for idx in range(len(args)):
            self.__db[
                self.__indexOid + (idx+1, self.__idx)
                ] = rfc1902.OctetString(args[idx])
        self.__idx = self.__idx + 1

devicesIndexInstrumController = DevicesIndexInstrumController()

# Basic SNMP engine configuration

if v2cArch:
    contexts = {}
else:
    snmpEngine = engine.SnmpEngine()

    config.addContext(snmpEngine, '')

    snmpContext = context.SnmpContext(snmpEngine)
        
    config.addV3User(
        snmpEngine, v3User,
        config.usmHMACMD5AuthProtocol, v3AuthKey,
        v3PrivProto, v3PrivKey
        )
        
# Build pysnmp Managed Objects base from device files information

for fullPath, textParser, communityName in getDevices(deviceDir):
    mibInstrum = MibInstrumController(
        DeviceFile(fullPath).indexText(textParser, forceIndexBuild), textParser
        )

    sys.stdout.write('Device %s\r\nSNMPv1/2c community name: %s\r\n' % \
                     (mibInstrum, communityName))

    if v2cArch:
        contexts[univ.OctetString(communityName)] = mibInstrum
        
        devicesIndexInstrumController.addDevice(
            fullPath, communityName
            )
    else:
        agentName = contextName = md5(univ.OctetString(communityName).asOctets()).hexdigest()

        if not v3Only:
            config.addV1System(
                snmpEngine, agentName, communityName, contextName=contextName
                )

        snmpContext.registerContextName(contextName, mibInstrum)
                 
        devicesIndexInstrumController.addDevice(
            fullPath, communityName, contextName
            )
                 
        sys.stdout.write('SNMPv3 context name: %s\r\n' % (contextName,))
        
    sys.stdout.write('%s\r\n' % ('-+' * 33,))
        
if v2cArch:
    def getBulkHandler(varBinds, nonRepeaters, maxRepetitions, readNextVars):
        if nonRepeaters < 0: nonRepeaters = 0
        if maxRepetitions < 0: maxRepetitions = 0
        N = min(nonRepeaters, len(varBinds))
        M = int(maxRepetitions)
        R = max(len(varBinds)-N, 0)
        if nonRepeaters:
            rspVarBinds = readNextVars(varBinds[:int(nonRepeaters)])
        else:
            rspVarBinds = []
        if M and R:
            for i in range(N,  R):
                varBind = varBinds[i]
                for r in range(1, M):
                    rspVarBinds.extend(readNextVars((varBind,)))
                    varBind = rspVarBinds[-1]

        return rspVarBinds
    
    def commandResponderCbFun(transportDispatcher, transportDomain,
                              transportAddress, wholeMsg):
        while wholeMsg:
            msgVer = api.decodeMessageVersion(wholeMsg)
            if msgVer in api.protoModules:
                pMod = api.protoModules[msgVer]
            else:
                sys.stdout.write('Unsupported SNMP version %s\r\n' % (msgVer,))
                return
            reqMsg, wholeMsg = decoder.decode(
                wholeMsg, asn1Spec=pMod.Message(),
                )
            
            communityName = reqMsg.getComponentByPosition(1)
            if communityName not in contexts:
                sys.stdout.write('Unknown community name %s from %s:%s\r\n' % (
                    communityName, transportDomain, transportAddress
                    ))
                return wholeMsg
            
            rspMsg = pMod.apiMessage.getResponse(reqMsg)
            rspPDU = pMod.apiMessage.getPDU(rspMsg)        
            reqPDU = pMod.apiMessage.getPDU(reqMsg)
    
            if reqPDU.isSameTypeWith(pMod.GetRequestPDU()):
                backendFun = contexts[communityName].readVars
            elif reqPDU.isSameTypeWith(pMod.SetRequestPDU()):
                backendFun = contexts[communityName].writeVars
            elif reqPDU.isSameTypeWith(pMod.GetNextRequestPDU()):
                backendFun = contexts[communityName].readNextVars
            elif hasattr(pMod, 'GetBulkRequestPDU') and \
                     reqPDU.isSameTypeWith(pMod.GetBulkRequestPDU()):
                if not msgVer:
                    sys.stdout.write('GETBULK over SNMPv1 from %s:%s\r\n' % (
                        transportDomain, transportAddress
                        ))
                    return wholeMsg
                backendFun = lambda varBinds: getBulkHandler(varBinds,
                    pMod.apiBulkPDU.getNonRepeaters(reqPDU),
                    pMod.apiBulkPDU.getMaxRepetitions(reqPDU),
                    contexts[communityName].readNextVars)
            else:
                sys.stdout.write('Unsuppored PDU type %s from %s:%s\r\n' % (
                    reqPDU.__class__.__name__, transportDomain,
                    transportAddress
                    ))
                return wholeMsg
    
            varBinds = backendFun(
                pMod.apiPDU.getVarBinds(reqPDU)
                )

            # Poor man's v2c->v1 translation
            
            if not msgVer:
                for idx in range(len(varBinds)):
                    oid, val = varBinds[idx]
                    if val.tagSet in (rfc1902.Counter64.tagSet,
                                      univ.Null.tagSet):
                        varBinds = pMod.apiPDU.getVarBinds(reqPDU)
                        pMod.apiPDU.setErrorStatus(rspPDU, 5)
                        pMod.apiPDU.setErrorIndex(rspPDU, idx+1)
                        break

            pMod.apiPDU.setVarBinds(rspPDU, varBinds)
            
            transportDispatcher.sendMessage(
                encoder.encode(rspMsg), transportDomain, transportAddress
                )
            
        return wholeMsg

    # Configure access to devices index
    
    contexts['index'] = devicesIndexInstrumController
    
    # Configure socket server
    
    transportDispatcher = AsynsockDispatcher()
    transportDispatcher.registerTransport(
            udp.domainName, udp.UdpTransport().openServerMode(agentAddress)
            )
    transportDispatcher.registerRecvCbFun(commandResponderCbFun)
else:
    sys.stdout.write('SNMPv3 credentials:\r\nUsername: %s\r\nAuthentication key: %s\r\nEncryption (privacy) key: %s\r\nEncryption protocol: %s\r\n' % (v3User, v3AuthKey, v3PrivKey, v3PrivProto))

    # Configure access to devices index

    config.addV1System(snmpEngine, 'index',
                       'index', contextName='index')

    snmpContext.registerContextName(
        'index', devicesIndexInstrumController
        )

    # Configure socket server

    config.addSocketTransport(
        snmpEngine,
        udp.domainName,
        udp.UdpTransport().openServerMode(agentAddress)
        )

    # SNMP applications

    cmdrsp.GetCommandResponder(snmpEngine, snmpContext)
    cmdrsp.SetCommandResponder(snmpEngine, snmpContext)
    cmdrsp.NextCommandResponder(snmpEngine, snmpContext)
    cmdrsp.BulkCommandResponder(snmpEngine, snmpContext)

    transportDispatcher = snmpEngine.transportDispatcher
    
sys.stdout.write('\r\nListening at %s\r\n' % (agentAddress,))

# Run mainloop

transportDispatcher.jobStarted(1) # server job would never finish
transportDispatcher.runDispatcher()
