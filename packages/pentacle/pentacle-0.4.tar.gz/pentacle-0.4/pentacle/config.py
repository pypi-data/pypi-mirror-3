# Network and Application Config
__all__ = ['Configuration']

from ConfigParser import ConfigParser, DEFAULTSECT, NoSectionError, NoOptionError
from optparse import OptionParser, Values
from os.path import dirname, abspath, normpath
import re

from .architecture import Component
from .runtime import Object, NewBuffer

# Todo: This module should require tons of documentation.  For example, vectored
# options, defaults operation (they're not interpolated further using Common),
# when optparse-derived default values are lists (and how they're semi-flattened),
# config.set (and its default_section passed through factories), simplification
# layers, and the priority of these option forms:
def getCmdlnOptionForms(name):
    yield name
    yield name.replace('-', '_')
def getSectionOptionForms(name):
    yield name
    yield name.replace('_', '-')

class DeferredDefaultValues(Values, object):
    class DefaultValue(Exception):
        def __init__(self, value):
            self.value = value

    def __init__(self, *args, **kwd):
        Values.__init__(self, *args, **kwd)
        self.__attrSet_counters = {} # Avoid counting defaults init.

    def __setattr__(self, name, value):
        # Track the number of times this is set.
        try: self.__attrSet_counters[name] = self.__attrSet_counters.get(name, 0) + 1
        except AttributeError:
            # Ignore non-existence counters variable during defaults initialization.
            pass

        self.__dict__[name] = value

    def getDefaultSensitive(self, name):
        '''
        Return the option value only if it was explicitly set.
        Otherwise, raise an exception with the default value.
        '''

        try: value = self.__dict__[name]
        except KeyError:
            raise AttributeError(name)

        if not self.__attrSet_counters.get(name, 0):
            # Raise the default value as an exception if it's not already set.
            raise self.DefaultValue(value)

        return value

    @classmethod
    def FromParserDefaults(self, parser):
        # Get normal default values from parser, but then convert to a simple
        # dict type for initialization of our class impl.
        values = parser.get_default_values()
        values = dict((n, getattr(values, n)) for n in parser.defaults.iterkeys())
        return self(values)

class Simplifications:
    @classmethod
    def Get(self, status):
        if status is True:
            return self.levelOneSimplification
        if callable(status):
            # Previous or custom simplifications
            return status

        return self.noSimplification

    @staticmethod
    def noSimplification(value):
        return value

    @staticmethod
    def levelOneSimplification(value):
        if isinstance(value, basestring):
            lval = value.lower()
            if lval in ('true', 'yes', 'on'):
                return True
            if lval in ('false', 'no', 'off'):
                return False
            if value.isdigit():
                return int(value)

        return value

# Please, don't even try to match negative numbers.
MATCH_OPTION_VECTOR = re.compile('(.*?)\.(\d+)').match

class Configuration(Component):
    Meta = Object.Meta('filename')

    @classmethod
    def FromCmdln(self, argv, default_config_file, *components, **kwd):
        # Build the cmdln-option parser, load components, then pass to ini.
        parser = OptionParser()
        parser.add_option('-C', '--config-file', default = default_config_file)

        for c in components:
            newP = c.addCmdlnOptions(parser)
            if newP is not None:
                parser = newP

        values = DeferredDefaultValues.FromParserDefaults(parser)
        (options, args) = parser.parse_args(argv, values = values)
        return self.FromCmdlnOptions(options, **kwd)

    @classmethod
    def FromCmdlnOptions(self, options, **kwd):
        config_file = self.getPathName(options.config_file)

        cfg = ConfigParser()
        cfg.read([config_file])

        return self(config_file, cfg, options, **kwd)

    @classmethod
    def FromString(self, string, **kwd):
        cfg = ConfigParser()
        cfg.readfp(NewBuffer(string))

        return self(None, cfg, **kwd)

    @classmethod
    def FromFile(self, filename, **kwd):
        cfg = ConfigParser()
        cfg.read([filename])

        return self(filename, cfg, **kwd)

    @classmethod
    def FromFileObject(self, fileObj, **kwd):
        cfg = ConfigParser()
        cfg.readfp(fileObj)

        return self(fileObj.name, cfg, **kwd)

    def __init__(self, filename, cfg, options = None, default_section = None):
        self.filename = filename or ''
        self.cfg = cfg
        self.options = options
        self.set = self.ConfigSet(self, section = default_section, simplify = True)
        self.loadVariables()

        # Configure the configurator:
        # self.simplify = True

    class ConfigSet: # (Object)
        def __init__(self, cfgObj, section = None, simplify = False):
            self.__cfgObj = cfgObj
            self.__section = section
            self.__simplify = simplify

        def __getattr__(self, name):
            return self.__cfgObj.getOption(name, section = self.__section,
                                           simplify = self.__simplify)

    def loadVariables(self):
        self.variables = {} # Because asDict uses it!

        cfgpath = abspath(normpath(self.filename))
        self.variables['config-file'] = cfgpath
        self.variables['config-dir'] = dirname(cfgpath)

        self.variables.update(self.getSectionObject('Common').asDict())

    def getOption(self, name, section = None, default = None, simplify = False):
        # Command-line always overrides.
        simplify = Simplifications.Get(simplify)
        if self.options is not None:
            for form in getCmdlnOptionForms(name):
                try: return simplify(self.options.getDefaultSensitive(form))
                except DeferredDefaultValues.DefaultValue, d:
                    default = d.value
                    break
                except AttributeError:
                    continue

        return self.getSectionOption(name, section, default = default, simplify = simplify)

    def getOptionMultiple(self, name, section = None, default = None, simplify = False):
        # Get all possible option values, merging.
        simplify = Simplifications.Get(simplify)
        result = []
        if self.options is not None:
            for form in getCmdlnOptionForms(name):
                try: oneOpt = simplify(self.options.getDefaultSensitive(form))
                except DeferredDefaultValues.DefaultValue, d:
                    default = d.value
                    break
                except AttributeError:
                    continue
                else:
                    if not isinstance(oneOpt, list):
                        result.append(oneOpt)

                    # Just one option.
                    break

        result.extend(self.getSectionOptionVector(name, section = section, default = default, simplify = simplify))
        return result
    __getitem__ = getOptionMultiple

    ALLOWED_SETOPTION_KWD = set(['simplify', 'section'])
    def getOptionSet(self, *names, **kwd):
        assert self.ALLOWED_SETOPTION_KWD.issuperset(kwd.keys())
        for n in names:
            yield self.getOption(n, **kwd)

    # Sections.
    def getSectionOption(self, name, section = None, default = None, simplify = False):
        if section is None:
            section = DEFAULTSECT

        simplify = Simplifications.Get(simplify)
        for form in getSectionOptionForms(name):
            try: return simplify(self.cfg.get(section, form, vars = self.variables))
            except (NoSectionError, NoOptionError):
                continue

        return default # don't simplify

    def getSectionOptionVector(self, name, section = None, default = None, simplify = False):
        try: sopts = self.cfg.options(section)
        except NoSectionError: pass
        else:
            top = [0]
            def ov(sopts):
                t = {}
                x = 0
                for n in sopts:
                    m = MATCH_OPTION_VECTOR(n)
                    if m is not None:
                        (o, i) = m.groups()
                        if o == name:
                            if i:
                                i = int(i)
                                if i > x:
                                    x = i
                            else:
                                i = 0

                            t[i] = self.cfg.get(section, n, vars = self.variables)

                top[0] = x
                return t

            simplify = Simplifications.Get(simplify)
            t = ov(sopts)
            if t:
                for i in xrange(top[0] + 1):
                    yield simplify(t.get(i))

                raise StopIteration

        # If nothing was found, use default(/semi-flattened), but DON'T SIMPLIFY.
        if isinstance(default, (list, tuple)):
            for v in default:
                yield v
        else:
            yield default

    def getSectionObject(self, name):
        return self.Section(self, name)

    class Section(Object):
        Meta = Object.Meta('name')

        def __init__(self, cfgObj, name):
            self.cfgObj = cfgObj
            self.name = name

        def getOption(self, opt, **kwd):
            return self.cfgObj.getOption(opt, section = self.name, **kwd)
        get = getOption

        def getOptionMultiple(self, name, **kwd):
            return self.cfgObj.getOptionMultiple(name, section = self.name, **kwd)
        __getitem__ = getOptionMultiple

        def options(self):
            return self.cfgObj.cfg.options(self.name)

        def asDict(self, multiple = False, **kwd):
            if multiple:
                return dict((n, self.getOptionMultiple(n, **kwd)) for n in self.options())

            # More basic: (no simplification)
            cfg = self.cfgObj.cfg
            vars = self.cfgObj.variables
            g = cfg.get
            s = self.name

            try: return dict((n, g(s, n, vars = vars)) for n in cfg.options(s))
            except NoSectionError:
                return dict()

    def sectionNames(self):
        return self.cfg.sections()
    def __iter__(self):
        return iter(self.sectionNames())

# This is another layer aimed at making configuration more convenient.
# Todo: move all this into ini.py??
SECTION_MATCH = re.compile(r'^\s*\[([^]]+)\]\s*$').match
VALUEPAIR_MATCH = re.compile('^\s*([^:]+)\s*:\s*(.*)$').match
COMMENT_MATCH = re.compile(r'^\s*;|#').match

def parseINI(inputSource):
    ini = {}
    sectionName = None

    for line in inputSource:
        # Ignore comments.
        if COMMENT_MATCH(line):
            continue

        # Match section header.
        m = SECTION_MATCH(line)
        if m is not None:
            n = m.groups()[0]
            if n != sectionName:
                sectionName = n
                currentSection = ini.setdefault(n, {})

            continue

        # Match value pair line.
        m = VALUEPAIR_MATCH(line)
        if m is not None:
            (name, value) = m.groups()

            if currentSection is None:
                sectionName = DEFAULTSECT
                currentSection = ini.setdefault(sectionName, {})

            currentSection[name] = value.rstrip()

    return ini

def buildSectionINI(__name, **values):
    # Automatic de-simplification.
    def norm(r = {}):
        for (n, v) in values.iteritems():
            try: e = [r[n]]
            except KeyError:
                if isinstance(v, bool):
                    v = 'true' if v else 'false'
                elif isinstance(v, (int, long, float)):
                    v = str(v)
                elif isinstance(v, INI.Value):
                    v = v.resolve()

                assert isinstance(v, basestring)
                assert '\n' not in v

                r[n] = v
            else:
                e.append(v)
                e[n] = v

        return r

    def rebuild():
        for (n, v) in norm().iteritems():
            n = n.replace('_', '-')
            if isinstance(v, list):
                for i in xrange(len(v)):
                    yield '%s.%d: %s' % (n, i, v[i])

            else:
                yield '%s: %s' % (n, v)

    return '[%s]\n%s\n' % (__name, '\n'.join(rebuild()))

def buildConfigINI(*sections):
    return '\n'.join(buildSectionINI(name, **values) \
                     for (name, values) in sections)

class INI:
    class Value:
        pass

    @classmethod
    def FromINI(self, source):
        if isinstance(source, basestring):
            source = NewBuffer(source)
        else:
            assert hasattr(source, 'read')

        return self(**parseINI(source))

    def toConfigObject(self, **kwd):
        return Configuration.FromString(self.build(), **kwd)

    def __init__(self, **init):
        self.sections = dict()

        for (n, s) in init.iteritems():
            assert isinstance(s, dict)
            for (k, v) in s.iteritems():
                k = k.replace('_', '-')
                self.sections.setdefault(n, {})[k] = v

    def __getitem__(self, name):
        if isinstance(name, basestring):
            name = name.split('.', 1)

        (section, option) = name
        option = option.replace('_', '-')
        return self.sections[section][option]

    def __setitem__(self, name, value):
        if isinstance(name, basestring):
            name = name.split('.', 1)

        (section, option) = name
        option = option.replace('_', '-')

        if isinstance(value, (list, tuple)):
            assert all(isinstance(v, (basestring, int, long, float, bool)) for v in value)
            s = self.sections.setdefault(section, {})[option] = list(value)
        else:
            assert isinstance(value, (basestring, int, long, float, bool))
            self.sections.setdefault(section, {})[option] = value

    def __delitem__(self, name):
        name = name.split('.', 1)
        if len(name) == 1:
            del self.sections[name[0]]
        else:
            (section, option) = name
            option = option.replace('_', '-')
            del self.sections[section][option]

    def build(self):
        return buildConfigINI(*self.sections.iteritems())
    def buildSection(self, name):
        return buildSectionINI(**self.sections[name])
    __str__ = build

    def __iter__(self):
        return self.sections.iterkeys()
    def options(self, name):
        return self.sections[name].iterkeys()

    def __iadd__(self, other):
        if isinstance(other, dict):
            other = INI(**other)

        for section in other:
            for o in other.options(section):
                name = '%s.%s' % (section, o)
                self[name] = other[name]

        return self

    def __add__(self, other):
        new = INI()
        new += self
        new += other
        return new

    def copy(self):
        return INI(**self.sections)
