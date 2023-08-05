# Storage Management Backend and Interfaces
__all__ = ['StorageManagement', 'StorageUnit', 'UserStorage']

import shelve
import re

from .runtime import *
from .architecture import *

class StorageManagement(Component):
    DEFAULT_SHELF_NAME = '.application.db'

    def __init__(self, application):
        Component.__init__(self, application)
        db_path = application.getConfigOption('db-path')
        self.shelf = shelve.open(self.getPathName(db_path))

    @classmethod
    def addCmdlnOptions(self, parser):
        parser.add_option('--db-path', '--db', default = self.DEFAULT_SHELF_NAME)
        parser.add_option('--dump-db')

    def getStorage(self, key, interface = None):
        unit = StorageUnit.ReadStore(self.shelf, key)
        return key.getStorageInterface(self.shelf, unit, interface)

    def dumpDB(self, filename):
        from json import dump as dumpJson
        db = dict(self.shelf.iteritems())
        fl = open(filename, 'wb')
        dumpJson(db, fl, indent = 2)
        fl.flush()
        fl.close()

    class AuxiliaryApi(ServiceBase):
        # Kind of a toy api for exploring a parked store.
        NAME = 'Storage::Aux'

        def lookupUnitAccess(self, name):
            if name == 'UserStorage':
                return UserStorage
            elif name == 'RightsStorage':
                return security.RightsManagement.RightsStorage

            raise NameError(name)

        def buildAuxiliaryStore(self, argv):
            class AuxApp:
                # Auxiliary application.
                logMessages = []
                log = logMessages.append

            # Build app and storage.
            from optparse import OptionParser
            parser = OptionParser()
            StorageManagement.addCmdlnOptions(parser)

            (options, args) = parser.parse_args(argv)
            storage = StorageManagement(AuxApp(), options, args)
            storage.application.storage = storage
            return storage


class StorageUnit:
    @classmethod
    def Open(self, app, *args, **kwd):
        return app.storage.getStorage(self.Key(*args, **kwd))

    def __init__(self, key, store, unit):
        self.key = key
        self.store = store
        self.unit = unit

    def synchronize(self):
        self.WriteStore(self.store, self.key, self.unit)

    @classmethod
    def getInterface(self, key, store, unit):
        return self.Interface(self(key, store, unit))

    @classmethod
    def ReadStore(self, store, key, create_unit = None):
        unitName = key.getUnitName()
        try: return store[unitName]
        except KeyError:
            unit = create_unit if callable(create_unit) else {}
            store[unitName] = unit
            store.sync()
            return unit

    @classmethod
    def WriteStore(self, store, key, unit):
        store[key.getUnitName()] = unit
        store.sync()

    STORAGE_REALM = '----'
    class StringKey:
        def __init__(self, storageClass, value):
            self.storageClass = storageClass
            self.value = value

        def getStorageInterface(self, store, unit, interface):
            return self.storageClass.getInterface(self, store, unit)
        def getUnitName(self):
            return '%s[%s]' % (self.storageClass.STORAGE_REALM, self.value)

    @classmethod
    def Key(self, *args, **kwd):
        return self.StringKey(self, *args, **kwd)

    @classmethod
    def GetUnitNamePattern(self):
        pattern = '^%s\[(?P<unit>.*?)\]$' % re.escape(self.STORAGE_REALM)
        return re.compile(pattern)

    @classmethod
    def MatchKeys(self, keys):
        p = self.GetUnitNamePattern().match
        for k in keys:
            m = p(k)
            if m is not None:
                yield (k, m.groupdict()['unit'])

    class Interface:
        def __init__(self, unit):
            self.unit = unit

        def getKey(self):
            return self.unit.key
        def synchronizeStore(self):
            self.unit.synchronize()

        def getValue(self, name, default = None):
            return self.unit.unit.get(name, default)
        def setValue(self, name, value):
            self.unit.unit[name] = value

        def __enter__(self):
            return self
        def __exit__(self, etype = None, value = None, tb = None):
            self.synchronizeStore()

class UserStorage(StorageUnit):
    STORAGE_REALM = 'UserStorage'

    class Interface(StorageUnit.Interface):
        AUTH_SECRET_KEY = 'auth-secret-key'

        def checkAccess(self, digest):
            # Basically hash username against secret key and compare to digest.
            # Makes the assumption that the key string-value is the same as the username.
            secretKey = self.getValue(self.AUTH_SECRET_KEY, '')
            calc = security.CalculateDigest(secretKey, self.getKey().value)
            return calc == digest

        def changeSecretKey(self, secretKey):
            self.setValue(self.AUTH_SECRET_KEY, secretKey)

        USER_ROLES = 'user-roles'
        PUBLIC_ROLE = 'PUBLIC'

        def getUserRoles(self):
            return setListAdd(self.getValue(self.USER_ROLES), self.PUBLIC_ROLE)
        def setUserRoles(self, *roles):
            self.setValue(self.USER_ROLES, list(roles))

        def addUserRole(self, role):
            self.setUserRoles(*setListAdd(self.getUserRoles(), role))
        def removeUserRole(self, role):
            self.setUserRoles(*setListRemove(self.getUserRoles(), role))

# This stuff should go into runtime (misc)
def setListAdd(thisSet, item):
    if thisSet is None:
        thisSet = []

    if item not in thisSet:
        thisSet.append(item)

    return thisSet

def setListRemove(thisSet, item):
    if thisSet is None:
        return []

    try: thisSet.remove(item)
    except ValueError: pass
    return thisSet

##    REGEX_SPECIAL_CHARS = r'()[].*$^\?+'
##    REGEX_SPECIAL_CHARS = [(c, r'\%s' % c) for c in REGEX_SPECIAL_CHARS]
##
##    def escape_regex(s):
##        # Escape a regular expression string so that it matches literally.
##        # Todo: speed this up.
##        for (c, r) in REGEX_SPECIAL_CHARS:
##            s = s.replace(c, r)
##
##        return s

def searchAllStorageUnits(store, *unitClasses):
    storeKeys = store.keys()
    for unitCls in unitClasses:
        for (k, n) in unitCls.MatchKeys(storeKeys):
            yield Synthetic(unitClass = unitCls,
                            key = k, name = n,
                            Open = lambda app, uc = unitCls, n = n: uc.Open(app, n))

def showStorageUnits(units):
    for u in units:
        print '%-30s: %s' % (u.unitClass.STORAGE_REALM, u.name)

from . import security
