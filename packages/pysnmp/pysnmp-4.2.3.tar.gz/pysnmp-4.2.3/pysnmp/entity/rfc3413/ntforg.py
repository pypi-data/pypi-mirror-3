import time
from pyasn1.compat.octets import null
from pysnmp.entity.rfc3413 import config
from pysnmp.proto.proxy import rfc2576
from pysnmp.proto.api import v2c
from pysnmp.smi import error
from pysnmp import nextid
from pysnmp import debug

getNextHandle = nextid.Integer(0x7fffffff)

class NotificationOriginator:
    acmID = 3  # default MIB access control method to use
    def __init__(self, snmpContext):
        self.__pendingReqs = {}
        self.__pendingNotifications = {}
        self.__context = snmpContext

    def processResponsePdu(
        self,
        snmpEngine,
        messageProcessingModel,
        securityModel,
        securityName,
        securityLevel,
        contextEngineId,
        contextName,
        pduVersion,
        PDU,
        statusInformation,
        sendPduHandle,
        cbInfo
        ):
        (cbFun, cbCtx) = cbInfo
        # 3.3.6d
        if sendPduHandle not in self.__pendingReqs:
            raise error.PySnmpError('Missing sendPduHandle %s' % sendPduHandle)

        ( origTransportDomain,
          origTransportAddress,
          origMessageProcessingModel,
          origSecurityModel,
          origSecurityName,
          origSecurityLevel,
          origContextEngineId,
          origContextName,
          origPduVersion,
          origPdu,
          origTimeout,
          origRetryCount,
          origRetries,
          metaSendPduHandle
          ) = self.__pendingReqs[sendPduHandle]

        del self.__pendingReqs[sendPduHandle]

        self.__pendingNotifications[metaSendPduHandle] -= 1

        snmpEngine.transportDispatcher.jobFinished(id(self))

        if statusInformation:
            debug.logger & debug.flagApp and debug.logger('processResponsePdu: metaSendPduHandle %s, sendPduHandle %s statusInformation %s' % (metaSendPduHandle, sendPduHandle, statusInformation))
            if origRetries == origRetryCount:
                debug.logger & debug.flagApp and debug.logger('processResponsePdu: metaSendPduHandle %s, sendPduHandle %s retry count %d exceeded' % (metaSendPduHandle, sendPduHandle, origRetries))
                if not self.__pendingNotifications[metaSendPduHandle]:
                    del self.__pendingNotifications[metaSendPduHandle]
                    self._handleResponse(
                        metaSendPduHandle,
                        statusInformation['errorIndication'],
                        cbFun,
                        cbCtx
                    )
                return

            # Convert timeout in seconds into timeout in timer ticks
            timeoutInTicks = float(origTimeout)/100/snmpEngine.transportDispatcher.getTimerResolution()
        
            # 3.3.6a
            sendPduHandle = snmpEngine.msgAndPduDsp.sendPdu(
                snmpEngine,
                origTransportDomain,
                origTransportAddress,
                origMessageProcessingModel,
                origSecurityModel,
                origSecurityName,
                origSecurityLevel,
                origContextEngineId,
                origContextName,
                origPduVersion,
                origPdu,
                1,                              # expectResponse
                timeoutInTicks,
                self.processResponsePdu,
                (cbFun, cbCtx)
                )

            self.__pendingNotifications[metaSendPduHandle] += 1

            snmpEngine.transportDispatcher.jobStarted(id(self))

            debug.logger & debug.flagApp and debug.logger('processResponsePdu: metaSendPduHandle %s, sendPduHandle %s, timeout %d, retry %d of %d' % (metaSendPduHandle, sendPduHandle, origTimeout, origRetries, origRetryCount))
        
            # 3.3.6b
            self.__pendingReqs[sendPduHandle] = (
                origTransportDomain,
                origTransportAddress,
                origMessageProcessingModel,
                origSecurityModel,
                origSecurityName,
                origSecurityLevel,
                origContextEngineId,
                origContextName,
                origPduVersion,
                origPdu,
                origTimeout,
                origRetryCount,
                origRetries + 1,
                metaSendPduHandle
                )
            return

        # 3.3.6c
        if not self.__pendingNotifications[metaSendPduHandle]:
            del self.__pendingNotifications[metaSendPduHandle]
            self._handleResponse(metaSendPduHandle, None, cbFun, cbCtx)

    def _handleResponse(
        self,
        sendRequestHandle,
        errorIndication,
        cbFun,
        cbCtx):
        cbFun(sendRequestHandle, errorIndication, cbCtx)
    
    def sendNotification(
        self,
        snmpEngine,
        notificationTarget,
        notificationName,
        additionalVarBinds=None,
        cbFun=None,
        cbCtx=None,
        contextName=null
        ):
        # 3.3
        ( notifyTag,
          notifyType ) = config.getNotificationInfo(
            snmpEngine, notificationTarget
            )

        metaSendPduHandle = getNextHandle()

        debug.logger & debug.flagApp and debug.logger('sendNotification: metaSendPduHandle %s, notifyTag %s, notifyType %s' % (metaSendPduHandle, notifyTag, notifyType))
                
        contextMibInstrumCtl = self.__context.getMibInstrum(
            contextName
            )
        
        for targetAddrName in config.getTargetNames(snmpEngine, notifyTag):
            ( transportDomain,
              transportAddress,
              timeout,
              retryCount,
              params ) = config.getTargetAddr(snmpEngine, targetAddrName)
            ( messageProcessingModel,
              securityModel,
              securityName,
              securityLevel ) = config.getTargetParams(snmpEngine, params)

            debug.logger & debug.flagApp and debug.logger('sendNotification: metaSendPduHandle %s, notifyTag %s yields: transportDomain %s, transportAddress %r, securityModel %s, securityName %s, securityLevel %s' % (metaSendPduHandle, notifyTag, transportDomain, transportAddress, securityModel, securityName, securityLevel))

            # 3.3.1 XXX
# XXX filtering's yet to be implemented
#             filterProfileName = config.getNotifyFilterProfile(params)

#             ( filterSubtree,
#               filterMask,
#               filterType ) = config.getNotifyFilter(filterProfileName)

            varBinds = []
            
            # 3.3.2 & 3.3.3
            sysUpTime, = contextMibInstrumCtl.mibBuilder.importSymbols(
                '__SNMPv2-MIB', 'sysUpTime'
                )

            if additionalVarBinds:
                for varName, varVal in additionalVarBinds:
                    if varName == sysUpTime.name:
                        varBinds.append((varName, varVal))
                        break
            if not varBinds:
                varBinds.append((sysUpTime.name,
                                 sysUpTime.syntax.clone())) # for actual value

            snmpTrapOid, = contextMibInstrumCtl.mibBuilder.importSymbols(
                '__SNMPv2-MIB', 'snmpTrapOID'
                )
            if notificationName:
                varBinds.append(
                    (snmpTrapOid.name,
                     snmpTrapOid.syntax.clone(notificationName))
                    )
            else:
                varBinds.append((snmpTrapOid.name, snmpTrapOid.syntax))

# XXX it's still not clear how to instantiate OBJECTS clause
#             # Get notification objects names
#             for notificationObject in snmpTrapVal.getObjects():
#                 mibNode, = contextMibInstrumCtl.mibBuilder.importSymbols(
#                     *notificationObject
#                     )
#                 try:
#                     objectInstance = mibNode.getNode(mibNode.name + (0,))
#                 except error.SmiError:
#                     return
#                 varBinds.append((objectInstance.name, objectInstance.syntax))

            for varName, varVal in additionalVarBinds:
                if varName in (sysUpTime.name, snmpTrapOid.name):
                    continue
                try:
                    snmpEngine.accessControlModel[self.acmID].isAccessAllowed(
                        snmpEngine, securityModel, securityName,
                        securityLevel, 'notify', contextName, varName
                        )
                except error.SmiError:
                    debug.logger & debug.flagApp and debug.logger('sendNotification: OID %s not allowed for %s, droppping notification' % (varName, securityName))
                    return
                else:
                    varBinds.append((varName, varVal))

            # 3.3.4
            if notifyType == 1:
                pdu = v2c.SNMPv2TrapPDU()
            elif notifyType == 2:
                pdu = v2c.InformRequestPDU()
            else:
                raise RuntimeError()
            v2c.apiPDU.setDefaults(pdu)
            v2c.apiPDU.setVarBinds(pdu, varBinds)

            # User-side API assumes SMIv2
            if messageProcessingModel == 0:
                pdu = rfc2576.v2ToV1(pdu)
                pduVersion = 0
            else:
                pduVersion = 1
            
            # 3.3.5
            if notifyType == 1:
                snmpEngine.msgAndPduDsp.sendPdu(
                    snmpEngine,
                    transportDomain,
                    transportAddress,
                    messageProcessingModel,
                    securityModel,
                    securityName,
                    securityLevel,
                    self.__context.contextEngineId,
                    contextName,
                    pduVersion,
                    pdu,
                    None
                    )
            else:
                # Convert timeout in seconds into timeout in timer ticks
                timeoutInTicks = float(timeout)/100/snmpEngine.transportDispatcher.getTimerResolution()

                # 3.3.6a
                sendPduHandle = snmpEngine.msgAndPduDsp.sendPdu(
                    snmpEngine,
                    transportDomain,
                    transportAddress,
                    messageProcessingModel,
                    securityModel,
                    securityName,
                    securityLevel,
                    self.__context.contextEngineId,
                    contextName,
                    pduVersion,
                    pdu,
                    1,                      # expectResponse
                    timeoutInTicks,
                    self.processResponsePdu,
                    (cbFun, cbCtx)
                    )

                debug.logger & debug.flagApp and debug.logger('sendNotification: metaSendPduHandle %s, sendPduHandle %s, timeout %d' % (metaSendPduHandle, sendPduHandle, timeout))
                
                # 3.3.6b
                self.__pendingReqs[sendPduHandle] = (
                    transportDomain,
                    transportAddress,
                    messageProcessingModel,
                    securityModel,
                    securityName,
                    securityLevel,
                    self.__context.contextEngineId,
                    contextName,
                    pduVersion,
                    pdu,
                    timeout,
                    retryCount,
                    1,
                    metaSendPduHandle
                )
               
                if metaSendPduHandle not in self.__pendingNotifications:
                    self.__pendingNotifications[metaSendPduHandle] = 0
                self.__pendingNotifications[metaSendPduHandle] += 1

                snmpEngine.transportDispatcher.jobStarted(id(self))

        debug.logger & debug.flagApp and debug.logger('sendNotification: metaSendPduHandle %s, notification(s) sent' % metaSendPduHandle)

        return metaSendPduHandle

# XXX
# move/group/implement config setting/retrieval at a stand-alone module

