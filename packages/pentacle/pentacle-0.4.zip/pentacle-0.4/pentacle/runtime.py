# Dealing with the Platform/Runtime Core
# todo:
#   break into package:
#       core.py (Most of these objects)
#       utility.py (Misc functional routines)
#
#       other platform-related modules
#
__all__ = ['Object', 'Synthetic', 'breakOn', 'set_trace', 'runcall',
           'getSystemException', 'getCurrentRuntimeFrame', 'showTraceback',
           'printException', 'basename', 'expanduser', 'expandvars', 'nth',
           'getCurrentSystemTime', 'LookupObject', 'MethodCall', 'Method',
           'threading', 'NewBuffer', 'sys', 'extractTraceback',
           'getCapitalizedName', 'synchronized', 'synchronizedWith',
           'getAttributeChain', 'Shuttle', 'buildCmdln',
           'Print', 'PrintTo', 'Throw', 'Catch', 'repeat',
           'sendSignal', 'thisProcessId', 'contextmanager']

from os.path import basename, expanduser, expandvars
from sys import exc_info as getSystemException, _getframe as getCurrentRuntimeFrame
from traceback import print_exc as printException, extract_tb
from thread import start_new_thread as _nth
from time import time as getCurrentSystemTime
from StringIO import StringIO as NewBuffer

class Unimplemented:
    def __init__(self, name, cause):
        self.name = name
        self.cause = cause

    def __call__(self, *args, **kwd):
        raise NotImplementedError(self.cause)

def ImportImplementation(moduleName, objectName = ''):
    try: return __import__(moduleName, fromlist = [objectName])
    except ImportError, e:
        return Unimplemented(moduleName, e)

##    sendSignal = ImportImplementation('os', 'kill')
##    thisProcessId = ImportImplementation('os', 'getpid')

try: from os import kill as sendSignal
except ImportError, e:
    sendSignal = Unimplemented('sendSignal', e)

try: from os import getpid as thisProcessId
except ImportError, e:
    thisProcessId = Unimplemented('thisProcessId', e)

import threading
import sys

from .debugging import breakOn, set_trace, runcall

class Object:
    class Meta:
        Attributes = []

        def __init__(self, *attributes):
            self.Attributes = attributes

        @classmethod
        def toString(self, instance):
            def getAttr(name):
                if callable(name):
                    attr = name(instance)
                    name = ''
                elif isinstance(name, (list, tuple)):
                    (name, function) = name
                    assert callable(function)
                    attr = function(instance)
                else:
                    attr = getattr(self, name)
                    if name.endswith('()') and callable(attr):
                        attr = attr()

                return (name, attr)

            return ', '.join('%s = %r' % getAttr(n) for n in self.Attributes)

        # Serialization??

    def __repr__(self):
        attrs = self.Meta.toString(self)
        return '<%s%s%s>' % (self.__class__.__name__,
                             attrs and ' ' or '', attrs)

    # __str__ = __repr__

class Synthetic:
    def __init__(self, **kwd):
        self.__dict__ = kwd
    def __repr__(self):
        return 'Synthetic: %r' % self.__dict__

    def update(self, values = None, **kwd):
        if isinstance(values, Synthetic):
            self.__dict__.update(values.__dict__)
        elif isinstance(values, dict):
            self.__dict__.update(values)
        self.__dict__.update(kwd)

# Should probably go in architecture:
class Method:
    # Should be called "Node" or something, since it's not always a method.
    def __init__(self, name, call, getprop = None):
        self.__name = name
        self.__call = call
        self.__getprop = getprop

    def __getattr__(self, name):
        return Method('%s.%s' % (self.__name, name),
                      self.__call, self.__getprop)

    def __call__(self, *args, **kwd):
        return self.__call(self.__name, *args, **kwd)

    @classmethod
    def GetProperty(self, methodObject):
        # Not this easy: should call another __getprop method that
        # doesn't rely in __getattr__ on the remote server, but something
        # adjacent to callEntityMethod.
        return methodObject.__getprop(methodObject.__name)

class MethodCall:
    def __init__(self, callMethod, getProperty = None):
        self.__callMethod = callMethod
        self.__getProperty = getProperty
    def __getattr__(self, name):
        return Method(name, self.__callMethod, self.__getProperty)

from types import MethodType, InstanceType

def getObjectAttribute(object, name):
    try: return getattr(object, name)
    except AttributeError:
        if isinstance(object, InstanceType):
            return getInstanceAttribute(object, name)

def walkAllBases(cls):
    visited = set()
    def _walk(c, w):
        visited.add(c)
        for b in c.__bases__:
            if b not in visited:
                w(b, w)

    _walk(cls, _walk)
    return visited

def getInstanceAttribute(object, name):
    cls = object.__class__
    try: member = getattr(cls, name)
    except AttributeError:
        for cls in walkAllBases(cls): # Rebinding variable 'cls'
            try: member = getattr(cls, name)
            except AttributeError:
                pass
        else:
            raise AttributeError(name)

    if isinstance(member, MethodType):
        # Bind it.
        if member.im_self is None:
            return MethodType(object, object, cls)

    return member

def getAttributeChain(object, name):
    for name in name.split('.'):
        object = getObjectAttribute(object, name)

    return object

def LookupObject(name, raise_import_errors = False):
    'A clever routine that can import an object from a system module from any attribute depth.'
    parts = name.split('.')

    moduleObject = None
    module = None
    n = len(parts)
    x = 0

    while x < n:
        name = '.'.join(parts[:x+1])
        moduleObject = module

        # Try to find the module that contains the object.
        try: module = __import__(name, globals(), locals(), [''])
        except ImportError:
            break

        x += 1

    # No top-level module could be imported.
    if moduleObject is None:
        if x == 1:
            # There was no sub-object name specified: normally,
            # we don't want namespaces, but let's allow it now.
            return module

        raise ImportError(name)

    object = moduleObject
    while x < n:
        # Now look for the object value in the module.

        # If an attribute can't be found -- this is where we raise the original import-error?
        ##    if raise_import_errors:
        ##        module = __import__(name, globals(), locals(), [''])

        object = getattr(object, parts[x])
        x += 1

    return object

def getCapitalizedName(name):
    return name[0].upper() + name[1:]

def showTraceback():
    f = getCurrentRuntimeFrame(1)
    stack = []
    while f:
        stack.append(f)
        f = f.f_back

    tb = []
    stack.reverse()
    for f in stack:
        co = f.f_code
        tb.append('%s(%d)%s()' % (basename(co.co_filename), f.f_lineno, co.co_name))

    print '\n'.join(tb) + '\n'


_sorted_system_paths_memo = None #: Internal
_sorted_system_paths_key = set()

def isSortedSystemPathMemoOutdated():
    if _sorted_system_paths_memo is None:
        return True

    fresh_key = set(sys.path)
    global _sorted_system_paths_key
    if _sorted_system_paths_key != fresh_key:
        _sorted_system_paths_key = fresh_key
        return True

def getSortedSystemPaths():
    if isSortedSystemPathMemoOutdated():
        global _sorted_system_paths_memo
        _sorted_system_paths_memo = [(len(p), p) for p in sys.path]
        _sorted_system_paths_memo.sort(lambda a, b:cmp(a[0], b[0])) # descending length?

    return _sorted_system_paths_memo

# This shouldn't have to change even if new paths are added.
_stripped_path_memo = {}

def stripSystemPath(filename, system_paths):
    try: return _stripped_path_memo[filename]
    except KeyError:
        for (n, p) in system_paths:
            if filename.startswith(p):
                if p:
                    # Chop off the path this module was loaded from.
                    stripped = filename[n+1:]
                    break
        else:
            # Nothing found??  Probably ''
            stripped = filename

        _stripped_path_memo[filename] = stripped
        return stripped

def extractTraceback(tb, limit = None, fullpaths = False):
    stack = extract_tb(tb, limit = limit)
    if not fullpaths:
        system_paths = getSortedSystemPaths()

        for i in xrange(len(stack)):
            # Strip off the path part used for locating.
            (filename, lineno, name, line) = stack[i]
            filename = stripSystemPath(filename, system_paths)
            stack[i] = (filename, lineno, name, line)

    return stack

def synchronized(function):
    lock = threading.Lock()
    def synchronizedFunction(*args, **kwd):
        with lock:
            return function(*args, **kwd)

    return synchronizedFunction

def synchronizedWith(object, recursive = False):
    def buildLock():
        return threading.RLock() \
               if recursive \
               else threading.Lock()

    if object is None:
        # Anonymous lock.
        __synch_lock = buildLock()
        def getLock():
            return __synch_lock
    else:
        # Control-object-accessible lock.
        def getLock():
            return object.__synch_lock

        try: getLock()
        except AttributeError:
            object.__synch_lock = buildLock()

    def makeSynchronizer(function):
        def synchronizedFunctionWith(*args, **kwd):
            with getLock():
                return function(*args, **kwd)

        return synchronizedFunctionWith

    return makeSynchronizer


class Shuttle:
    def __init__(self, function, *args, **kwd):
        self.function = function
        self.curriedArgs = args
        self.curriedKwd = kwd

    def __call__(self, *theseArgs, **thisKwd):
        args = self.curriedArgs + theseArgs
        kwd = self.curriedKwd.copy()
        kwd.update(thisKwd)
        return self.function(*args, **kwd)

def buildCmdlnWithBase(baseArgs, baseOptions, *args, **kwd):
    args = list(baseArgs) + list(args)
    opts = baseOptions.copy()
    opts.update(kwd)

    def iterateOptions(opts):
        for (n, v) in opts.iteritems():
            if isinstance(v, (list, tuple)):
                for x in v:
                    yield (n, x)

            else:
                yield (n, v)

    def optionToSwitch((n, v)):
        n = n.replace('_', '-')
        if v is True:
            return '--%s' % n

        return '--%s=%s' % (n, v)

    cmdln = map(optionToSwitch, iterateOptions(opts))
    cmdln.extend(args)

    return cmdln

def buildCmdln(*args, **kwd):
    return buildCmdlnWithBase((), {}, *args, **kwd)

def nth(function, *args, **kwd):
    return _nth(function, args, kwd)

def Catch(f, *catches, **others):
    try: return f()
    except:
        from sys import exc_info
        (etype, value, tb) = exc_info()

        for (ctype, cf) in catches:
            if isinstance(value, ctype):
                return cf(etype, value, tb)

        try: excall = others['Except']
        except KeyError: raise etype, value, tb
        else: return excall(etype, value, tb)

    finally:
        try: fin = others['Finally']
        except KeyError: pass
        else: fin()

def Print(*args):
    print ' '.join(map(str, args))
def PrintTo(stream, *args):
    print >> stream, ' '.join(map(str, args))

def Throw(etype, *args, **kwd):
    raise etype(*args, **kwd)

def repeat(f, n, filter = None):
    from __builtin__ import filter as ff
    return ff(filter, (f(x) for x in xrange(n)))

# Sorry: require this:
from contextlib import contextmanager
