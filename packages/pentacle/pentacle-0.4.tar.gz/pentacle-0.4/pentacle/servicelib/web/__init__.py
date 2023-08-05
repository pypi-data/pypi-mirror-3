# Spline Web Controller.
from ...architecture import ServiceBase
from ...runtime import Object, nth, contextmanager

from ...client import Authorization, Session

from ...bus import ServiceManagerName
from ...bus.partners import getManagerOptions

from errno import EINTR
from types import ClassType as newClassObject
from select import error as select_error
import platform

HTML_PROLOGUE = '''\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
'''

HTML_PROLOGUE = '<html><head>\n'

class Management(ServiceBase):
    NAME = 'PenobscotRobotics[Spline::Web::Management]'
    SERVER_NAME = 'SplineManagementServer'

    class Controller(Object):
        # Used by views, etc.
        def __init__(self, application, service):
            self.application = application
            self.service = service
            self.document = dict(start = HTML_PROLOGUE)

        @property
        def hostName(self):
            return platform.node()

        @property
        def managerSession(self):
            try: return self.cachedManagerSession
            except AttributeError:
                mgrOptions = getManagerOptions(self.application.config)
                auth = Authorization(mgrOptions.username or '',
                                     mgrOptions.secret_key or '')

                client = auth.Open(mgrOptions.address, mgrOptions.port)
                self.cachedManagerSession = client

                return client

        @property
        def managerApi(self):
            'Open a connection to the Spline service manager partner.'

            # Todo: catch faults and produce synthetic tracebacks for django debug??
            # Since this is a context-manager, we can catch errors (like disconnections)
            # and re-connect.  No wait -- the best thing is a connection-alive checker.
            try: return self.cachedManagerApi.invoke
            except AttributeError:
                api = self.managerSession.api.open(ServiceManagerName)
                self.cachedManagerApi = api

                return api.invoke

        def reloadViews(self):
            from dj import views, urls
            reload(views); reload(urls)

        def shutdownManager(self):
            try: self.cachedManagerApi.close()
            except AttributeError: pass
            return self.managerSession.call.stopApplication()

    def Activate(self, apiMgr):
        ServiceBase.Activate(self, apiMgr)
        webController = self.Controller(apiMgr.application, self)

        serverClass = BuildServerClass(self.SERVER_NAME)
        self.server = serverClass(webController)

        self.server.server_start()
        apiMgr.application.log('%s Server -- Port %d' % \
                               (self.NAME, self.server.server_address[1]))

        # OMFG -- todo: open if configured this way.
        from os import environ
        environ['DISPLAY'] = '1' # X-based browser.

        import webbrowser
        webbrowser.open('http://%s:%s' % self.server.server_address)

    def getWebServerInfo(self):
        return dict(port = self.server.server_address[1])

# Server Construction.
class ServerControl:
    def set_running(self, value = True):
        self.__running = value
    def is_running(self):
        try: return (self.__running)
        except AttributeError:
            return False

    ##    def process_request_thread(self, *args, **kwd):
    ##        import pdb; pdb.set_trace()
    ##        return ThreadingMixin.process_request_thread(self, *args, **kwd)

    def server_loop(self):
        while self.is_running():
            # import pdb; pdb.set_trace()
            self.server_handle_request()

    def server_handle_request(self):
        try: self.handle_request()
        except select_error, e:
            if e.args[0] != EINTR:
                # A process signal was sent, ignore and continue.
                (etype, value, tb) = sys.exc_info()
                raise etype, value, tb

        except KeyboardInterrupt:
            self.server_stop()

    def server_start(self):
        self.set_running(True)
        nth(self.server_loop)

    def server_stop(self):
        self.set_running(False)
    def server_shutdown(self):
        # XXX!
        self.server_stop()
        self.server_close()

    def runningState(self):
        return self.is_running() and 'RUNNING' or 'STOPPED'

def BuildServerClass(ServerName):
    # This abstracts the server implementation somewhat.
    from SocketServer import ThreadingMixIn as ServerCompartment
    from falcon import FalconManagementServer

    return newClassObject(ServerName,
                          (FalconManagementServer,
                           ServerCompartment,
                           ServerControl),
                          dict(baseControlClass = ServerControl))
