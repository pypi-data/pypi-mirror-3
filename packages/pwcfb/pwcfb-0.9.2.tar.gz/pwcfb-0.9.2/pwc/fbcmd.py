#
#   PROGRAM:     Power Console
#   MODULE:      stdcmd.py
#   DESCRIPTION: Standard built-in commands
#
#  The contents of this file are subject to the Initial
#  Developer's Public License Version 1.0 (the "License");
#  you may not use this file except in compliance with the
#  License. You may obtain a copy of the License at
#  http://www.firebirdsql.org/index.php?op=doc&id=idpl
#
#  Software distributed under the License is distributed AS IS,
#  WITHOUT WARRANTY OF ANY KIND, either express or implied.
#  See the License for the specific language governing rights
#  and limitations under the License.
#
#  The Original Code was created by Pavel Cisar
#
#  Copyright (c) 2006 Pavel Cisar <pcisar@users.sourceforge.net>
#  and all contributors signed below.
#
#  All Rights Reserved.
#  Contributor(s): ______________________________________.

#---Classes---#000000#FFFFFF---------------------------------------------------

import pkg_resources
from pyparsing import *
from pwc.base import *
from pwc.stdcmd import ShowExtender
from inspect import getdoc, currentframe
import os.path
import sys
import types
import fbcore as fb
import fdb as kdb
#import kinterbasdb as kdb
#if not kdb.initialized:
    #kdb.init(type_conv=200)
from Itpl import itplns
from pprint import pformat
from operator import attrgetter

BLOBID       = (Word(hexnums) + ':' + 
                Word(hexnums)).setName('blobid')
DBIDENT      = (Word(alphas,alphanums+'_$').setParseAction(
                upcaseTokens) | 
                QuotedString('"',escQuote='"',unquoteResults=False)).setName('dbident')
DBIDENT.exprs[0].errmsg = 'Database object name expected'
SQLCOMMENT   = QuotedString('/*', multiline=True, endQuoteChar='*/')

class fbObjectRenderer(object):
    udf_param_types = ['BY VALUE','','BY DESCRIPTOR','',
                       'BY SCALAR_ARRAY','NULL','ERROR-type-unknown']
    def __init__(self, display):
        self.display = display
    def visitDatabase(self,db):
        info = db.getDatabaseInfo([kdb.isc_info_page_size,
                                  kdb.isc_info_db_size_in_pages,
                                  kdb.isc_info_sweep_interval,
                                  kdb.isc_info_forced_writes,
                                  kdb.isc_info_oldest_transaction,
                                  kdb.isc_info_oldest_active,
                                  kdb.isc_info_oldest_snapshot,
                                  kdb.isc_info_next_transaction,
                                  #kdb.isc_info_base_level,
                                  #kdb.isc_info_limbo,
                                  kdb.isc_info_ods_version,
                                  kdb.isc_info_ods_minor_version])
        lines = []
        lines.append('Database: %s' % db.dsn)
        lines.append(' Owner: %s, Current user: %s' % (db.owner_name,db.user))
        # Secondary files
        files = [f for f in db.files if not f.isShadow()]
        files.sort(key=attrgetter('sequence'))
        for f in files:
            lines.append(' File %i: %s, length %i, start %i' % 
                         (f.sequence,f.file_name,f.length,f.start))
        # Shadows
        shadows = {}
        for shadow in (f for f in db.files if f.isShadow()):
            shadows.setdefault(shadow.shadow_number,[]).append(shadow)
        sn = shadows.keys()
        sn.sort()
        for si in sn:
            shadow = shadows[si]
            shadow.sort(key=attrgetter('sequence'))
            for f in shadow:
                if f.sequence == 0:
                    lines.append(' Shadow %i: %s%s%s%s' % 
                                 (f.shadow_number,f.file_name,
                                  iif(f.isInactive(),' inactive',''),
                                  iif(f.isManual(),' manual',' auto'),
                                  iif(f.isConditional(),' conditional','')))
                else:
                    lines.append('   File %i: %s%s%s' % 
                                 (f.sequence,f.file_name,
                                  iif(f.length is not None,' length %s' % f.length,''),
                                  iif(f.start is not None,' start %s' % f.start,'')))
        # Other interesting attributes
        lines.append(' Page size = %i' % info[kdb.isc_info_page_size])
        lines.append(' Database pages allocated = %i' % info[kdb.isc_info_db_size_in_pages])
        lines.append(' Sweep interval = %i' % info[kdb.isc_info_sweep_interval])
        lines.append(' Forced writes are %s' % iif(info[kdb.isc_info_forced_writes],'ON','OFF'))
        lines.append(' Transaction - oldest = %i' % info[kdb.isc_info_oldest_transaction])
        lines.append(' Transaction - oldest active = %i' % info[kdb.isc_info_oldest_active])
        lines.append(' Transaction - oldest snapshot = %i' % info[kdb.isc_info_oldest_snapshot])
        lines.append(' Transaction - Next = %i' % info[kdb.isc_info_next_transaction])
        lines.append(' ODS = %i.%i' % (info[kdb.isc_info_ods_version],info[kdb.isc_info_ods_minor_version]))
        lines.append(' Default Character set: %s' % db.default_character_set)
        # Statistics
        lines.append(' Number of tables: %i' % len(db.tables))
        lines.append(' Number of views: %i' % len(db.views))
        lines.append(' Number of domains: %i' % len(db.domains))
        lines.append(' Number of procedures: %i' % len(db.procedures))
        lines.append(' Number of triggers: %i' % len(db.triggers))
        lines.append(' Number of exceptions: %i' % len(db.exceptions))
        lines.append(' Number of generators: %i' % len(db.generators))
        lines.append(' Number of functions: %i' % len(db.functions))
        self.display.writeLines(lines)
    def visitDomain(self,domain):
        lines = []
        lines.append('%-33s %s %s' % (domain.name,domain.datatype,
                                      iif(domain.nullable,'Nullable','Not Null')))
        if domain.computed_source:
            lines.append('%-33s %s' % (' ',domain.computed_source))
        if domain.default_source:
            lines.append('%-33s %s' % (' ',domain.default_source))
        if domain.validation_source:
            lines.append('%-33s %s' % (' ',domain.validation_source))
        self.display.writeLines(lines)
    def visitException(self,exception):
        self.display.write('%-33s %s\n' % (exception.name,exception.message))
    def visitTableColumn(self,column):
        lines = []
        domain = column.getDomain()
        default = iif(column.default_value,column.default_value,
                      domain.default_source)
        lines.append('%-33s %s%s %s %s' % (column.name,
            iif(domain.isSystemObject(),'','('+column.domain_name+') '),
            column.datatype,iif(column.nullable,'Nullable','Not Null'),
            iif(default,default,'')))
        if domain.computed_source:
            lines.append('%-33s Computed by: %s' % (' ',domain.computed_source))
        if domain.validation_source:
            lines.append('%-33s %s' % (' ',domain.validation_source))
        self.display.writeLines(lines)
    def visitTable(self,table):
        lines = []
        # Header
        lines.append('Table %s (%i) owned by %s' % (table.name, table.relation_id, 
                                                    table.owner_name))
        if table.external_file:
            lines.append(' external file: %s' % table.external_file)
        # Columns
        cols = table.columns
        cols.sort(key=attrgetter('position'))
        for column in cols:
            domain = column.getDomain()
            default = iif(column.default_value,column.default_value,
                          domain.default_source)
            lines.append(' %-33s %s%s %s %s' % (column.name,
                iif(column.getDomain().isSystemObject(),'','('+column.domain_name+') '),
                column.datatype,iif(column.nullable,'Nullable','Not Null'),
                iif(default,default,'')))
            if domain.computed_source:
                lines.append(' %-33s Computed by: %s' % (' ',domain.computed_source))
            if domain.validation_source:
                lines.append(' %-33s %s' % (' ',domain.validation_source))
        # Constraints
        constraints = [c for c in table.constraints if not c.isNotNull()]
        if len(constraints) > 0:
            lines.extend(['','Constraints:'])
        for constraint in constraints:
            lines.append('%s %s:' % (constraint.constraint_type,constraint.name))
            params = ''
            if constraint.isPrimaryKey() or constraint.isUnique():
                params = 'Index %s(%s)' % (constraint.index_name,
                    ','.join(constraint.db.getIndex(constraint.index_name).segments))
                lines.append(' %s' % params)
            elif constraint.isForeignKey():
                ref_constraint = constraint.db.getConstraint(constraint.uq_constraint_name)
                ref = 'References %s %s(%s)' % (ref_constraint.relation_name, 
                        ref_constraint.index_name,
                        ','.join(constraint.db.getIndex(ref_constraint.index_name).segments))
                params = 'Index %s(%s)' % (constraint.index_name,
                    ','.join(constraint.db.getIndex(constraint.index_name).segments))
                lines.append(' %s' % params)
                lines.append(' %s' % ref)
            elif constraint.isCheck():
                lines.append(' %s' % constraint.db.getTrigger(constraint.trigger_names[0]).source)
        # Triggers
        if len(table.triggers) > 0:
            lines.extend(['','Triggers:'])
        for trigger in table.triggers:
            lines.append('%s, Sequence: %i, Type: %s, %s' % (trigger.name,
                            trigger.sequence,trigger.getTypeAsString(),
                            iif(trigger.isActive(),'Active','INACTIVE')))
        # Indices
        if len(table.indices) > 0:
            lines.extend(['','Indices:'])
        for index in table.indices:
            if index.isSystemObject():
                if index.foreign_key:
                    system = '(FK)'
                else:
                    system = ''
                system = ' system%s' % system
            else:
                system = None
            if index.expression:
                computed = ' computed by ' + index.expression
            else:
                computed = None
            lines.append('%s%s%s%s index on %s' % 
                         (index.name, iif(index.inactive,' INACTIVE',''), 
                          iif(index.unique,' unique',''),iif(system,system,''),
                          iif (computed,computed,'('+','.join(index.segments)+')')))
        self.display.writeLines(lines)
    def visitIndex(self,index):
        if index.isSystemObject():
            if index.foreign_key:
                system = '(FK)'
            else:
                system = ''
            system = ' system%s' % system
        else:
            system = None
        if index.expression:
            computed = ' computed by ' + index.expression
        else:
            computed = None
        self.display.write('%s%s%s%s index on %s%s\n' % 
                     (index.name, iif(index.inactive,' INACTIVE',''), 
                      iif(index.unique,' unique',''),iif(system,system,''),
                      index.table_name,iif (computed,computed,'('+','.join(index.segments)+')')))
    def visitCollation(self,collation):
        self.display.write('Collation %s (%i), character set %s\n' % 
                           (collation.name,collation.id,collation.getCharacterSet().name))
    def visitCharacterSet(self,character_set):
        lines = []
        lines.append('%s (%i) %i byte(s) per character, default collation %s' % 
                     (character_set.name,character_set.id,character_set.bytes_per_character,character_set.default_collate_name))
        for collation in character_set.collations:
            lines.append('  %s (%i)' % (collation.name,collation.id))
        self.display.writeLines(lines)
    def visitGenerator(self,generator):
        self.display.write('Generator %s, current value is %i\n' % 
                           (generator.name,generator.value))
    def visitConstraint(self,constraint):
        lines = []
        if constraint.isNotNull():
            set_on = '%s(%s)' % (constraint.relation_name,constraint.column_name)
        else:
            set_on = constraint.relation_name
        lines.append('%s %s constraint on %s:' % (constraint.name,
                                                  constraint.constraint_type,set_on))
        params = ''
        if constraint.isPrimaryKey() or constraint.isUnique():
            params = 'Index %s(%s)' % (constraint.index_name,
                ','.join(constraint.db.getIndex(constraint.index_name).segments))
            lines.append(' %s' % params)
        elif constraint.isForeignKey():
            ref_constraint = constraint.db.getConstraint(constraint.uq_constraint_name)
            ref = 'References %s %s(%s)' % (ref_constraint.relation_name, 
                    ref_constraint.index_name,
                    ','.join(constraint.db.getIndex(ref_constraint.index_name).segments))
            params = 'Index %s(%s)' % (constraint.index_name,
                ','.join(constraint.db.getIndex(constraint.index_name).segments))
            lines.append(' %s' % params)
            lines.append(' %s' % ref)
        elif constraint.isCheck():
            lines.append(' %s' % constraint.db.getTrigger(constraint.trigger_names[0]).source)
        self.display.writeLines(lines)
    def visitViewColumn(self,column):
        domain = column.getDomain()
        self.display.writeLine('%-33s %s%s %s' % (column.name,
            iif(domain.isSystemObject(),'','('+column.domain_name+') '),
            column.datatype,iif(column.nullable,'Nullable','Not Null')))
    def visitView(self,view):
        lines = []
        # Header
        lines.append('View %s (%i) owned by %s' % (view.name, view.relation_id, 
                                                    view.owner_name))
        # Columns
        cols = view.columns
        cols.sort(key=attrgetter('position'))
        for column in cols:
            domain = column.getDomain()
            lines.append(' %-33s %s%s %s' % (column.name,
                iif(domain.isSystemObject(),'','('+column.domain_name+') '),
                column.datatype,iif(column.nullable,'Nullable','Not Null')))
        # Triggers
        if len(view.triggers) > 0:
            lines.extend(['','Triggers:'])
        for trigger in view.triggers:
            lines.append('%s, Sequence: %i, Type: %s, %s' % (trigger.name,
                            trigger.sequence,trigger.getTypeAsString(),
                            iif(trigger.isActive(),'Active','INACTIVE')))
        lines.append('View Source:')
        lines.append('============')
        lines.extend(view.source_sql.split('\n'))
        self.display.writeLines(lines)
    def visitTrigger(self,trigger):
        lines = []
        if trigger.isDbTrigger():
            target = ''
        else:
            target = 'on %s, ' % trigger.relation_name
        lines.append('%s trigger %s %s%s, Sequence: %i' % 
                     (iif(trigger.isActive(),'Active','Inactive'),trigger.name,target,
                        trigger.getTypeAsString(),trigger.sequence))
        lines.extend(trigger.source.split('\n'))
        self.display.writeLines(lines)
    def visitProcParameter(self,param):
        self.display.writeLine('%s, procedure %s %s parameter of type %s' % 
                               (param.name,param.procedure_name,
                                iif(param.parameter_type==0,'INPUT','OUTPUT'),
                                param.datatype))
    def visitProcedure(self,procedure):
        self.display.writeLine('Procedure %s, Owner: %s' % (procedure.name,
                                                            procedure.owner_name))
        self.display.writeLine('='*80)
        self.display.writeLines(procedure.source.splitlines())
        self.display.writeLine('='*80)
        if procedure.input_params or procedure.output_params:
            self.display.writeLine('Parameters:')
        if procedure.input_params:
            for param in procedure.input_params:
                self.display.writeLine('%-33s INPUT %s' % (param.name,param.datatype))
        if procedure.output_params:
            for param in procedure.output_params:
                self.display.writeLine('%-33s OUTPUT %s' % (param.name,param.datatype))
    def visitRole(self,role):
        self.display.writeLine('Role %s, owner %s' % (role.name,role.owner_name))
    def visitDependency(self,dependency):
        pass
    def visitFunction(self,function):
        lines = []
        lines.append('Function %s:' % function.name)
        lines.append(' Library: %s' % function.module_name)
        lines.append(' Entrypoint: %s' % function.entrypoint)
        for arg in function.arguments:
            ptype = min(arg.mechanism,len(self.udf_param_types))
            if  arg.position == function.return_argument:
                lines.append(' Returns: %s%s%s' % (iif(arg.mechanism >= 0,self.udf_param_types[ptype]+' ',''),
                                iif(arg.mechanism < 0,'FREE_IT ',''),arg.datatype))
            else:
                lines.append(' Argument %i: %s %s' % (arg.position,
                                self.udf_param_types[ptype],arg.datatype))
        self.display.writeLines(lines)
    def visitFunctionArgument(self,argument):
        lines = []
        ptype = min(argument.mechanism,len(self.udf_param_types))
        if  argument.position == argument.function.return_argument:
            lines.append('Function %s return argument: %s%s%s' % 
                         (argument.function_name,
                          iif(argument.mechanism >= 0,self.udf_param_types[ptype]+' ',''),
                          iif(argument.mechanism < 0,'FREE_IT ',''),argument.datatype))
        else:
            lines.append('Function %s argument %i: %s %s' % 
                         (argument.function_name,
                          argument.position,
                          self.udf_param_types[ptype],argument.datatype))
        self.display.writeLines(lines)
    def handle_list(self,obj):
        self.display.writeLine(pformat(obj))
    def handle_dict(self,obj):
        text = pformat(obj)
        self.display.writeLine(pformat(obj))

class fbController(object):
    """Helper class to exctend controller with Firebird-related specific data.
    
    Holds disctionary of attached databases (key is var name in local context)
    and main database.
    """
    
    autocommit_ddl = True
    print_stats    = False
    echo           = False
    list_format    = False
    row_count      = False
    show_plan      = False
    show_plan_only = False
    headings       = True
    time           = False
    warnings       = True
    sql_dialect    = 3
    charset        = None
    
    def __init__(self, controller):
        self.databases = {}
        self.main_database = None
        self.controller = controller
    def getMainDatabase(self):
        return self.databases.get(self.main_database,None)
    def getDatabase(self,name):
        return self.databases.get(name,None)
    def setDatabase(self,db,name):
        self.main_database = name
        self.databases[name] = db
    def setMainDatabase(self,db):
        self.main_database = db

class helpFirebird(HelpProvider):
    """Help Provider for Firebird PowerConsole commands and other Firebird topics"""

    help_firebird = """TODO: Help for topic Firebird.
    """
    help_sql = """Firebird package for PowerConsole should support all valid DSQL statements and
many ISQL commands as well (see Firebird documentation for details).

However, there are some exceptions and additions:
- SET TRANSACTION does not support table reservation options (yet).
- CREATE DATABASE and CONNECT support addtional optional argument (must be last one):
AS <var> that makes the Database object accessible under specified name instead
default alias "db".
"""

class cmdConnect(Command):
    def __init__(self, controller):
        super(cmdConnect,self).__init__(controller)
        controller._fbc = fbController(controller)
        
        self.keyConnect     = self._makeNameNode(CaselessKeyword('connect'))
        # we don't need to keep next tokens as instance attributes
        keyUser     = CaselessKeyword('user')
        keyPassword = CaselessKeyword('password')
        keyCache    = CaselessKeyword('cache')
        keyRole     = CaselessKeyword('role')
        keyAs       = CaselessKeyword('as')
        keyHost     = CaselessKeyword('host')
        optUser     = keyUser + QuotedString("'").setResultsName('user').setFailAction(self._fail)
        optPassword = keyPassword + QuotedString("'").setResultsName('password').setFailAction(self._fail)
        optCache    = keyCache + self.INTEGER.setResultsName('cache').setFailAction(self._fail)
        optRole     = keyRole + QuotedString("'").setResultsName('role').setFailAction(self._fail)
        optAs       = keyAs + self.IDENT.setResultsName('intoVar').setFailAction(self._fail)
        optHost     = keyHost + self.IDENT.setResultsName('host').setFailAction(self._fail)

        # CONNECT 'dsn' [USER 'user'][PASSWORD 'password']
        #  [CACHE int ][ROLE 'role'][AS var]
        self.cmdConnect  = self.keyConnect \
            + QuotedString("'").setName('filename').setResultsName('db') \
            + Optional(optHost) + Optional(optUser) + Optional(optPassword) \
            + Optional(optCache) + Optional(optRole) + Optional(optAs) \
            + Optional(';')
        self.cmdConnect.setParseAction(self._compile)

    def _getGrammar(self):
        return self.cmdConnect
    def _getCmdKeyword(self):
        return self.keyConnect
    def execute(self,db,**kwargs):
        """Attach to the Firebird database.

        usage: 
        CONNECT 'dsn or db' [HOST host][USER 'user'][PASSWORD 'password']
          [CACHE int ][ROLE 'role'][AS var][;]

        If connection is sucessfuly established, this database connection is set
        as main working database. Database object is stored and accessible under
        default alias "db" or as alias specified by optional AS argument. If
        alias name is already used for other attached database, this database is
        disconnected.
"""
        fbc = self.controller._fbc
        name = kwargs.get('intoVar','db')
        user = kwargs.get('user','sysdba')
        if kwargs.has_key('host'):
            kwargs['database'] = db
        else:
            kwargs['dsn'] = db
        kwargs['dialect'] = fbc.sql_dialect
        if fbc.charset:
            kwargs['charset'] = fbc.charset
        try:
            d = fb.Database(**kwargs)
            db = fbc.getDatabase(name)
            if db:
                db.close()
            self.controller._fbc.setDatabase(d, name)
            self.controller.locals[name] = d
            self.controller.write('Database %s as %s, user %s\n' % (d.dsn, name, user))
        except kdb.OperationalError, e:
            self.controller.writeErr("Error: %s" % str(e[0]))
            self.controller.writeErr(str(e[1]))

class cmdDisconnect(Command):
    def __init__(self, controller):
        super(cmdDisconnect,self).__init__(controller)
        self.keyDisconnect = self._makeNameNode(CaselessKeyword('disconnect'))
        # READY [<dbvar>]
        self.cmdDisconnect = self.keyDisconnect + Optional(self.ARG.setResultsName('arg'))
        self.cmdDisconnect.setParseAction(self._compile)

    def _getGrammar(self):
        return self.cmdDisconnect
    def _getCmdKeyword(self):
        return self.keyDisconnect
    def execute(self,arg=None):
        """Disconnects from attached Firebird database.

        usage: 
        DISCONNECT [dbvar]
        
        Without argument, it will disconnect from current working database.
        If argument is specified, it must be a name of previously connected
        database (implicit name 'db' or name specified by AS argument) that
        should be disconnected.
"""
        fbc = self.controller._fbc
        if arg:
            dbvar = arg
        else:
            dbvar = fbc.main_database
        db = fbc.getDatabase(dbvar)
        if not db:
            self.writeErr("Unknown database '%s'\n" % dbvar)
            return

        db.close()
        self.controller.write('Database %s disconnected.\n' % dbvar)
        del fbc.databases[dbvar]
        if fbc.main_database == dbvar:
            if len(fbc.databases.keys()) == 0:
                fbc.main_database = None
                self.controller.write('No other databases attached.\n')
            else:
                fbc.setMainDatabase(fbc.databases.keys()[0])
                db = fbc.getMainDatabase()
                self.controller.write('Switching main database to %s as %s, user %s\n' % 
                                      (db.dsn, fbc.main_database, db.user))

class cmdReady(Command):
    def __init__(self, controller):
        super(cmdReady,self).__init__(controller)
        self.keyReady = self._makeNameNode(CaselessKeyword('ready'))
        # READY [<dbvar>]
        self.cmdReady = self.keyReady + Optional(self.ARG.setResultsName('arg'))
        self.cmdReady.setParseAction(self._compile)

    def _getGrammar(self):
        return self.cmdReady
    def _getCmdKeyword(self):
        return self.keyReady
    def execute(self,arg=None):
        """Show list of attached Firebird databases or select the working database.

        usage: 
        READY [dbvar]
        
        Without argument, it will list all attached databases.
        If argument is specified, it must be a name of previously connected
        database (implicit name 'db' or name specified by AS argument).
"""
        fbc = self.controller._fbc
        if arg:
            if arg in fbc.databases:
                fbc.setMainDatabase(arg)
                self.write("Main database set to %s\n" % arg)
            else:
                self.writeErr("Unknown database '%s'\n" % arg)
        else:
            if len(fbc.databases) > 0:
                self.write('Attached databases:\n')
                for k,v in fbc.databases.items():
                    self.write("Database %s is %s, user %s\n" % (k,v.dsn,v.user))
                db = fbc.main_database
                self.write()
                if not db:
                    self.write("Main database was not specified.\n")
                else:
                    self.write('Main database is %s\n' % db)
            else:
                self.write("No Firebird database attached.\n")

class showDatabase(ShowExtender):
    
    def __init__(self,controller):
        super(showDatabase,self).__init__(controller)
        
        self.keyDatabase   = self._makeNameNode(Empty()) + \
            (CaselessKeyword('database') | CaselessKeyword('db'))
        self.cmdShow = (self.keyDatabase + 
                        Optional(self.IDENT.setResultsName('dbvar')) + 
                        Optional(';'))

    def _getGrammar(self):
        return self.cmdShow
    def _getCmdKeyword(self):
        return self.keyDatabase
    def execute(self,dbvar=None):
        """DATABASE [<dbvar>]
    Detail about current or specified attached database.
        """
        fbc = self.controller._fbc
        if dbvar:
            db = fbc.getDatabase(dbvar)
        else:
            db = fbc.getMainDatabase()
            dbvar = fbc.main_database
        if not db:
            self.writeErr('No database attached.\n')
            return
        return db

class showDbObjects(ShowExtender):
    def __init__(self,controller):
        super(showDbObjects,self).__init__(controller)
        
        cmdNameNode = self._makeNameNode(Empty())
        keySystem = Optional(CaselessKeyword('system').setResultsName('system').setParseAction(self._tokenTotrue))
        optInDB   = Optional(CaselessKeyword('in')+
                             self.IDENT.setResultsName('dbvar').setFailAction(self._fail))

        optTables = (keySystem+CaselessKeyword('tables').setResultsName('category'))
        optTable  = CaselessKeyword('table').setResultsName('category')+ \
                  DBIDENT.setResultsName('name').setFailAction(self._fail)
        keyTables = optTables | optTable
        
        optIndices = (keySystem+CaselessKeyword('indices').setResultsName('category'))
        optIndex  = CaselessKeyword('index').setResultsName('category')+ \
                  DBIDENT.setResultsName('name').setFailAction(self._fail)
        keyIndices = optIndices | optIndex
        
        optDomains = (keySystem+CaselessKeyword('domains').setResultsName('category'))
        optDomain  = CaselessKeyword('domain').setResultsName('category')+ \
                  DBIDENT.setResultsName('name').setFailAction(self._fail)
        keyDomains = optDomains | optDomain
        
        optExceptions = CaselessKeyword('exceptions').setResultsName('category')
        optException  = CaselessKeyword('exception').setResultsName('category')+ \
                  DBIDENT.setResultsName('name').setFailAction(self._fail)
        keyExceptions = optExceptions | optException
        
        optGenerators = (keySystem+CaselessKeyword('generators').setResultsName('category'))
        optGenerator  = CaselessKeyword('generator').setResultsName('category')+ \
                  DBIDENT.setResultsName('name').setFailAction(self._fail)
        keyGenerators = optGenerators | optGenerator
        
        optFunctions = (keySystem+CaselessKeyword('functions').setResultsName('category'))
        optFunction  = CaselessKeyword('function').setResultsName('category')+ \
                  DBIDENT.setResultsName('name').setFailAction(self._fail)
        keyFunctions = optFunctions | optFunction
        
        optProcedures = (keySystem+CaselessKeyword('procedures').setResultsName('category'))
        optProcedure  = CaselessKeyword('procedure').setResultsName('category')+ \
                  DBIDENT.setResultsName('name').setFailAction(self._fail)
        keyProcedures = optProcedures | optProcedure
        
        optTriggers = (keySystem+CaselessKeyword('triggers').setResultsName('category'))
        optTrigger  = CaselessKeyword('trigger').setResultsName('category')+ \
                  DBIDENT.setResultsName('name').setFailAction(self._fail)
        keyTriggers = optTriggers | optTrigger
        
        optViews = (keySystem+CaselessKeyword('views').setResultsName('category'))
        optView  = CaselessKeyword('view').setResultsName('category')+ \
                  DBIDENT.setResultsName('name').setFailAction(self._fail)
        keyViews = optViews | optView
        
        optCharsets = CaselessKeyword('character').setResultsName('category').setParseAction(replaceWith('character_sets')) + \
                      CaselessKeyword('sets')
        optCharset  = CaselessKeyword('character').setResultsName('category').setParseAction(replaceWith('_CharacterSet')) + \
                  CaselessKeyword('set') + \
                  DBIDENT.setResultsName('name').setFailAction(self._fail)
        keyCharsets = optCharsets | optCharset
        
        optCollations = CaselessKeyword('collations').setResultsName('category')
        optCollation  = CaselessKeyword('collation').setResultsName('category')+ \
                  DBIDENT.setResultsName('name').setFailAction(self._fail)
        keyCollations = optCollations | optCollation
        
        optRoles = CaselessKeyword('roles').setResultsName('category')
        optRole  = CaselessKeyword('role').setResultsName('category')+ \
                  DBIDENT.setResultsName('name').setFailAction(self._fail)
        keyRoles = optRoles | optRole
        
        optFunctions = CaselessKeyword('functions').setResultsName('category')
        optFunction  = CaselessKeyword('function').setResultsName('category')+ \
                  DBIDENT.setResultsName('name').setFailAction(self._fail)
        keyFunctions = optFunctions | optFunction
        
        optAll = (keyTables | keyIndices | keyDomains | keyExceptions | 
                  keyGenerators | keyFunctions |keyProcedures | keyTriggers | 
                  keyViews | keyCharsets | keyCollations | keyRoles | keyFunctions)
        
        self.keyShow = cmdNameNode + optAll
        self.cmdShow = cmdNameNode + optAll + optInDB + Optional(';')

    def _getGrammar(self):
        return self.cmdShow
    def _getCmdKeyword(self):
        return self.keyShow
    def _write(self,obj):
        if isinstance(obj,(fb.Database,fb.BaseDBObject)):
            display = self.controller.ui_provider.getDisplay('fdb.show.object',UI_OBJECT)
            display.writeObject(obj)
        elif obj and isiterable(obj):
            l = [x.name for x in obj if hasattr(x,'name')]
            l.sort()
            if hasattr(obj[0],'_get_show_header'):
                l.insert(0,obj[0]._get_show_header())
            display = self.controller.ui_provider.getDisplay('fdb.show.list',UI_LIST)
            display.writeList(l)
        else:
            self.writeErr("No database object to print.\n")
    def execute(self,category,name=None,dbvar=None,system=False):
        """[SYSTEM] TABLES | TABLE <dbident> [IN <dbvar>]
[SYSTEM] INDICES | INDEX <dbident> [IN <dbvar>]
[SYSTEM] DOMAINS | DOMAIN <dbident> [IN <dbvar>]
[SYSTEM] PROCEDURES | PROCEDURE <dbident> [IN <dbvar>]
[SYSTEM] TRIGGERS | TRIGGER <dbident> [IN <dbvar>]
[SYSTEM] VIEWS | VIEW <dbident> [IN <dbvar>]
[SYSTEM] GENERATORS | GENERATOR <dbident> [IN <dbvar>]
[SYSTEM] FUNCTIONS | FUNCTION <dbident> [IN <dbvar>]
EXCEPTIONS | EXCEPTION <dbident> [IN <dbvar>]
CHARACTER SETS | CHARACTER SET <dbident> [IN <dbvar>]
COLLATIONS | COLLATION <dbident> [IN <dbvar>]
ROLES | ROLE <dbident> [IN <dbvar>]

    List of object names or object details in current or specified attached database.
        """
        if dbvar:
            db = self.controller._fbc.getDatabase(dbvar)
        else:
            db = self.controller._fbc.getMainDatabase()
        if not db:
            self.writeErr('No database attached.\n')
            return
        # WARNING: This implementation is compact and elegant, but depends
        # on direct mapping of grammar keyword (category) to attribute names
        # on fbcore.Database, so it may break when you change the grammar
        # or names of these attributes
        if category.startswith('_'):
            category = category[1:]
        else:
            if name == None:
                category = category.lower()
            else:
                category = category.title()
        if name == None:
            if system:
                obj = getattr(db,'sys' + category,None)
            else:
                obj = getattr(db,category,None)
        else:
            obj = getattr(db,'get' + category,None)(name)
        self._write(obj)

class cmdSQL(Command):
    """Executes SQL command on working database"""

    usesTerminator = True
    SQL_PARAM_SEPARATOR   = '<<'
    SQL_STORE_SEPARATOR   = '>>'
    
    def __init__(self,controller):
        super(cmdSQL,self).__init__(controller)

        self.cursor = None
        self.uncommitted_ddl = False

        # Grammar for PowerConsole

        FILENAME     = QuotedString("'",unquoteResults=False).setName('filename')
        # SQL commands
        keyCommit   = CaselessKeyword('commit')
        keyRollback = CaselessKeyword('rollback')
        keyAlter    = CaselessKeyword('alter')
        keyCreate   = CaselessKeyword('create')
        keyDelete   = CaselessKeyword('delete')
        keyDrop     = CaselessKeyword('drop')
        keyExecute  = CaselessKeyword('execute')
        keyGrant    = CaselessKeyword('grant')
        keyInsert   = CaselessKeyword('insert')
        keyRecreate = CaselessKeyword('recreate')
        keyRelease  = CaselessKeyword('release')
        keyRevoke   = CaselessKeyword('revoke')
        keySavepoint= CaselessKeyword('savepoint')
        keySelect   = CaselessKeyword('select')
        keyUpdate   = CaselessKeyword('update')
        keySet      = CaselessKeyword('set')
        keyWork     = CaselessKeyword('work')

        # Second level keywords
        keyGenerator   = CaselessKeyword('generator')
        keyStatistics  = CaselessKeyword('statistics')
        keyTransaction = CaselessKeyword('transaction')
        
        # Composite SQL commands
        cmdSetGen      = Combine(keySet + White() + keyGenerator)
        cmdSetStat     = Combine(keySet + White() + keyStatistics)
        cmdTransaction = Combine(keySet + White() + keyTransaction)

        # Grammar trick to sink all SQL commands into this class
        self.keySQL   = self._makeNameNode(Empty()) 

        self.cmdAll  = (keySelect | keyCommit | keyRollback | keyAlter | keyCreate | 
                        keyDelete | keyDrop | keyExecute | keyGrant | keyInsert |
                        keyRecreate | keyRelease | keyRevoke | keySavepoint | 
                        keyUpdate ^ cmdSetGen ^ cmdSetStat ^ cmdTransaction
            )

        # Multiline SQL command
        CHUNK = CharsNotIn('\n')
        SQL = OneOrMore(CHUNK + (
                        (Optional(OneOrMore(lineEnd.setParseAction(replaceWith('\\n')))) +
                        FollowedBy(CHUNK)) ^
                        Optional(lineEnd.suppress())
                        )
            )
        
        self.cmdSQL  = self.keySQL + \
            Combine(self.cmdAll + Optional(SQL)).setResultsName('sql')
        self.cmdSQL.setParseAction(self._compile)
        
        # Internally used grammars

        # CREATE DATABASE | SCHEMA 'dsn' [HOST host][USER 'user'][PASSWORD 'password']
        #  [PAGE_SIZE [=] int] [LENGTH [=] int [PAGE[S]]]
        #  [DEFAULT CHARACTER SET charset]
        #  <secondary-file>
        #  [AS var]
        #
        # <secondary-file> = FILE 'filename' 
        #   [LENGTH [=] int [PAGE[S]] | STARING [AT [PAGE]] int ]
        keyUser     = CaselessKeyword('user')
        keyPassword = CaselessKeyword('password')
        keyAs       = CaselessKeyword('as')
        keyHost     = CaselessKeyword('host')
        keyPagesize = CaselessKeyword('page_size')
        keyLength   = CaselessKeyword('length')
        keyStarting = CaselessKeyword('starting')
        keyPage     = CaselessKeyword('page')
        keyPages    = CaselessKeyword('pages')
        keyDatabase = CaselessKeyword('database')
        keyFile     = CaselessKeyword('file')
        keyCharset  = Combine(CaselessKeyword('default')+White()+
                              CaselessKeyword('character')+White()+
                              CaselessKeyword('set'))
        optUser     = keyUser + QuotedString("'").setResultsName('user').setFailAction(self._fail)
        optPassword = keyPassword + QuotedString("'").setResultsName('password').setFailAction(self._fail)
        optAs       = keyAs + self.IDENT.setResultsName('intoVar').setFailAction(self._fail)
        optHost     = keyHost + self.IDENT.setResultsName('host').setFailAction(self._fail)
        
        optFileLength = (keyLength+Optional('=')+self.INTEGER.setFailAction(self._fail)
                         +Optional(keyPages|keyPage))
        optFileStart  = (keyStarting+Optional(CaselessKeyword('at')
                                              +Optional(keyPage))
                         +self.INTEGER.setFailAction(self._fail))
        optFileSpec   = keyFile+FILENAME.setFailAction(self._fail)+ \
                        Optional(optFileLength | optFileStart)
        optDbFiles    = ZeroOrMore(optFileSpec)
        self.keyCreateDatabase = Combine(CaselessKeyword('create') + White() + 
                    (keyDatabase | CaselessKeyword('schema')))

        self.CreateDatabase  = self.keyCreateDatabase \
            + FILENAME.copy().setParseAction(removeQuotes).setResultsName('db') \
            + Optional(optHost) + Optional(optUser) + Optional(optPassword) \
            + Optional(keyPagesize+Optional('=')+self.INTEGER.setResultsName('page_size').setFailAction(self._fail)) \
            + Optional(keyLength+Optional('=')+self.INTEGER.setResultsName('length').setFailAction(self._fail)+
                       Optional(keyPages|keyPage)) \
            + Optional(keyCharset+DBIDENT.setResultsName('character_set'))  \
            + Combine(optDbFiles,joinString=' ',adjacent=False).setResultsName('files') \
            + Optional(optAs)

        # DROP DATABASE
        self.DropDatabase = Combine(keyDrop + White() + keyDatabase) \
            + Optional(self.IDENT.setResultsName('inVar'))
        
        # SAVEPOINT-related commands
        SAVEPOINT_NAME = (Word(alphas,alphanums+'_$').setParseAction(upcaseTokens) | 
                          QuotedString('"',escQuote='"',unquoteResults=False)).setName('savepoint').setResultsName('savepoint')
        SAVEPOINT_NAME.exprs[0].errmsg = 'Savepoint name expected'
        
        self.SavepointFamily = (
            (keySavepoint.setResultsName('category') + SAVEPOINT_NAME.setFailAction(self._fail)) |
            (keyRelease.setResultsName('category') + keySavepoint + SAVEPOINT_NAME.setFailAction(self._fail) +
            Optional(CaselessKeyword('only')).setResultsName('only').setParseAction(self._tokenTotrue)) | 
            (keyRollback.setResultsName('category') + Optional(keyWork) + CaselessKeyword('to') +
             Optional(keySavepoint) + SAVEPOINT_NAME.setFailAction(self._fail))
        )
        
        # SEt TRANSACTION
        keyRead          = CaselessKeyword('read')
        keyWrite         = CaselessKeyword('write')
        keyWait          = CaselessKeyword('wait')
        keyNo            = CaselessKeyword('no')
        keyOnly          = CaselessKeyword('only')
        keyIsolation     = CaselessKeyword('isolation')
        keyLevel         = CaselessKeyword('level')
        keySnapshot      = CaselessKeyword('snapshot')
        keyTable         = CaselessKeyword('table')
        keyStability     = CaselessKeyword('stability')
        keyCommitted     = CaselessKeyword('committed')
        keyRecordVersion = CaselessKeyword('record_version')
        keyReserving     = CaselessKeyword('reserving')
        keyFor           = CaselessKeyword('for')
        keyShared        = CaselessKeyword('shared')
        keyProtected     = CaselessKeyword('protected')
        
        keyNoVersion      = Combine(keyNo+White()+keyRecordVersion)
        keyReadWrite      = Combine(keyRead+White()+keyWrite)
        keyReadOnly       = Combine(keyRead+White()+keyOnly)
        keyNoWait         = Combine(keyNo+White()+keyWait)
        keyIsolationLevel = Combine(keyIsolation+White()+keyLevel)
        keyTableStability = Combine(keyTable+White()+keyStability)
        keyStableSnapshot = Combine(keySnapshot+White()+keyTableStability)
        keyReadCommitted  = Combine(keyRead+White()+keyCommitted)
        
        optTable  = DBIDENT
        
        self.SetTransaction = (cmdTransaction + 
            Optional(keyReadWrite | keyReadOnly.setResultsName('read_only').setParseAction(self._tokenTotrue)) + 
            Optional(keyWait | keyNoWait.setResultsName('nowait').setParseAction(self._tokenTotrue)) +
            Optional(Optional(keyIsolationLevel)+
                     (keyStableSnapshot | 
                      keySnapshot | 
                      (keyReadCommitted +
                       Optional(keyNoVersion | 
                                keyRecordVersion.setResultsName('versions').setParseAction(self._tokenTotrue)))).setResultsName('isolation'))
            )

    def __norm(self,str):
        if isinstance(str,types.StringTypes):
            str = str.strip()
            if str == '':
                return None
            else:
                return str

    def _getGrammar(self):
        return self.cmdSQL
    def _getCmdKeyword(self):
        return self.keySQL + self.cmdAll
    def _checkCmd(self, grammar, cmdstr):
        try:
            ret = grammar.parseString(cmdstr)
        except ParseException:
            return False
        else:
            return True
    def _makeTPB(self,isolation='read committed',versions=False,nowait=False,read_only=False):
        tpb = kdb.TPB()
        if read_only:
            tpb.access_mode = kdb.isc_tpb_read
        if nowait:
            tpb.lock_resolution = kdb.isc_tpb_nowait
        if isolation == 'snapshot':
            tpb.isolation_level = kdb.isc_tpb_concurrency
        elif 'stability' in isolation:
            tpb.isolation_level = kdb.isc_tpb_consistency
        elif 'committed' in isolation:
            if versions:
                tpb.isolation_level = (kdb.isc_tpb_read_committed,kdb.isc_tpb_rec_version)
            else:
                tpb.isolation_level = (kdb.isc_tpb_read_committed,kdb.isc_tpb_no_rec_version)
        return tpb.render()

    def execute(self,sql):
        fbc = self.controller._fbc
        # CREATE DATABASE is special case...
        if self._checkCmd(self.keyCreateDatabase,sql):
            stm = self.CreateDatabase.parseString(sql,True)
            kwargs = dict(stm.items())
            name = kwargs.get('intoVar','db')
            user = kwargs.get('user','sysdba')
            if kwargs.has_key('host'):
                kwargs['database'] = kwargs['db']
            else:
                kwargs['dsn'] = kwargs['db']
            del kwargs['db']
            kwargs['dialect'] = fbc.sql_dialect
            if fbc.charset:
                kwargs['charset'] = fbc.charset
            try:
                d = fb.createDatabase(**kwargs)
                fbc.setDatabase(d, name)
                self.controller.locals[name] = d
                self.controller.write('Database %s as %s, user %s\n' % (d.dsn, name, user))
            except kdb.OperationalError, e:
                self.controller.writeErr("Error: %s" % str(e[0]))
                self.controller.writeErr(str(e[1]))
            return

        try:
            db = fbc.getMainDatabase()
        except:
            self.controller.write('No database attached.\n')
            return

        # And DROP DATABASE as well...
        if self._checkCmd(self.DropDatabase,sql):
            stm = self.DropDatabase.parseString(sql,True)
            dbvar = stm.get('inVar',fbc.main_database)
            db = fbc.getDatabase(dbvar)
            if not db:
                self.writeErr("Unknown database '%s'\n" % dbvar)
                return
            db.drop()
            self.controller.write('Database %s dropped.\n' % dbvar)
            del fbc.databases[dbvar]
            if fbc.main_database == dbvar:
                if len(fbc.databases.keys()) == 0:
                    fbc.main_database = None
                    self.controller.write('No other databases attached.\n')
                else:
                    fbc.setMainDatabase(fbc.databases.keys()[0])
                    db = fbc.getMainDatabase()
                    self.controller.write('Switching main database to %s as %s, user %s\n' % 
                                          (db.dsn, fbc.main_database, db.user))
            return
        
        # Other SQL statements
        line = itplns(sql,self._getUserNamespace(),self._getContextLocals())
        try:
            # check for store variable
            line,sep,var = line.partition(self.SQL_STORE_SEPARATOR)
            var = self.__norm(var)
            # check input parameters
            sql,sep,params = line.partition(self.SQL_PARAM_SEPARATOR)
            params = self.__norm(params)
            if params is not None:
                try:
                    params = eval(params,self._getUserNamespace(),self._getContextLocals())
                except Exception, e:
                    self.controller.writeErr('%s:%s\n' % (e.__class__, e))
                    return
                if not isiterable(params):
                    self.controller.writeErr('SQL parameters must be iterable\n')
                    return

            if self.cursor is None:
                self.cursor = db.cursor()
            # To conserve resources, we use shared self.cursor
            # except when independent one (accessible from shell) is requested
            if var is None:
                c = self.cursor
            else:
                c = db.cursor()
                self._getContextLocals()[var] = c
            
            statement = c.prep(sql)
            if fbc.show_plan:
                self.write('\n%s\n' % statement.plan)
                if fbc.show_plan_only:
                    return
                else:
                    self.write('\n')
            stmt_type = statement.statement_type

            if stmt_type == kdb.isc_info_sql_stmt_commit:
                c.transaction.commit()
                if self.uncommitted_ddl:
                    self.uncommitted_ddl = False
                    db.reload()

            elif stmt_type == kdb.isc_info_sql_stmt_ddl:
                c.execute(sql)
                if self.controller._fbc.autocommit_ddl:
                    c.transaction.commit()
                    self.uncommitted_ddl = False
                    db.reload()
                else:
                    self.uncommitted_ddl = True

            elif stmt_type == kdb.isc_info_sql_stmt_rollback:
                c.transaction.rollback()
                self.uncommitted_ddl = False

            elif stmt_type in [kdb.isc_info_sql_stmt_delete,
                               kdb.isc_info_sql_stmt_insert,
                               kdb.isc_info_sql_stmt_update]:
                if params:
                    c.execute(sql,params)
                else:
                    c.execute(sql)

            elif stmt_type == kdb.isc_info_sql_stmt_savepoint:
                # This is tricky, it could be SAVEPOINT, RELEASE or ROLLBACK
                stm = self.SavepointFamily.parseString(sql,True)
                if stm.category == 'savepoint':
                    c.transaction.savepoint(stm.savepoint)
                elif stm.category == 'rollback':
                    c.transaction.rollback(stm.savepoint)
                elif stm.category == 'release':
                    c.execute(sql)
                else:
                    raise pcError('Uknown savepoint statement category %s' % stm.category)

            elif stmt_type in [kdb.isc_info_sql_stmt_select,
                               kdb.isc_info_sql_stmt_exec_procedure]:
                if params:
                    c.execute(sql,params)
                else:
                    c.execute(sql)
                if var is None and c.description is not None:
                    display = self.controller.ui_provider.getDisplay('fdb.sql',UI_TABLE)
                    description = [(f[kdb.DESCRIPTION_NAME],
                                   max(len(f[kdb.DESCRIPTION_NAME]),
                                        f[kdb.DESCRIPTION_DISPLAY_SIZE])) 
                                   for f in c.description]
                    display.writeTable(description,c)

            elif stmt_type == kdb.isc_info_sql_stmt_start_trans:
                # TODO: table reservation
                if c.transaction.resolution == 0:
                    if self.controller.ui_provider.promptYN('Commit current transaction'):
                        c.transaction.commit()
                        if self.uncommitted_ddl:
                            self.uncommitted_ddl = False
                            db.reload()
                    else:
                        self.write('Rolling back work.\n')
                        c.transaction.rollback()
                        self.uncommitted_ddl = False
                stm = self.SetTransaction.parseString(sql,True)
                tpb_args = dict(stm.items())
                c.transaction.begin(tpb=self._makeTPB(**tpb_args))

            elif stmt_type == kdb.isc_info_sql_stmt_set_generator:
                c.execute(sql)

            else: # get_segment, put_segment, select_for_upd
                self.writeErr('This SQL statement type is not supported (yet)\n')
                return
            
        except kdb._ALL_EXCEPTION_CLASSES, e:
            self.writeErr('SQL Error!\n')
            self.writeErr(str(e[1])+'\n')
        except Exception,e:
            self.writeErr("%s : %s\n" % (str(e.__class__), str(e)))

class cmdSQLComment(Command):
    def __init__(self, controller):
        super(cmdSQLComment,self).__init__(controller)
        controller._fbc = fbController(controller)
        
        self.keyCmdName  = self._makeNameNode(Empty())
        # we don't need to keep next tokens as instance attributes

        self.cmdSQLComment = self.keyCmdName + SQLCOMMENT
        self.cmdSQLComment.setParseAction(self._compile)

    def _getGrammar(self):
        return self.cmdSQLComment
    def _getCmdKeyword(self):
        return self._makeNameNode(Literal('/*'))
    def execute(self,**kwargs):
        # We generally ignore comments
        pass

class cmdSet(Command):
    def __init__(self, controller):
        super(cmdSet,self).__init__(controller)
        controller._fbc = fbController(controller)
        
        self.keyCmdName = self._makeNameNode(Empty())
        self.keySet     = self._makeNameNode(CaselessKeyword('set'))
        # we don't need to keep next tokens as instance attributes
        keyON      = CaselessKeyword('on')
        keyOFF     = CaselessKeyword('off')
        keyDialect = CaselessKeyword('dialect')
        keySql     = CaselessKeyword('sql')
        keyNames   = CaselessKeyword('names')
        keyAutoDDL = CaselessKeyword('autoddl') | CaselessKeyword('auto')
        keyPlan    = CaselessKeyword('plan')
        keyPlanOnly= CaselessKeyword('planonly')
        dialectNo  = oneOf(['1','2','3']).setParseAction(self._tokenToInt)
        dialectNo.errmsg = 'expected 1, 2 or 3'

        optCharset = Word(alphas,alphanums+'_-')
        optCharset.errmsg = 'character set name'
        optSQLDialect = keySql + keyDialect.setResultsName('opt') + \
                      dialectNo.setResultsName('value')
        optAutoDDL = keyAutoDDL.setResultsName('opt') + \
                   Optional(keyON | keyOFF).setResultsName('value')
        optNames = keyNames.setResultsName('opt') + \
                 optCharset.setResultsName('value')
        optPlan = keyPlan.setResultsName('opt') + \
                 Optional(keyON | keyOFF).setResultsName('value')
        optPlanOnly = keyPlanOnly.setResultsName('opt') + \
                 Optional(keyON | keyOFF).setResultsName('value')
        self.cmdSet = self.keyCmdName + self.keySet + \
            (optSQLDialect + Optional(';') | 
             optAutoDDL + Optional(';') | 
             optNames + Optional(';') | 
             optPlan + Optional(';') | 
             optPlanOnly + Optional(';') | 
             Optional(';') +LineEnd())
        self.cmdSet.setParseAction(self._compile)

    def _getGrammar(self):
        return self.cmdSet
    def _getCmdKeyword(self):
        return self.keySet
    def _ONOFF(self,value):
        return iif(value,'ON','OFF')
    def _setOption(self,value,fbc, option_name):
        if value is None:
            setattr(fbc,option_name,not getattr(fbc,option_name))
        else:
            setattr(fbc,option_name,value.upper() == 'ON')
    def execute(self,**kwargs):
        """Firebird SQL environment configuration.

SET                      Display current SET options.
SET SQL DIALECT <num>    Sets SQL DIALECT used for new connection or created databases.
SET AUTO[DDL] [ON | OFF] Toggle autocommit of DDL statements.
SET NAMES <charset>      Set name of runtime character set.
SET PLAN [ON | OFF]      Toggle display of query access plan.
SET PLANONLY [ON | OFF]  Toggle display of query plan without executing.

For compatibility with ISQL, you may optionally end each command with ';' (only).
        """
        opt = kwargs.get('opt','').upper()
        fbc = self.controller._fbc
        if not opt:
            lines = []
            display = self.controller.ui_provider.getDisplay('fdb.sql',UI_LIST)
            lines.append('Print statistics:   %s' % self._ONOFF(fbc.print_stats))
            lines.append('Echo commands:      %s' % self._ONOFF(fbc.echo))
            lines.append('List format:        %s' % self._ONOFF(fbc.list_format))
            lines.append('Row count:          %s' % self._ONOFF(fbc.row_count))
            lines.append('Autocomit DDL:      %s' % self._ONOFF(fbc.autocommit_ddl))
            lines.append('Access plan:        %s' % self._ONOFF(fbc.show_plan))
            lines.append('Access plan only:   %s' % self._ONOFF(fbc.show_plan_only))
            lines.append('Column headings:    %s' % self._ONOFF(fbc.headings))
            lines.append('Terminator:         %s' % self.controller.terminator)
            lines.append('Time:               %s' % self._ONOFF(fbc.time))
            lines.append('Warnings:           %s' % self._ONOFF(fbc.warnings))
            lines.append('SQL dialect:        %i' % fbc.sql_dialect)
            if fbc.charset:
                lines.append('Connection charset: %s' % fbc.charset)
            display.writeList(lines)
        elif opt.startswith('AUTO'):
            self._setOption(kwargs.get('value'),fbc,'autocommit_ddl')
        elif opt == 'DIALECT':
            fbc.sql_dialect = kwargs.get('value',3)
        elif opt == 'NAMES':
            charset = kwargs.get('value').upper()
            fbc.charset = iif(charset == 'NONE',None,charset)
        elif opt == 'PLAN':
            self._setOption(kwargs.get('value'),fbc,'show_plan')
        elif opt == 'PLANONLY':
            self._setOption(kwargs.get('value'),fbc,'show_plan_only')
            if fbc.show_plan_only:
                fbc.show_plan = True

class packageFirebird(ExtensionPackage):
    """Firebird Package handler object for PowerConsole.
    """

    def __init__(self):
        super(packageFirebird,self).__init__('pwcfb')
    
    def show_extensions(self):
        return [showDatabase,showDbObjects]
    def object_renderers(self):
        return [fbObjectRenderer]
    def commands(self):
        return [cmdConnect,cmdDisconnect,cmdReady,cmdSQLComment,cmdSet,cmdSQL]
    def help_providers(self):
        return [helpFirebird]
    def add_options(self,parser):
        pass
        #parser.add_option('--type-conv',type='choice',metavar='CODE',
                          #choices=['100','200','199','300'],
                          #help='Code of KInterbasDB type conversion to use')
    def process_options(self,options,args):
        pass
        #if options.type_conv:
            #if not kdb.initialized:
                #kdb.init(type_conv=int(options.type_conv))
            #else:
                #raise pcError('KInterbasDB already initialized. Can''t set the conversion type.')
