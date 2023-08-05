#!/usr/bin/python
#
#   PROGRAM:     Firebird PowerConsole
#   MODULE:      fbcore.py
#   DESCRIPTION: Firebird Database Model Classes
#
#  The contents of this file are subject to the Initial
#  Developer's Public License Version 1.0 (the "License");
#  you may not use this file except in compliance with the
#  License. You may obtain a copy of the License at
#  http://www.ibphoenix.com/main.nfs?a=ibphoenix&page=ibp_idpl.
#
#  Software distributed under the License is distributed AS IS,
#  WITHOUT WARRANTY OF ANY KIND, either express or implied.
#  See the License for the specific language governing rights
#  and limitations under the License.
#
#  The Original Code was created by Pavel Cisar
#  for the Firebird Open Source RDBMS project.
#  http://www.firebirdsql.org
#
#  Copyright (c) 2006-2009 Pavel Cisar <pcisar@users.sourceforge.net>
#  and all contributors signed below.
#
#  All Rights Reserved.
#  Contributor(s): ______________________________________.

import sys
import os
from pwc.base import LateBindingProperty, iif
import fdb as kdb
import unittest
import string

#--- Constants

FBCORE_VERSION  = "0.7"

# Firebird Field Types

FBT_SMALLINT            = 7
FBT_INTEGER             = 8
FBT_QUAD                = 9
FBT_FLOAT               = 10
FBT_CHAR                = 14
FBT_DOUBLE_PRECISION    = 27
FBT_DATE                = 35
FBT_VARCHAR             = 37
FBT_CSTRING             = 40
FBT_BLOB_ID             = 45
FBT_BLOB                = 261
FBT_SQL_DATE            = 12
FBT_SQL_TIME            = 13
FBT_SQL_TIMESTAMP       = 35
FBT_BIGINT              = 16

MAX_INTSUBTYPES     = 2
MAX_BLOBSUBTYPES    = 8

TRIGGER_TYPE_SHIFT  = 13
TRIGGER_TYPE_MASK   = (0x3 << TRIGGER_TYPE_SHIFT)
TRIGGER_TYPE_DML    = (0 << TRIGGER_TYPE_SHIFT)
TRIGGER_TYPE_DB	    = (1 << TRIGGER_TYPE_SHIFT)

column_types =  {FBT_SMALLINT: "SMALLINT",
                 FBT_INTEGER: "INTEGER",
                 FBT_QUAD: "QUAD",
                 FBT_FLOAT: "FLOAT",
                 FBT_CHAR: "CHAR",
                 FBT_DOUBLE_PRECISION: "DOUBLE PRECISION",
                 FBT_VARCHAR: "VARCHAR",
                 FBT_CSTRING: "CSTRING",
                 FBT_BLOB_ID: "BLOB_ID",
                 FBT_BLOB: "BLOB",
                 FBT_SQL_TIME: "TIME",
                 FBT_SQL_DATE: "DATE",
                 FBT_SQL_TIMESTAMP: "TIMESTAMP",
                 FBT_BIGINT: "BIGINT"
                }
integral_subtypes = ("UNKNOWN","NUMERIC","DECIMAL")
blob_sub_types    = ("BINARY","TEXT","BLR","ACL","RANGES","SUMMARY",
                     "FORMAT","TRANSACTION_DESCRIPTION","EXTERNAL_FILE_DESCRIPTION")

trigger_prefix_types = ["BEFORE","AFTER"]
trigger_suffix_types = ["","INSERT","UPDATE","DELETE"]
trigger_db_types     = ["CONNECT","DISCONNECT","TRANSACTION START",
                        "TRANSACTION COMMIT","TRANSACTION ROLLBACK"]
#--- Functions

def splitDSN(dsn):
    """Do our best to extract host and database specification from DSN."""
    if dsn[:2] == '\\\\':
        i = dsn.find('\\',2)
        host = dsn[2:i]
        db = dsn[i:]
    else:
        # TCP/IP (or Windows pathname)
        colon = dsn.find(':')
        if colon in (-1, 1):
            # If the first colon is exactly the second character
            # we'll assume that it's Windows pathname.
            host = None
            db = dsn
        else:
            host, db = dsn.split(':',1)
    return host, db

def isKeyword(ident):
    ## ToDo: Implement isKeyword
    return False
    
def createDatabase(**args):
    """Creates new database.
    """
    if 'dsn' in args:
        dsn = args['dsn']
        host, database = splitDSN(dsn)
    else:
        database = args.get('database')
        host = args.get('host')
        if host != None:
            dsn = host + ':' + database
        else:
            dsn = database
    user = args.get('user')
    if user == None:
        args['user'] = user = os.environ.get('ISC_USER')
    password = args.get('password')
    
    # Parameter checks
    
    cmd = "create database '%s' user '%s' password '%s'" % (dsn,user,password)
    if 'page_size' in args:
        cmd = '%s page_size %i' % (cmd,args['page_size'])
    if 'length' in args:
        cmd = '%s length %i' % (cmd,args['length'])
    if 'character_set' in args:
        cmd = '%s default character set %s' % (cmd,args['character_set'])
    if 'files' in args:
        cmd = '%s %s' % (cmd,args['files'])
    dialect = args.get('dialect',3)
    con = kdb.create_database(cmd,dialect)
    # If we should connect with some character set, we have to reconnect with
    # it instead using the created KInterbasDB connection object
    if 'charset' in args:
        con.close()
    else:
        args['handle']=con
    return Database(**args)

def _createGetMethod(id):
    return lambda self:self._attributes[id]


#--- Exceptions

class Error(Exception):
    pass

#--- Classes

class Database(object):
    """This class represents a database.

    It contains methods to attach, create or drop database, properties
    and methods to access metadata or create new metadata objects.
    """

    dsn = host = db = user = None

    def __init__(self,**args):
        """Constructor.
        """
        super(Database,self).__init__()
        self.__clear()
        self.optAlwaysQuote = False
        
        if args.has_key('dsn'):
            self.dsn = args['dsn']
            self.host, self.database = splitDSN(self.dsn)
        else:
            self.database = args.get('database')
            self.host = args.get('host')
            if self.host != None:
                self.dsn = self.host + ':' + self.database
            else:
                self.dsn = self.database
        self.user = args.get('user')
        if self.user == None:
            args['user'] = self.user = os.environ.get('ISC_USER')

        if 'handle' in args:
            self._con = args['handle']
        else:
            self._con = kdb.connect(**args)

        if 'charset' in args:
            self.character_set = args['charset']
        else:
            self.character_set = None
        
        #tpb = kdb.TPB
        #tpb.access_mode = kdb.isc_tpb_read
        #tpb.isolation_level = (kdb.isc_tpb_read_committed, kdb.isc_tpb_rec_version)
        self._sys_transaction = self._con.trans()
        self._user_transaction = self._con.trans()
        self.__c = self._user_transaction.cursor()
        self.__ic = self._sys_transaction.cursor()
        self.__ic.execute('select * from RDB$DATABASE')
        row = self.__ic.fetchonemap()
        self.__description = row['RDB$DESCRIPTION']
        self.__default_character_set = row['RDB$CHARACTER_SET_NAME'].strip()
        self.__security_class = row['RDB$SECURITY_CLASS']
        self.__ic.execute("select * from RDB$RELATIONS where RDB$RELATION_NAME = 'RDB$DATABASE'")
        row = self.__ic.fetchonemap()
        self.__owner = row['RDB$OWNER_NAME'].strip()
        # Load enumerate types defined in RDB$TYPES table
        # Object types
        self.__ic.execute("select RDB$TYPE, RDB$TYPE_NAME from RDB$TYPES where RDB$FIELD_NAME = 'RDB$OBJECT_TYPE'")
        self.enumObjectTypes = {}
        self.enumObjectTypeCodes = {}
        for row in self.__ic.iter():
            self.enumObjectTypes[row[0]] = row[1].strip()
            self.enumObjectTypeCodes[row[1].strip()] = row[0]
        # Field types
        self.__ic.execute("select RDB$TYPE, RDB$TYPE_NAME from RDB$TYPES where RDB$FIELD_NAME = 'RDB$FIELD_TYPE'")
        self.enumFieldTypes = dict([(key,value.strip()) for key, value in self.__ic.iter()])
        # Field sub types
        self.__ic.execute("select RDB$TYPE, RDB$TYPE_NAME from RDB$TYPES where RDB$FIELD_NAME = 'RDB$FIELD_SUB_TYPE'")
        self.enumFieldSubtypes = dict([(key,value.strip()) for key, value in self.__ic.iter()])
        # Function types
        self.__ic.execute("select RDB$TYPE, RDB$TYPE_NAME from RDB$TYPES where RDB$FIELD_NAME = 'RDB$FUNCTION_TYPE'")
        self.enumFunctionTypes = dict([(key,value.strip()) for key, value in self.__ic.iter()])
        # Mechanism Types
        self.__ic.execute("select RDB$TYPE, RDB$TYPE_NAME from RDB$TYPES where RDB$FIELD_NAME = 'RDB$MECHANISM'")
        self.enumMechanismTypes = dict([(key,value.strip()) for key, value in self.__ic.iter()])
        # System Flag Types
        self.__ic.execute("select RDB$TYPE, RDB$TYPE_NAME from RDB$TYPES where RDB$FIELD_NAME = 'RDB$SYSTEM_FLAG'")
        self.enumSystemFlagTypes = dict([(key,value.strip()) for key, value in self.__ic.iter()])
        # Trigger Types
        self.__ic.execute("select RDB$TYPE, RDB$TYPE_NAME from RDB$TYPES where RDB$FIELD_NAME = 'RDB$TRIGGER_TYPE'")
        self.enumTriggerTypes = dict([(key,value.strip()) for key, value in self.__ic.iter()])
        # Transaction State Types
        self.__ic.execute("select RDB$TYPE, RDB$TYPE_NAME from RDB$TYPES where RDB$FIELD_NAME = 'RDB$TRANSACTION_STATE'")
        self.enumTransactionStateTypes = dict([(key,value.strip()) for key, value in self.__ic.iter()])
        self._sys_transaction.commit()

    #--- private

    def __objectByName(self,list,name):
        for o in list:
            if o.name == name:
                return o
        return None

    def __clear(self):
        self._con = self.__c = self.__ic = None
        self.dsn = self.user = self.database = None
        self.reload()

    #--- protected

    def _selectRow(self,cmd,params=None,commit=True):
        if params:
            self.__ic.execute(cmd,params)
        else:
            self.__ic.execute(cmd)
        row = self.__ic.fetchonemap()
        if commit:
            self._sys_transaction.commit()
        return row
    def _select(self,cmd,params=None):
        if params:
            self.__ic.execute(cmd,params)
        else:
            self.__ic.execute(cmd)
        return self.__ic.itermap()
    def _execute(self,cmd,params=None,commit=True):
        if params:
            self.__ic.execute(cmd,params)
        else:
            self.__ic.execute(cmd)
        if commit:
            self._sys_transaction.commit()
    def _commit(self):
        self._sys_transaction.commit()
    def _getFieldDimensions(self,field):
        l = ['[']
        self.__ic.execute("""select * from RDB$FIELD_DIMENSIONS 
          where RDB$FIELD_NAME = '%s'
          order by RDB$DIMENSION""" % field.name)
        for row in  self.__ic.itermap():
            if row['RDB$DIMENSION'] > 0:
                l.append(', ')
            if row['RDB$LOWER_BOUND'] == 1:
                l.append('%ld' % row['RDB$UPPER_BOUND'])
            else:
                l.append('%ld:%ld' % (row['RDB$LOWER_BOUND'],row['RDB$UPPER_BOUND']))
        l.append(']')
        return ''.join(l)

    #--- special attribute access methods

    def _get_description(self):
        return self.__description
    def _set_description(self,value):
        return
    def _get_default_character_set(self):
        return self.__default_character_set
    def _get_owner_name(self):
        return self.__owner
    def _set_default_character_set(self,value):
        return
    def _get_security_class(self):
        return self.__security_class

    def _get_collations(self):
        if not self.__collations:
            self.__ic.execute("select * from rdb$collations")
            self.__collations = [Collation(self,row) for row in self.__ic.itermap()]
            self._sys_transaction.commit()
        return self.__collations
    def _get_character_sets(self):
        if not self.__character_sets:
            self.__ic.execute("select * from rdb$character_sets")
            self.__character_sets = [CharacterSet(self,row) for row in self.__ic.itermap()]
            self._sys_transaction.commit()
        return self.__character_sets
    def _get_exceptions(self):
        if not self.__exceptions:
            self.__ic.execute("select * from rdb$exceptions")
            self.__exceptions = [Exception(self,row) for row in self.__ic.itermap()]
            self._sys_transaction.commit()
        return self.__exceptions
    def _getAllDomains(self):
        if self.__domains is None:
            self.__ic.execute("select * from rdb$fields")
            self.__domains = [Domain(self,row) for row in self.__ic.itermap()]
            self._sys_transaction.commit()
        return self.__domains
    def _get_domains(self):
        return [d for d in self._getAllDomains() if not d.isSystemObject()]
    def _get_sysdomains(self):
        return [d for d in self._getAllDomains() if d.isSystemObject()]
    def _getAllTables(self):
        if not self.__tables:
            self.__ic.execute("select * from rdb$relations where rdb$view_blr is null")
            self.__tables = [Table(self,row) for row in self.__ic.itermap()]
            self._sys_transaction.commit()
        return self.__tables
    def _get_tables(self):
        return [t for t in self._getAllTables() if not t.isSystemObject()]
    def _get_systables(self):
        return [t for t in self._getAllTables() if t.isSystemObject()]
    def _getAllViews(self):
        if not self.__views:
            self.__ic.execute("select * from rdb$relations where rdb$view_blr is not null")
            self.__views = [View(self,row) for row in self.__ic.itermap()]
            self._sys_transaction.commit()
        return self.__views
    def _get_views(self):
        return [v for v in self._getAllViews() if not v.isSystemObject()]
    def _get_sysviews(self):
        return [v for v in self._getAllViews() if v.isSystemObject()]
    def _get_constraintIndices(self):
        if not self.__constraint_indices:
            self.__ic.execute("select RDB$INDEX_NAME, RDB$RELATION_NAME from RDB$RELATION_CONSTRAINTS where RDB$INDEX_NAME is not null")
            self.__constraint_indices = dict([(key.strip(),value.strip()) for key, value in self.__ic.iter()])
            self._sys_transaction.commit()
        return self.__constraint_indices
    def _getAllIndices(self):
        if not self.__indices:
            self.__ic.execute("select * from rdb$indices")
            self.__indices = [Index(self,row) for row in self.__ic.itermap()]
            self._sys_transaction.commit()
        return self.__indices
    def _get_indices(self):
        return [i for i in self._getAllIndices() if not i.isSystemObject()]
    def _get_sysindices(self):
        return [i for i in self._getAllIndices() if i.isSystemObject()]
    def _getAllGenerators(self):
        if not self.__generators:
            self.__ic.execute("select * from rdb$generators")
            self.__generators = [Generator(self,row) for row in self.__ic.itermap()]
            self._sys_transaction.commit()
        return self.__generators
    def _get_generators(self):
        return [g for g in self._getAllGenerators() if not g.isSystemObject()]
    def _get_sysgenerators(self):
        return [g for g in self._getAllGenerators() if g.isSystemObject()]
    def _getAllTriggers(self):
        if not self.__triggers:
            self.__ic.execute("select * from rdb$triggers")
            self.__triggers = [Trigger(self,row) for row in self.__ic.itermap()]
            self._sys_transaction.commit()
        return self.__triggers
    def _get_triggers(self):
        return [g for g in self._getAllTriggers() if not g.isSystemObject()]
    def _get_systriggers(self):
        return [g for g in self._getAllTriggers() if g.isSystemObject()]
    def _getAllProcedures(self):
        if not self.__procedures:
            self.__ic.execute("select * from rdb$procedures")
            self.__procedures = [Procedure(self,row) for row in self.__ic.itermap()]
            self._sys_transaction.commit()
        return self.__procedures
    def _get_procedures(self):
        return [p for p in self._getAllProcedures() if not p.isSystemObject()]
    def _get_sysprocedures(self):
        return [p for p in self._getAllProcedures() if p.isSystemObject()]
    def _get_constraints(self):
        if not self.__constraints:
            self.__ic.execute("""select * from rdb$relation_constraints C
left outer join rdb$ref_constraints R on C.rdb$constraint_name = R.rdb$constraint_name
left outer join rdb$check_constraints K on C.rdb$constraint_name = K.rdb$constraint_name""")
            self.__constraints = [Constraint(self,row) for row in self.__ic.itermap()]
            self._sys_transaction.commit()
            # Check constrains need special care because they're doubled
            # (select above returns two records for them with different trigger names)
            checks = [c for c in self.__constraints if c.isCheck()]
            self.__constraints = [c for c in self.__constraints if not c.isCheck()]
            dchecks = {}
            for check in checks:
                dchecks.setdefault(check.name,list()).append(check)
            for checklist in dchecks.values():
                names = [c._attributes['RDB$TRIGGER_NAME'] for c in checklist]
                check = checklist[0]
                check._attributes['RDB$TRIGGER_NAME'] = names
                self.__constraints.append(check)
        return self.__constraints
    def _get_roles(self):
        if not self.__roles:
            self.__ic.execute("select * from rdb$roles")
            self.__roles = [Role(self,row) for row in self.__ic.itermap()]
            self._sys_transaction.commit()
        return self.__roles
    def _get_dependencies(self):
        if not self.__dependencies:
            self.__ic.execute("select * from rdb$dependencies")
            self.__dependencies = [Dependency(self,row) for row in self.__ic.itermap()]
            self._sys_transaction.commit()
        return self.__dependencies
    def _get_functions(self):
        if not self.__dependencies:
            self.__ic.execute("select * from rdb$functions")
            self.__functions = [Function(self,row) for row in self.__ic.itermap()]
            self._sys_transaction.commit()
        return self.__functions
    def _get_files(self):
        if not self.__files:
            self.__ic.execute("select * from rdb$files")
            self.__files = [DbFile(self,row) for row in self.__ic.itermap()]
            self._sys_transaction.commit()
        return self.__files

    #--- Properties

    description = LateBindingProperty(_get_description,_set_description,None,"Database description or None if it doesn't have a description.")
    owner_name = LateBindingProperty(_get_owner_name,None,None,"Database owner name.")
    default_character_set = LateBindingProperty(_get_default_character_set,_set_default_character_set,None,"Default character set name, NULL if it's character set NONE.")
    security_class = LateBindingProperty(_get_security_class,None,None,"Can refer to the security class applied as databasewide access control limits.")

    collations      = LateBindingProperty(_get_collations,None,None,"List of all collations in database.\nItems are :class:`Collation` objects.")
    character_sets  = LateBindingProperty(_get_character_sets,None,None,"List of all character sets in database.\nItems are CharacterSet objects.")
    exceptions      = LateBindingProperty(_get_exceptions,None,None,"List of all exceptions in database.\nItems are :class:`Exception` objects.")
    generators      = LateBindingProperty(_get_generators,None,None,"List of all user generators in database.\nItems are :class:`Generator` objects.")
    sysgenerators   = LateBindingProperty(_get_sysgenerators,None,None,"List of all system generators in database.\nItems are :class:`Generator` objects.")
    domains         = LateBindingProperty(_get_domains,None,None,"List of all user domains in database.\nItems are :class:`Domain` objects.")
    sysdomains      = LateBindingProperty(_get_sysdomains,None,None,"List of all system domains in database.\nItems are :class:`Domain` objects.")
    indices         = LateBindingProperty(_get_indices,None,None,"List of all user indices in database.\nItems are :class:`Index` objects.")
    sysindices      = LateBindingProperty(_get_sysindices,None,None,"List of all system indices in database.\nItems are :class:`Index` objects.")
    tables          = LateBindingProperty(_get_tables,None,None,"List of all user tables in database.\nItems are :class:`Table` objects.")
    systables       = LateBindingProperty(_get_systables,None,None,"List of all system tables in database.\nItems are :class:`Table` objects.")
    views           = LateBindingProperty(_get_views,None,None,"List of all user views in database.\nItems are :class:`View` objects.")
    sysviews        = LateBindingProperty(_get_sysviews,None,None,"List of all system views in database.\nItems are :class:`View` objects.")
    triggers        = LateBindingProperty(_get_triggers,None,None,"List of all user triggers in database.\nItems are :class:`Trigger` objects.")
    systriggers     = LateBindingProperty(_get_systriggers,None,None,"List of all system triggers in database.\nItems are :class:`Trigger` objects.")
    procedures      = LateBindingProperty(_get_procedures,None,None,"List of all user procedures in database.\nItems are :class:`Procedure` objects.")
    sysprocedures   = LateBindingProperty(_get_sysprocedures,None,None,"List of all system procedures in database.\nItems are :class:`Procedure` objects.")
    constraints     = LateBindingProperty(_get_constraints,None,None,"List of all constraints in database.\nItems are :class:`Constraint` objects.")
    roles           = LateBindingProperty(_get_roles,None,None,"List of all roles in database.\nItems are :class:`Role` objects.")
    dependencies    = LateBindingProperty(_get_dependencies,None,None,"List of all dependencies in database.\nItems are :class:`Dependency` objects.")
    functions       = LateBindingProperty(_get_functions,None,None,"List of all user functions defined in database.\nItems are :class:`Function` objects.")
    files           = LateBindingProperty(_get_files,None,None,"List of all extension and shadow files defined for database.\nItems are :class:`DbFile` objects.")

    #--- Public

    def acceptVisitor(self,visitor):
        visitor.visitDatabase(self)
    
    #--- Basic Database manipulation routines

    def commit(self):
        """Commits transaction.
        """
        self._user_transaction.commit()
    def rollback(self):
        """Rollback transaction.
        """
        self._user_transaction.rollback()
    def close(self):
        """Close connection to the database.
        """
        if self._con:
            self._con.close()
            self.__clear()
    def drop(self):
        """Drop attached database.
        """
        if self._con:
            try:
                self._con.drop_database()
            finally:
                self.__clear()
    def cursor(self):
        return self._user_transaction.cursor()
    def reload(self,data=None):
        if (not data or data == "tables"):
            self.__tables = None
        if (not data or data == "views"):
            self.__views = None
        if (not data or data == "domains"):
            self.__domains = None
        if (not data or data == "indices"):
            self.__indices = None
            self.__constraint_indices = None
        if (not data or data == "dependencies"):
            self.__dependencies = None
        if (not data or data == "generators"):
            self.__generators = None
        if (not data or data == "triggers"):
            self.__triggers = None
        if (not data or data == "procedures"):
            self.__procedures = None
        if (not data or data == "constraints"):
            self.__constraints = None
        if (not data or data == "collations"):
            self.__collations = None
        if (not data or data == "character sets"):
            self.__character_sets = None
        if (not data or data == "exceptions"):
            self.__exceptions = None
        if (not data or data == "roles"):
            self.__roles = None
        if (not data or data == "functions"):
            self.__functions = None
        if (not data or data == "files"):
            self.__files = None
    def getCollation(self,name):
        return self.__objectByName(self._get_collations(),name)
    def getCharacterSet(self,name):
        return self.__objectByName(self._get_character_sets(),name)
    def getException(self,name):
        return self.__objectByName(self._get_exceptions(),name)
    def getGenerator(self,name):
        return self.__objectByName(self._getAllGenerators(),name)
    def getIndex(self,name):
        return self.__objectByName(self._getAllIndices(),name)
    def getDomain(self,name):
        """Return :class:`Domain` object with specified name."""
        return self.__objectByName(self._getAllDomains(),name)
    def getTable(self,name):
        return self.__objectByName(self._getAllTables(),name)
    def getView(self,name):
        return self.__objectByName(self._getAllViews(),name)
    def getTrigger(self,name):
        return self.__objectByName(self._getAllTriggers(),name)
    def getProcedure(self,name):
        return self.__objectByName(self._getAllProcedures(),name)
    def getConstraint(self,name):
        return self.__objectByName(self._get_constraints(),name)
    def getRole(self,name):
        return self.__objectByName(self._get_roles(),name)
    def getFunction(self,name):
        return self.__objectByName(self._get_functions(),name)
    def getFile(self,name):
        return self.__objectByName(self._get_files(),name)
    def getCollationById(self,charset_id,collation_id):
        for collation in self._get_collations():
            if (collation.character_set_id == charset_id) and (collation.id == collation_id):
                return collation
        else:
            return None
    def getCharacterSetById(self,id):
        for charset in self._get_character_sets():
            if charset.id == id:
                return charset
        else:
            return None
    def getDatabaseInfo(self,request):
        return self._con.db_info(request)

class BaseDBObject(object):
    def __init__(self,db,attributes):
        self.db = db
        self._con = db._con
        self._typeCode = []
        self.__observers = []
        self._attributes = dict(attributes)

    #--- protected

    def _stripAttribute(self,attr):
        if self._attributes[attr]:
            self._attributes[attr] = self._attributes[attr].strip()
    def _needsQuoting(self,ident):
        if not ident:
            return False
        if self.db.optAlwaysQuote:
            return True
        if len(ident) >= 1 and ident[0] not in string.ascii_uppercase:
            return True
        for char in ident:
            if char not in string.ascii_uppercase + string.digits + '$_':
                return True
        return isKeyword(ident)
    def _notifyObservers(self,data=None):
        for o in self.__observers:
            o.update(self,data)
    def _get_name(self):
        return None
    def _get_description(self):
        return self._attributes.get('RDB$DESCRIPTION',None)
    def _set_description(self,desc):
        pass
    
    #--- properties

    name = LateBindingProperty(_get_name,None,None,"Database object name or None if object doesn't have a name.")
    description = LateBindingProperty(_get_description,_set_description,None,"Database object description or None if object doesn't have a description.")

    #--- Public
    
    def acceptVisitor(self,visitor):
        visitor.visitMetadataItem(self)
    def attachObserver(self,observer):
        self.__observers.append(observer)
    def detachObserver(self,observer):
        self.__observers.remove(observer)
    def detachAllObservers(self):
        self.__observers.clear()
    def isSystemObject(self):
        """Return True if this database object is system object.
        """
        return iif(self._attributes.get('RDB$SYSTEM_FLAG',False),True,False)
    def getQuotedName(self):
        if self._needsQuoting(self.name):
            return '"%s"' % self.name
        else:
            return self.name
    def getDependents(self):
        """Return list of all database objects that depend on this one.
        """
        return [d for d in self.db.dependencies if d.depended_on_name == self.name and 
            d.depended_on_type in self._typeCode]
    def getDependencies(self):
        """Return list of database objects that this objects depend on.
        """
        return [d for d in self.db.dependencies if d.dependent_name == self.name and 
            d.dependent_type in self._typeCode]

class Collation(BaseDBObject):
    """Represents collation."""
    def __init__(self,db,attributes):
        super(Collation,self).__init__(db,attributes)

        self._stripAttribute('RDB$COLLATION_NAME')

    #--- Protected

    def _get_name(self):
        return self._attributes['RDB$COLLATION_NAME']
    def _get_id(self):
        return self._attributes['RDB$COLLATION_ID']
    def _get_character_set_id(self):
        return self._attributes['RDB$CHARACTER_SET_ID']
    
    #--- Properties
    
    id = LateBindingProperty(_get_id,None,None,"Collation ID.")
    character_set_id = LateBindingProperty(_get_character_set_id,None,None,"Character set ID associated with collation.")
    
    #--- Public
    
    def getCharacterSet(self):
        """Return :class:`CharacterSet` object to which this collation belongs.
        """
        return self.db.getCharacterSetById(self.character_set_id)
    def acceptVisitor(self,visitor):
        visitor.visitCollation(self)
    #def isSystemObject(self):
        #return self._attributes['RDB$SYSTEM_FLAG'] == 1

class CharacterSet(BaseDBObject):
    """Represents character set.
    """
    def __init__(self,db,attributes):
        super(CharacterSet,self).__init__(db,attributes)

        self._stripAttribute('RDB$CHARACTER_SET_NAME')
        self._stripAttribute('RDB$DEFAULT_COLLATE_NAME')

    #--- protected

    def _get_name(self):
        return self._attributes['RDB$CHARACTER_SET_NAME']
    def _get_id(self):
        return self._attributes['RDB$CHARACTER_SET_ID']
    def _get_bytes_per_character(self):
        return self._attributes['RDB$BYTES_PER_CHARACTER']
    def _get_default_collate_name(self):
        return self._attributes['RDB$DEFAULT_COLLATE_NAME']
    def _get_collations(self):
        r = [c for c in self.db.collations if c.character_set_id == self.id]
        return r

    #--- properties

    id = LateBindingProperty(_get_id,None,None,"Character set ID.")
    bytes_per_character = LateBindingProperty(_get_bytes_per_character,None,None,"Size of characters in bytes.")
    default_collate_name = LateBindingProperty(_get_default_collate_name,None,None,"Name of default collate.")
    collations = LateBindingProperty(_get_collations,None,None,"List of Collations associated with character set.")

    #--- Public
    
    def acceptVisitor(self,visitor):
        visitor.visitCharacterSet(self)
    def getCollation(self,name):
        """Return :class:`Collation` object with specifid name that belongs to
this character set.
        """
        for col in self.collations:
            if col.name == name:
                return col
        return None
    def getCollationById(self,id):
        """Return :class:`Collation` object with specifid id that belongs to
this character set.
        """
        for col in self.collations:
            if col.id == id:
                return col
        return None

class Exception(BaseDBObject):
    """Represents database exception.
    """
    def __init__(self,db,attributes):
        super(Exception,self).__init__(db,attributes)
        self._typeCode = [7,]

        self._stripAttribute('RDB$EXCEPTION_NAME')

    #--- Protected

    def _get_name(self):
        return self._attributes['RDB$EXCEPTION_NAME']
    def _get_id(self):
        return self._attributes['RDB$EXCEPTION_NUMBER']
    def _get_message(self):
        return self._attributes['RDB$MESSAGE']
    
    #--- Properties

    id = LateBindingProperty(_get_id,None,None,"System-assigned unique exception number.")
    message = LateBindingProperty(_get_message,None,None,"Custom message text.")

    #--- Public
    
    def acceptVisitor(self,visitor):
        visitor.visitException(self)

class Generator(BaseDBObject):
    """Represents database generator.
    """
    def __init__(self,db,attributes):
        super(Generator,self).__init__(db,attributes)
        self._typeCode = [14,]

        self._stripAttribute('RDB$GENERATOR_NAME')

    #--- protected

    def _get_name(self):
        return self._attributes['RDB$GENERATOR_NAME']
    def _get_id(self):
        return self._attributes['RDB$GENERATOR_ID']
    def _get_value(self):
        return self.db._selectRow("select GEN_ID(%s,0) from RDB$DATABASE" % self.name)['GEN_ID']
    def _set_value(self,value):
        ## ToDo: Implement Generator._set_value
        pass

    #--- Properties

    id = LateBindingProperty(_get_id,None,None,"Internal number ID of the generator.")
    value = LateBindingProperty(_get_value,_set_value,None,"Current generator value.")

    #--- Public
    
    def acceptVisitor(self,visitor):
        visitor.visitGenerator(self)
    #def isSystemObject(self):
        #return self._attributes['RDB$SYSTEM_FLAG'] == 1

class Index(BaseDBObject):
    """Represents database index.
    """
    def __init__(self,db,attributes):
        super(Index,self).__init__(db,attributes)
        self._typeCode = [6,10]

        self.__segments = None
        self._stripAttribute('RDB$INDEX_NAME')
        self._stripAttribute('RDB$RELATION_NAME')
        self._stripAttribute('RDB$FOREIGN_KEY')

    #--- Protected

    def _get_name(self):
        return self._attributes['RDB$INDEX_NAME']
    def _get_table_name(self):
        return self._attributes['RDB$RELATION_NAME']
    def _get_id(self):
        return self._attributes['RDB$INDEX_ID']
    def _get_unique(self):
        return self._attributes['RDB$UNIQUE_FLAG'] == 1
    def _get_inactive(self):
        return self._attributes['RDB$INDEX_INACTIVE'] == 1
    def _get_index_type(self):
        return self._attributes['RDB$INDEX_TYPE']
    def _get_foreign_key(self):
        return self._attributes['RDB$FOREIGN_KEY']
    def _get_expression(self):
        return self._attributes['RDB$EXPRESSION_SOURCE']
    def _get_statistics(self):
        return self._attributes['RDB$STATISTICS']
    def _get_segments(self):
        if not self.__segments:
            self.__segments = []
            if self._attributes['RDB$SEGMENT_COUNT'] > 0:
                for row in self.db._select("""select rdb$field_name 
from rdb$index_segments where rdb$index_name = ? order by rdb$field_position""",(self.name,)):
                    self.__segments.append(row['rdb$field_name'].strip())
        return self.__segments
    def _set_description(self,desc):
        self._attributes['RDB$DESCRIPTION'] = desc
        self.db._execute("""update RDB$INDICES set RDB$DESCRIPTION = ? 
where RDB$INDEX_NAME = ?""",(desc,self.name))
        self._notifyObservers()

    #--- Properties

    table_name = LateBindingProperty(_get_table_name,None,None,"The name of the table the index applies to.")
    id = LateBindingProperty(_get_id,None,None,"Internal number ID of the index.")
    unique = LateBindingProperty(_get_unique,None,None,"True if the index is unique.")
    inactive = LateBindingProperty(_get_inactive,None,None,"True if the index is currently inactive.")
    index_type = LateBindingProperty(_get_index_type,None,None,"")
    foreign_key = LateBindingProperty(_get_foreign_key,None,None,"name of the associated foreign key constraint, or None.")
    expression = LateBindingProperty(_get_expression,None,None,"Source of an expression or None.")
    statistics = LateBindingProperty(_get_statistics,None,None,"Latest selectivity of the index.")
    segments = LateBindingProperty(_get_segments,None,None,"List of index segment names.")

    #--- Public
    
    def acceptVisitor(self,visitor):
        visitor.visitIndex(self)
    def isSystemObject(self):
        return self._attributes['RDB$SYSTEM_FLAG'] or self.db._get_constraintIndices().has_key(self.name)

    #--- Actions

    def getSQLCommand(self,action):
        a = action.upper() 
        if a == 'RECOMPUTE':
            return "set statistics index %s ;" % self.name
        elif a == 'ACTIVATE':
            return "alter index %s active ;" % self.name
        elif a == 'DEACTIVATE':
            return "alter index %s inactive ;" % self.name
        else:
            return None

class TableColumn(BaseDBObject):
    """Represents table column.
    """
    def __init__(self,db,table,attributes):
        super(TableColumn,self).__init__(db,attributes)
        self._typeCode = [3,9]
        
        self.__table = table
        self._stripAttribute('RDB$FIELD_NAME')
        self._stripAttribute('RDB$RELATION_NAME')
        self._stripAttribute('RDB$FIELD_SOURCE')

    #--- Protected
    
    def _get_name(self):
        return self._attributes['RDB$FIELD_NAME']
    def _get_field_name(self):
        return self._attributes['RDB$FIELD_NAME']
    def _set_field_name(self,value):
        ## ToDo: Implement TableColumn._set_field_name
        pass
    def _get_table_name(self):
        return self._attributes['RDB$RELATION_NAME']
    def _get_domain_name(self):
        return self._attributes['RDB$FIELD_SOURCE']
    def _set_domain_name(self,value):
        ## ToDo: Implement TableColumn._set_domain_name
        pass
    def _get_position(self):
        return self._attributes['RDB$FIELD_POSITION']
    def _set_position(self,value):
        ## ToDo: Implement TableColumn._set_position
        pass
    def _get_security_class(self):
        return self._attributes['RDB$SECURITY_CLASS']
    def _get_nullable(self):
        return not self._attributes['RDB$NULL_FLAG']
    def _get_default_value(self):
        return self._attributes['RDB$DEFAULT_SOURCE']
    def _set_default_value(self,value):
        ## ToDo: Implement TableColumn._set_default_value
        pass
    def _get_collation_id(self):
        return self._attributes['RDB$COLLATION_ID']
    def _get_datatype(self):
        return self.getDomain().datatype
    def _set_datatype(self,value):
        ## ToDo: Implement TableColumn._set_datatype
        pass
    def _set_description(self,desc):
        self._attributes['RDB$DESCRIPTION'] = desc
        self.db._execute("""update RDB$RELATION_FIELDS set RDB$DESCRIPTION = ? 
where RDB$FIELD_NAME = ? and RDB$RELATION_NAME = ?""",(desc,self.field_name,self.table_name))
        self._notifyObservers()

    #--- Properties

    field_name = LateBindingProperty(_get_field_name,_set_field_name,None,"Name of the column.")
    table_name = LateBindingProperty(_get_table_name,None,None,"Name of the table this column belongs to.")
    domain_name = LateBindingProperty(_get_domain_name,_set_domain_name,None,"Name of the domain this column is based on.")
    position = LateBindingProperty(_get_position,_set_position,None,"Column's sequence number in row.")
    security_class = LateBindingProperty(_get_security_class,None,None,"Security class name or None.")
    nullable = LateBindingProperty(_get_nullable,None,None,"True if column can accept NULL values.")
    default_value = LateBindingProperty(_get_default_value,_set_default_value,None,"Default value for column or None.")
    collation_id = LateBindingProperty(_get_collation_id,None,None,"Collation ID or None.")
    datatype = LateBindingProperty(_get_datatype,_set_datatype,None,"Comlete SQL datatype definition.")
    
    #--- Public
    
    def acceptVisitor(self,visitor):
        visitor.visitTableColumn(self)
    def getDomain(self):
        """Return :class:`Domain` object for this column.
        """
        return self.db.getDomain(self.domain_name)
    def getCollation(self):
        """Return :class:`Collation` object that belongs to this character column.
        """
        if self.collation_id:
            return self.db.getCollationById(self,self.collation_id)
        return None
    def getDependents(self):
        """Return list of all database objects that depend on this one.
        """
        return [d for d in self.db.dependencies if d.depended_on_name == self.table_name and 
            d.depended_on_type == 0 and d.field_name == self.name]
    def getDependencies(self):
        """Return list of database objects that this objects depend on.
        """
        return [d for d in self.db.dependencies if d.dependent_name == self.table_name and 
            d.dependent_type == 0 and d.field_name == self.name]

class ViewColumn(BaseDBObject):
    """Represents view column.
    """
    def __init__(self,db,view,attributes):
        super(ViewColumn,self).__init__(db,attributes)
        self._typeCode = [3,9]
        
        self.__view = view
        self._stripAttribute('RDB$FIELD_NAME')
        self._stripAttribute('RDB$BASE_FIELD')
        self._stripAttribute('RDB$RELATION_NAME')
        self._stripAttribute('RDB$FIELD_SOURCE')

    #--- Protected
    
    def _get_name(self):
        return self._attributes['RDB$FIELD_NAME']
    def _get_field_name(self):
        return self._attributes['RDB$FIELD_NAME']
    def _get_base_field(self):
        return self._attributes['RDB$BASE_FIELD']
    def _get_view_context(self):
        return self._attributes['RDB$VIEW_CONTEXT']
    def _get_view_name(self):
        return self._attributes['RDB$RELATION_NAME']
    def _get_domain_name(self):
        return self._attributes['RDB$FIELD_SOURCE']
    def _get_position(self):
        return self._attributes['RDB$FIELD_POSITION']
    def _get_security_class(self):
        return self._attributes['RDB$SECURITY_CLASS']
    def _get_nullable(self):
        return not self._attributes['RDB$NULL_FLAG']
    def _get_collation_id(self):
        return self._attributes['RDB$COLLATION_ID']
    def _get_datatype(self):
        return self.getDomain().datatype
    def _set_description(self,desc):
        self._attributes['RDB$DESCRIPTION'] = desc
        self.db._execute("""update RDB$RELATION_FIELDS set RDB$DESCRIPTION = ? 
where RDB$FIELD_NAME = ? and RDB$RELATION_NAME = ?""",(desc,self.field_name,self.table_name))
        self._notifyObservers()

    #--- Properties

    field_name = LateBindingProperty(_get_field_name,None,None,"Name of the column.")
    base_field = LateBindingProperty(_get_base_field,None,None,"The column name from the base table.")
    view_name = LateBindingProperty(_get_view_name,None,None,"Name of the view this column belongs to.")
    view_context = LateBindingProperty(_get_view_context,None,None,"Internal number ID for the base table where the field come from.")
    domain_name = LateBindingProperty(_get_domain_name,None,None,"Name of the domain this column is based on.")
    position = LateBindingProperty(_get_position,None,None,"Column's sequence number in row.")
    security_class = LateBindingProperty(_get_security_class,None,None,"Security class name or None.")
    nullable = LateBindingProperty(_get_nullable,None,None,"True if column can accept NULL values.")
    collation_id = LateBindingProperty(_get_collation_id,None,None,"Collation ID or None.")
    datatype = LateBindingProperty(_get_datatype,None,None,"Comlete SQL datatype definition.")
    
    #--- Public
    
    def acceptVisitor(self,visitor):
        visitor.visitViewColumn(self)
    def getDomain(self):
        """Return :class:`Domain` object for this column."""
        return self.db.getDomain(self.domain_name)
    def getCollation(self):
        """Return :class:`Collation` object that belongs to this column."""
        if self.collation_id:
            return self.db.getCollationById(self,self.collation_id)
        return None
    def getDependents(self):
        """Return list of all database objects that depend on this one.
        """
        return [d for d in self.db.dependencies if d.depended_on_name == self.view_name and 
            d.depended_on_type == 1 and d.field_name == self.name]
    def getDependencies(self):
        """Return list of database objects that this objects depend on.
        """
        return [d for d in self.db.dependencies if d.dependent_name == self.view_name and 
            d.dependent_type == 1 and d.field_name == self.name]

class Domain(BaseDBObject):
    def __init__(self,db,attributes):
        super(Domain,self).__init__(db,attributes)
        self._typeCode = [9]

        self._stripAttribute('RDB$FIELD_NAME')

    #--- Protected

    def _get_name(self):
        return self._attributes['RDB$FIELD_NAME']
    def _get_computed_source(self):
        return self._attributes['RDB$COMPUTED_SOURCE']
    def _get_validation_source(self):
        return self._attributes['RDB$VALIDATION_SOURCE']
    def _get_default_source(self):
        return self._attributes['RDB$DEFAULT_SOURCE']
    def _set_default_source(self,value):
        ## ToDo: Implement Domain._set_default_value
        pass
    def _get_length(self):
        return self._attributes['RDB$FIELD_LENGTH']
    def _get_scale(self):
        return self._attributes['RDB$FIELD_SCALE']
    def _get_field_type(self):
        return self._attributes['RDB$FIELD_TYPE']
    def _get_sub_type(self):
        return self._attributes['RDB$FIELD_SUB_TYPE']
    def _get_segment_length(self):
        return self._attributes['RDB$SEGMENT_LENGTH']
    def _get_external_length(self):
        return self._attributes['RDB$EXTERNAL_LENGTH']
    def _get_external_scale(self):
        return self._attributes['RDB$EXTERNAL_SCALE']
    def _get_external_type(self):
        return self._attributes['RDB$EXTERNAL_TYPE']
    def _get_dimensions(self):
        return self._attributes['RDB$DIMENSIONS']
    def _get_character_length(self):
        return self._attributes['RDB$CHARACTER_LENGTH']
    def _get_collation_id(self):
        return self._attributes['RDB$COLLATION_ID']
    def _get_character_set_id(self):
        return self._attributes['RDB$CHARACTER_SET_ID']
    def _get_precision(self):
        return self._attributes['RDB$FIELD_PRECISION']
    def _get_nullable(self):
        return not self._attributes['RDB$NULL_FLAG']
    def _get_datatype(self):
        l = []
        if self.dimensions != None:
            l.append('ARRAY OF %s ' % self.db._getFieldDimensions(self))
        precision_known = False
        if self.field_type in (FBT_SMALLINT,FBT_INTEGER,FBT_BIGINT):
            if self.precision != None:
                if (self.sub_type > 0) and (self.sub_type < MAX_INTSUBTYPES):
                    l.append('%s(%d, %d)' % \
                      (integral_subtypes[self.sub_type],self.precision,-self.scale))
                    precision_known = True
        if not precision_known:
            if (self.field_type == FBT_SMALLINT) and (self.scale < 0):
                l.append('NUMERIC(4, %d)' % -self.scale)
            elif (self.field_type == FBT_INTEGER) and (self.scale < 0):
                l.append('NUMERIC(9, %d)' % -self.scale)
            elif (self.field_type == FBT_DOUBLE_PRECISION) and (self.scale < 0):
                l.append('NUMERIC(15, %d)' % -self.scale)
            else:
                l.append(column_types[self.field_type])
        if self.field_type in (FBT_CHAR,FBT_VARCHAR):
            l.append('(%d)' % iif(self.character_length == None,self.length,self.character_length))
        if self.field_type == FBT_BLOB:
            l.append(' segment %u, subtype ' % self.segment_length)
            if self.sub_type >= 0 and self.sub_type <= MAX_BLOBSUBTYPES:
                l.append(blob_sub_types[self.sub_type])
            else:
                l.append('%d' % self.sub_type)
        if self.field_type in (FBT_CHAR,FBT_VARCHAR,FBT_BLOB):
            if self.character_set_id is not None and \
              (self.db.getCharacterSetById(self.character_set_id).name != self.db.default_character_set) or self.collation_id:
                if (self.character_set_id is not None):
                    l.append(' CHARACTER SET %s' % self.db.getCharacterSetById(self.character_set_id).name)
                if self.collation_id is not None:
                    l.append(' COLLATE %s' % self.db.getCollationById(self.character_set_id,self.collation_id).name)
        return ''.join(l)
    def _set_datatype(self,value):
        ## ToDo: Implement Domain._set_datatype
        pass
    def _set_description(self,desc):
        self._attributes['RDB$DESCRIPTION'] = desc
        self.db._execute("update RDB$FIELDS set RDB$DESCRIPTION = ? where RDB$FIELD_NAME = ?",(desc,self.name))
        self._notifyObservers()

    #--- Properties

    computed_source = LateBindingProperty(_get_computed_source,None,None,"Expression that defines the COMPUTED BY column or None.")
    validation_source = LateBindingProperty(_get_validation_source,None,None,"Expression that defines the CHECK constarint for the column or None.")
    default_source = LateBindingProperty(_get_default_source,_set_default_source,None,"Expression that defines the default value or None.")
    length = LateBindingProperty(_get_length,None,None,"Length of the column in bytes.")
    scale = LateBindingProperty(_get_scale,None,None,"Negative number representing the scale of NUMBER and DECIMAL column.")
    field_type = LateBindingProperty(_get_field_type,None,None,"Number code of the data type defined for the column.")
    sub_type = LateBindingProperty(_get_sub_type,None,None,"BLOB subtype.")
    segment_length = LateBindingProperty(_get_segment_length,None,None,"For BLOB columns, a suggested length for BLOB buffers.")
    external_length = LateBindingProperty(_get_external_length,None,None,"Length of field as it is in an external table. Always 0 for regular tables.")
    external_scale = LateBindingProperty(_get_external_scale,None,None,"Scale factor of an integer field as it is in an external table.")
    external_type = LateBindingProperty(_get_external_type,None,None,"Data type of the field as it is in an external table.")
    dimensions = LateBindingProperty(_get_dimensions,None,None,"Number of dimensions defined, if column is an array type. Always zero for non-array columns.")
    character_length = LateBindingProperty(_get_character_length,None,None,"Length of CHAR and VARCHAR column, in characters (not bytes).")
    collation_id = LateBindingProperty(_get_collation_id,None,None,"Number ID of the collation sequence (if defined) for a character column.")
    character_set_id = LateBindingProperty(_get_character_set_id,None,None,"Number ID of the character set for a character or text BLOB column.")
    precision = LateBindingProperty(_get_precision,None,None,"Indicates the number of digits of precision available to the data type of the column.")
    nullable = LateBindingProperty(_get_nullable,None,None,"True if domain is not defined with NOT NULL.")
    datatype = LateBindingProperty(_get_datatype,_set_datatype,None,"Comlete SQL datatype definition.")

    #--- Public
    
    def acceptVisitor(self,visitor):
        visitor.visitDomain(self)
    def isSystemObject(self):
        """Return True if this database object is system object.
        """
        return (self._attributes['RDB$SYSTEM_FLAG'] == 1) or self.name.startswith('RDB$')
    def getCollation(self):
        """Return :class:`Collation` object that belongs to this domain.
        """
        if self.collation_id != None:
            return self.db.getCollationById(self.character_set_id,self.collation_id)
        return None
    def getCharacterSet(self):
        """Return :class:`CharacterSet` object that belongs to this domain.
        """
        if self.character_set_id != None:
            return self.db.getCharacterSetById(self.character_set_id)
        return None

class Dependency(BaseDBObject):
    """Maps dependency between database objects.
    """
    def __init__(self,db,attributes):
        super(Dependency,self).__init__(db,attributes)
        
        self._stripAttribute('RDB$DEPENDENT_NAME')
        self._stripAttribute('RDB$DEPENDED_ON_NAME')
        self._stripAttribute('RDB$FIELD_NAME')

    #--- Protected
    
    def _get_dependent_name(self):
        return self._attributes['RDB$DEPENDENT_NAME']
    def _get_dependent_type(self):
        return self._attributes['RDB$DEPENDENT_TYPE']
    def _get_field_name(self):
        return self._attributes['RDB$FIELD_NAME']
    def _get_depended_on_name(self):
        return self._attributes['RDB$DEPENDED_ON_NAME']
    def _get_depended_on_type(self):
        return self._attributes['RDB$DEPENDED_ON_TYPE']
    
    #--- Properties
    
    dependent_name   = LateBindingProperty(_get_dependent_name,None,None,"")
    dependent_type   = LateBindingProperty(_get_dependent_type,None,None,"")
    field_name       = LateBindingProperty(_get_field_name,None,None,"")
    depended_on_name = LateBindingProperty(_get_depended_on_name,None,None,"")
    depended_on_type = LateBindingProperty(_get_depended_on_type,None,None,"")
    
    #--- Public
    
    def acceptVisitor(self,visitor):
        visitor.visitDependency(self)
    def getDependent(self):
        """Return dependent database object.
        """
        if self.dependent_type == 0:
            t = self.db.getTable(self.dependent_name)
            if self.field_name:
                return t.getColumn(self.field_name)
            else:
                return t
        elif self.dependent_type == 1:
            return self.db.getView(self.dependent_name)
        elif self.dependent_type == 2:
            return self.db.getTrigger(self.dependent_name)
        elif self.dependent_type == 3:
            ## ToDo: Implement handler for COMPUTED FIELDs if necessary
            return None
        elif self.dependent_type == 4:
            ## ToDo: Implement handler for VALIDATION if necessary
            return None
        elif self.dependent_type == 5:
            return self.db.getProcedure(self.dependent_name)
        elif self.dependent_type == 6:
            return self.db.getIndex(self.dependent_name)
        elif self.dependent_type == 7:
            return self.db.getException(self.dependent_name)
        elif self.dependent_type == 8:
            ## ToDo: Implement handler for USER if necessary
            return None
        elif self.dependent_type == 9:
            ## ToDo: Implement handler for FIELD if necessary
            return None
        elif self.dependent_type == 10:
            return self.db.getIndex(self.dependent_name)
        elif self.dependent_type == 11:
            ## ToDo: Implement handler for DEPENDENT COUNT if necessary
            return None
        elif self.dependent_type == 12:
            ## ToDo: Implement handler for USER GROUP if necessary
            return None
        elif self.dependent_type == 13:
            return self.db.getRole(self.dependent_name)
        elif self.dependent_type == 14:
            return self.db.getGenerator(self.dependent_name)
        elif self.dependent_type == 15:
            ## ToDo: Implement handler for UDF
            return None
        elif self.dependent_type == 16:
            ## ToDo: Implement handler for BLOB_FILTER
            return None
        return None
    def getDependency(self):
        """Return database object on which the other one depends.
        """
        if self.depended_on_type == 0:
            t = self.db.getTable(self.depended_on_name)
            if self.field_name:
                return t.getColumn(self.field_name)
            else:
                return t
        elif self.depended_on_type == 1:
            return self.db.getView(self.depended_on_name)
        elif self.depended_on_type == 2:
            return self.db.getTrigger(self.depended_on_name)
        elif self.depended_on_type == 3:
            ## ToDo: Implement handler for COMPUTED FIELDs if necessary
            return None
        elif self.depended_on_type == 4:
            ## ToDo: Implement handler for VALIDATION if necessary
            return None
        elif self.depended_on_type == 5:
            return self.db.getProcedure(self.depended_on_name)
        elif self.depended_on_type == 6:
            return self.db.getIndex(self.depended_on_name)
        elif self.depended_on_type == 7:
            return self.db.getException(self.depended_on_name)
        elif self.depended_on_type == 8:
            ## ToDo: Implement handler for USER if necessary
            return None
        elif self.depended_on_type == 9:
            ## ToDo: Implement handler for FIELD if necessary
            return None
        elif self.depended_on_type == 10:
            return self.db.getIndex(self.depended_on_name)
        elif self.depended_on_type == 11:
            ## ToDo: Implement handler for DEPENDENT COUNT if necessary
            return None
        elif self.depended_on_type == 12:
            ## ToDo: Implement handler for USER GROUP if necessary
            return None
        elif self.depended_on_type == 13:
            return self.db.getRole(self.depended_on_name)
        elif self.depended_on_type == 14:
            return self.db.getGenerator(self.depended_on_name)
        elif self.depended_on_type == 15:
            ## ToDo: Implement handler for UDF
            return None
        elif self.depended_on_type == 16:
            ## ToDo: Implement handler for BLOB_FILTER
            return None
        return None
    
class Constraint(BaseDBObject):
    """Represents table or column constraint.
    """
    def __init__(self,db,attributes):
        super(Constraint,self).__init__(db,attributes)

        self._stripAttribute('RDB$CONSTRAINT_NAME')
        self._stripAttribute('RDB$CONSTRAINT_TYPE')
        self._stripAttribute('RDB$RELATION_NAME')
        self._stripAttribute('RDB$DEFERRABLE')
        self._stripAttribute('RDB$INITIALLY_DEFERRED')
        self._stripAttribute('RDB$INDEX_NAME')
        self._stripAttribute('RDB$TRIGGER_NAME')
        self._stripAttribute('RDB$CONST_NAME_UQ')
        self._stripAttribute('RDB$MATCH_OPTION')
        self._stripAttribute('RDB$UPDATE_RULE')
        self._stripAttribute('RDB$DELETE_RULE')

    #--- Protected

    def _get_name(self):
        return self._attributes['RDB$CONSTRAINT_NAME']
    def _get_constraint_name(self):
        return self._attributes['RDB$CONSTRAINT_NAME']
    def _get_constraint_type(self):
        return self._attributes['RDB$CONSTRAINT_TYPE']
    def _get_relation_name(self):
        return self._attributes['RDB$RELATION_NAME']
    def _get_deferrable(self):
        return self._attributes['RDB$DEFERRABLE']
    def _get_initially_deferred(self):
        return self._attributes['RDB$INITIALLY_DEFERRED']
    def _get_index_name(self):
        return self._attributes['RDB$INDEX_NAME']
    def _get_trigger_names(self):
        if self.isCheck():
            return self._attributes['RDB$TRIGGER_NAME']
        else:
            return []
    def _get_column_name(self):
        if self.isNotNull():
            return self._attributes['RDB$TRIGGER_NAME']
        else:
            return None
    def _get_uq_constraint_name(self):
        return self._attributes['RDB$CONST_NAME_UQ']
    def _get_match_option(self):
        return self._attributes['RDB$MATCH_OPTION']
    def _get_update_rule(self):
        return self._attributes['RDB$UPDATE_RULE']
    def _get_delete_rule(self):
        return self._attributes['RDB$DELETE_RULE']

    #--- Properties

    constraint_name = LateBindingProperty(_get_constraint_name,None,None,"Name of a table-level constraint.")
    constraint_type = LateBindingProperty(_get_constraint_type,None,None,"primary key/unique/foreign key/check/not null.")
    relation_name   = LateBindingProperty(_get_relation_name,None,None,"Name of the table this constraint applies to.")
    deferrable      = LateBindingProperty(_get_deferrable,None,None,"Currently NO in all cases; reserved for future use.")
    initially_deferred = LateBindingProperty(_get_initially_deferred,None,None,"Currently NO in all cases; reserved for future use.")
    index_name      = LateBindingProperty(_get_index_name,None,None,"Name of the index that enforces the constraint.\nApplicable if constraint is primary key/unique or foreign key.")
    trigger_names   = LateBindingProperty(_get_trigger_names,None,None,"For a CHECK constraint, this is list trigger names that enforces the constraint.")
    column_name     = LateBindingProperty(_get_column_name,None,None,"For a NOT NULL constraint, this is the name of the column to which the constraint applies.")
    uq_constraint_name = LateBindingProperty(_get_uq_constraint_name,None,None,"For a FOREIGN KEY constraint, this is the name of the unique or primary key constraint referred by this constraint.")
    match_option    = LateBindingProperty(_get_match_option,None,None,"For a FOREIGN KEY constraint only. Current value is FULL in all cases.")
    update_rule     = LateBindingProperty(_get_update_rule,None,None,"For a FOREIGN KEY constraint, this is the action applicable to when primary key is updated.")
    delete_rule     = LateBindingProperty(_get_delete_rule,None,None,"For a FOREIGN KEY constraint, this is the action applicable to when primary key is deleted.")

    #--- Public
    
    def acceptVisitor(self,visitor):
        visitor.visitConstraint(self)
    def isSystemObject(self):
        """Return True if this database object is system object.
        """
        return True
    def isNotNull(self):
        """Return True if it's NOT NULL constraint.
        """
        return self.constraint_type == 'NOT NULL'
    def isPrimaryKey(self):
        """Return True if it's PRIMARY KEY constraint.
        """
        return self.constraint_type == 'PRIMARY KEY'
    def isForeignKey(self):
        """Return True if it's FOREIGN KEY constraint.
        """
        return self.constraint_type == 'FOREIGN KEY'
    def isUnique(self):
        """Return True if it's UNIQUE constraint.
        """
        return self.constraint_type == 'UNIQUE'
    def isCheck(self):
        """Return True if it's CHECK constraint.
        """
        return self.constraint_type == 'CHECK'
    def isDeferrable(self):
        """Return True if it's DEFERRABLE constraint.
        """
        return self.deferrable != 'NO'
    def isInitiallyDeferred(self):
        """Return True if it's INITIALLY DEFERRED constraint.
        """
        return self.initially_deferred != 'NO'

class Table(BaseDBObject):
    """Represents Table in database.
    """
    def __init__(self,db,attributes):
        super(Table,self).__init__(db,attributes)
        self._typeCode = [0,]

        self.__columns = None

        self._stripAttribute('RDB$RELATION_NAME')
        self._stripAttribute('RDB$OWNER_NAME')
        self._stripAttribute('RDB$SECURITY_CLASS')
        self._stripAttribute('RDB$DEFAULT_CLASS')

    #--- Protected

    def _get_name(self):
        return self._attributes['RDB$RELATION_NAME']
    def _get_relation_id(self):
        return self._attributes['RDB$RELATION_ID']
    def _get_dbkey_length(self):
        return self._attributes['RDB$DBKEY_LENGTH']
    def _get_format(self):
        return self._attributes['RDB$FORMAT']
    def _get_table_name(self):
        return self._attributes['RDB$RELATION_NAME']
    def _get_security_class(self):
        return self._attributes['RDB$SECURITY_CLASS']
    def _get_external_file(self):
        return self._attributes['RDB$EXTERNAL_FILE']
    def _get_owner_name(self):
        return self._attributes['RDB$OWNER_NAME']
    def _get_default_class(self):
        return self._attributes['RDB$DEFAULT_CLASS']
    def _get_flags(self):
        return self._attributes['RDB$FLAGS']
    def _set_description(self,desc):
        self._attributes['RDB$DESCRIPTION'] = desc
        self.db._execute("""update RDB$RELATIONS set RDB$DESCRIPTION = ? 
where RDB$RELATION_NAME = ?""",(desc,self.table_name))
        self._notifyObservers()
    def _get_indices(self):
        return [i for i in self.db._getAllIndices() if i.table_name == self.name]
    def _get_triggers(self):
        return [t for t in self.db.triggers if t.relation_name == self.name]
    def _get_constraints(self):
        return [c for c in self.db.constraints if c.relation_name == self.name]
    def _get_columns(self):
        if not self.__columns:
            self.__columns = [TableColumn(self.db,self,row) for row in 
                self.db._select("select * from rdb$relation_fields where rdb$relation_name = ? order by rdb$field_position",(self.table_name,))]
            self.db._commit()
        return self.__columns

    #--- Properties

    relation_id     = LateBindingProperty(_get_relation_id,None,None,"Internam number ID for the table.")
    dbkey_length    = LateBindingProperty(_get_dbkey_length,None,None,"Length of the RDB$DB_KEY column in bytes.")
    format          = LateBindingProperty(_get_format,None,None,"Internal format ID for the table.")
    table_name      = LateBindingProperty(_get_table_name,None,None,"Name of the table.")
    security_class  = LateBindingProperty(_get_security_class,None,None,"Security class that define access limits to the table.")
    external_file   = LateBindingProperty(_get_external_file,None,None,"Full path to the external data file, if any.")
    owner_name      = LateBindingProperty(_get_owner_name,None,None,"User name of table's creator.")
    default_class   = LateBindingProperty(_get_default_class,None,None,"Default security class.")
    flags           = LateBindingProperty(_get_flags,None,None,"Internal flags.")

    columns     = LateBindingProperty(_get_columns,None,None,"Returns list of columns defined for table.\nItems are :class:`TableColumn` objects.")
    constraints = LateBindingProperty(_get_constraints,None,None,"Returns list of constraints defined for table.\nItems are :class:`Constraint` objects.")
    indices     = LateBindingProperty(_get_indices,None,None,"Returns list of indices defined for table.\nItems are :class:`Index` objects.")
    triggers    = LateBindingProperty(_get_triggers,None,None,"Returns list of triggers defined for table.\nItems are :class:`Trigger` objects.")

    #--- Public
    
    def acceptVisitor(self,visitor):
        visitor.visitTable(self)
    #def isSystemObject(self):
        #return self._attributes['RDB$SYSTEM_FLAG'] > 0
    def getColumn(self,name):
        """Return :class:`TableColumn` object with specified name.
        """
        for col in self.columns:
            if col.name == name:
                return col
        return None
    
class View(BaseDBObject):
    """Represents database View.
    """
    def __init__(self,db,attributes):
        super(View,self).__init__(db,attributes)
        self._typeCode = [1,]

        self.__columns = None

        self._stripAttribute('RDB$RELATION_NAME')
        self._stripAttribute('RDB$VIEW_SOURCE')
        self._stripAttribute('RDB$OWNER_NAME')
        self._stripAttribute('RDB$SECURITY_CLASS')
        self._stripAttribute('RDB$DEFAULT_CLASS')

    #--- Protected

    def _get_name(self):
        return self._attributes['RDB$RELATION_NAME']
    def _get_source_sql(self):
        return self._attributes['RDB$VIEW_SOURCE']
    def _get_relation_id(self):
        return self._attributes['RDB$RELATION_ID']
    def _get_dbkey_length(self):
        return self._attributes['RDB$DBKEY_LENGTH']
    def _get_format(self):
        return self._attributes['RDB$FORMAT']
    def _get_view_name(self):
        return self._attributes['RDB$RELATION_NAME']
    def _get_security_class(self):
        return self._attributes['RDB$SECURITY_CLASS']
    def _get_owner_name(self):
        return self._attributes['RDB$OWNER_NAME']
    def _get_default_class(self):
        return self._attributes['RDB$DEFAULT_CLASS']
    def _get_flags(self):
        return self._attributes['RDB$FLAGS']
    def _set_description(self,desc):
        self._attributes['RDB$DESCRIPTION'] = desc
        self.db._execute("""update RDB$RELATIONS set RDB$DESCRIPTION = ? 
where RDB$RELATION_NAME = ?""",(desc,self.view_name))
        self._notifyObservers()
    def _get_triggers(self):
        return [t for t in self.db.triggers if t.relation_name == self.name]
    def _get_columns(self):
        if not self.__columns:
            self.__columns = [ViewColumn(self.db,self,row) for row in 
                self.db._select("select * from rdb$relation_fields where rdb$relation_name = ? order by rdb$field_position",(self.view_name,))]
            self.db._commit()
        return self.__columns

    #--- Properties

    source_sql      = LateBindingProperty(_get_source_sql,None,None,"The query specification.")
    relation_id     = LateBindingProperty(_get_relation_id,None,None,"Internal number ID for the view.")
    dbkey_length    = LateBindingProperty(_get_dbkey_length,None,None,"Length of the RDB$DB_KEY column in bytes.")
    format          = LateBindingProperty(_get_format,None,None,"Internal format ID for the view.")
    view_name       = LateBindingProperty(_get_view_name,None,None,"Name of the view.")
    security_class  = LateBindingProperty(_get_security_class,None,None,"Security class that define access limits to the view.")
    owner_name      = LateBindingProperty(_get_owner_name,None,None,"User name of view's creator.")
    default_class   = LateBindingProperty(_get_default_class,None,None,"Default security class.")
    flags           = LateBindingProperty(_get_flags,None,None,"Internal flags.")

    columns     = LateBindingProperty(_get_columns,None,None,"Returns list of columns defined for view.\nItems are :class:`ViewColumn` objects.")
    triggers    = LateBindingProperty(_get_triggers,None,None,"Returns list of triggers defined for view.\nItems are :class:`Trigger` objects.")

    #--- Public
    
    def acceptVisitor(self,visitor):
        visitor.visitView(self)
    #def isSystemObject(self):
        #return self._attributes['RDB$SYSTEM_FLAG'] > 0
    def getColumn(self,name):
        """Return :class:`TableColumn` object with specified name.
        """
        for col in self.columns:
            if col.name == name:
                return col
        return None
    def getTrigger(self,name):
        """Return :class:`Trigger` object with specified name.
        """
        for t in self.triggers:
            if t.name == name:
                return t
        return None
    
class Trigger(BaseDBObject):
    """Represents trigger.
    """
    def __init__(self,db,attributes):
        super(Trigger,self).__init__(db,attributes)
        self._typeCode = [2,]

        self._stripAttribute('RDB$TRIGGER_NAME')
        self._stripAttribute('RDB$RELATION_NAME')

    #--- Protected

    def _getActionTime(self):
        return (self.trigger_type + 1) & 1
    def _getActionType(self,slot):
        return ((self.trigger_type + 1) >> (slot * 2 - 1)) & 3
    def _get_name(self):
        return self._attributes['RDB$TRIGGER_NAME']
    def _get_relation_name(self):
        return self._attributes['RDB$RELATION_NAME']
    def _get_trigger_name(self):
        return self._attributes['RDB$TRIGGER_NAME']
    def _get_sequence(self):
        return self._attributes['RDB$TRIGGER_SEQUENCE']
    def _get_trigger_type(self):
        return self._attributes['RDB$TRIGGER_TYPE']
    def _get_source(self):
        return self._attributes['RDB$TRIGGER_SOURCE']
    def _get_flags(self):
        return self._attributes['RDB$FLAGS']
    def _set_description(self,desc):
        self._attributes['RDB$DESCRIPTION'] = desc
        self.db._execute("""update RDB$TRIGGERS set RDB$DESCRIPTION = ? 
where RDB$TRIGGER_NAME = ?""",(desc,self.trigger_name))
        self._notifyObservers()
    def _isType(self,type_code):
        atype = self._getActionType(1)
        if atype == type_code:
            return True
        atype = self._getActionType(2)
        if atype and atype == type_code:
            return True
        atype = self._getActionType(3)
        if atype and atype == type_code:
            return True
        return False

    #--- Properties

    relation_name   = LateBindingProperty(_get_relation_name,None,None,"Name of the table or view  that the trigger is for.")
    trigger_name    = LateBindingProperty(_get_trigger_name,None,None,"Name of the trigger.")
    sequence        = LateBindingProperty(_get_sequence,None,None,"Sequence (position) of trigger. Zero  usually means no sequence defined.")
    trigger_type    = LateBindingProperty(_get_trigger_type,None,None,"Numeric code for trigger type that define what event and when are covered by trigger.")
    source          = LateBindingProperty(_get_source,None,None,"PSQL source code.")
    flags           = LateBindingProperty(_get_flags,None,None,"Internal flags.")

    #--- Public
    
    def acceptVisitor(self,visitor):
        visitor.visitTrigger(self)
    def isActive(self):
        """Return True if this trigger is active."""
        return self._attributes['RDB$TRIGGER_INACTIVE'] == 0
    def isBeforeAction(self):
        """Return True if this trigger is set for BEFORE action."""
        return self._getActionTime() == 0
    def isDbTrigger(self):
        """Return True if this trigger is database trigger."""
        return (self.trigger_type & TRIGGER_TYPE_MASK) == TRIGGER_TYPE_DB
    def isAfterAction(self):
        """Return True if this trigger is set for AFTER action."""
        return self._getActionTime() == 1
    def isInsertAction(self):
        """Return True if this trigger is set for INSERT operation."""
        return self._isType(1)
    def isUpdateAction(self):
        """Return True if this trigger is set for UPDATE operation."""
        return self._isType(2)
    def isDeleteAction(self):
        """Return True if this trigger is set for DELETE operation."""
        return self._isType(3)
    def getTypeAsString(self):
        """Return string with action and operation specification."""
        l = []
        if self.isDbTrigger():
            l.append('ON '+trigger_db_types[self.trigger_type & ~TRIGGER_TYPE_DB])
        else:
            l.append(trigger_prefix_types[self._getActionTime()])
            l.append(trigger_suffix_types[self._getActionType(1)])
            sufix = self._getActionType(2)
            if sufix:
                l.append('OR')
                l.append(trigger_suffix_types[sufix])
            sufix = self._getActionType(3)
            if sufix:
                l.append('OR')
                l.append(trigger_suffix_types[sufix])
        return ' '.join(l)

class ProcParameter(BaseDBObject):
    """Represents procedure parameter.
    """
    def __init__(self,db,proc,attributes):
        super(ProcParameter,self).__init__(db,attributes)

        self.__proc = proc
        self._stripAttribute('RDB$PARAMETER_NAME')
        self._stripAttribute('RDB$PROCEDURE_NAME')
        self._stripAttribute('RDB$FIELD_SOURCE')

    #--- Protected

    def _get_name(self):
        return self._attributes['RDB$PARAMETER_NAME']
    def _get_parameter_name(self):
        return self._attributes['RDB$PARAMETER_NAME']
    def _get_procedure_name(self):
        return self._attributes['RDB$PROCEDURE_NAME']
    def _get_sequence(self):
        return self._attributes['RDB$PARAMETER_NUMBER']
    def _get_parameter_type(self):
        return self._attributes['RDB$PARAMETER_TYPE']
    def _get_field(self):
        return self._attributes['RDB$FIELD_SOURCE']
    def _get_datatype(self):
        return self.getDomain().datatype
    def _set_description(self,desc):
        self._attributes['RDB$DESCRIPTION'] = desc
        self.db._execute("""update RDB$PROCEDURE_PARAMS set RDB$DESCRIPTION = ? 
where RDB$PARAMETER_NAME = ? and RDB$PROCEDURE_NAME = ?""",(desc,self.parameter_name,self.procedure_name))
        self._notifyObservers()

    #--- Properties

    parameter_name  = LateBindingProperty(_get_parameter_name,None,None,"Name of the parameter.")
    procedure_name  = LateBindingProperty(_get_procedure_name,None,None,"Name of the stored procedure.")
    sequence        = LateBindingProperty(_get_sequence,None,None,"Sequence (position) of parameter.")
    parameter_type  = LateBindingProperty(_get_parameter_type,None,None,"Indicetas whether parameter is input(0) or output(1).")
    field           = LateBindingProperty(_get_field,None,None,"System-generated unique column name.")
    datatype        = LateBindingProperty(_get_datatype,None,None,"Comlete SQL datatype definition.")

    #--- Public
    
    def acceptVisitor(self,visitor):
        visitor.visitProcParameter(self)
    #def isSystemObject(self):
        #return self._attributes['RDB$SYSTEM_FLAG'] > 0
    def getDomain(self):
        """Return :class:`Domain` object for this parameter."""
        return self.db.getDomain(self.field)
    
class Procedure(BaseDBObject):
    """Represents stored procedure.
    """
    def __init__(self,db,attributes):
        super(Procedure,self).__init__(db,attributes)
        self._typeCode = [5,]

        self.__inputParams = self.__outputParams = None
        
        self._stripAttribute('RDB$PROCEDURE_NAME')
        self._stripAttribute('RDB$OWNER_NAME')

    #--- Protected

    def _get_name(self):
        return self._attributes['RDB$PROCEDURE_NAME']
    def _get_procedure_name(self):
        return self._attributes['RDB$PROCEDURE_NAME']
    def _get_id(self):
        return self._attributes['RDB$PROCEDURE_NAME']
    def _get_source(self):
        return self._attributes['RDB$PROCEDURE_SOURCE']
    def _get_security_class(self):
        return self._attributes['RDB$SECURITY_CLASS']
    def _get_owner_name(self):
        return self._attributes['RDB$OWNER_NAME']
    def _set_description(self,desc):
        self._attributes['RDB$DESCRIPTION'] = desc
        self.db._execute("""update RDB$PROCEDURES set RDB$DESCRIPTION = ? 
where RDB$PROCEDURE_NAME = ?""",(desc,self.procedure_name))
        self._notifyObservers()
    def _get_input_params(self):
        if self._attributes['RDB$PROCEDURE_INPUTS'] and not self.__inputParams:
            self.__inputParams = [ProcParameter(self.db,self,row) for row in 
                self.db._select("select * from rdb$procedure_parameters where rdb$procedure_name = ? and rdb$parameter_type = 0 order by rdb$parameter_number",(self.procedure_name,))]
            self.db._commit()
        return self.__inputParams
    def _get_output_params(self):
        if self._attributes['RDB$PROCEDURE_OUTPUTS'] and not self.__outputParams:
            self.__outputParams = [ProcParameter(self.db,self,row) for row in 
                self.db._select("select * from rdb$procedure_parameters where rdb$procedure_name = ? and rdb$parameter_type = 1 order by rdb$parameter_number",(self.procedure_name,))]
            self.db._commit()
        return self.__outputParams

    #--- Properties

    procedure_name  = LateBindingProperty(_get_procedure_name,None,None,"Name of the stored procedure.")
    id              = LateBindingProperty(_get_id,None,None,"Internal unique ID number.")
    source          = LateBindingProperty(_get_source,None,None,"PSQL source code.")
    security_class  = LateBindingProperty(_get_security_class,None,None,"Security class that define access limits to the procedure.")
    owner_name      = LateBindingProperty(_get_owner_name,None,None,"User name of procedure's creator.")

    input_params    = LateBindingProperty(_get_input_params,None,None,"List of procedure input parameters.\nInstances are ProcParameter instances.")
    output_params   = LateBindingProperty(_get_output_params,None,None,"List of procedure output parameters.\nInstances are ProcParameter instances.")


    #--- Public
    
    def acceptVisitor(self,visitor):
        visitor.visitProcedure(self)

class Role(BaseDBObject):
    """Represents user role.
    """
    def __init__(self,db,attributes):
        super(Role,self).__init__(db,attributes)
        self._typeCode = [13,]

        self._stripAttribute('RDB$ROLE_NAME')
        self._stripAttribute('RDB$OWNER_NAME')

    #--- Protected

    def _get_name(self):
        return self._attributes['RDB$ROLE_NAME']
    def _get_role_name(self):
        return self._attributes['RDB$ROLE_NAME']
    def _get_owner_name(self):
        return self._attributes['RDB$OWNER_NAME']

    #--- Properties

    role_name  = LateBindingProperty(_get_role_name,None,None,"Role name.")
    owner_name = LateBindingProperty(_get_owner_name,None,None,"User name of role owner.")

    #--- Public
    
    def acceptVisitor(self,visitor):
        visitor.visitRole(self)
    def isSystemObject(self):
        """Return True if this database object is system object.
        """
        return False

class FunctionArgument(BaseDBObject):
    """Represets UDF argument.
    """
    def __init__(self,db,function,attributes):
        super(FunctionArgument,self).__init__(db,attributes)
        self._typeCode = [15,]
        self.function = function

        self._stripAttribute('RDB$FUNCTION_NAME')

    #--- Protected

    def _get_name(self):
        return self._attributes['RDB$FUNCTION_NAME']+'_'+str(self._get_position())
    def _get_function_name(self):
        return self._attributes['RDB$FUNCTION_NAME']
    def _get_position(self):
        return self._attributes['RDB$ARGUMENT_POSITION']
    def _get_mechanism(self):
        return self._attributes['RDB$MECHANISM']
    def _get_length(self):
        return self._attributes['RDB$FIELD_LENGTH']
    def _get_scale(self):
        return self._attributes['RDB$FIELD_SCALE']
    def _get_field_type(self):
        return self._attributes['RDB$FIELD_TYPE']
    def _get_sub_type(self):
        return self._attributes['RDB$FIELD_SUB_TYPE']
    def _get_character_length(self):
        return self._attributes['RDB$CHARACTER_LENGTH']
    def _get_character_set_id(self):
        return self._attributes['RDB$CHARACTER_SET_ID']
    def _get_precision(self):
        return self._attributes['RDB$FIELD_PRECISION']
    def _get_datatype(self):
        l = []
        precision_known = False
        if self.field_type in (FBT_SMALLINT,FBT_INTEGER,FBT_BIGINT):
            if self.precision != None:
                if (self.sub_type > 0) and (self.sub_type < MAX_INTSUBTYPES):
                    l.append('%s(%d, %d)' % \
                      (integral_subtypes[self.sub_type],self.precision,-self.scale))
                    precision_known = True
        if not precision_known:
            if (self.field_type == FBT_SMALLINT) and (self.scale < 0):
                l.append('NUMERIC(4, %d)' % -self.scale)
            elif (self.field_type == FBT_INTEGER) and (self.scale < 0):
                l.append('NUMERIC(9, %d)' % -self.scale)
            elif (self.field_type == FBT_DOUBLE_PRECISION) and (self.scale < 0):
                l.append('NUMERIC(15, %d)' % -self.scale)
            else:
                l.append(column_types[self.field_type])
        if self.field_type in (FBT_CHAR,FBT_VARCHAR,FBT_CSTRING):
            l.append('(%d)' % iif(self.character_length is None,self.length,self.character_length))
        if self.field_type == FBT_BLOB:
            if self.sub_type >= 0 and self.sub_type <= MAX_BLOBSUBTYPES:
                l.append(' subtype %s' %blob_sub_types[self.sub_type])
            else:
                l.append(' subtype %d' % self.sub_type)
        if self.field_type in (FBT_CHAR,FBT_VARCHAR,FBT_CSTRING,FBT_BLOB) \
           and self.character_set_id is not None:
            l.append(' CHARACTER SET %s' % self.db.getCharacterSetById(self.character_set_id).name)
        return ''.join(l)

    #--- Properties

    function_name    = LateBindingProperty(_get_function_name,None,None,"Function name.")
    position         = LateBindingProperty(_get_position,None,None,"Argument position.")
    mechanism        = LateBindingProperty(_get_mechanism,None,None,"How argument is passed.")
    field_type       = LateBindingProperty(_get_field_type,None,None,"Number code of the data type defined for the argument.")
    length           = LateBindingProperty(_get_length,None,None,"Length of the column in bytes.")
    scale            = LateBindingProperty(_get_scale,None,None,"Negative number representing the scale of NUMBER and DECIMAL argument.")
    precision        = LateBindingProperty(_get_precision,None,None,"Indicates the number of digits of precision available to the data type of the column.")
    sub_type         = LateBindingProperty(_get_sub_type,None,None,"BLOB subtype.")
    character_length = LateBindingProperty(_get_character_length,None,None,"Length of CHAR and VARCHAR column, in characters (not bytes).")
    character_set_id = LateBindingProperty(_get_character_set_id,None,None,"Number ID of the character set for a character or text BLOB column.")
    datatype         = LateBindingProperty(_get_datatype,None,None,"Comlete SQL datatype definition.")

    #--- Public
    
    def acceptVisitor(self,visitor):
        visitor.visitFunctionArgument(self)


class Function(BaseDBObject):
    """Represents user defined function.
    """
    def __init__(self,db,attributes):
        super(Function,self).__init__(db,attributes)
        self._typeCode = [15,]
        self.__arguments = None

        self._stripAttribute('RDB$FUNCTION_NAME')
        self._stripAttribute('RDB$MODULE_NAME')
        self._stripAttribute('RDB$RETURN_ARGUMENT')

    #--- Protected

    def _get_name(self):
        return self._attributes['RDB$FUNCTION_NAME']
    def _get_function_name(self):
        return self._attributes['RDB$FUNCTION_NAME']
    def _get_module_name(self):
        return self._attributes['RDB$MODULE_NAME']
    def _get_entrypoint(self):
        return self._attributes['RDB$ENTRYPOINT']
    def _get_return_argument(self):
        return self._attributes['RDB$RETURN_ARGUMENT']
    def _get_arguments(self):
        if not self.__arguments:
            self.__arguments = [FunctionArgument(self.db,self,row) for row in 
                                self.db._select("select * from rdb$function_arguments where rdb$function_name = ? order by rdb$argument_position",(self.function_name,))]
            self.db.commit()
        return self.__arguments

    #--- Properties

    function_name   = LateBindingProperty(_get_function_name,None,None,"Function name.")
    module_name     = LateBindingProperty(_get_module_name,None,None,"Module name.")
    entrypoint      = LateBindingProperty(_get_entrypoint,None,None,"Entrypoint in module.")
    return_argument = LateBindingProperty(_get_return_argument,None,None,"Ordinal position of return argument in parameter list.")
    arguments       = LateBindingProperty(_get_arguments,None,None,"List of function arguments.")

    #--- Public
    
    def acceptVisitor(self,visitor):
        visitor.visitFunction(self)

class DbFile(BaseDBObject):
    """Represents database extension or shadow file.
    """
    FILE_SHADOW = 1
    FILE_INACTIVE = 2
    FILE_MANUAL = 4
    FILE_CONDITIONAL = 16
    
    def __init__(self,db,attributes):
        super(DbFile,self).__init__(db,attributes)
        self._typeCode = []

        self._stripAttribute('RDB$FILE_NAME')
        self._name = os.path.basename(self.file_name)

    #--- Protected

    def _get_name(self):
        return self._name
    def _get_file_name(self):
        return self._attributes['RDB$FILE_NAME']
    def _get_sequence(self):
        return self._attributes['RDB$FILE_SEQUENCE']
    def _get_start(self):
        return self._attributes['RDB$FILE_START']
    def _get_length(self):
        return self._attributes['RDB$FILE_LENGTH']
    def _get_shadow_number(self):
        return self._attributes['RDB$SHADOW_NUMBER']
    def _get_flags(self):
        return self._attributes['RDB$FILE_FLAGS']

    #--- Properties

    file_name     = LateBindingProperty(_get_file_name,None,None,"File name.")
    sequence      = LateBindingProperty(_get_sequence,None,None,"File sequence number.")
    start         = LateBindingProperty(_get_start,None,None,"File start page number.")
    length        = LateBindingProperty(_get_length,None,None,"File length in pages.")
    shadow_number = LateBindingProperty(_get_shadow_number,None,None,"Shadow file number.")
    flags         = LateBindingProperty(_get_flags,None,None,"File flags.")

    #--- Public
    
    def acceptVisitor(self,visitor):
        visitor.visitDbFile(self)
    def isShadow(self):
        """Return True if this file represents SHADOW.
        """
        return iif(self.flags & self.FILE_SHADOW,True,False)
    def isManual(self):
        """Return True if it's MANUAL shadow file.
        """
        return iif(self.flags & self.FILE_MANUAL,True,False)
    def isInactive(self):
        """Return True if it's INACTIVE shadow file.
        """
        return iif(self.flags & self.FILE_INACTIVE,True,False)
    def isConditional(self):
        """Return True if it's CONDITIONAL shadow file.
        """
        return iif(self.flags & self.FILE_CONDITIONAL,True,False)

