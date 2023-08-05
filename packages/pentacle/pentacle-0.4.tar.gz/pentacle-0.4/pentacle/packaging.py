# Package Object Model
__all__ = ['Command', 'Response', 'Fault',
           'PackageReader', 'NotAvailableError', 'interpretResponse']

from os import SEEK_SET, SEEK_END

from .encoding import *
from .runtime import *

class Command:
    @classmethod
    def FromPackage(self, package, entitySpace):
        msg = entitySpace.unpackMessage(package)
        if isinstance(msg, list):
            assert len(msg) in (3, 4, 5)
            return self(*msg)

        raise TypeError(type(msg))

    def __init__(self, command, serialId, flags, args = (), kwd = {}):
        assert isinstance(command, basestring)
        if isinstance(args, dict):
            # If there are no positional args then:
            # "shift these [parameters] back right."
            kwd = args
            args = ()
        else:
            assert isinstance(args, (list, tuple))
            assert isinstance(kwd, dict)

        self.command = command
        self.serialId = serialId
        self.flags = flags # encrypted, compressed, encoded, etc.
        self.args = args
        self.kwd = kwd

    def __repr__(self):
        return self.CommandString(self.command, self.serialId, self.args, self.kwd)

    @classmethod
    def CommandString(self, cmd, nr, args, kwd):
        args = ', '.join(map(repr, args))
        kwd = ', '.join('%s = %r' % (nv) for nv in kwd.iteritems())

        if nr is None:
            return '%s(%s%s%s)' % (cmd, args, args and kwd and ', ' or '', kwd)
        else:
            return '%s[%d](%s%s%s)' % (cmd, nr, args, args and kwd and ', ' or '', kwd)

class Response:
    @classmethod
    def FromPackage(self, package, entitySpace):
        msg = entitySpace.unpackMessage(package)
        if isinstance(msg, list):
            assert len(msg) is 2
            (serialId, response) = msg
            assert len(response) is 2
            return self(serialId, *response)

        raise TypeError(type(msg))

    def __init__(self, serialId, success, result):
        self.serialId = serialId
        self.success = success
        if success:
            self.result = result
        else:
            self.error_type = result[0]
            self.error_value = result[1]
            self.error_traceback = result[2]

    def __repr__(self):
        to = (' to [#%s]' % self.serialId) if self.serialId is not None else ''

        if self.success:
            return '%s%s -> %r' % (self.__class__.__name__, to, self.result)
        else:
            return '%s%s -> %s: %s' % (self.__class__.__name__, to,
                                       self.error_type, self.error_value)


# Peer Network I/O
READING_SIZE = 1
READING_PACKAGE = 2

class NotAvailableError(EOFError):
    def __init__(self, nbytes, available):
        EOFError.__init__(self, 'Bytes requested: %d, bytes available: %d' % (nbytes, available))
        self.nbytes = nbytes
        self.available = available

class PackageReader:
    def __init__(self):
        self.data_buffer = NewBuffer()
        self.state = READING_SIZE
        self.read_point = None
        self.pkg_size = 0
        self.pkg_size_length = 0

    def flip_buffer(self):
        if self.read_point is None:
            # Go into read mode.
            self.read_point = 0
        else:
            # Rewrite the buffer, go back into write mode.
            db = self.data_buffer
            db.seek(self.read_point, SEEK_SET)
            self.data_buffer = NewBuffer(db.read())
            self.read_point = None

    def read_bytes(self, nbytes):
        n = self.data_buffer.tell()
        d = self.data_buffer.read(nbytes)
        x = len(d)
        if x != nbytes:
            self.data_buffer.seek(n, SEEK_SET)
            raise NotAvailableError(nbytes, x)

        self.read_point += nbytes
        return d

    def write_data(self, data):
        # print '...', data
        b = self.data_buffer
        b.seek(0, SEEK_END)
        b.write(data)
        b.seek(0, SEEK_SET)

    def increasePackageSize(self, addend):
        self.pkg_size = IncreasePackageSize(self.pkg_size, addend)
    def packageSizeTerminated(self, addend):
        return PackageSizeTerminated(addend)

    READ_SIZE = 1024

    def handle_read(self):
        ##    if self.debug:
        ##        import pdb; pdb.set_trace()

        data = self.recv(self.READ_SIZE)
        if data == '':
            self.handle_close()
            return

        self.write_data(data)
        self.flip_buffer()

        # Network-sensitive data reading state machine:
        try:
            # Try to read all packages.
            while True:
                if self.state == READING_SIZE:
                    while True:
                        # Read variable-length big integer:
                        size_addend = self.read_bytes(1)

                        # Increase current package size.
                        self.increasePackageSize(size_addend)

                        if self.packageSizeTerminated(size_addend):
                            # Total package size received -- Go on to read package.
                            self.state = READING_PACKAGE
                            break

                        # Increase and continue.
                        self.pkg_size_length += 1

                if self.state == READING_PACKAGE: # Why test?
                    package = self.read_bytes(self.pkg_size)
                    self.state = READING_SIZE
                    self.pkg_size = 0
                    self.pkg_size_length = 0
                    self.handleIncomingPackage(package)

        except NotAvailableError:
            pass
        finally:
            self.flip_buffer()

class Fault(Exception):
    def __init__(self, etype, value, tb):
        self.error_type = etype
        self.error_value = value
        self.error_traceback = tb

        Exception.__init__(self, self.toString())

    def toString(self, tb = False):
        if not tb:
            return '%s: %s' % (self.error_type, self.error_value)

        d = ['Traceback (most recent call last):']
        for (filename, lineno, name, line) in self.error_traceback:
            d.append('  File "%s", line %d, in %s' % \
                     (filename, lineno, name))
            d.append('    %s' % line)

        d.append('%s: %s' % (self.error_type, self.error_value))
        return '\n'.join(d)

def interpretResponse(response, callEntityMethod = None, getEntityProperty = None):
    if response.success:
        result = response.result
        if isinstance(result, EntitySpace.Proxy):
            return EntitySpace.Binding(result, callEntityMethod, getEntityProperty)

        return result

    raise Fault(response.error_type,
                response.error_value,
                response.error_traceback)
