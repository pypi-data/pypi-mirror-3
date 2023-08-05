# Pentacle Client Support (User-Auth-Group)
'''
from pentacle.client import support
user = support.User('login', 'secret')
group = user['~/services']

group.managerConfig(port = 7040)
group.serviceConfig('docmgr',
                    partner_name = 'Westmetal Documents',
                    service_api = '@westmetal/document/browser')

group.docmgr.openUrl('http://google.com')
'''

from . import Session, Client, CalculateDigest
from ..config import Configuration, INI
from ..application import Application
from ..runtime import *
from ..bus import ServiceManagerName

from os.path import expanduser, expandvars, join as joinpath
from os import makedirs
from errno import ENOENT, EEXIST
from collections import namedtuple
import re

def ensure_directory(paths):
    try: makedirs(paths)
    except OSError:
        (etype, value, tb) = getSystemException()
        if value.errno != EEXIST:
            raise (etype, value, tb)

MANAGER_PREFIX = '.manager'
MANAGER_SECTION = 'Manager'
SERVICE_SECTION = 'Service'

class Group(object):
    # A Group manages a group of service-partner clients configured
    # using a directory of files that describe their services and relationship
    # to a Spline Manager.
    #
    # The primary purpose is to expose a simplified object-oriented service
    # access to a no-brainer external configuration system.
    #
    def __init__(self, main_path, interpolate = True, user = None):
        self._main_path = main_path
        self._interpolate = interpolate
        self._user = user
        self._services = dict()

    def _getPathFromMain(self, *args):
        path = self._main_path
        if self._interpolate:
            path = expandvars(expanduser(path))

        return joinpath(path, *args)

    class NoConfigFile(IOError):
        pass

    def _getConfigFromMain(self, name = MANAGER_PREFIX):
        try: fileObj = open(self._getPathFromMain('%s.cfg' % name))
        except IOError:
            (etype, value, tb) = getSystemException()
            if value.errno == ENOENT:
                raise self.NoConfigFile(name)

            raise (etype, value, tb)

        return Configuration.FromFileObject(fileObj)

    def _getManagerFullAddress(self):
        # Todo: some kind of unification with server configs (sections?)
        cfg = self._getConfigFromMain()
        cfg = cfg.ConfigSet(cfg, section = MANAGER_SECTION, simplify = True)
        return (cfg.address or 'localhost', cfg.port or Application.DEFAULT_PORT)

    def _getServiceFullAddress(self, partner_name):
        (address, port) = self._getManagerFullAddress()
        with Session(self._user.Open(address, port)) as mgr:
            with mgr.api(ServiceManagerName) as spline:
                info = spline.GetPartnerInfo(partner_name)
                return (address, info['service_port'])

    def _getServiceConfigData(self, name):
        cfg = self._getConfigFromMain(name)
        cfg = cfg.ConfigSet(cfg, section = SERVICE_SECTION, simplify = True)
        service_api = cfg.service_api
        partner_name = cfg.partner_name

        # (Maybe do this validation earlier??)
        assert service_api
        assert partner_name
        return dict(service_api = service_api,
                    partner_name = partner_name)

    def _getServiceConf(self, name):
        try: return self._services[name]
        except KeyError:
            s = self._services[name] = self.ServiceConf(self, name)
            return s

    def _getServiceAccess(self, name):
        return self._getServiceConf(name).access

    def __getattr__(self, name):
        # Get a service object.
        if name.startswith('_'):
            return object.__getattribute__(self, name)

        return self._getServiceAccess(name)

    def __setitem__(self, name, value):
        # Write a config file.
        value = str(value)
        with open(self._getPathFromMain(name) + '.cfg', 'wb') as fl:
            fl.write(value)
            fl.flush()

    def serviceConfig(self, name, **kwd):
        ensure_directory(self._getPathFromMain())
        self[name] = INI(**{SERVICE_SECTION: kwd})

    def managerConfig(self, **kwd):
        ensure_directory(self._getPathFromMain())
        self[MANAGER_PREFIX] = INI(**{MANAGER_SECTION: kwd})

    class ServiceConf:
        def __init__(self, group, name):
            self._group = group
            self._name = name

        def getConfigData(self):
            # Collect data for connecting to the service-api
            data = self._group._getServiceConfigData(self._name)
            (address, service_port) = self._group._getServiceFullAddress(data['partner_name'])
            return (address, service_port, data['service_api'])

        def openApi(self):
            # OpenPartneredClient -- Make the connection now, return the
            # invocator to the remote service api by name.
            (address, service_port, service_api) = self.getConfigData()
            assert isinstance(service_port, int)

            client = self._group._user.Open(address, service_port)
            return client.api.open(service_api)

        @property
        def access(self):
            try: return self._api.invoke
            except AttributeError:
                api = self._api = self.openApi()
                return api.invoke

        # ok, and toString or INI-building auto-write functionality.

class Authorization:
    def __init__(self, username, secretKey):
        self.username = username
        self.secretKey = secretKey

    def Open(self, hostname, port):
        client = Client.Open(hostname, port)
        return self.Authenticate(client)

    def Authenticate(self, client):
        auth = CalculateDigest(self.secretKey, self.username)
        client.call.login(self.username, auth)
        return client

class User(Authorization):
    # Provides a top-level grouping of different calling configurations
    # as well as an authorization mechanism for complete access.
    def Group(self, main_path, *args, **kwd):
        try: n = self._groups
        except AttributeError:
            n = self._groups = {}

        try: return n[main_path]
        except KeyError:
            kwd['user'] = self
            c = n[main_path] = Group(main_path, *args, **kwd)
            return c

    def __getitem__(self, main_path):
        return self.Group(main_path)

class APICall:
    class APIHandle:
        class APIHandleCall:
            def __init__(self, call, getprop = None):
                self.__call = call
                self.__getprop = getprop

            def __getattr__(self, name):
                return Method(name, self.__call, self.__getprop)

            def __repr__(self):
                return '<%s: %r>' % (self.__class__.__name__, self.__api)

        def __init__(self, api, name):
            self.api = api
            self.name = name
            # Q: Why not 'call'? to match Client<-MethodCall
            self.invoke = self.APIHandleCall(api.call, api.getprop)
            self.closed = False

        def __repr__(self):
            return '<%s: %s>' % (self.__class__.__name__, self.name)

        def __del__(self):
            self.close()
        def close(self):
            if not self.closed:
                self.api.call('closeApi')
                self.closed = True

    class APIMethod(MethodCall):
        def __init__(self, name, call, getprop = None):
            self.__name = name
            self.__call = call
            self.__getprop = getprop

        def __repr__(self):
            return '<%s: %s>' % (self.__class__.__name__, self.__name)

        def __getattr__(self, name):
            return Method(name, self.__call, self.__getprop)

        # Context Control:
        def __enter__(self):
            self.__call('openApi', self.__name)
            return self

        def __exit__(self, etype = None, value = None, tb = None):
            self.__call('closeApi')

    def __init__(self, call, getprop = None):
        self.call = call
        self.getprop = getprop
    def __call__(self, name):
        return self.APIMethod(name, self.call, self.getprop)

    def __repr__(self):
        return '<%s>' % (self.__class__.__name__)

    def open(self, name):
        self.call('openApi', name)
        return self.APIHandle(self, name)

class PentacleServiceEndpoint(namedtuple('PentacleServiceEndpoint', 'scheme host port service')):
    # Parses into the 'netloc' part (excluding username, password -> to be provided separately)
    # Excludes // from netloc
    # Preceding / in 'path' (service) unecessary
    #    (XXX no good for services that start with digits)
    _pentacle_endpoint = re.compile('^([^/:]+):([^/?]*):([0-9]+)(.*)$')

    @classmethod
    def Parse(self, endpoint):
        m = self._pentacle_endpoint.match(endpoint)
        assert m is not None
        (scheme, host, port, service) = m.groups()
        return self(scheme, host, port, service)

    __slots__ = ()

    def getendpoint(self):
        return '%s:%s:%s%s' % (self.scheme, self.host, self.port, self.service)

    def open(self, user):
        assert self.scheme.lower() == 'pentacle'
        client = user.Open(self.host, int(self.port))
        return client.api.open(self.service)

Endpoint = PentacleServiceEndpoint

def printFault(fault, cause = False, byline = 'REMOTE FAULT:'):
    # todo: move into misc.
    if cause:
        print 'Fault Caused Locally By:'
        printException()
        print

    print byline
    print fault.toString(tb = True)

class CompressIfWorthIt:
    THRESHOLD = .70
    All = Object()

    def __init__(self, threshold = None, level = None):
        self.threshold = self.THRESHOLD
        self.level = level if level is not None else self.All

    def __iter__(self):
        if self.level is self.All:
            yield 3
            # yield 2
            yield 1
        else:
            yield self.level

    def worthIt(self, z, u):
        print 'WORTH IT??: (%d/%d) %f' % (z, u, float(z) / u)

        # This probably will only be worth it for messages of a certain size.
        return (float(z) / u) < self.threshold

    def __call__(self, data):
        data_length = len(data)
        for level in self:
            compressed = Compress(data, level)
            if self.worthIt(len(compressed), data_length):
                return compressed

        return data

def ApplyCompressionChannel(channel, level = None, threshold = None):
    if level is not None:
        if isinstance(level, basestring):
            if level.isdigit():
                level = int(level)
            else:
                assert level == 'all'

        if isinstance(threshold, basestring):
            import re
            m = re.match('^(\d+)%$', threshold)
            assert m is not None
            threshold = int(m.groups()[0]) / 100.0

        channel.compression_level = CompressIfWorthIt(threshold, level)
