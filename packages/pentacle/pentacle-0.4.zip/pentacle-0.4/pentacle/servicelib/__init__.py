from ..architecture import ServiceBase, Engine
from ..runtime import Synthetic, LookupObject, getCurrentSystemTime, contextmanager, breakOn

# (Test) Services.
class ClockService(ServiceBase):
    NAME = 'ClockService::API'

    def setClockTicking(self, clockTime):
        self.clockTime = clockTime
    def getClockTime(self):
        return getCurrentSystemTime() - self.clockTime

class SystemDebug(ServiceBase):
    NAME = 'System::Debugging'

    def stopAndReload(self):
        # Hmm.  Quit the engine, wait for it to close, reload
        # all pentacle modules and restart??
        pass

    def copyover(self): # New args??
        self.application.engine.postMessage(CopyoverMessage())

    def enableTracing(self):
        set_trace()
    def fail(self, message = 'Force Fail'):
        raise RuntimeError(message)

    # lookupObject = staticmethod(LookupObject)
    def lookupObject(self, name):
        return LookupObject(name)

    def evaluate(self, source):
        code = compile(source, '', 'eval')
        return eval(source, globals(), globals())

    def execute(self, source):
        code = compile(source, '', 'exec')
        exec code in globals(), globals()

    def compile(self, source, filename, mode):
        return compile(source, filename, mode)

    def hotModule(self, code = None, name = None, filename = None, reload = False):
        from types import CodeType, ModuleType
        if isinstance(code, basestring):
            code = compile(code, filename or '', 'exec')
        else:
            assert isinstance(code, CodeType)

        from sys import modules
        if name is None:
            raise NotImplementedError('RandomModuleName()')
            name = RandomModuleName(modules)

            # New
            mod = ModuleType(name)
            modules[name] = mod
        else:
            try: mod = modules[name]
            except KeyError:
                # New
                mod = ModuleType(name)
                modules[name] = mod
            else:
                assert reload

        ns = mod.__dict__
        if code:
            exec code in ns, ns

        return mod

class CopyoverMessage(Engine.Message):
    def dispatch(self):
        from os import execve
        from sys import argv

        # Shut down the network:
        #   Stop receiving/handling any new commands.
        #   Flush remaining output buffers.
        #   Write session map to disk (to hold onto connections)
        #   Initiate execve(argv)

class ObjectDirectory(ServiceBase):
    NAME = 'System::Directory'

    def getWholeDirectory(self):
        import sys
        try: return sys._object_directory
        except AttributeError:
            sys._object_directory = d = {}
            return d

    def getObject(self, name):
        return self.getWholeDirectory().get(name)
    def setObject(self, name, value):
        self.getWholeDirectory()[name] = value

    __getitem__ = getObject
    __setitem__ = setObject

    def newObject(self, **values):
        return Synthetic(**values)

class RemoteConsole(ServiceBase):
    # Redirect stdin/stdout, provide parallel interaction thread
    # (because the streams shall be bound to engine/network comm)
    NAME = 'Console::Remote'

    # This should grab console for only the requesting peer (assuming there is one),
    # and automatically release it on disconnect.  For now, it's exposed to everyone!
    def getStdoutBuffer(self):
        try: return self.stdout_buffer
        except AttributeError:
            self.stdout_buffer = buf = NewBuffer()
            return buf

    def getStderrBuffer(self):
        try: return self.stderr_buffer
        except AttributeError:
            self.stderr_buffer = buf = NewBuffer()
            return buf

    def getStdinChannel(self):
        try: return self.stdin_channel
        except AttributeError:
            self.stdin_channel = channel = NewBuffer()
            return channel

    def readStdout(self, *args, **kwd):
        return self.getStdoutBuffer().read(*args, **kwd)
    def readStderr(self, *args, **kwd):
        return self.getStdoutBuffer().read(*args, **kwd)
    def writeStdin(self, *args, **kwd):
        return self.getStdinChannel().write(*args, **kwd)

    #@property
    @contextmanager
    def focus(self):
        # Todo: Shouldn't allow this more than once...
        stdout = sys.__stdout__ = sys.stdout
        stderr = sys.__stderr__ = sys.stderr
        stdin = sys.__stdin__ = sys.stdin

        sys.stdout = self.getStdoutBuffer()
        sys.stderr = self.getStderrBuffer()
        sys.stdin = self.getStdinChannel()

        try: yield
        finally:
            sys.stdout = stdout
            sys.stderr = stderr
            sys.stdin = stdin

    def open(self):
        cx = self.focus()
        cx.__enter__()
        return cx.__exit__

class Tunnel(ServiceBase):
    NAME = 'Pentacle::Tunnel'

    def openClient(self, address, port):
        from pentacle.client import Client
        return Client.Open(address, port)
