#
# SNMP Data Recorder
#
# Written by Ilya Etingof <ilya@glas.net>, 2010-2011
#

import getopt
import time
import sys
from pyasn1.type import univ
from pysnmp.proto import rfc1902
from pysnmp.entity import engine, config
from pysnmp.carrier.asynsock.dgram import udp
from pysnmp.entity.rfc3413 import cmdgen

# Defaults
quietFlag = False
snmpVersion = 1
snmpCommunity = 'public'
v3User = None
v3AuthKey = None
v3PrivKey = None
v3AuthProto = config.usmNoAuthProtocol
v3PrivProto = config.usmNoPrivProtocol
v3Context = ''
agentAddress = (None, 161)
startOID = (1, 3, 6)
stopOID = None
outputFile = sys.stderr

helpMessage = 'Usage: %s [--help] [--debug=<category>] [--quiet] [--v1|2c|3] [--community=<string>] [--v3-user=<username>] [--v3-auth-key=<key>] [--v3-priv-key=<key>] [--v3-auth-proto=<MD5|SHA>] [--v3-priv-proto=<DES|AES>] [--context=<string>] [--agent-address=<IP>] [--agent-port] [--start-oid=<OID>] [--stop-oid=<OID>] [--output-file=<filename>]\r\n' % sys.argv[0]

try:
    opts, params = getopt.getopt(sys.argv[1:], 'h',
        ['help', 'debug=', 'quiet', 'v1', 'v2c', 'v3', 'community=', 'v3-user=', 'v3-auth-key=', 'v3-priv-key=', 'v3-auth-proto=', 'v3-priv-proto=', 'context=', 'agent-address=', 'agent-port=', 'start-oid=', 'stop-oid=', 'output-file=']
        )
except Exception:
    sys.stdout.write('%s\r\n%s\r\n' % (sys.exc_info()[1], helpMessage))
    sys.exit(-1)

if params:
    sys.stdout.write('extra arguments supplied %s\r\n' % params + helpMessage)
    sys.exit(-1)

for opt in opts:
    if opt[0] == '-h' or opt[0] == '--help':
        sys.stdout.write(helpMessage)
        sys.exit(-1)
    if opt[0] == '--debug':
        debug.setLogger(debug.Debug(opt[1]))
    if opt[0] == '--quiet':
        quietFlag = True
    if opt[0] == '--v1':
        snmpVersion = 0
    if opt[0] == '--v2c':
        snmpVersion = 1
    if opt[0] == '--v3':
        snmpVersion = 3
    if opt[0] == '--community':
        snmpCommunity = opt[1]
    if opt[0] == '--v3-user':
        v3User = opt[1]
    if opt[0] == '--v3-auth-key':
        v3AuthKey = opt[1]
    if opt[0] == '--v3-auth-proto':
        if opt[1].upper() == 'MD5':
            v3AuthProto = config.usmHMACMD5AuthProtocol
        elif opt[1].upper() == 'SHA':
            v3AuthProto = config.usmHMACSHAAuthProtocol
        else:
            sys.stdout.write('bad v3 authentication protocol\r\n')
            sys.exit(-1)        
    if opt[0] == '--v3-priv-key':
        v3PrivKey = opt[1]
    if opt[0] == '--v3-priv-proto':
        if opt[1].upper() == 'DES':
            v3PrivProto = config.usmDESPrivProtocol
        elif opt[1].upper() == 'AES':
            v3PrivProto = config.usmAesCfb128Protocol
        else:
            sys.stdout.write('bad v3 privacy protocol\r\n')
            sys.exit(-1)
    if opt[0] == '--context':
        snmpContext = opt[1]
    if opt[0] == '--agent-address':
        agentAddress = (opt[1], agentAddress[1])
    if opt[0] == '--agent-port':
        agentAddress = (agentAddress[0], int(opt[1]))
    if opt[0] == '--start-oid':
        startOID = tuple(univ.ObjectIdentifier(opt[1]))
    if opt[0] == '--stop-oid':
        stopOID = tuple(univ.ObjectIdentifier(opt[1]))
    if opt[0] == '--output-file':
        outputFile = open(opt[1], 'w')

# Catch missing params

if agentAddress[0] is None:
    sys.stdout.write('--agent-address is missing\r\n%s' % helpMessage)
    sys.exit(-1)
if snmpVersion == 3:
    if v3User is None:
        sys.stdout.write('--v3-user is missing\r\n%s' % helpMessage)
        sys.exit(-1)
    if v3PrivKey and not v3AuthKey:
        sys.stdout.write('--v3-auth-key is missing\r\n%s' % helpMessage)
        sys.exit(-1)

# SNMP configuration

snmpEngine = engine.SnmpEngine()

if snmpVersion == 3:
    if v3PrivKey is None and v3AuthKey is None:
        secLevel = 'noAuthNoPriv'
    elif v3PrivKey is None:
        secLevel = 'authNoPriv'
    else:
        secLevel = 'authPriv'
    if v3AuthKey is not None and v3AuthProto == config.usmNoAuthProtocol:
        v3AuthProto = config.usmHMACMD5AuthProtocol
    if v3PrivKey is not None and v3PrivProto == config.usmNoPrivProtocol:
        v3PrivProto = config.usmDESPrivProtocol
    config.addV3User(
        snmpEngine, v3User,
        v3AuthProto, v3AuthKey,
        v3PrivProto, v3PrivKey,
        )
else:
    v3User = 'agt'
    secLevel = 'noAuthNoPriv'
    config.addV1System(snmpEngine, v3User, snmpCommunity)

config.addTargetParams(snmpEngine, 'pms', v3User, secLevel, snmpVersion)

config.addTargetAddr(
    snmpEngine, 'tgt', config.snmpUDPDomain, agentAddress, 'pms'
    )

config.addSocketTransport(
    snmpEngine,
    config.snmpUDPDomain,
    udp.UdpSocketTransport().openClientMode()
    )

# Device file writer

def deviceFileOutput(oid, val):
    outputFile.write('%s|%s' % (
        oid.prettyPrint(), sum([ x for x in val.tagSet[0] ])
        ) )
    if val.tagSet in (univ.OctetString.tagSet,
                      rfc1902.Opaque.tagSet,
                      rfc1902.IpAddress.tagSet):
        nval = val.asNumbers()
        if nval and nval[-1] == 32 or [ x for x in nval if x < 32 or x > 126 ]:
            outputFile.write('x')
            val = ''.join([ '%.2x' % x for x in nval ])
    else:
        val = val.prettyPrint()

    outputFile.write('|%s\n' % val)

# SNMP worker

def cbFun(sendRequestHandle, errorIndication, errorStatus, errorIndex,
          varBindTable, cbCtx):
    if errorIndication and errorIndication != 'oidNotIncreasing':
        sys.stdout.write('%s\r\n' % errorIndication)
        return
    # SNMPv1 response may contain noSuchName error *and* SNMPv2c exception,
    # so we ignore noSuchName error here
    if errorStatus and errorStatus != 2:
        sys.stdout.write('%s\r\n' % errorStatus.prettyPrint())
        return
    for varBindRow in varBindTable:
        for oid, val in varBindRow:
            if val is None:
                continue
            deviceFileOutput(oid, val)
            cbCtx['count'] = cbCtx['count'] + 1
            if not quietFlag:
                sys.stdout.write('OIDs dumped: %s\r' % cbCtx['count']),
                sys.stdout.flush()
    for oid, val in varBindTable[-1]:
        if oid < startOID or stopOID and oid >= stopOID:
            return # stop on out of range condition
        if val is not None:
            break
    else:
        return # stop on end-of-table
    return 1 # continue walking

cmdGen = cmdgen.NextCommandGenerator()

cbCtx = {
    'count': 0
    }

cmdGen.sendReq(
    snmpEngine, 'tgt', ((startOID, None),), cbFun, cbCtx
    )

t = time.time()

snmpEngine.transportDispatcher.runDispatcher()

t = time.time() - t

if not quietFlag:
    sys.stdout.write(
        'OIDs dumped: %s, elapsed: %.2f sec, rate: %.2f OIDs/sec\r\n' % \
        (cbCtx['count'], t, t and cbCtx['count']//t or "fast")
        )
