# Application
__all__ = ['Application', 'ApiManagement']

from code import InteractiveConsole as IC
import sys
import os

from .architecture import *
from .network import *
from .security import *
from .storage import *
from .runtime import *
from .config import *

from . import __version__ as pentacleVersion
from . import buildApplicationVersion

APPLICATION_NAME = 'PentacleApp'
__identity__ = buildApplicationVersion(APPLICATION_NAME, pentacleVersion)

class Application(Object): # (Engine)
    DEFAULT_PORT = 7040
    DEFAULT_CONFIG_FILE = '~/.pentacle/application.cfg'

    PENTACLE_CONFIG_ENV_VAR = 'PENTACLE_CONFIG'

    def __init__(self, config):
        self.config = config
        self.version = self.getConfigOption('version', default = __identity__)

        self.storage = StorageManagement(self)
        self.security = RightsManagement(self)
        self.api = ApiManagement(self)

        # Todo: somethings like this could be updated live.
        self.logTypes = self.getConfigOption('log-types') or []

        # Build and activate Network and Engine.
        self.engine = Engine(self.getConfigOption('engine-timeout'))
        self.engine.application = self

        if self.useNetwork():
            (address, port) = self.getConfigOptionSet('bind-address', 'port',
                                                      section = 'Network',
                                                      simplify = True)

            def logNetworkBoot(msg):
                self.logNetwork('%s: %s' % (self.version, msg))

            self.network = HostNetwork(self.engine, port, address = address)
            self.network.open_mother_socket(logNetworkBoot)

    def log(self, message):
        print message
    audit = log

    def logLevel(self, logType, message):
        if logType in self.logTypes or 'all' in self.logTypes:
            self.log(message)

    def logException(self, message = None):
        if message:
            self.log(message)

        printException()

    def logNetwork(self, message):
        # self.logLevel('network', message)
        self.log(message)

    def getConfigOption(self, name, first = True, **kwd):
        kwd.setdefault('section', 'Application')
        result = self.config.getOptionMultiple(name, **kwd)
        try: return result[0] if first else result
        except IndexError:
            pass

    def getConfigOptionSet(self, *names, **kwd):
        kwd.setdefault('section', 'Application')
        return self.config.getOptionSet(*names, **kwd)

    def getConfigOptionMultiple(self, *args, **kwd):
        kwd.setdefault('section', 'Application')
        return self.config.getOptionMultiple(*args, **kwd)

    # Runtime Management.
    debug = False
    def networkThread(self):
        # todo: move all this into network..?
        # import pdb; pdb.set_trace()
        self._running_network = True
        try:
            with self.network.asyncoreLock():
                while getattr(self, '_running_network', False):
                    ##    if self.debug:
                    ##        import pdb; pdb.set_trace()

                    # print 'Poll Cycle'
                    self.network.pollCycle()

        except self.network.AlreadyServing:
            # Quietly ignore and terminate loop.
            del self._running_network

        except:
            # Pass to application log??
            import traceback
            traceback.print_exc()

    def profileEngine(self):
        profileName = self.getConfigOption('profile-name')
        if profileName:
            from profile import Profile
            profile = Profile()

            try: profile.runcall(self.engine.run)
            finally:
                profile.dump_stats(profileName)

            return True

    def runEngine(self):
        if not self.profileEngine():
            self.engine.run()

    def stopNetwork(self):
        try: del self._running_network
        except AttributeError: pass
        self.network.interruptTimeout()

    def stop(self):
        self.stopNetwork()
        self.engine.stop()

    def run(self):
        # Run network in thread.
        DEBUG('running network')
        nth(self.networkThread)

        DEBUG('running engine')
        # Run engine driver in main thread.
        try: self.runEngine()
        except KeyboardInterrupt:
            self.log('Console Interrupt')
            self.stop()
        else:
            self.log('Engine Stopped')

    # Front End.
    @classmethod
    def addCmdlnOptions(self, parser):
        parser.add_option('--emhw', action = 'store_true')
        parser.add_option('--profile-name')
        parser.add_option('--log-type', action = 'append',
                          default = [], dest = 'log_types')

        # Make some bad assumptions about ClientOptions interoperability.
        # This came from a need to blend application options with client
        # options in spline, so it could be configured as an app on the
        # cmdln.  Todo: come up with a better way to do this.
        from optparse import OptionConflictError
        try: parser.add_option('--debug', action = 'store_true')
        except OptionConflictError: pass
        else: AddNetworkCmdlnOptions(self, parser)

    @classmethod
    def Boot(self, argv = None, config_file = None):
        if config_file is None:
            config_file = os.environ.get(self.PENTACLE_CONFIG_ENV_VAR,
                                         self.DEFAULT_CONFIG_FILE)

        config = Configuration.FromCmdln(argv, config_file,
                                         self, StorageManagement,
                                         RightsManagement, ApiManagement,
                                         default_section = 'Application')

        if config.set.debug: # or True:
            import pdb; pdb.set_trace()

        return self(config)

    def useNetwork(self):
        # Determine if the given configuration/options need to host peers.
        if self.getConfigOption('emhw', simplify = True):
            return False
        if self.getConfigOption('dump-db'):
            return False
        # if self.getConfigOption('no-network'):
        #    return False

        return True

    # Todo: Maybe split this into the server-class application and a cmdln app (for emhw)
    @classmethod
    def Main(self, argv = None):
        global app
        app = self.Boot(argv)

        if app.getConfigOption('emhw'):
            # Emergency Mode Holigraphic Wizard
            try: import readline
            except ImportError:
                pass

            import pentacle
            ic = IC(locals = dict(app = app, pentacle = pentacle,
                                  g = Synthetic(**globals())))
            ic.interact()
        elif app.getConfigOption('dump-db'):
            outfile = app.getConfigOption('dump-db')
            app.log('Dumping Storage DB to: %r' % outfile)
            app.storage.dumpDB(outfile)
        else:
            app.run()

    # Interaction Modes
    class InitialMode(SubcommandMode):
        def popMode(self, peer):
            if self.previousMode is not None:
                # Cannot go beyond initial mode (if there isn't one).
                BaseMode.popMode(self, peer)

        def doIdentify(self, engine, peer):
            return engine.application.version

        def doLogin(self, engine, peer, username, authKey):
            mode = peer.login(engine, username, authKey)
            if mode is None:
                return False

            peer.mode = mode
            engine.log('Logged In: %r -> %s' % (peer, username))

    # Note: Override this class if you want to shape your application and still have authentication.
    # But, you don't really need to since it's secure.  What you want to do is activate service apis
    #     and grant access to them.
    #
    # Todo: consider subclassing UnboundApiMode, so that another mode doesn't have to be open
    # in order to enjoy object method remoting benefits.
    #
    class LoggedInMode(InitialMode):
        Meta = Object.Meta('username')
        def __init__(self, peer, username):
            BaseMode.__init__(self, peer)
            self.username = username

        def getStorage(self, engine):
            return UserStorage.Open(engine.application, self.username)

        # Actions:
        def doWhoami(self, engine, peer):
            return self.username
        def doLogout(self, engine, peer):
            self.popMode(peer)
        def doStillConnected(self, engine, peer):
            return True

        def doOpenApi(self, engine, peer, apiName = None):
            if apiName is None:
                peer.mode = UnboundApiMode(self)
            else:
                apiObject = engine.application.api.getUserApiObject(self.username, apiName)
                if apiObject is not None:
                    # Why not engine.application.api.ApiMode??
                    peer.mode = ApiManagement.ApiMode(self, apiObject)

        # Todo: move into account-service api
        def doChangeSecretKey(self, engine, peer, secretKey):
            # Note: You wouldn't really want to pass this over the network.
            # todo: diffie-hellman?
            storage = self.getStorage(engine)
            storage.changeSecretKey(secretKey)

        # Todo: move into application-control service api
        def doStopApplication(self, engine, peer):
            # engine.getController().mode.username
            app = engine.application
            if app.security.isUserActionPermitted(self.username, 'stop-application'):
                app.stop()

        # Todo: move into security-control service api
        def doGrantPermission(self, engine, peer, actionName, permissionName, userPrincipalName, withGrant = False):
            security = engine.application.security
            thePerm = '%s:%s' % (actionName, permissionName)
            withGrantPerm = 'with-grant:' + thePerm
            if security.isUserActionPermitted(self.username, withGrantPerm):
                security.grantUserAction(userPrincipalName, thePerm)
                if withGrant:
                    security.grantUserAction(userPrincipalName, withGrantPerm)

        def doRevokePermission(self, engine, peer, permissionName, userPrincipalName, actionName):
            raise NotImplementedError

        # High-Powered: (used for testing)
        def doPowerUp(self, engine, peer):
            if engine.application.security.isUserActionPermitted(self.username, 'wizard-mode'):
                peer.mode = self.WizardMode(self)

        class WizardMode(SubcommandMode):
            # Powerful Mode -- UNCHECKED ACCESS.
            def doPowerDown(self, engine, peer):
                self.popMode(peer)
            def doMe(self, engine, peer):
                return peer


main = Application.Main
bootServer = Application.Boot

class ApiManagement(Component):
    class ServiceManager(ServiceBase): # Different from Spline.ServiceManager
        NAME = 'API::Management'

        # Allow access to dynamically load in new api services.
        def loadNewServiceApi(self, serviceApi):
            return self.apiMgr.loadServiceApiObject(serviceApi)
        def getAllApiNames(self):
            return self.apiMgr.apiDirectory.keys()
        def isApiAvailable(self, name):
            return name in self.apiMgr.apiDirectory

        def getAvailableMethods(self, serviceName):
            return self.apiMgr.getAvailableMethods(serviceName)

        # ! High-powered:
        def plugApi(self, name, api):
            return self.apiMgr.plugApi(name, api)
        def unplugApi(self, name):
            return self.apiMgr.unplugApi(name)

        def addSystemPath(self, path):
            return self.apiMgr.addSystemPath(path)

    @classmethod
    def addCmdlnOptions(self, parser):
        parser.add_option('--service-path', action = 'append', default = [])
        parser.add_option('--service-api', action = 'append', default = [])

    def __init__(self, application):
        self.application = application
        self.apiDirectory = {}

        for path in application.getConfigOptionMultiple('service-path', section = 'Services'):
            self.addSystemPath(path)

        self.loadServiceApiObject(self.ServiceManager)
        for serviceApi in application.getConfigOptionMultiple('service-api', section = 'Services'):
            self.loadServiceApiObject(serviceApi)

    def addSystemPath(self, newPath):
        if newPath not in sys.path:
            sys.path.append(newPath)

    def loadServiceApiObject(self, apiClass):
        if isinstance(apiClass, basestring):
            apiClass = LookupObject(apiClass)

        # assert issubclass(apiClass, ServiceBase)
        api = apiClass()

        self.plugApi(api.NAME, api)
        return api

    def plugApi(self, name, api):
        if name not in self.apiDirectory:
            self.application.log('Installing API: %s' % name)
            self.apiDirectory[name] = api

            try: activate = api.Activate
            except AttributeError: pass
            else: activate(self)

    def unplugApi(self, name):
        try: api = self.apiDirectory[name]
        except KeyError: pass
        else:
            try: deactivate = api.Deactivate
            except AttributeError: pass
            else: deactivate()

    def getAvailableMethods(self, serviceName):
        if self.application.security.isUserActionPermitted(username, 'access-api:%s' % apiName):
            try: apiObject = self.apiDirectory[apiName]
            except KeyError: raise NameError(serviceName)

            # Return set of names in API exposed by service.
            return [name for name in dir(apiObject) if apiObject.isExposedMethod(name)]

    def getUserApiObject(self, username, apiName):
        if self.application.security.isUserActionPermitted(username, 'access-api:%s' % apiName):
            return self.apiDirectory[apiName]

    class ApiError(RuntimeError):
        pass

    class ApiMode(UnboundApiMode):
        # Some Entity RPC
        def __init__(self, peer, apiObject):
            BaseMode.__init__(self, peer)
            self.apiObject = apiObject

        #@breakOn
        def defaultCommand(self, engine, peer, name, *args, **kwd):
            with self.apiObject(engine, peer, name) as method:
                if not callable(method):
                    # ApiError?
                    raise TypeError('Method not callable: %s' % name)

                return method(*args, **kwd)
