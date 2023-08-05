# Local debugging.
from pdb import set_trace, runcall

def breakOn(function):
    def debugCall(*args, **kwd):
        set_trace()
        return function(*args, **kwd)

    print 'DEBUGGING ON', functionName(function)
    return debugCall

def functionName(function):
    return '%s.%s' % (getattr(function, '__module__', '?'),
                      getattr(function, '__name__', '?'))
