#!python
# -*- coding: UTF-8 -*-
# Service Partner LINE: A Manager Daemon for the Pentacle System Bus
# Copyright 2011 Clint Banis & Penobscot Robotics.  All rights reserved.
# Pronounciation: splīn
#

from ..application import bootServer, Application
from ..architecture import ServiceBase, Event
from ..config import Configuration
from ..client import Client, ClientOptions, Session, Authorization
from ..runtime import breakOn, getCurrentSystemTime, Object, LookupObject, thisProcessId, nth
from ..network import SocketBindMethod, AsyncoreControl
from ..storage import StorageUnit
from ..packaging import Fault

from .. import buildApplicationVersion

from . import __version__ as busVersion
from . import *
from .services import *

import socket
import errno

# Todo: Merge this functionality with pentacle application.
# (Note that this is a subsystem identity, actually, specific to the service API)
SERVICE_NAME = 'SplineBus'
__service_identity__ = buildApplicationVersion(SERVICE_NAME, busVersion)

class ServiceManager(ServiceBase):
    NAME = ServiceManagerName
    Methods = ['Identify', 'RegisterAsPartner', 'GetManagerStats', 'GetPartnerInfo']

    # Managing runlevels:
    class PartnerManager:
        class PartnerStorage(StorageUnit):
            STORAGE_REALM = 'PartnerStorage'

            class Interface(StorageUnit.Interface):
                def getServicePort(self):
                    return self.getValue('servicePort')
                def setServicePort(self, port):
                    self.setValue('servicePort', port)

                def getBootTime(self):
                    return self.getValue('bootTime')
                def setBootTime(self, time):
                    self.setValue('bootTime', time)

        def __init__(self, svcMgr, apiMgr):
            # Associate service and API managers with routines accessible to partner services.
            self.svcMgr = svcMgr
            self.apiMgr = apiMgr

        def OpenStorage(self, partnerName):
            return self.PartnerStorage.Open(self.apiMgr.application, partnerName)

        DYNAMIC_PORT_RANGE = [30750, 31000]
        def getDynamicPort(self, bindAddress = '127.0.0.1'):
            bindMethod = SocketBindMethod.New(bindAddress)
            try: return OpenAvailablePort(xrange(*self.DYNAMIC_PORT_RANGE), bindMethod)
            except SystemError, e:
                raise SystemError('%s in range: %s' % (e, self.DYNAMIC_PORT_RANGE))

        def getManagerPort(self):
            return self.apiMgr.application.network.port

        # Actions.
        PartnerBooted = Event('spline-partner-booted')
        def partnerBooted(self, partner):
            self.PartnerBooted(self.apiMgr.application.engine, partner)

        PartnerInjected = Event('spline-partner-injected')
        def partnerInjected(self, partner):
            self.PartnerInjected(self.apiMgr.application.engine, partner)

        PartnerUpdated = Event('spline-partner-updated')
        def partnerUpdated(self, partner):
            self.PartnerUpdated(self.apiMgr.application.engine, partner)

    def Activate(self, apiMgr):
        # Configurate the service manager.
        cfg = apiMgr.application.config.getSectionObject('Spline')
        self.partners = {}

        # Provide unique access to the manager from partner service handlers.
        partnerManager = self.PartnerManager(self, apiMgr)

        loadOrder = []
        for pCfgName in cfg.getOptionMultiple('partner'):
            if pCfgName:
                # todo: fail on load?
                pCfg = Configuration.FromFile(pCfgName)
                partner = Partner.FromConfig(pCfg)
                if partner.name in self.partners:
                    pass # log error
                else:
                    self.partners[partner.name] = partner
                    loadOrder.append(partner.name)

                    # Load state of currently-running service.
                    partner.RestoreTrackedState(partnerManager)

        # Stats.
        self.activationTime = getCurrentSystemTime()
        if cfg.getOption('public-access', simplify = True):
            apiMgr.application.security.grantPublicAction('access-api:%s' % self.NAME)

        # External Partner Connections.
        #@breakOn
        def doRegisterAsPartner(configString, digest = None):
            # Load configuration.
            pCfg = Configuration.FromString(configString)
            partner = Partner.FromConfig(pCfg)
            name = partner.name

            # Find by name in already-loaded partners.
            try: match = self.partners[name]
            except KeyError:
                # Inject new partner with configured custom handler.
                self.partners[name] = partner
                loadOrder.append(partner)

                apiMgr.application.log('Injecting Partner: %s' % name)
                partner.inject(partnerManager, pCfg)

            else:
                # Match authorization key.
                if not match.isAuthorized(partner, digest, configString):
                    raise AuthorizationError('Not authorized: %s' % name)

                # Update configuration.
                apiMgr.application.log('Updating Partner: %s' % name)
                match.updateStatus(partnerManager, pCfg)

        def doGetLoadOrder():
            return list(loadOrder) # copy

        # Defined inline to protect cellular variables.
        self.RegisterAsPartner = doRegisterAsPartner
        self.GetLoadOrder = doGetLoadOrder

        # Do in another thread.
        @nth
        def bootPartners():
            # Boot partner runlevels.
            for n in loadOrder:
                # todo: ignore/log problems?  disabled partner state?
                apiMgr.application.log('Booting Partner: %s' % n)
                self.partners[n].boot(partnerManager)

    ##    def Deactivate(self):
    ##        # Auto-kill.
    ##        pass

    def Identify(self):
        return __service_identity__

    def GetManagerStats(self):
        return dict(running_duration = getCurrentSystemTime() - self.activationTime,
                    partners = self.partners.keys(),
                    process_id = thisProcessId())

    def GetPartnerInfo(self, name):
        return self.partners[name].GetInfo()

# Startup.
def isInstanceRunning(options):
    # First attempt to see if an instance is already running.
    with Session(Authorization(options.username or '',
                               options.secret_key or '') \
                 .Open(options.address, options.port)) as client:

        DEBUG('Opening Spline API for Identification...')
        with client.api(ServiceManager.NAME) as spline:
            if isRecognizedServer(spline.Identify(), APPLICATION_NAME):
                # Already started -- do nothing.
                return True

    raise UnknownServer(identity)

def Start(config_file, argv = None):
    cfg = Configuration.FromCmdln(argv, config_file, ClientOptions, Application)

    try: running = isInstanceRunning(cfg.set)
    except socket.error, e:
        if e.errno not in [errno.EAGAIN, errno.EBADF, errno.ECONNREFUSED]:
            raise

        running = False
    except (UnknownServer, AuthenticationError), e:
        print '%s: %s' % (e.__class__.__name__, e)
        return
    except Fault, fault:
        print 'FAULT ON CONNECT:\n%s' % fault.toString(True)
        return

    if not running:
        # Boot up a new instance.
        DEBUG('Booting Spline...')
        boot = bootServer # breakOn(bootServer)
        app = boot(config_file = config_file)

        # Ensure the ServiceManager is installed -- this blocks the
        # rest of the application (including engine-message processing).
        svcMgr = app.api.loadServiceApiObject(ServiceManager)

        # Want to start up the host network:
        DEBUG('services booted')
        AsyncoreControl.waitForAsyncoreEnd()
        DEBUG('Spline host-ready')

        app.run()

        # What about shutdown?? We may want to kill off some children...
        # Or, at least notify listeners.  I suppose notification would
        # have to be done within the loop, so really a timed shutdown.
        #
        # (Or, do this within Deactivate)
        for partnerName in svcMgr.GetLoadOrder():
            svcMgr.partners[partnerName].doAutokill()

if __name__ == '__main__':
    # import pdb; pdb.set_trace()
    Start(getDefaultSplineConfigFilename())
