# Process Architecture
# Todo:
#   Move into runtime/core
#
__all__ = ['Engine', 'Event', 'Component', 'Serializable',
           'BaseMode', 'SubcommandMode', 'UnboundApiMode',
           'ServiceBase']

import Queue

from .runtime import *

# Event Driver
class Engine(Object):
    def __init__(self, application, timeout = None):
        self.application = application
        self.controllerStack = []
        self.messageQueue = Queue.Queue()
        self.timeout = timeout

    class Stop(SystemExit):
        pass

    class Message(Object): # Shouldn't this be called Action?
        def dispatch(self, engine):
            raise NotImplementedError

    # Main Application Loop.
    def run(self):
        try:
            while True:
                try: msg = self.messageQueue.get(timeout = self.timeout)
                except Queue.Empty:
                    continue

                if isinstance(msg, BaseException):
                    raise msg
                elif isinstance(msg, self.Message):
                    self.dispatchMessage(msg)

        except self.Stop:
            pass

    def postMessage(self, msg):
        self.messageQueue.put(msg)
    def stop(self):
        self.messageQueue.put(self.Stop())

    def dispatchMessage(self, msg):
        # print '   dispatching:', msg, '(%s)' % id(msg)
        try: msg.dispatch(self)
        except self.Stop:
            raise
        except:
            self.logException('Exception handling: %r' % msg)

        # print '   done with %s' % id(msg)

    @contextmanager
    def Controller(self, ctlr):
        self.controllerStack.append(ctlr)
        try: yield
        finally:
            self.controllerStack.pop()

    def getController(self):
        try: return self.controllerStack[-1]
        except IndexError:
            pass # raise self.NoController

    # Logging
    def log(self, message):
        self.application.log(message)
    def logException(self, message = None):
        from traceback import format_exc
        tb = format_exc()
        self.logMessage(message + tb)

    class LogMessage(Message):
        def __init__(self, message):
            self.message = message
        def dispatch(self, engine):
            engine.log(self.message)

    def logMessage(self, message):
        self.postMessage(self.LogMessage(message))

class Event(Object):
    class Result(RuntimeError): # Why error?  Should be like BaseException
        def __init__(self, result):
            self.result = result

    def __init__(self, name):
        self.name = name
        self.listeners = []

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.name)

    def addListener(self, listener):
        self.listeners.append(listener)
    def removeListenser(self, listener):
        self.listeners.remove(listener)

    def __iadd__(self, listener):
        self.addListener(listener)
        return self
    def __isub__(self, listener):
        self.removeListener(listener)
        return self

    def Listen(self, function):
        # Decorator.
        self += function
        return function

    def broadcast(self, *args, **kwd):
        for n in self.listeners:
            try: n(self, *args, **kwd)
            except self.Result, r:
                return r.result
            except:
                # ??
                printException()

    # Post a dispatchable message:
    class EventBroadcast(Engine.Message):
        def __init__(self, event, args, kwd):
            self.event = event
            self.args = args
            self.kwd = kwd

        def __repr__(self):
            return '<%s: %r>' % (self.__class__.__name__, self.event)

        def dispatch(self, engine):
            self.event.broadcast(engine, *self.args, **self.kwd)

    def __call__(self, engine, *args, **kwd):
        engine.postMessage(self.EventBroadcast(self, args, kwd))

class Component(Object):
    def __init__(self, application):
        self.application = application

    @classmethod
    def getPathName(self, path):
        return expanduser(expandvars(path))

    @classmethod
    def addCmdlnOptions(self, parser):
        pass


# Input/Command Modes
class BaseMode(Object):
    def __init__(self, previous = None):
        self.previousMode = previous
    def popMode(self, peer):
        peer.mode = self.previousMode

class UnknownCommandError(NameError):
    pass

class SubcommandMode(BaseMode):
    def interpretCommand(self, engine, peer, name, *args, **kwd):
        # Note: the kwd names could interfere with the method impl params.
        action = getattr(self, 'do%s' % getCapitalizedName(name), None)
        if callable(action):
            return action(engine, peer, *args, **kwd)

        return self.defaultCommand(engine, peer, name, *args, **kwd)

    def defaultCommand(self, engine, peer, name, *args, **kwd):
        # if self._previous_mode:
        #    return self._previous_mode.interpretCommand(engine, peer, name, *args, **kwd)

        # Note: most notably, all unhandled commands do this: are you logged in to the api?
        # raise UnknownCommandError(name) ??
        pass

class UnboundApiMode(SubcommandMode):
    def doCallEntityMethod(self, engine, peer, refId, methodName, *args, **kwd):
        try: object = peer.dataChannel.getObjectOrError(refId)
        except ValueError:
            # The object wasn't proxied??  It must have gone away.
            raise ApiManagement.ApiError("The object referred to by #%d doesn't exist" % refId)
        else:
            # Got the real object: call its method, straight-away!
            method = getAttributeChain(object, methodName)
            return method(*args, **kwd)

    def doGetEntityProperty(self, engine, peer, refId, propertyName):
        try: object = peer.dataChannel.getObjectOrError(refId)
        except ValueError:
            # The object wasn't proxied??  It must have gone away.
            raise ApiManagement.ApiError("The object referred to by #%d doesn't exist" % refId)
        else:
            # Return property on real object.
            return getAttributeChain(object, propertyName)

    def doCloseApi(self, engine, peer):
        peer.mode.popMode(peer)

# Encoding
class Serializable:
    # Interface
    pass


# Services
def ApiMethod(function):
    function.apiMethod_Exposed = True
    return function

def isApiMethod(function):
    return getattr(function, 'apiMethod_Exposed', False)

# Thoughts on exposing the Service API:
#
#    Leverage the existing Meta model for runtime Objects.  This means
#      declaring exposed methods through the Meta, or, declaring unsafe
#      methods that shouldn't be exposed.
#
#    Define exposed methods using an explicit member, like 'Methods' on
#      the service class.
#    Of course, expose methods using decorators.
#
#    Consider wrapping objects returned to limit their exposure, as well,
#      all defined by the service-api map (in the Meta).
#           Wrap using a decorator is most obvious, easiest.
#           What about doing a default Activate or ctor to scan those
#             specified in Meta?
#

class ServiceBase(Object):
    NAME = 'DefaultService'
    def Activate(self, apiMgr):
        self.apiMgr = apiMgr

    @contextmanager
    def __call__(self, engine, peer, name):
        # Setup: Put engine/peer into externally-accessible context?
        ##    if not self.isExposedMethod(name):
        ##        raise AttributeError(name)

        if self.isReservedAttribute(name):
            raise AttributeError(name)

        yield getAttributeChain(self, name)

    @classmethod
    def isReservedAttribute(self, name):
        # Pretty sure this is enough to just deny external access to the application,
        # while leaving it open internally, since this is the api gateway.
        return name in ['application', 'Activate', 'Deactivate', '__init__']

    ##    @classmethod
    ##    def isExposedMethod(self, name):
    ##        return isApiMethod(getattr(self, name, None))
