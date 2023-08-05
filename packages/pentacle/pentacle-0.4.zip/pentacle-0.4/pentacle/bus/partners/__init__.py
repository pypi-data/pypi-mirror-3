# Client Bus -- Service Partner processes use these routines for backtalk.
# Also, non-partner processes can use these routines to access services.
from ...application import Application
from ...packaging import Fault
from ...client import Session, Client, Authorization
from ...config import INI
from .. import *

import os
import socket
import errno

# todo:
#   Not share the same application database files (directly)
#   Smooth over all configuration
#   How much autonomy does a service have if the manage isn't running?
#       Should it boot the manager?  No, but we can at least run and
#       then how do we communicate the port to spline-tracked state?

# Adhoc Service Partners
BASE = INI(Partner = dict(handler = 'adhoc')) # Err why adhoc again??

def partnerConf(name, port, **other):
    # Prepares a message that will be used to update the service manager partner records.
    return str(BASE + dict(Partner = dict(name = name),
                           Program = dict(service_port = port)) \
               + other)

def registerAs(partnerConfig, authKey, mgrOptions = None):
    assert isinstance(partnerConfig, basestring)
    if mgrOptions is None:
        mgrOptions = getDefaultSplineConfig().set

    from pentacle.client import Authorization, CalculateDigest
    digest = CalculateDigest(authKey, partnerConfig)

    # XXX This requires some kind of login to access the api, but
    # it's kind of hard to access this mode information that way,
    # so we do another hmac digest here??  Todo: Clean this up.
    auth = Authorization(mgrOptions.username or '', mgrOptions.secret_key or '')
    with Session(auth.Open(mgrOptions.address, mgrOptions.port)) as client:
        with client.api(ServiceManagerName) as spline:
            spline.RegisterAsPartner(partnerConfig, digest)

def getManagerOptions(appConfig, section = 'Manager'):
    # Really just trying to get another ConfigSet object
    ##    mgrConf = appConfig.getSectionObject(section).asDict()
    ##    mgrConf = INI(**{section: mgrConf})
    ##    return mgrConf.toConfigObject(default_section = section)
    return appConfig.ConfigSet(appConfig, section = section, simplify = True)

class PartneredApplication(Application):
    @classmethod
    def Main(self, argv = None):
        # A Pentacle server application that boots as a partner.
        app = self.Boot(argv)
        app.UpdateRegistration()
        app.run()

    class InitialMode(Application.InitialMode):
        def doIdentify(self, engine, peer):
            # See bus.isRecognizedServer and ProgramPartner.checkRunlevelActivity
            return '%s; partnerName = %s' % (engine.application.version,
                                             engine.application.partnerName)

    def IntegratePartnerName(self, partnerName):
        self.partnerName = partnerName

    def getConfiguration(self):
        # return dict(Application = dict(weblink = ''))
        return dict()

    def UpdateRegistration(self):
        # Also, get the spline manager port from the environment.

        partnerName = os.environ.get(PENTACLE_PARTNER_NAME_ENV_VAR)
        if partnerName:
            # Necessary for uniquely identifying partners by Spline.
            self.IntegratePartnerName(partnerName)

            # The primary payload is the service port.
            conf = self.getConfiguration()

            try: registerAs(partnerConf(partnerName, self.network.port, **conf),
                            os.environ.get(PENTACLE_PARTNER_AUTH_ENV_VAR, ''),
                            mgrOptions = getManagerOptions(self.config))

            except Fault, fault:
                print 'REGISTRATION ERROR:\n%s' % fault.toString(True)
            except socket.error, e:
                if e.errno in [errno.EAGAIN, errno.EBADF, errno.ECONNREFUSED]:
                    print 'SERVICE MANAGER NOT AVAILABLE (%s)' % errno.errorcode[e.errno]
                else:
                    raise

Main = PartneredApplication.Main

# Client Services -- put in pentacle.client/support??
def OpenPartneredClient(partner_name, cfg = None, **kwd):
    if cfg is None:
        section = 'SplineClient'
        cfg = INI(**{section: dict(address = 'localhost',
                                   port = kwd.pop('port', Application.DEFAULT_PORT))})
        cfg += {section: kwd}
        cfg = cfg.toConfigObject(default_section = section)

    options = cfg.set

    # First, connect to the manager.
    auth = Authorization(options.username or '', options.secret_key or '')
    with Session(auth.Open(options.address, options.port)) as client:
        with client.api(ServiceManagerName) as spline:
            info = spline.GetPartnerInfo(partner_name)
            service_port = info['service_port']

    # Next, connect to the partnered service.
    if isinstance(service_port, int):
        return Client.Open(options.address, service_port)

def partnerBreakConsole(partnerName, cfg = None):
    # A pretty specific way of break-debugging any partnered service.
    cfg = getDefaultSplineConfig(cfg)
    auth = Authorization(options.username or '', options.secret_key or '')
    partneredClient = OpenPartneredClient(partnerName, cfg)
    with Session(auth.Authenticate(partneredClient)) as client:
        with client.api('Console::Remote') as console:
            pentacle.shell.InteractWith(console)
