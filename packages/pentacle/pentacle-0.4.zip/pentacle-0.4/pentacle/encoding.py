# Data Format Encoding
__all__ = ['IncreasePackageSize', 'PackageSizeTerminated', 'EncodePackageSize',
           'Packager', 'Unpackager', 'Serializable', 'Mapping', 'Compress',
           'EntitySpace']

__others__ = ['unpackMessage', 'packMessage', 'unpackMessageSize', 'unpackMessageBuffer',
              'encodeMessage', 'encodeCommand', 'encodeResponse', 'encodeException',
              'encodePackageSize', 'encodePackage', 'flattenCommandMessage']

import types

from .runtime import *
from .architecture import Serializable

# Encoding Model
def getInstanceClassName(instance):
    cls = instance.__class__
    return '%s.%s' % (cls.__module__, cls.__name__)

class Table(dict):
    def __init__(self, **preflags):
        self.preflags = preflags

    def matching(self, type, **flags):
        effective = self.preflags.copy()
        effective.update(flags)

        # Decorator.
        def makeDispatcher(function):
            self[type] = function
            function._packaging_flags = effective
            return function

        return makeDispatcher

    @classmethod
    def IsFlagged(self, function, *flags):
        try: p = function._packaging_flags
        except AttributeError: return False
        else:
            for f in flags:
                if not p.get(f):
                    return False

            return True


COMPRESSION_LEVEL = {1: 'zlib', 2: 'gzip', 3: 'bz2'}

def Compress(packed, level):
    try: packed = packed.encode(COMPRESSION_LEVEL[level])
    except KeyError: return packed
    else: return 'Z%d%s' % (level, packed)

class Packager:
    def __init__(self, entityMap, buf = None, memo = None):
        self.entityMap = entityMap
        self.reset(buf = buf, memo = memo)

    def reset(self, buf = None, memo = None):
        self.buf = NewBuffer() if buf is None else buf
        self.memo = {}

    def compress(self, packed, level):
        if callable(level):
            return level(packed)

        return Compress(packed, level)

    def pack(self, value, compression = False):
        self.packObject(value, self.buf.write)
        packed = self.buf.getvalue()
        return self.compress(packed, compression)

    packaging = Table()

    def packObject(self, object, write):
        # Todo: write a version that pre-scans for memoized/marking requirements.
        # This will cut down on space required (marks set for every single object).
        # Will require a second packaging table for tracking this, and building
        # an intermediate id set to determine if the objects should be marked.
        if isinstance(object, Method):
            # SUPER-SPECIAL CASE!
            # Send this method request inline:
            result = Method.GetProperty(object)
            self.packObject(result, write)
            return

        mark = False
        try: p = self.packaging[type(object)]
        except KeyError:
            p = self.__class__.packUnknown
        else:
            if not Table.IsFlagged(p, 'primitive'):
                vId = id(object)
                try: mark = self.memo[vId]
                except KeyError:
                    mark = len(self.memo)
                    self.memo[vId] = mark
                else:
                    write('M%d#' % mark)
                    return

        if mark is not False:
            write('K%d#' % mark)
        p(self, object, write)

        ##    # Remembers already-packed objects.
        ##    vId = id(object)
        ##    try: mark = self.memo[vId]
        ##    except KeyError:
        ##        try: p = self.packaging[type(object)]
        ##        except KeyError:
        ##            p = self.__class__.packUnknown
        ##        else:
        ##            # If it's a new object, encode packed structure,
        ##            # but only if it's a known type.  This way, we're
        ##            # not marking references.
        ##            if not Table.IsFlagged(p, 'primitive'):
        ##                self.memo[vId] = len(self.memo)
        ##
        ##        p(self, object, write)
        ##    else:
        ##        # Otherwise, just encode the memory id.
        ##        write('M%d#' % mark)

    def packUnknown(self, object, write):
        refId = self.entityMap.getObjectRef(object)
        write('R%d#' % refId)

    def packProxy(self, value, write):
        write('R%d#' % value.refId)


    # Basic Primitives.
    @packaging.matching(types.BooleanType, primitive = True)
    def packBoolean(self, value, write):
        write('T' if value else 'F')

    @packaging.matching(types.NoneType, primitive = True)
    def packNone(self, value, write):
        write('N')

    # Numerical Types.
    @packaging.matching(types.IntType, primitive = True)
    def packInteger(self, value, write):
        write('I%d#' % value)

    @packaging.matching(types.FloatType, primitive = True)
    def packDecimal(self, value, write):
        write('D%f#' % value)

    @packaging.matching(types.LongType, primitive = True)
    def packInteger(self, value, write):
        write('L%ld#' % value)

    try:
        @packaging.matching(types.ComplexType, primitive = True)
        def packComplex(self, value, write):
            write('J%d+%d#' % (value.real, value.imag))

    except AttributeError:
        pass

    # String Types.
    @packaging.matching(types.StringType)
    def packString(self, value, write):
        write('S%d#%s' % (len(value), value))

    @packaging.matching(types.UnicodeType)
    def packUnicode(self, value, write):
        write('U%d#%s' % (len(value), value))

    # Structure Types.
    @packaging.matching(types.TupleType)
    def packTuple(self, value, write):
        write('P%d#' % len(value))
        for v in value:
            self.packObject(v, write)

    @packaging.matching(types.ListType)
    def packList(self, value, write):
        write('W%d#' % len(value))
        for v in value:
            self.packObject(v, write)

    @packaging.matching(types.DictType)
    def packDict(self, value, write):
        write('A%d#' % len(value))
        for (n, v) in value.iteritems():
            self.packObject(n, write)
            self.packObject(v, write)

    # Object Types.
    @packaging.matching(types.InstanceType)
    def packInstance(self, value, write):
        if isinstance(value, EntitySpace.Proxy):
            # Handle this separately from packUnknown, because
            # we don't want some dickhead to serialize it.
            self.packProxy(value, write)

        elif isinstance(value, EntitySpace.Binding):
            self.packProxy(EntitySpace.Binding.GetProxy(value), write)

        elif isinstance(value, Serializable):
            n = getInstanceClassName(value)
            write('H%d#%s' % (len(n), n))
            if getattr(value, '__getstate__'):
                write('S')
                state = value.__getstate__()
                self.packObject(state, write)

            else:
                write('D')
                self.packObject(value.__dict__, write)
        else:
            self.packUnknown(value, write)

class Unpackager:
    def __init__(self, entityMap, buf = None, memo = None):
        self.entityMap = entityMap
        self.reset(buf = buf, memo = memo)

    def reset(self, buf = None, memo = None):
        self.buf = NewBuffer() if buf is None else buf
        self.memo = {}

    def uncompress(self, packed, level):
        try: return packed.decode(COMPRESSION_LEVEL[level])
        except KeyError:
            return packed

    def unpack(self, m):
        if m[0] == 'Z':
            m = self.decompress(m[2:], int(m[1]))

        return self.unpackBuffer(NewBuffer(m))

    def unpackBuffer(self, buf):
        r = buf.read
        def readHash():
            b = ''
            while True:
                c = r(1)
                if c == '':
                    raise EOFError('Expected #')
                if c == '#':
                    return b

                b += c

        self.read = r
        self.readHash = readHash
        return self.unpackObject()

    def unpackObject(self):
        c = self.read(1)
        if c == 'M':
            # Read mark id for previously-memorized object.
            mark = int(self.readHash())
            return self.memo[mark]

        elif c == 'K':
            # Read mark id for this record.
            mark = int(self.readHash())
            c = self.read(1)
        else:
            mark = False

        # Read the object.
        u = self.packaging[c]
        object = u(self, self.readHash)

        if mark is not False:
            # Remember this object.
            self.memo[mark] = object

        return object

    packaging = Table()

    # Basic Primitives.
    @packaging.matching('N')
    def unpackNone(self, readHash):
        return None

    @packaging.matching('T')
    def unpackTrue(self, readHash):
        return True

    @packaging.matching('F')
    def unpackFalse(self, readHash):
        return False

    # Numerical Types.
    @packaging.matching('I')
    def unpackInteger(self, readHash):
        return int(readHash())

    @packaging.matching('D')
    def unpackDecimal(self, readHash):
        return float(readHash())

    @packaging.matching('L')
    def unpackInteger(self, readHash):
        return long(readHash())

    try:
        ComplexType = types.ComplexType

        @packaging.matching('J')
        def unpackComplex(self, readHash):
            (real, imag) = readHash().split('+')
            real = int(real)
            imag = int(imag)

            return self.ComplexType(real, imag)

    except AttributeError:
        pass

    # String Types.
    @packaging.matching('S')
    def unpackString(self, readHash):
        return str(self.read(int(readHash())))

    @packaging.matching('U')
    def unpackUnicode(self, readHash):
        return unicode(self.read(int(readHash())))

    # Structure Types.
    @packaging.matching('P')
    def unpackTuple(self, readHash):
        uo = self.unpackObject
        return tuple(uo() for x in xrange(int(readHash())))

    @packaging.matching('W')
    def unpackList(self, readHash):
        uo = self.unpackObject
        return [uo() for x in xrange(int(readHash()))]

    @packaging.matching('A')
    def unpackDict(self, readHash):
        uo = self.unpackObject
        return dict((uo(), uo()) for x in xrange(int(readHash())))

    # Object Types.
    @packaging.matching('H')
    def deserializeInstance(self, readHash):
        # Read class name and try to find/import it.
        className = self.read(int(readHash()))
        classObject = LookupClassObject(className)

        # Instantiate with nullary constructor.
        instance = classObject()

        # Reconstruct State.
        c = self.read(1)
        if c == 'S':
            state = self.unpackObject(readHash)
            instance.__setstate__(state)
        elif c == 'D':
            instance.__dict__ = self.unpackObject(readHash)
        else:
            raise TypeError('Instance deserialization type: %r' % c)

    # Reference Types.
    @packaging.matching('R')
    def deferenceEntity(self, readHash):
        return self.entityMap.getObjectOrProxy(int(readHash()))

class Mapping(dict):
    # Todo: weakref of proxied objects (is this sufficient policy?)
    # Also, this is blending into the 'packaging' concept, because of
    #    maintaining a data space.
    class Proxy:
        def __init__(self, refId):
            self.refId = refId
        def __repr__(self):
            return '<%s: %s>' % (self.__class__.__name__, self.refId)

    class Binding(MethodCall):
        # An entity proxy that has been bound to a controlling endpoint.
        def __init__(self, proxy, callEntityMethod, getEntityProperty):
            MethodCall.__init__(self, self.__callProxyMethod, self.__getProxyProperty)
            self.__proxy = proxy
            self.__callEntityMethod = callEntityMethod
            self.__getEntityProperty = getEntityProperty

        def __repr__(self):
            return '<%s: %r>' % (self.__class__.__name__, self.__proxy)

        def __callProxyMethod(self, name, *args, **kwd):
            return self.__callEntityMethod(self.__proxy, name, *args, **kwd)
        def __getProxyProperty(self, name):
            return self.__getEntityProperty(self.__proxy, name)

        def __call__(self, *args, **kwd):
            return self.__callEntityMethod(self.__proxy, '__call__', *args, **kwd)

        @classmethod
        def GetProxy(self, binding):
            # Return the private variable.
            return binding.__proxy

    def getObjectRef(self, object):
        oId = id(object)
        if oId not in self:
            self[oId] = object

        return oId

    def getObjectOrProxy(self, oId):
        try: return self[oId]
        except KeyError:
            proxy = self[oId] = self.Proxy(oId)
            return proxy

    def getObjectOrError(self, oId):
        try: return self[oId]
        except KeyError:
            raise ValueError(oId)

# Mixins:
class EntityPackaging:
    compression_level = None

    def packMessage(self, message, compression = None):
        if compression is None:
            compression = self.compression_level

        p = Packager(self)
        return p.pack(message, compression = compression)

    def unpackMessage(self, message):
        u = Unpackager(self)
        return u.unpack(message)

class EntityCoding:
    def encodePackageSize(self, size):
        return EncodePackageSize(size)
    def encodePackage(self, package):
        return self.encodePackageSize(len(package)) + package
    def encodeMessage(self, message):
        return self.encodePackage(self.packMessage(message))

    def flattenCommandMessage(self, command, (serialId, flags), args, kwd):
        # assert isinstance(command, basestring)
        message = [command, serialId, flags]
        if args:
            message.append(args)
        if kwd:
            message.append(kwd)

        return message

    def encodeSerialCommand(self, command, (serialId, flags), *args, **kwd):
        flat = self.flattenCommandMessage(command, (serialId, flags), args, kwd)
        return self.encodeMessage(flat)
    def encodeNonSerialCommand(self, command, *args, **kwd):
        return self.encodeSerialCommand(command, (None, 0), *args, **kwd)

    def encodeResponse(self, serialId, response):
        return self.encodeMessage([serialId, [True, response]])
    def encodeException(self, serialId, (etype, value, tb)):
        return self.encodeMessage([serialId, [False, (etype, value, tb)]])

class EntitySpace(Mapping, EntityPackaging, EntityCoding):
    pass


# Data Segment Routines

# These do not work because I don't understand byte-order:
##    def EncodePackageSize(size):
##        buf = ''
##        lo = 0
##        while size:
##            lo = (size & 255)
##            buf += chr(lo)
##            size >>= 8
##
##        if (lo & 128):
##            buf += chr(0)
##
##        return buf
##
##    def IncreasePackageSize(size, addend):
##        # low endian (?)
##        return (size << 8) + ord(addend)
##
##    def PackageSizeTerminated(addend):
##        return not (ord(addend) & (128))

# Less packed style:
def EncodePackageSize(size):
    return '%d.' % size

def IncreasePackageSize(size, addend):
    if addend.isdigit():
        return size * 10 + int(addend)

    return size

def PackageSizeTerminated(addend):
    return addend == '.'


# Other Routines
def unpackMessageSize(buf):
    size = 0
    size_length = 0

    for size_length in xrange(len(buf)):
        c = buf[size_length]
        size = IncreasePackageSize(size, c)
        if PackageSizeTerminated(c):
            break

    return (size, size_length)

def unpackMessageBuffer(buf):
    (size, i) = unpackMessageSize(buf)
    buf = buf[i:]
    assert len(buf) == size
    return unpackMessage(buf)

defaultSpace = EntitySpace()
packMessage = defaultSpace.packMessage
unpackMessage = defaultSpace.unpackMessage

from marshal import loads as unpackMessageBinary
from marshal import dumps as packMessageBinary

# Testing
def inspectPackedMessage(message):
    buf = NewBuffer(message)
    inspectPackedBuffer(buf)

def writeIndent(indent, message, stream = None, tab = '  '):
    if stream is None:
        from sys import stdout as stream

    stream.write(tab * indent)
    stream.write(message)
    stream.write('\n')

def inspectPackedBuffer(buf, indent = 0):
    r = buf.read

    def readHash():
        b = ''
        while True:
            c = r(1)
            if c == '':
                raise EOFError('Expected #')
            if c == '#':
                return b

            b += c

    c = r(1)
    if c:
        if c == 'K':
            writeIndent(indent, 'Mark: #%d' % int(readHash()))
            inspectPackedBuffer(buf, indent = indent + 1)

        elif c == 'M':
            writeIndent(indent, '[ Marked #%s ]' % readHash())

        elif c in 'NTF':
            writeIndent(indent, str(dict(N = None, T = True, F = False)))

        elif c in 'IDLJ':
            writeIndent(indent, '%s: %r' % (dict(I = 'Integer',
                                                 D = 'Float',
                                                 L = 'Long',
                                                 J = 'Complex')[c],
                                            readHash()))

        elif c in 'SU':
            n = int(readHash())
            writeIndent(indent, '%s: %s' % (dict(S = 'String',
                                                 U = 'Unicode')[c],
                                            r(n)))

        elif c in 'PW':
            n = int(readHash())
            writeIndent(indent, '%s (%d):' % (dict(P = 'Tuple',
                                                   W = 'List')[c],
                                              n))

            indent += 1
            for x in xrange(n):
                inspectPackedBuffer(buf, indent = indent)

            indent -= 1

        elif c == 'A':
            n = int(readHash())
            writeIndent(indent, 'Dict (%d):' % n)

            indent += 1
            for x in xrange(n):
                writeIndent(indent, 'Key:')
                inspectPackedBuffer(buf, indent = indent + 1)

                writeIndent(indent, 'Value:')
                inspectPackedBuffer(buf, indent = indent + 1)

            indent -= 1

        elif c == 'H':
            writeIndent(indent, 'Instance:')
            indent += 1
            writeIndent(indent, 'Class Name:')
            inspectPackedBuffer(buf, indent = indent + 1)

            c = r(1)
            assert c

            if c in 'SD':
                writeIndent(indent, '%s:' % dict(S = 'State',
                                                 D = 'Dict')[c])

                inspectPackedBuffer(buf, indent = indent + 1)

            else:
                raise TypeError('Instance deserialization type: %r' % c)

        elif c == 'R':
            writeIndent(indent, 'Entity Reference: #%s' % readHash())

        else:
            writeIndent(indent, c + buf.read())

def test():
    o = object()
    structure = [[5, 'Hi There', 8.43, (6j + 1)], ()]
    s2 = [structure, [structure]]
    data = [o, o, dict(n = o, structure = structure,
                       s2 = s2)]

    b = packMessage(data)
    inspectPackedMessage(b)

    # defaultSpace.clear()

    value = unpackMessage(b)
    from pprint import pprint
    pprint(value)

if __name__ == '__main__':
    test()
