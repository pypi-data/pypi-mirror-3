# Copyright 2011 Clint Banis
import os

__version__ = 0.1
ServiceManagerName = 'ServiceManager::SplineBus'

__all__ = ['__version__', 'ServiceManagerName', 'isRecognizedServer',
           'SPLINE_CONFIG_ENV_VAR', 'DEFAULT_SPLINE_CONFIG_FILE',
           'PENTACLE_PARTNER_NAME_ENV_VAR', 'PENTACLE_PARTNER_AUTH_ENV_VAR',
           'getDefaultSplineConfigFilename', 'getDefaultSplineConfig',
           'busPartnerMain', 'PartnerNameFeature',
           'AuthenticationError', 'UnknownServer', 'UnknownSignalName']

class AuthenticationError(Exception):
    pass
class UnknownServer(Exception):
    pass
class UnknownSignalName(NameError):
    pass

SPLINE_CONFIG_ENV_VAR = 'SPLINE_CONFIG'
DEFAULT_SPLINE_CONFIG_FILE = '~/.spline/application.cfg'

PENTACLE_PARTNER_NAME_ENV_VAR = 'PENTACLE_PARTNER_NAME'
PENTACLE_PARTNER_AUTH_ENV_VAR = 'PENTACLE_PARTNER_AUTH'

def getDefaultSplineConfigFilename(default_file = None):
    return os.environ.get(SPLINE_CONFIG_ENV_VAR, default_file) \
           or DEFAULT_SPLINE_CONFIG_FILE

def getDefaultSplineConfig(cfg = None, default_file = None):
    if cfg is None:
        cfgfile = getDefaultSplineConfigFilename(default_file)
        cfg = Configuration.FromFile(cfgfile)

    return cfg

def PartnerNameFeature(name):
    return ('partnerName', name)

def isRecognizedServer(ident, appName = None, appVersion = None, appFeatures = None):
    if isinstance(ident, basestring):
        parts = [p.strip() for p in ident.split(';')]
        if parts:
            (name, version) = parts[0].split('/')
            name = name.lower()
            version = float(version)

            if isinstance(appName, (list, tuple)):
                if name not in (n.lower() for n in appName):
                    return False

            elif isinstance(appName, basestring):
                if name != appName.lower():
                    return False

            if isinstance(appVersion, (list, tuple)):
                if version < appVersion:
                    return False

            if isinstance(appFeatures, (list, tuple)):
                foundFeatures = dict()
                for p in parts[1:]:
                    feature = p.split('=', 1)
                    if len(feature) == 1:
                        foundFeatures[feature[0].strip()] = True
                    elif len(feature) == 2:
                        foundFeatures[feature[0].strip()] = feature[1].strip()

                # Must match all these features.
                for f in appFeatures:
                    if isinstance(f, basestring):
                        if f not in foundFeatures:
                            return False

                    elif isinstance(f, (list, tuple)):
                        (name, value) = f
                        if foundFeatures[name] != value:
                            return False

                # todo: detect feature versions?

            # Pretty much recognize based on the criteria.
            return True

    # Did not identify itself in a way we can understand.
    return None

# The module name used for booting partner main application entry.
def busPartnerMain():
    from partners import main # relative
    return main.__name__
