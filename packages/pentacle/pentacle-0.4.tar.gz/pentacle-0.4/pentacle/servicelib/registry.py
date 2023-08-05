# Active System Object Registry & Directory
# Builtin Pentacle Service Partner
'''
Pentacle Bus Active Database Partner
====================================

This module contains the ActiveRegistry service for a Pentacle database service partner.
Use the API Manager to load this service by specifying the class's fully qualified name.

(Relies on SQLObject.)

'''

from ..architecture import ServiceBase
from ..storage import StorageUnit
from ..runtime import Object

import os, errno
from os.path import join as joinpath, normpath, abspath
from types import ClassType as buildClass

class ActiveRegistry(ServiceBase):
    '''
    ActiveRegistry (Service)
    ========================

    This class is loaded as a Pentacle service, and activates itself.
    See the documentation for the `Activate` method to find out how to
    configure it.

    Note that the service name for this class is::

        PenobscotRobotics[Registry::Active]

    '''

    NAME = 'PenobscotRobotics[Registry::Active]'
    DEFAULT_DB_CONTAINER = 'ardbs'

    class RegistryStorage(StorageUnit):
        'A storage unit definition for a toplevel active registry entry.'
        STORAGE_REALM = 'ActiveRegistry'

    def Activate(self, apiMgr):
        ServiceBase.Activate(self, apiMgr)
        self.dbContainerPath = apiMgr.application \
            .getConfigOption('root-path', default = self.DEFAULT_DB_CONTAINER)

        try: os.makedirs(self.dbContainerPath)
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise

    def OpenDirectory(self, name):
        'Pass the name of the toplevel registry entry, and the storage interface is returned.'
        return self.RegistryStorage.Open(self.apiMgr.application, name)

    def OpenDB(self, name = None):
        'Return a newly-opened (or existing) active database session object.'

        if name is None:
            return ActiveDB.OpenMemory(self)

        return ActiveDB.Open(self, name)

class ActiveDB(Object):
    Meta = Object.Meta('name')

    _open_cache = {}
    _memory = object()

    @classmethod
    def Open(self, registry, name):
        try: return self._open_cache[name]
        except KeyError:
            import sqlobject
            uri = self.getUriFor(registry, name)
            conn = sqlobject.connectionForURI(uri)
            db = self._open_cache[name] = self(registry, sqlobject, name, conn)
            return db

    @classmethod
    def OpenMemory(self, registry):
        try: return self._open_cache[self._memory]
        except KeyError:
            import sqlobject
            conn = sqlobject.connectionForURI('sqlite:///:memory:')
            db = self._open_cache[self._memory] = self(registry, sqlobject, name, conn)
            return db

    @classmethod
    def getUriFor(self, registry, name):
        # todo: also configure the protocol here?  Could use sqlalchemy+mssql
        path = joinpath(registry.dbContainerPath, name + '.db')
        path = abspath(normpath(path))

        # Open the connection with a unique class registry for each db.
        # todo: should we be escaping the db name for this parameter value?
        return 'sqlite://%s?registry=%s' % (path, name)

    def __init__(self, registry, sqlobject, name, conn):
        self.registry = registry
        self.sqlobject = sqlobject
        self.name = name
        self.conn = conn

        self.tables = {}
        self.sqlObjectBaseClass = sqlobject.SQLObject
        self.sqlObjectCols = sqlobject.col

    class Table(Object):
        Meta = Object.Meta('schema')

        class Schema(Object):
            # An externally-defined table.
            Meta = Object.Meta('name', ['columns', lambda schema:len(schema.columns)])

            class Column(Object):
                Meta = Object.Meta('name', ['data-type', lambda col:'%s(%s)' % (col.data_type, col.size)])

                def __init__(self, name, data_type, size = 0, fixed = None,
                             nullable = False, index = None, constraints = ()):

                    self.name = name
                    self.data_type = data_type
                    self.size = size

                COLUMN_TYPE_MAP = dict(string = 'StringCol',
                                       integer = 'IntCol',
                                       pickle = 'PickleCol')

                def build(self, sqlObjectCols):
                    # Build the actual SQLObject column.
                    colClass = getattr(sqlObjectCols, self.COLUMN_TYPE_MAP[self.data_type])
                    return (self.name, colClass())

                @classmethod
                def define(self, colDef):
                    if isinstance(colDef, (tuple, list)):
                        # Unpack from schema definition.
                        if len(colDef) == 3:
                            (name, args, kwd) = colDef
                        elif len(colDef) == 2:
                            (name, args) = colDef
                        else:
                            raise IndexError(repr(colDef))
                    else:
                        raise TypeError(type(colDef).__name__)

                    # Construct this column specification.
                    return self(name, *args, **kwd)

            def __init__(self, name, *columns):
                self.name = name
                self.columns = columns
                self.table = None # One instance per schema.

            def build(self, db):
                # Builds a definition.
                return buildClass(db.getTableName(self.name),
                                  (db.sqlObjectBaseClass,),
                                  dict(c.build(db.sqlObjectCols)
                                       for c in self.columns))

            def open(self, db):
                if self.table is None:
                    self.table = db.tableConnectImpl(self.build(db))

                return self.table

            def drop(self, db):
                db.tableDropImpl(self.tableObj)

        def __init__(self, db, schema):
            self.schema = schema
            self.tableObj = schema.open(db)

        # Accessors.
        def newRecord(self, **kwd):
            return self.tableObj(**kwd)
        def getRecord(self, **kwd):
            return self.tableObj.selectBy(**kwd)

    # Helpers.
    def getTableName(self, name):
        # Note: the classes will be differentiated via class registry.
        return name

    def tableConnectImpl(self, t):
        t._connection = self.conn
        if not t.tableExists():
            t.createTable()

        return t

    def tableDropImpl(self, t):
        if t.tableExists():
            t.dropTable()

    # Accessors.
    def tableNeedsDefinition(self, name):
        return name in self.tables

    def defineColumn(self, name, *args, **kwd):
        return (name, args, kwd)

    def defineTable(self, name, *columns):
        # what about alter table??
        assert not self.tableNeedsDefinition(name)
        columns = map(self.Table.Schema.Column.define, columns)
        self.tables[name] = self.Table.Schema(name, *columns)
        return name

    def openTable(self, name):
        return self.Table(self, self.tables[name])
    def dropTable(self, name):
        self.tables[name].schema.drop(self)

    def listTables(self):
        return self.tables.keys()
    def close(self):
        pass

##    with client.api('PenobscotRobotics[Registry::Active]') as registry:
##        with closing(registry.OpenDB('mine')) as db:
##            db.defineTable('main',
##                           db.defineColumn('systemName', 'string'),
##                           db.defineColumn('version', 'integer'))
##
##            tableDefs = registry.OpenDirectory('my/table/definitions')
##            for (name, columns, records) in tableDefs.iteritems():
##                if db.tableNeedsDefinition(name):
##                    db.defineTable(name, *columns)
##
##                t = db.openTable(name)
##                for r in records:
##                    t.newRecord(**r)
