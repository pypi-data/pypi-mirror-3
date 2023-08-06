# GET Command Generator
# Sends a number of GET queries to various Agents
from pysnmp.entity.rfc3413.oneliner import cmdgen

# ( ( authData, transportTarget, varNames ), ... )
targets = (
    # 1-st target (SNMPv1 over IPv4/UDP)
    ( cmdgen.CommunityData('public', mpModel=0),
      cmdgen.UdpTransportTarget(('localhost', 161)),
      ( cmdgen.MibVariable('SNMPv2-MIB', 'sysDescr', 0),
        cmdgen.MibVariable('SNMPv2-MIB', 'sysLocation', 0) ) ),
    # 2-nd target (SNMPv2c over IPv4/UDP)
    ( cmdgen.CommunityData('public'),
      cmdgen.UdpTransportTarget(('localhost', 161)),
      ( cmdgen.MibVariable('SNMPv2-MIB', 'sysDescr', 0),
        cmdgen.MibVariable('SNMPv2-MIB', 'sysLocation', 0) ) ),
    # 3-nd target (SNMPv3 over IPv4/UDP)
    ( cmdgen.UsmUserData('usr-md5-des', 'authkey1', 'privkey1'),
      cmdgen.UdpTransportTarget(('localhost', 161)),
      ( cmdgen.MibVariable('SNMPv2-MIB', 'sysDescr', 0),
        cmdgen.MibVariable('SNMPv2-MIB', 'sysLocation', 0) ) ),
    # 4-th target (SNMPv3 over IPv6/UDP)
    ( cmdgen.UsmUserData('usr-md5-none', 'authkey1'),
      cmdgen.Udp6TransportTarget(('::1', 161)),
      ( cmdgen.MibVariable('SNMPv2-MIB', 'sysDescr', 0),
        cmdgen.MibVariable('SNMPv2-MIB', 'sysLocation', 0) ) ),
    # N-th target
    # ...
)

def cbFun(sendRequestHandle, errorIndication, errorStatus, errorIndex,
          varBinds, cbCtx):
    (authData, transportTarget) = cbCtx
    print('%s via %s' % (authData, transportTarget))
    if errorIndication:
        print(errorIndication)
        return 1
    if errorStatus:
        print('%s at %s' % (
            errorStatus.prettyPrint(),
            errorIndex and varBinds[int(errorIndex)-1] or '?'
            )
        )
        return 1
    
    for oid, val in varBinds:
        if val is None:
            print(oid.prettyPrint())
        else:
            print('%s = %s' % (oid.prettyPrint(), val.prettyPrint()))

cmdGen  = cmdgen.AsynCommandGenerator()

for authData, transportTarget, varNames in targets:
    cmdGen.getCmd(
        authData, transportTarget, varNames,
        # User-space callback function and its context
        (cbFun, (authData, transportTarget)),
        lookupNames=True, lookupValues=True
    )

cmdGen.snmpEngine.transportDispatcher.runDispatcher()
