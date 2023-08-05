# Asyncore-driven Network.
__all__ = ['AddNetworkCmdlnOptions', 'HostNetwork', 'Peer',
           'AsyncoreControl', 'asyncore', 'socket']

import asyncore
import socket
import errno

from .architecture import *
from .packaging import *
from .storage import *
from .runtime import *
from .encoding import *
from .security import *

def DEBUG(log, *args):
    pass # log(' '.join(map(str, args)))

NOBIND = [errno.EPERM, errno.EADDRINUSE]
    ##    # Todo: this could be more robust
    ##    if sys.platform == 'cygwin':
    ##        NOBIND = errno.EPERM
    ##    elif sys.platform == 'win32':
    ##        NOBIND = errno.WSAEACESS
    ##    else:
    ##        raise SystemError('Unknown platform for bind error: %s' % sys.platform)

def OpenAvailablePort(portRange, bindMethod):
    for port in portRange:
        if bindMethod(port):
            return port

    raise SystemError('Could find no available port')

class PortBindingMethod:
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address

    def __call__(self, port):
        # Should be the same for asyncore dispatcher and regular system socket
        try: self.bind(port)
        except socket.error, e:
            if e.errno not in NOBIND:
                raise
        else:
            self.socket.listen(5)
            return True

class DispatcherBindMethod(PortBindingMethod):
    def bind(self, port):
        self.socket.bind((self.address, port))

class SocketBindMethod(PortBindingMethod):
    @classmethod
    def New(self, bindAddress):
        return self(socket.socket(socket.AF_INET, socket.SOCK_STREAM), bindAddress)

    def bind(self, port):
        self.socket.bind(self.address, port)

class InterruptableSocket:
    class InterruptPortConfig:
        keySize = 64
        internalPortRange = [30700, 30799]
        address = '127.0.0.1'

        @classmethod
        def OpenAvailable(self, mother, port_ranger = xrange):
            bindMethod = DispatcherBindMethod(mother, self.address)
            try: return OpenAvailablePort(port_ranger(*self.internalPortRange), bindMethod)
            except SystemError, e:
                raise SystemError('%s in range: %s' % (e, self.internalPortRange))

    class InterruptOpener(asyncore.dispatcher):
        class InterruptPeer(asyncore.dispatcher_with_send):
            def __init__(self, opener, socketMap, (host, port)):
                self.__opener = opener
                asyncore.dispatcher_with_send.__init__(self, map = socketMap)
                self.connectToPort(host, port)

            def connectToPort(self, host, port):
                self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connect((host, port))

            def handle_connect(self):
                # Send the key.
                self.send(self.__opener.getSecretKey())

        class InterruptIncoming(asyncore.dispatcher):
            def __init__(self, opener, socketMap, sock):
                self.__opener = opener
                self.data_buffer = NewBuffer()
                asyncore.dispatcher.__init__(self, sock = sock, map = socketMap)

            def writable(self):
                return False

            def handle_read(self):
                # Initial state -- read secret key to determine that this is our own.
                buf = self.data_buffer

                keySize = self.__opener.getSecretKeySize()
                readSize = keySize - self.data_buffer.tell()

                data = self.recv(readSize)
                if data == '':
                    # todo: log error?
                    self.close()
                    return

                buf.write(data)
                pos = buf.tell()

                if pos > keySize:
                    # todo: log error?
                    self.close()

                elif pos == keySize:
                    value = buf.getvalue()
                    buf.truncate(0)

                    if self.__opener.submitSecretKeyReponse(value):
                        # Key accepted, switch to interruptable mode.
                        self.handle_read = self.handleInterruptRead

            def handleInterruptRead(self):
                ##    print 'Receiving Interrupt:',
                ##    print repr(self.recv(1))
                self.recv(1)

        INTERRUPT_NOTREADY = 0
        INTERRUPT_FAILED = 1
        INTERRUPT_CONNECTED = 2

        def __init__(self, socketMap, portConfig, secretKey):
            asyncore.dispatcher.__init__(self, map = socketMap)
            self.socketMap = socketMap
            self.__secretKey = secretKey
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__state = self.INTERRUPT_NOTREADY
            self.__wait = threading.Event()
            port = self.openInterruptPort(portConfig)
            # print 'Interruptable Connection Port: %s' % port
            self.__peer = self.InterruptPeer(self, socketMap, (portConfig.address, port))

        def handle_accept(self):
            (conn, addr) = self.accept()
            self.InterruptIncoming(self, self.socketMap, conn)

        def openInterruptPort(self, portConfig):
            return portConfig.OpenAvailable(self)

        def getSecretKey(self):
            return self.__secretKey
        def getSecretKeySize(self):
            return len(self.__secretKey)

        def submitSecretKeyReponse(self, value):
            if value != self.__secretKey:
                # Fail -- why?
                self.failSecretKeyResponse()
                return False

            self.switchIntoInterruptMode()
            return True

        def failSecretKeyResponse(self):
            self.close()
            self.__state = self.INTERRUPT_FAILED
            self.__wait.set()

        def switchIntoInterruptMode(self):
            self.close()
            # print 'Enabling Interrupt Mode.'
            self.__state = self.INTERRUPT_CONNECTED
            self.__wait.set()

        def getStatus(self):
            while not self.__wait.isSet():
                self.__wait.wait()

            return self.__state

        def isConnected(self):
            return self.__state == self.INTERRUPT_CONNECTED
        def sendInterrupt(self):
            if self.isConnected():
                self.__peer.send('\x00')

    def initialize_interrupt(self, portConfig, socketMap):
        try:
            if self.__opener.isConnected():
                return

        except AttributeError:
            pass

        secretKey = GenerateSecretKey(portConfig.keySize)
        self.__opener = opener = self.InterruptOpener(socketMap, portConfig, secretKey)

    def interruptTimeout(self):
        # Always wait before we send the interrupt, because we want it to succeed
        # in the event that the poll timeout is forever.
        if self.__opener.getStatus() == self.__opener.INTERRUPT_CONNECTED:
            self.__opener.sendInterrupt()

    interruptConfig = InterruptPortConfig

class InterruptableSignal:
    # Can't seem to get this one to work.
    interruptConfig = None
    def initialize_interrupt(self, config, map):
        pass

    if sys.platform == 'cygwin':
        # from signal import SIGPIPE as INTERRUPT_SIGNAL
        from signal import SIGIO as INTERRUPT_SIGNAL
        def interruptTimeout(self):
            if self.shouldInterrupt():
                print 'Interrupting Network...'
                sendSignal(thisProcessId(), self.INTERRUPT_SIGNAL)
                # modify interruption rate...
    else:
        def interruptTimeout(self):
            pass

Interruptable = InterruptableSocket


# Note on asyncore's poll/set
#
# Select limits the number of descriptors to FD_SETSIZE, which doesn't allow for
# massive numbers of connections, whereas poll is variable (and much less limited).
#
# However, poll is not implemented on all systems, making the tradeoff one between
# portability and capacity.
#

def AddNetworkCmdlnOptions(application, parser):
    parser.add_option('--port', default = application.DEFAULT_PORT)
    parser.add_option('--bind-address', default = HostNetwork.BIND_ADDRESS)
    # parser.add_option('--no-network', action = 'store_true')

class AsyncoreControl:
    # Inheriting both HostNetwork and Client so that dual-functioning service
    # partners can cooperatively serve i/o flow.

    class AlreadyServing(RuntimeError):
        pass

    # Todo: combine timing/responsiveness control into this class, or, some
    # complex algorithm for cutover to host-style cycling?
    TIMEOUT = 0.3 # Good responsiveness
    _asyncore_run_lock = threading.Lock()

    ##    def asyncoreLock(self):
    ##        return self._asyncore_run_lock

    @classmethod
    @contextmanager
    def asyncoreLock(self, blocking = False):
        if not self._asyncore_run_lock.acquire(blocking):
            # Pretty much, some other part of the application decided to start
            # serving the single asyncore batch (probably the client) -- let it go.
            raise self.AlreadyServing

        try: yield
        finally: self._asyncore_run_lock.release()

    @classmethod
    def startAsyncore(self):
        try:
            with self.asyncoreLock():
                # When the context exits, lock is released, waiting ex-thread begins.
                nth(self.runAsyncore)

        except self.AlreadyServing:
            pass

    @classmethod
    def waitForAsyncoreEnd(self):
        with self.asyncoreLock(True):
            # Effectively join at when the lock is momentarily free.
            pass

    @classmethod
    def runAsyncore(self):
        with self.asyncoreLock(True):
            # XXX this needs to be atomic with the lock, but I don't want
            # to have to lock for every socket map check.  So, try not to
            # start a new connection immediately after the last one closes.
            #
            # (I could probably use some other threading object)
            while asyncore.socket_map:
                asyncore.loop(timeout = self.TIMEOUT,
                              count = 1) # , use_poll = True)

class HostNetwork(asyncore.dispatcher, Interruptable, AsyncoreControl, Object):
    # (Not an architectural component, but an engine subsystem)
    BIND_ADDRESS = '0.0.0.0'

    def __init__(self, engine, port, address = None, ConnectionClass = None):
        # We want to separate network hosts, but unfortunately the partner
        # architecture uses Client asyncore, so we're just always going to
        # use default map.
        self.socketMap = None # asyncore.socket_map -- {}
        asyncore.dispatcher.__init__(self, map = self.socketMap)

        if isinstance(port, int):
            self.port_auto = False
            self.port = port
        else:
            assert port.lower() == 'auto'
            self.port_auto = True
            self.port = None

        self.address = address is None and self.BIND_ADDRESS or address

        self.connections = []
        self.engine = engine
        self.ConnectionClass = ConnectionClass or Peer

        self.nextTimeout = self.networkTiming().next
        self.nextWakeupTime = None

    PORT_RANGE = [30300, 30650]
    def configurablePortRange(self):
        # Todo: from self.engine.application.configuration??
        return xrange(*self.PORT_RANGE)

    def open_mother_socket(self, log = False):
        if self.socket is None:
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.set_reuse_addr()

            if self.port_auto:
                bindMethod = DispatcherBindMethod(self, self.address)
                portRange = self.configurablePortRange()

                try: self.port = OpenAvailablePort(portRange, bindMethod)
                except SystemError, e:
                    raise SystemError('%s in range: %s' % (e, portRange))
            else:
                self.bind((self.address, self.port))
                self.listen(5)

        if log:
            log('Mother Socket Opened [%s:%s]' % (self.address, self.port))

        self.initialize_interrupt(self.interruptConfig, self.socketMap)

    def handle_accept(self):
        (socket, addr) = self.accept()
        self.newConnection(socket, addr)

    def newConnection(self, socket, address = None):
        conn = self.ConnectionClass(self, socket, address)
        self.connections.append(conn)
        self.engine.logMessage('New Connection %r' % conn)

    def closeConnection(self, conn):
        if conn in self.connections:
            # Error occurred before newConnection was called.
            # XXX This doesn't really make sense.. newConnection
            # should always be called (synchronously) before close...
            self.connections.remove(conn)
            self.engine.logMessage('Disconnected %r' % conn)

    def pollCycle(self):
        timeout = self.nextTimeout()
        self.nextWakeupTime = None if timeout is None else \
                              getCurrentSystemTime() + timeout

        asyncore.loop(timeout = timeout,
                      map = self.socketMap,
                      count = 1) # , use_poll = True)

    # XXX Why are there still network blockages?
    BASE_NETWORK_TIMEOUT = 1.0 # None # 5.0 # 0.1 # Very responsive
    def networkTiming(self):
        # todo: make adaptable network timeout:
        #    If it's being interrupted alot, then decrease the timeout
        #    If it's not being interrupted much, increase timeout
        while True:
            yield self.BASE_NETWORK_TIMEOUT

    responsiveness_threshold = 1.0 # Poor responsiveness
    def timeUntilWakeup(self):
        if self.nextWakeupTime is None:
            raise ValueError('Coma')

        return (self.nextWakeupTime - getCurrentSystemTime())

    def shouldInterrupt(self):
        try:
            if self.timeUntilWakeup() > self.responsiveness_threshold:
                return True

        except ValueError:
            pass


class SynchronizedSendingDispatcher(asyncore.dispatcher_with_send):
    def __init__(self, *args, **kwd):
        asyncore.dispatcher_with_send.__init__(self, *args, **kwd)

        self.__sending = Object()
        bufferMutex = synchronizedWith(self.__sending, recursive = True)
        self.initiate_send = bufferMutex(self.initiate_send)
        self.send = bufferMutex(self.send)

    # SENDBUF_PACKET_SIZE = Variable
    # 512 is the default, but it's no good if even most trivial exceptions
    # occur, because it will bump against the nonresponsive network poll.
    # So, it should be variable: either the peer can change it, or it can
    # adapt to current network performance.

    ##    SENDBUF_SIZE = 2048 # 512
    ##    def initiate_send(self):
    ##        num_sent = 0
    ##        num_sent = asyncore.dispatcher.send(self, self.out_buffer[:self.SENDBUF_SIZE])
    ##        self.out_buffer = self.out_buffer[num_sent:]
    ##        print '[ SENT %d ]' % num_sent
    ##
    ##        # Effectively, this is called while network is polling (sleep),
    ##        # but just sending on the socket of changing .out_buffer isn't
    ##        # enough (since writable is only called before the timeout).
    ##        # So the network thread doesn't wake up unless a signal causes
    ##        # it to EINTR.  Here we are over in the engine, because all
    ##        # functions are just thrown to it indiscriminately, so we're just
    ##        # going to have to interrupt it!
    ##        return num_sent

    ##    def send(self, data):
    ##        ##    if self.debug:
    ##        ##        self.log_info('sending %s' % repr(data))
    ##        self.out_buffer = self.out_buffer + data
    ##        x = self.initiate_send()
    ##        print '[ SENT %d ] %s' % (x, self.socket.send)
    ##        return x

class Peer(PackageReader, SynchronizedSendingDispatcher, Object):
    loggedInEvent = Event('peer-logged-in')

    def __init__(self, network, socket, address):
        SynchronizedSendingDispatcher.__init__(self, sock = socket, map = network.socketMap)
        PackageReader.__init__(self)
        self.network = network
        self.client_address = address
        self.deferred_response = {}
        self.mode = network.engine.application.InitialMode()
        self.dataChannel = EntitySpace()

    def __repr__(self):
        addr = self.client_address
        return '[%s:%d] %r' % (addr[0], addr[1], self.mode) 

    def handle_close(self):
        # showTraceback()
        self.network.closeConnection(self)
        self.close()

    def handleIncomingPackage(self, package):
        self.log('package', 'INCOMING-PACKAGE: %s' % package)
        self.log('engine', 'ENGINE-MESSAGE-QUEUE:\n%s' % '\n'.join(map(str, self.network.engine.messageQueue.queue)))
        try: cmd = Command.FromPackage(package, self.dataChannel)
        except:
            #@breakOn
            def handleMalformedPackage(package):
                print
                print 'MALFORMED PACKAGE:'
                from .encoding import inspectPackedMessage
                inspectPackedMessage(package)

            # This should alert the client (but we don't push, even if the request is flawed).
            # We should just close it.
            printException()
            handleMalformedPackage(package)

        else:
            if cmd is not None:
                self.network.engine.postMessage(self.PeerCommandMessage(self, cmd))

    class PeerCommandMessage(Engine.Message):
        def __init__(self, peer, command):
            self.peer = peer
            self.command = command

        def __repr__(self):
            return '<%s: %r>' % (self.__class__.__name__,
                                 self.command)

        def dispatch(self, engine):
            self.peer.dispatchCommand(engine, self.command)

    class ResponseDeferred(Exception):
        def __init__(self, tracked = True):
            self.tracked = tracked

        def bind(self, peer, cmd):
            self.peer = peer
            self.command = command
            return self

        def finish(self):
            if self.tracked:
                self.peer.finishDeferredResponse(self.command.serialId)

        def response(self, engine, response):
            self.peer.handleCommandResponse(engine, self.command, response)
            self.finish()
        def exception(self, engine, (etype, value, tb)):
            self.peer.handleCommandException(engine, self.command, (etype, value, tb))
            self.finish()

    #@breakOn
    def dispatchCommand(self, engine, cmd):
        # This should really be part of the application, since it makes decisions
        # about package contents (exception traceback??)
        self.log('command', 'COMMAND: %s' % cmd)

        with engine.Controller(self):
            # The client kwd names could interfere with the actual method params.
            try: response = self.mode.interpretCommand(engine, self, cmd.command, *cmd.args, **cmd.kwd)
            except self.ResponseDeferred, e:
                d = e.bind(self, cmd)
                if e.tracked:
                    nr = cmd.serialId
                    assert nr is not None
                    assert nr not in self.deferred_response
                    self.deferred_response[nr] = d
            except:
                self.log('command', 'EXCEPTION')
                self.handleCommandException(engine, cmd, getSystemException())
                self.network.interruptTimeout()
            else:
                self.log('command', 'RESPONSE: %s' % repr(response))
                self.handleCommandResponse(engine, cmd, response)
                self.network.interruptTimeout()

    def log(self, logType, message):
        self.network.engine.application.logLevel(logType, message)


    ##    def sendLater(self, data):
    ##        # XXX Why does this just go away?
    ##        # Multithreading problem?
    ##        self.out_buffer += data
    ##    def sendNow(self, data):
    ##        self.socket.send(data)

    def handleCommandResponse(self, engine, cmd, response):
        data = self.dataChannel.encodeResponse(cmd.serialId, response)
        self.log('package', 'RESPONSE-PACKAGE: %r' % data)
        self.send(data)

    def handleCommandException(self, engine, cmd, (etype, value, tb)):
        etype = etype.__name__
        value = str(value)
        tb = extractTraceback(tb) # Limit this to privileged mode? (application)
        DEBUG(engine.log, 'EXCEPTION: (%s) %s' % (etype, value))
        self.send(self.dataChannel.encodeException(cmd.serialId, (etype, value, tb)))

    def finishDeferredResponse(self, serialId):
        del self.deferred_response[serialId]

    # For tracked deferments:
    def succeedDeferredResponse(self, engine, serialId, response):
        d = self.deferred_response[serialId]
        d.response(engine, response)
    def failDeferredResponse(self, engine, serialId, (etype, value, tb)):
        d = self.deferred_response[serialId]
        d.exception(engine, (etype, value, tb))

    def login(self, engine, username, authKey):
        assert isinstance(username, basestring)
        storage = UserStorage.Open(engine.application, username)
        if storage.checkAccess(authKey):
            # Login succeeds!
            self.loggedInEvent(engine, self)
            return engine.application.LoggedInMode(self, username)
