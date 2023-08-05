# Peer Data Client
from ..encoding import *
from ..runtime import *
from ..network import *
from ..security import *
from ..packaging import *
from ..application import *
from ..architecture import *

import pdb
import socket
from contextlib import closing as Session

DEFAULT_PORT = Application.DEFAULT_PORT
DEFAULT_HOST = 'localhost'

class ClientOptions(Component):
    @classmethod
    def addCmdlnOptions(self, parser):
        parser.add_option('--port', default = DEFAULT_PORT, type = int)
        parser.add_option('--service-partner-name')
        parser.add_option('--support-dir')
        parser.add_option('--endpoint')
        parser.add_option('--address', default = DEFAULT_HOST)
        parser.add_option('--username')
        parser.add_option('--secret-key', default = '')
        parser.add_option('--api-test', action = 'store_true')
        parser.add_option('--quit', action = 'store_true')
        parser.add_option('--examine', action = 'store_true')
        parser.add_option('--compression-level')
        parser.add_option('--compression-threshold')
        parser.add_option('--open-system-api', action = 'store_true')
        parser.add_option('--enable-timing-tests', action = 'store_true')
        parser.add_option('--open-spline-api', action = 'store_true')
        parser.add_option('-g', '--debug', action = 'store_true')
        parser.add_option('--open-api')

    @classmethod
    def getCmdlnParser(self):
        from optparse import OptionParser
        parser = OptionParser()
        self.addCmdlnOptions(parser)
        return parser

    @classmethod
    def parseCmdln(self, argv = None):
        parser = self.getCmdlnParser()
        return parser.parse_args(argv)

class Client(PackageReader, asyncore.dispatcher_with_send, AsyncoreControl):
    @classmethod
    def Open(self, address, port, wait = True):
        # The preferred way to open a client connection.
        handler = self()
        handler.openConnection(address, port)
        if wait:
            handler.WaitForConnection()

        return handler

    def __init__(self, *args, **kwd):
        '''\
        Creates a new Client instance based on asyncore.dispatcher_with_send.
        Arguments and keywords are passed directly to that base class constructor.

        This constructor also sets up the `entity-space <EntitySpace>`__ data channel
        for handling packages, and builds locking versions of network functions for
        synchronizing the user's thread with the asyncore thread.

        This constructor also composes two access objects:
            * call `MethodCall`
            * api `APICall <pentacle.client.APICall>`__

        Which allow for smooth remoting syntax, pointing back to the Client
        communication routines.
        '''
        asyncore.dispatcher_with_send.__init__(self, *args, **kwd)
        PackageReader.__init__(self)
        self.dataChannel = EntitySpace()
        self.deferred_responses = {} # Ordered?
        self.command_nr = 0

        deferredMutex = synchronizedWith(None, recursive = True)
        self.pushResponse = deferredMutex(self.pushResponse)
        self.getWaitState = deferredMutex(self.getWaitState)

        self.call = MethodCall(self.callCommand, self.getEntityProperty) #: X{MethodCall}
        self.api = APICall(self.callCommand, self.getEntityProperty) #: X{APICall}

    def __repr__(self):
        cls = self.__class__
        if self.addr:
            return '<%s.%s: [%s:%d]>' % (cls.__module__, cls.__name__) + self.addr

        return '<%s.%s>' % (cls.__module__, cls.__name__)

    def openConnection(self, address, port):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connectWait = threading.Event()
        self.connectError = None
        self.connect((address, port))

        self.startAsyncore() # if necessary.

    ##    def close(self):
    ##        import pdb; pdb.set_trace()
    ##        # raise RuntimeError('closing?')

    def WaitForConnection(self):
        while not self.connectWait.isSet():
            self.connectWait.wait()

        if self.connected:
            return True

        if self.connectError:
            raise self.connectError

    # Asyncore Handlers.
    def handle_connect(self):
        self.connectWait.set()

    def handle_read(self):
        try: PackageReader.handle_read(self)
        except socket.error, e:
            self.connectError = e
            self.connectWait.set()

    def handle_write_event(self):
        try: asyncore.dispatcher_with_send.handle_write_event(self)
        except socket.error, e:
            self.connectError = e
            self.connectWait.set()

    def handle_expt_event(self):
        # Strangely, this is called after a failed write for refused connections.
        # So we're racing on connectError (and double connectWait.set, btw)
        try: asyncore.dispatcher_with_send.handle_expt_event(self)
        except socket.error, e:
            self.connectError = e
            self.connectWait.set()

    # Command Invocation.
    def sendSerialCommand(self, command, (serialId, flags), *args, **kwd):
        data = self.dataChannel.encodeSerialCommand(command, (serialId, flags), *args, **kwd)
        # DEBUG('COMMAND[#%d]: %s' % (serialId, data))
        self.send(data)

    def newSerialId(self):
        try: return self.command_nr
        finally: self.command_nr += 1

    def callCommand(self, command, *args, **kwd):
        serialId = self.newSerialId()
        self.sendSerialCommand(command, (serialId, 0), *args, **kwd)
        DEBUG('   sent command', serialId, command)
        response = self.waitForResponse(serialId)
        DEBUG('   command response:', response)
        return interpretResponse(response,
                                 callEntityMethod = self.callEntityMethod,
                                 getEntityProperty = self.getEntityProperty)

    rpc_callEntityMethod = 'callEntityMethod'
    def callEntityMethod(self, proxy, *args, **kwd):
        return self.callCommand(self.rpc_callEntityMethod, proxy.refId, *args, **kwd)

    rpc_getEntityProperty = 'getEntityProperty'
    def getEntityProperty(self, proxy, name):
        return self.callCommand(self.rpc_getEntityProperty, proxy.refId, name)

    # Data Communications.
    def handleIncomingPackage(self, package):
        # DEBUG('RECEIVED-PACKAGE:', package)
        response = Response.FromPackage(package, self.dataChannel)
        if response is not None:
            serialId = response.serialId
            if serialId is None:
                # Do some default handling.
                try: print interpretResponse(response)
                except Fault, fault:
                    print fault
            else:
                # DEBUG('PUSHING RESPONSE:', response)
                self.pushResponse(serialId, response)

    def pushResponse(self, serialId, response):
        # Notify waiter.
        try: waiting = self.deferred_responses[serialId]
        except KeyError:
            # DEBUG('GOT RESPONSE BEFORE WAITER: [#%d]' % serialId)
            waiting = [None, response]
            self.deferred_responses[serialId] = waiting
        else:
            # DEBUG('POSTING RESPONSE TO WAITER: [#%d]' % serialId)
            del self.deferred_responses[serialId]
            waiting[1] = response
            waiting[0].set()

    def getWaitState(self, serialId):
        try: waiting = self.deferred_responses[serialId]
        except KeyError:
            waiting = [threading.Event(), None]
            self.deferred_responses[serialId] = waiting

        return waiting

    def waitForResponse(self, serialId, timeout = 0.4):
        waiting = self.getWaitState(serialId)
        if waiting[0] is not None:
            wait = waiting[0]
            # DEBUG('WAITING FOR [#%d]...' % serialId)
            while not wait.isSet():
                wait.wait(timeout = timeout)

        return waiting[1]

    ##    def write_data(self, data):
    ##        print '...', data
    ##        return PackageReader.write_data(self, data)

from support import *
