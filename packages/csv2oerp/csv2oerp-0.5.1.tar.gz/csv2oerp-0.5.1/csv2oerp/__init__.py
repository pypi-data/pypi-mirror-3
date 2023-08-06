#!/usr/bin/env python
# -*- coding: utf8 -*-
################################################################################
#
# Copyright (c) 2012 STEPHANE MANGIN. (http://le-spleen.net) All Rights Reserved
#                    Stéphane MANGIN <stephane.mangin@freesbee.fr>
# Copyright (c) 2012 OSIELL SARL. (http://osiell.com) All Rights Reserved
#                    Eric Flaux <contact@osiell.com>
# 
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
# 
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# 
################################################################################

"""

csv2oerp is intended to be used to simplify data migration into OpenERP.

"""

import os
import sys
import xmlrpclib
import copy
import logging
import logging.handlers
from copy import copy
from copy import deepcopy
from optparse import OptionParser
import exceptions
import unicode_csv
from pprint import pformat
import tools
import fields

from constants_and_vars import STATS
from constants_and_vars import FORMAT
from constants_and_vars import ACTION_PATTERN
from constants_and_vars import HOST
from constants_and_vars import USER
from constants_and_vars import UID
from constants_and_vars import PORT
from constants_and_vars import DB
from constants_and_vars import PWD 
from constants_and_vars import EXIT_OK, EXIT_WARNING, EXIT_ERROR, EXIT_UNKNOWN

def _get_special_actions(model):
    res = {}
    for item, attr in ACTION_PATTERN.iteritems():
        res[item] = attr in model.split('::')[0].split(',') and True or False
    return res

def set_global_connection(*args, **kwargs):
    raise DeprecationWarning('set_global_connection is deprecated.'
            'Use connect method instead.')

def _connect():
    """ Open a connection throught a socket to OpenERP XMLRPC service
    return an uid and a opened socket linked to this connection

    """
    global UID
    url = 'http://%s:%s/xmlrpc/' % (HOST, PORT)
    sock_common = xmlrpclib.ServerProxy(url + 'common', allow_none=True)
    UID = sock_common.login(DB, USER, PWD)
    return xmlrpclib.ServerProxy(url + 'object', allow_none=True)

def connect(host=HOST, port=PORT, user=USER, pwd=PWD, dbname=DB):
    """Set globals constants needed to initialize a connection to openerp

    :param host: IP or DNS name of the OERP server
    :type host: str
    :param port: Port number to reach
    :type port: int
    :param user: Username in the OERP server
    :type user: str
    :param pwd: Password of the username
    :type pwd: str
    :param dbname: Name of the database to reach
    :type dbname: str
    :raises: nothing

    """
    global HOST, USER, PORT, DB, PWD, OERP
    HOST = host
    PORT = port
    USER = user
    PWD = pwd
    DB = dbname
    OERP = _connect()


class Import(object):
    """Main class which provides the functionnal part of the importation process
    
    .. note:: `sys.argv` is integrated if you want to use the command line parser.

    Here are the available command line arguments::

        -h, --help                  Show this kind of help message and exit
        -o OFFSET, --offset=OFFSET  Offset (Usually for header omission)
        -l LIMIT, --limit=LIMIT     Limit
        -c, --check-mapping         Check mapping template
        -v, --verbose               Verbose mode
        -d, --debug      
           debug mode
        -q, --quiet                 Doesn't print anything to stdout

    """

    @property
    def server(self):
        """ Return the current socket connection to the OpenERP server (xmlrpc).

        """
        return self._server

    @property
    def host(self):
        """ Return the current connection host for this session.

        """
        return self._host

    @property
    def port(self):
        """ Return the current connection port for this session.

        """
        return self._port

    @property
    def db(self):
        """ Return the current database name for this session.

        """
        return self._db

    @property
    def user(self):
        """ Return the current username for this session.

        """
        return self._user

    @property
    def uid(self):
        """ Return the current UID for this session.

        """
        return self._uid

    @property
    def pwd(self):
        """ Return the current password for this session

        """
        return self._pwd
    
    @property
    def lines(self):
        """Getting all lines from CSV parser
        
        :returns: list

        """
        return self._lines

    @property
    def options(self):
        """Getting all arguments from command line (OptionParser)

        """
        return self._options

    @property
    def mapping(self):
        """Getting columns mapping configuration

        """
        return self._columns_mapping

    @property
    def lang(self):
        """Getting current language

        """
        return self._lang

    def __init__(self):
        self._arg_treatments()
        self._syslog_mode = False
        self._columns_mapping = {}
        self._lines = None
        self._server = None
        self._uid = None
        self._preconfigure = None
        self._relationnal_prefix = 'REL_'
        self._current_mapping = None
        self._lang = 'fr_FR'
        self._encoding = 'utf-8'
        self._logger = None

    def _arg_treatments(self):
        parser = OptionParser()
        parser.add_option("-o", "--offset",
                action="store",
                type="int",
                dest="offset",
                default=0,
                help="Offset (Usually for header omission)")
        parser.add_option("-c", "--check-mapping",
                action="store_true",
                dest="checkmapping",
                default=False,
                help="Check mapping template")
        parser.add_option("-d", "--debug",
                action="store_true",
                dest="debug",
                default=False,
                help="debug mode")
        parser.add_option("-v", "--verbose",
                action="store_true",
                dest="verbose",
                default=False,
                help="verbose mode")
        parser.add_option("-q", "--quiet",
                action="store_true",
                dest="quiet",
                default=False,
                help="don't print anything to stdout")
        parser.add_option("-l", "--limit",
                action="store",
                dest="limit",
                type="int",
                default=None,
                help="Limit")
        # Connection options
        parser.add_option("-u", "--username",
                action="store",
                dest="username",
                default=USER,
                help="Username")
        parser.add_option("-p", "--password",
                action="store",
                dest="password",
                default=PWD,
                help="Password")
        parser.add_option("-r", "--host",
                action="store",
                dest="host",
                default=HOST,
                help="Host to contact")
        parser.add_option("-t", "--port",
                action="store",
                dest="port",
                default=PORT,
                help="Port used")
        parser.add_option("-b", "--database",
                action="store",
                dest="dbname",
                default=DB,
                help="Database name")
        (self._options, args) = parser.parse_args()
        self._host = self.options.host
        self._port = self.options.port
        self._db = self.options.dbname
        self._user = self.options.username
        self._pwd = self.options.password
        return 

    #===========================================================================
    # SETTER
    #===========================================================================
    def connect(self, host=HOST, port=PORT, user=USER, pwd=PWD, dbname=DB):
        """Declare a new connection to an OpenERP instance.
        
        .. note:: Needed if several CSV files acts in differents OpenERP
        servers. Otherwise, please use the ``csv2oerp.connect`` function

        :param host: IP or DNS name of the OERP server
        :type host: str
        :param port: Port number to reach
        :type port: int
        :param user: Username in the OERP server
        :type user: str
        :param pwd: Password of the username
        :type pwd: str
        :param dbname: Name of the database to reach
        :type dbname: str
        :returns: bool

        """
        self._host = host
        self._port = port
        self._user = user
        self._pwd = pwd
        self._db = dbname
        return True

    def set_logger(self, name=None):
        """Configure and initialize the logger facility

        .. note:: Optionnal

        :param name: Name of the logger
        :type name: str
        :returns: bool
        
        """
        global STATS, FORMAT
        try:
            basename, extension = os.path.splitext(self._filename)
        except:
            basename = name
        logfile = os.path.join(basename+".log")
        buff = open(logfile, 'w')
        buff.close()
        self._logger = logging.getLogger(name or basename)
        if self._syslog_mode:
            self._hdlr = logging.handlers.SysLogHandler(
                address=self._syslog_mode,
                facility=logging.handlers.SysLogHandler.LOG_USER
            )
        else:
            self._hdlr = logging.FileHandler(logfile)

        # Format du logger
        STATS['importfile'] = self._filename
        formatter = logging.Formatter(FORMAT)
        self._hdlr.setFormatter(formatter)
        self._logger.addHandler(self._hdlr)
        if self.options.debug:
            self._logger.setLevel(logging.DEBUG) #show all messages of severity >= DEBUG
        else:
            self._logger.setLevel(logging.INFO) #show all messages of severity >= INFO
        
        if not self.options.quiet:
            if self.options.verbose:
                logging.basicConfig(format=FORMAT) # console log
    
        self._logger.info("Logger set to '%s'" % basename, extra=STATS)
        return True

    def _is_model(self, model):
        """Check model validity
        
        :returns: bool

        """
        res = self.server.execute(self.db, self.uid, self.pwd,
                'ir.model', 'search', [('model', '=', model)])
        return bool(res)
    
    def _is_model_defined(self, model):
        return model in self.mapping.keys()

    def _is_field(self, model, attr):
        """Check field validity
        
        :returns: bool

        """
        for pattern in ACTION_PATTERN.values():
            if attr.count(pattern):
                attr.replace(pattern, '')
        res = self.server.execute(self.db, self.uid, self.pwd, model, 'fields_get')
        if attr in res:
            return True
        return False

    def _check_mapping(self, mapping):
        """Check mapping for semantics errors

         .. note:: Also setup the logger and initialize OpenERP connection

        """
        #======================================================================
        # Open socket
        #======================================================================
        try:
            self._open_connection()
        except Exception as error:
            self._logger.error("connection problem : %s" % error, extra=STATS)
            sys.exit(EXIT_ERROR)
        
        if not self.options.checkmapping:
            self._logger.info("Mapping check disabled ...", extra=STATS)
            return True

        mapping = deepcopy(mapping)
        title = "Errors occured during mapping check :\n___________________\n\n"
        res = ""
        # Mapping must be iterable throught pair of item
        if not hasattr(mapping, 'iteritems'):
            res += "\t* Mapping must be iterable throught pairs of item\n\n"
            res += "=> %s" % error
        else:
            for model, columns in mapping.iteritems():
                self._logger.info("Checking model '%s' ..." % model, extra=STATS)
                # Check if model exist
                if model.startswith(self._relationnal_prefix):
                    model = model.split('::')[1]
                    columns = [columns]
                elif model.startswith('NO_UPDATE'):
                    model = model.split('::')[1]
                
                if not self._is_model(model):
                    res += "\t* '%s' does not exist, \n\n" % model
                    continue
                
                # Check if value is a well formed tuple
                for obj in columns:
                    if not hasattr(obj, 'iteritems'):
                        res += "\t* List of fields must be iterable throught\
pairs of item and objects (non relationnal) must be in a list.\n\n"
                        res += "=> %s" % error
                    else:
                        for attr, tuple_val in obj.iteritems():
                            self._logger.debug("Checking field '%s'" % attr,
                                    extra=STATS)
                            for patt in ACTION_PATTERN.values():
                                if attr.count(patt):
                                    attr = attr.split('::')[1]
                            
                            if attr != 'id' and not self._is_field(model, attr):
                                res += "\t* '%s' '%s' does not exist, \n\n" %\
                                        (model, attr)
                                continue
                            try:
                                if callable(tuple_val):
                                    tuple_val = tuple_val()[0]
                                (name, lambda_func, searchable) = tuple_val
                                if name is None and not callable(lambda_func):
                                    res += "\t* You must indicate either a column\
number or a function or both in a field definition, \n\n"
                            except:
                                res += "\t* '%s' '%s' definition is not well\
formed, \n\n" % (model, attr)

        if res != "":
            raise Exception(title + res)
        else:
            return True
            
    def set_input_file(self, filename, delimiter=',', quotechar='"',
            encoding='utf8'):
        """Set the CSV file to use for importation.

        """
        global STATS
        self._filename = filename
        STATS['importfile'] = self._filename
        self._separator = delimiter
        self._quote = quotechar
        self._encoding = encoding
        # Initialize logger
        if not self._logger:
            self.set_logger()
        return True
    
    set_filename_to_import = set_input_file

    def set_input_base(host, port, user, pwd, dbname):
        """ Configure the mysql base to import from.

        :param host: IP or DNS name of the MySQL server
        :type host: str
        :param port: Port number to reach
        :type port: int
        :param user: Username
        :type user: str
        :param pwd: Password of the username
        :type pwd: str
        :param dbname: Name of the database to reach
        :type dbname: str
        :raises: nothing
        
        .. versionadded:: 0.5.1

        """
        return NotImplemented

    def set_preconfigure_script(self, filename):
        """Declare a parrallel script which will be called before importation.

        It must implement a main method which take in params the instance of 
        Import class, it will be able to use all facilities from Import class.

        It must return a list of lines (lines already list too)

        """
        self._preconfigure = filename

    def log(self, level, msg, line=None, model=None):
        """Allow to use the internal logger to log special message outside of
        the importation process.

        """
        global STATS
        STATS['importfile'] = self._filename
        if level not in ('debug', 'info', 'warning', 'error'):
            raise Exception("logger, invalid level")
        old_line = STATS['line_num']
        if line:
            STATS['line_num'] = line
        if not self._logger:
            self.set_logger()
        getattr(self._logger, level)("CP %s%s" % (model and '<%-25s> ' %\
                model or '', msg), extra=STATS)
        STATS['line_num'] = old_line

    def set_syslog(self, arg):
        """Set if syslog must be used instead of a file.

        """
        self._syslog_mode = arg

    def get_lines_from_value(self, column, value):
        """ Retrieve lines which have value at column

        :param column: The column index
        :type column: int
        :param value: The value to compare from
        :type value: value
        :returns: tuple (int, list)

        """
        res = []
        for line in self.lines:
            value_type = type(line[column])
            value = value_type(value) or value
            if line[column] == value:
                res.append(line)
        return res
    
    def get_index_from_value(self, column, value, withcast=True):
        """ Retrieve lines which have ``value`` at ``column``

        By default ``value`` will be casted by ``column`` value type
        overwrite it by withcast=False
        
        :param column: The column index
        :type column: int
        :param value: The value to compare from
        :type value: value
        :returns: int

        """
        res = []
        index = 0
        for line in self.lines:
            value_type = type(line[column])
            value = withcast and value_type(value) or value
            if line[column] == value:
                res.append(index)
            index += 1
        return res
    
    #===========================================================================
    # OpenERP connection - XMLRPC
    #===========================================================================
    def _open_connection(self):
        """ Open a connection throught a socket to OpenERP XMLRPC service
        return an uid and a opened socket linked to this connection
    
        """
        url = 'http://%s:%s/xmlrpc/' % (self.host, self.port)
        sock_common = xmlrpclib.ServerProxy(url + 'common', allow_none=True)
        self._uid = sock_common.login(self.db, self.user, self.pwd)
        self._server = xmlrpclib.ServerProxy(url + 'object', allow_none=True)
 
    def _csv_open(self, f):
        """ Return a CSV reader object
        
        """
        return unicode_csv.Reader(f, delimiter=self._separator, quotechar=self._quote)

    #===========================================================================
    # Search and call methods
    #===========================================================================
    def _get_callback(self, line, model, callback, key, content):
        """Call the callback function after adding it some usefull stuff
        * get_lines method which allow to retreive a line matching values from
            columns in the actual specified line's columns
        * get_line retrieve a line by its index
        
        We don't intercept any Exceptions, these from callback would be masqued

        """
        res = None
        if callback:
            res = callback(self, model, key, content, line)
        else:
            res = content
        return res

    def _get_content(self, model, column, callback):
        """Return a value by its column position or the callback function

        """
        try:
            column = eval(column)
        except:
            pass
        # List of indices case
        if isinstance(column, list):
            content = u""
            for ind in column:
                content += " "+STATS['actual_line'][ind]
        elif column is not None:
            try:
                content = STATS['actual_line'][column]
            except IndexError:
                raise exceptions.ColumnIndexError(model,
                        'Invalid column index `%s`' % column, self._logger)
        else:
            content = callback
        return content
    
    def _noupdate_relation(self, model, data, search):
        """Return id of a similar object for the same line fonctionnality and 
        the same model

        """
        if 'CREATED::id' in self.mapping[model]\
                and self.mapping[model]['CREATED::id']:
            return self.mapping[model]['CREATED::id']
        return False

    def _unique_relation(self, model, data, search):
        """Return id of a similar object for the same line fonctionnality and 
        the same model

        """
        for each_model in self.mapping:
            if _get_special_actions(each_model)['unique']\
                    and  model.split('::')[1] == each_model.split('::')[1]:
                if 'CREATED::id' in self.mapping[each_model]\
                        and self.mapping[each_model]['CREATED::id']:
                    search = data.keys()
                    search.remove('CREATED::search')
                    res = self.search(model.split('::')[1], data, search)
                    if res\
                    and self.mapping[each_model]['CREATED::id'] in res:
                        self._logger.debug('<%20s> UNIQUE Replacement' %\
                                model, extra=STATS)
                        return self.mapping[each_model]['CREATED::id']
        return False

    def _create_relation(self, line, model):
        """Launch a sub function to import the new relation id

        """
        id = None
        try:
            data_rels = self.mapping[model]
        except:
            raise Exception("'%s' relation not found !" % model)

        if not isinstance(data_rels, list):
            data_rels = [data_rels]
        
        for data_rel in data_rels:
            if 'CREATED::id' in data_rel and data_rel['CREATED::id']:
                id = data_rel['CREATED::id']
            else:
                if 'CREATED::search' in data_rel:
                    search_rel = data_rel['CREATED::search']
                else:
                    try:
                        search_rel = self._convert(line, model, data_rel)
                    except exceptions.SkipObjectException:
                        return False
                
                # If relation is unique inside actual model
                if _get_special_actions(model)['unique']:
                    id = self._unique_relation(model, data_rel, search_rel)
                # If relation is not updating
                elif _get_special_actions(model)['noupdate']:
                    id = self._noupdate_relation(model, data_rel, search_rel)
                
                if not id:
                    (state, model, id) = self.create(model.split('::')[1],
                            data_rel, search_rel)
                data_rel['CREATED::id'] = id
        return id 

    #===========================================================================
    # Lines, objects, fields modification methods
    #===========================================================================
    def _skip_line(self, line, data, model, type_='skip'):
        """Raise an SkipLineException if 'SKIP' is found in data keys
        and if callback returns True

        """
        if type_ == 'skip':
            mode = ACTION_PATTERN[type_]
            compare_value = True
        elif type_ == 'required':
            mode = ACTION_PATTERN[type_]
            compare_value = False
        for key, value in data.items():
            if key.startswith(mode):
                (column, callback, searchable) = value
                content = self._get_content(model, column, callback)
                if callback is not None:
                    returned_value = self._get_callback(line, model, callback,
                            key, content)
                    if returned_value is compare_value:
                        raise exceptions.SkipLineException(model,
                                msg='%s is required' % key.split('::')[1],
                                log=self.logger)
                    else:
                        # rename key becomed unusefull
                        data[key.split('::')[1]] = data[key]
                        del data[key]
                    self._logger.debug('<%-25s> processing %s=%s' % (model, key,
                        returned_value), extra=STATS)
                else:
                    content = self._get_content(model, column, callback)
                    if content:
                        data[key.split('::')[1]] = data[key]
                        del data[key]
                        self._logger.debug('<%-25s> processing %s=%s' % (model,
                            key, content), extra=STATS)
                    else:
                        raise exceptions.SkipLineException(model,
                                log=self._logger)


    def _replace_line(self, line, data, model):
        """Dynamic method to modify/replace current field by another one(s)

        WARNING : DO NOT WORK WITHOUT HEAVY BUGS

        """
        for key, value in data.items():
            if key.startswith(ACTION_PATTERN['replace']):
                (column, callback, searchable) = value
                content = self._get_content(model, column, callback)
                if callback is not None:
                    returned_value = self._get_callback(line, model, callback,
                            key, content)
                    if isinstance(returned_value, dict):
                        self._logger.debug('<%-25s> processing %s' % (model,
                            key), extra=STATS)
                        for item, value in returned_value.iteritems():
                            self._logger.debug('<%-25s> modifying "%s" to %s' %\
                                    (model, item, value), extra=STATS)
                            data[item] = value
                        del data[key]
                    elif returned_value is False:
                        data[key.split('::')[1]] = copy(data[key])
                        del data[key]
                    elif callable(returned_value):
                        value = self._get_callback(line, model, returned_value,
                            key, content)
                        if value in self.mapping.keys():
                            data[key] = (data[key][0], returned_value,
                                    data[key][2])
                        else:
                            data[key] = (data[key][0], value, data[key][2])
                    else:
                        del data[key]
                else:
                    self._logger.debug('<%-25s> processing %s=%s' % (model, key,
                        content), extra=STATS)

    def _ignore_object(self, line, data, model):
        """Raise an SkipObjectException if 'IGNORE::' is found in data keys
        and if callback returns True

        """
        for key, value in data.items():
            if key.startswith(ACTION_PATTERN['ignore']):
                (column, callback, searchable) = value
                content = self._get_content(model, column, callback)
                if callback is not None:
                    returned_value = self._get_callback(line, model, callback,
                            key, content)
                    if returned_value:
                        raise exceptions.SkipObjectException(model,
                                log=self._logger)
                    else:
                        # Finally remove key unusefull and create new one with
                        # correct tuple without callback
                        content = (column, None, searchable)
                        data[key.split('::')[1]] = content
                        del data[key]
                        self._logger.debug('<%-25s> processing %s=%s' % (model,
                            key, returned_value), extra=STATS)
                else:
                    self._logger.debug('<%-25s> processing %s=%s' % (model, key,
                        content), extra=STATS)
    
    #===========================================================================
    # Main import private methods
    #===========================================================================
    def _convert(self, line, model, data, encoding="UTF-8"):
        """Search for vals in line

        """
        global STATS
        search = []
        ToRemove = []
        
        if 'CREATED::search' in data.iterkeys():
            self._logger.debug('<%-25s> previous search:%s' % (model,
                data['CREATED::search']), extra=STATS)
            return data['search']
        
        # Record function functionnality integration and type verification
        #=======================================================================
        for attr, column in deepcopy(data).iteritems():

            if isinstance(column, fields.Base):
                # Result of Column call
                new_tuple, actions = column()
                actions = ','.join(actions).upper().strip(',')

                if actions:
                    del data[attr]
                    attr = "%s::%s" % (actions, attr)

                data[attr] = new_tuple

            elif not isinstance(column, tuple):
                raise Exception('Field\'s column definition must be tuple\
 or Column class')

        # Exceptions if any
        #=======================================================================
        self._skip_line(line, data, model, type_='skip')
        self._skip_line(line, data, model, type_='required')
        self._ignore_object(line, data, model)
        self._replace_line(line, data, model) 

        # Main process boucle
        #=======================================================================
        for item, tuple_val in data.iteritems():

            # Relationnal key, do not process until remove the prefix
            current_model = model

            if current_model.startswith(self._relationnal_prefix)\
                    or current_model.startswith('NO_UPDATE'):
                current_model = model.split('::')[1]
            
            column = -1 # Default
            searchable = False
            (column, callback, searchable) = tuple_val
            content = self._get_content(model, column, callback)
            
            if callback is not None:
                if callable(callback):
                    content = self._get_callback(line, current_model, callback,
                            item, content)
                else:
                    STATS['errors'] += 1
                    self._logger.error('callback must be a function'
                        '(for example a lambda function)', extra=STATS)
                    raise exceptions.SkipLineException(log=self._logger)
                
                # If result is a relation, so launch relation creation function
                if isinstance(content, str) and content.startswith("REL_"):
                    self._logger.debug('<%-25s> == REL %s ==' % (model, content),
                            extra=STATS)
                    content = self._create_relation(line, content)
                    self._logger.debug('<%-25s> == END %s ==' % (model, content),
                            extra=STATS)

            elif column is None:
                STATS['errors'] += 1
                self._logger.error('callback is mandatory', extra=STATS)
                raise exceptions.SkipLineException()
            #else:
            #    self.logger.error('Callback or columns is mandatory.', extra=STATS)
            
            self._logger.debug('<%-25s> processing %s=%s' % (model, item, content),
                    extra=STATS)
                
            # Add this item to search criteria
            if searchable:
                search.append(item)
            data[item] = content

            #Cleaning dict items with null value
            if content in ("", " ", None):
               ToRemove.append(item)
           
        for item in ToRemove:
            del data[item]
        data['CREATED::search'] = search
        return search
    
    def _create(self, model, data, search):
        """Effective object creation process within model and data values
        Search for a previous object before creation within search param
        Do not search for previous object if first_import is True
        
        :param model: Name of the OERP class model
        :type model: str
        :param data: Data dictionnary to transmit to OERP create/write method
        :type data: dict
        :param search: List of field used to search for an existing object
        :type search: list
        :returns tuple (['new', 'old', 'none'], id):
        :raises: Nothing:
        
        """
        global STATS
        STATS['importfile'] = self._filename
        update = True
        if model.count('NO_UPDATE'):
            update = False
        if model.count('::'):
            model = model.split('::')[1]
        res = [False]
        error = None
        state = 'old'
        search = self.search(model, data, search)
        if 'CREATED::id' in data and data['CREATED::id']:
            res = [int(data['CREATED::id'])]
            self._logger.info("<%-25s> ALREADY%s" % (model, res), extra=STATS)
        else:
            if 'id' in data:
                search = [int(data['id'])]
                del data['id']

            self._logger.debug('<%-25s> data:%s' % (model, data), extra=STATS)
            if not data:
                self._logger.warning("<%-25s> Null values" % model, extra=STATS)
                STATS['objects'][model]['skipped'] += 1
                res = [False]
            else:
                try:
                    if not search:
                        state = "new"
                        res = [self.server.execute(self.db,
                            self.uid, self.pwd, model, 'create', data,
                            {'lang': self.lang})]
                        self._logger.info("<%-25s> CREATE%s" % (model, res),
                                extra=STATS)
                        STATS['object_created'] += 1
                        STATS['objects'][model]['created'] += 1
                    else:
                        state = 'old'
                        res = search or [False]
                        if update:
                            self.server.execute(self.db,
                                self.uid, self.pwd, model, 'write', res, data,
                                {'lang': self.lang})
                            self._logger.info("<%-25s> WRITE%s"% (model, res),
                                    extra=STATS)
                            STATS['object_written'] += 1
                            STATS['objects'][model]['written'] += 1
                    
                except xmlrpclib.Fault as err:
                    error = unicode(err.faultString + (err.faultCode or ''))\
                            or 'Unknown error (xmlrplib.Fault)'
                except Exception as err:
                    error = unicode(err) or 'Unknown error (Exception)'
        if error:
            res = [False]
            state = 'none'
            self._logger.warning("<%-25s> NOT CONSISTENT -> %s(%s)" %\
                    (model, search, error), extra=STATS)
            self._logger.debug("<%-25s> id:%s|state:%s|%s" %\
                    (model, search, state, pformat(data)), extra=STATS)
            STATS['warnings'] += 1
            STATS['objects'][model]['skipped'] += 1
            STATS['objects'][model]['error'] += 1
        
        data['CREATED::id'] = res[0]
        return (state, model, res[0])

    def _apply_model(self, model, line):
        """Convert a model from mapping with his values from line

        :param model: Name of the model
        :type model: str
        :param line: Number of the line
        :type line: int
        :returns boolean:
        :raises: Nothing:
        """

        try:
            search = self._convert(line, model, self.mapping[model])
            self._columns_mapping[model]['search'] = search
        except exceptions.SkipObjectException:
            return False
        return True
    
    #===========================================================================
    # Public methods
    #===========================================================================
    def set_lang(self, code='fr_FR'):
        """Set current lang
        
        :param code: The standardized code of a language
        :type code: str

        """
        self._lang = code
    
    def search(self, model, data, search=None):
        """Return a list of IDs of records matching the given criteria
        in ``data`` parameter, ``data`` must be of the form ``{'name': 'Agrolait'}``.
        ``search`` define wich must be of the form ``['name', 'firstname']``

        >>> self.search('res.partner', {'name': 'Agrolait'}, ['name'])
        [3]

        :param model: Name of the OERP class model
        :type model: str
        :param data: Data dictionnary to transmit to OERP create/write method
        :type data: dict
        :param search: List of fields to be used for search
        :type search: list
        :returns: a list of IDs
        :raises: Nothing
        
        """
        global STATS
        STATS['importfile'] = self._filename
        if search is None:
            search = []
        if not data:
            return [] 
        res = []
        list_search = []
        self._logger.debug('<%-25s> search:%s' % (model, search), extra=STATS)

        for item in search:
            if item in data.keys():
                list_search.append((item, '=', data[item]))

        self._logger.debug('<%-25s> list_search:%s' % (model, list_search), extra=STATS)

        for (item, sign, val) in copy(list_search):
            if val in ("", " ", None):
                list_search = []

        if list_search:
            res = self.server.execute(self.db, self.uid, self.pwd, model, 'search',
                    list_search, 0, False, False, {'lang': self.lang})
            self._logger.debug('<%-25s> search result %s' % (model, res), extra=STATS)
        
        return res

    def create(self, model, data, search):
        """Object's automatic and abstracted creation from model

        Logged public method
        
        :param model: Name of the OERP class model
        :type model: str
        :param data: Data dictionnary to transmit to OERP create/write method
        :type data: dict
        :param search: List of fields to be used for search
        :type search: list
        :returns tuple (['new', 'old', 'none'], model, id):
        :raises: Nothing:
        
        """
        if not data:
            return ('none', model, False)
        if 'CREATED::search' in data:
            search = data['CREATED::search']
            data.pop('CREATED::search')
        (state, model, id) = self._create(model, data, search)
        return (state, model, id)

    def set_mapping(self, mapping):
        """Columns mapping configuration

        See ``Creation of your Columns mapping`` for further details.
        
        """
        STATS['importfile'] = self._filename
        self._check_mapping(mapping)
        self._current_mapping = mapping

    def start(self):
        """Main function to define and launch the importation

        """
        global STATS 
        STATS['importfile'] = self._filename
        # Initialize logger
        if not self._logger:
            self.set_logger()
        if not self.options.quiet:
            sys.stdout.write('\n')
            sys.stdout.write('*'*79 + '\n')
            sys.stdout.write('* Processing %-64s *\n' % self._filename)
        if DB and not self.db:
            self.set_connection(HOST, PORT, USER, PWD, DB)
        elif not DB and self.db:
            pass
        elif not DB and not self.db:
            raise Exception('You have to configure a connection to an existing OpenERP instance.')


        # Checking mapping
        if self._current_mapping is None:
            raise Exception("No mapping has been defined, use 'setMapping' first !")
        
        # Keeping objects actions to stats further
        for model, fields in self._current_mapping.iteritems():
            if model.startswith(self._relationnal_prefix):
                model = model.split('::')[1]
            if model not in STATS['objects']:
                STATS['objects'][model] = {
                        'name': model, 
                        'written': 0,
                        'created': 0,
                        'skipped': 0,
                        'error': 0,
                        }

        #=======================================================================
        # Open file, call preconfigure if given in arg
        #=======================================================================
        with open(self._filename, 'r') as f:
            limit = self.options.limit
            self._lines = tools.clean_lines(list(self._csv_open(f)))
            self._logger.info("Lines: %s" % int(len(self.lines)), extra=STATS)
            # If the line of titles is the first line of the file, we skip it
            if self.options.offset:
                self._lines = self.lines[self.options.offset:]
                STATS['line_skipped'] += self.options.offset
                self._logger.info("Offset: %s" % self.options.offset, extra=STATS)

            self._lines = limit and self.lines[:limit] or self.lines
            self._logger.info("Limit: %s" % int(len(self.lines)), extra=STATS)
            if self._preconfigure:
                script_to_import, script_extention = os.path.splitext(self._preconfigure)
                if script_extention == '.py':
                    self._lines = __import__(script_to_import).main(self)
            # Initialisation de l'incrémenteur de ligne
            STATS['line_num'] = self.options.offset
           
            #===================================================================
            # Begin the import
            #===================================================================
            try:
                for line in self.lines:
                    
                    STATS['actual_line'] = line
                    STATS['line_num'] += 1
                    model = 'unknown'
                    try:
                        #=======================================================
                        # Instanciate a dictionnary which will receive values
                        # from CSV line according to columns mapping
                        self._columns_mapping = deepcopy(self._current_mapping)
                        self._logger.debug('+++++ NEW LINE +++++',
                                extra=STATS)
                        
                        #=======================================================
                        # Calculating values to import
                        #=======================================================
                        search = {}
                        try:
                            # Iterate through models not starting with REL_
                            for model, datas in self.mapping.items():
                                if model.startswith(self._relationnal_prefix):
                                    continue
                                try:
                                    for data in datas:
                                        search = self._convert(STATS['line_num'],
                                                model, data)
                                        (state, model, id) = self.create(model,
                                                data, search)
                                except exceptions.SkipObjectException:
                                    continue
                            
                        except exceptions.SkipLineException:
                            continue
                    
                    #except Exception as error:
                    #    STATS['errors'] += 1
                    #    self.logger.error("%s %s" % (model, error),extra=STATS)
                     
                    finally:
                        STATS['line_done'] = STATS['line_num']
                #===============================================================
                # End of import
                #===============================================================
                self._logger.info("END import", extra=STATS)
            except KeyboardInterrupt:
                self._logger.error('CTRL^C caught !', extra=STATS)

#            except exceptions.NotConsistentError as error:
#                self._logger.info("""
#
#FATAL ERROR (%s)
#------------------------------------------
#  line: %s
# model: %s
# state: %s
#search: %s
#  data:
#  
#%s
#
#            """ % (error, STATS['line_num'], model, state, search, pformat(data)), extra=STATS)
#            
            finally:
                if not self.options.quiet:
                    sys.stdout.write('*'*79 + '\n')
                    sys.stdout.write('Object Skipped %(object_skipped)11s' %
                            STATS)
                    sys.stdout.write(' | Line Skipped %(line_skipped)11s' %
                            STATS)
                    sys.stdout.write(' | Total Errors %(line_skipped)10s' %
                            STATS)
                    sys.stdout.write('\n')
                    sys.stdout.write('Object Created %(object_created)11s' %
                            STATS)
                    sys.stdout.write(' | Line Done    %(line_done)11s' %
                            STATS)
                    sys.stdout.write(' | Total Warnings%(line_skipped)9s' %
                            STATS)
                    sys.stdout.write('\n')
                    sys.stdout.write('Object Written %(object_written)11s' %
                            STATS)
                    sys.stdout.write('\n')
                    
                STATS = {
                    'importfile': None,
                    'actual_line': 0,
                    'line_num': 0,
                    'errors': 0,
                    'warnings': 0,
                    'line_skipped': 0,
                    'line_done': 0,
                    'object_skipped': 0,
                    'object_created': 0,
                    'object_written': 0,
                    'objects': STATS['objects']
                    }
            return True



def purge_stats():
    """Re-initialize objects activities resume

    """
    global STATS
    STATS = {
        'actual_line': 0,
        'line_num': 0,
        'errors': 0,
        'warnings': 0,
        'line_skipped': 0,
        'line_done': 0,
        'object_skipped': 0,
        'object_created': 0,
        'object_written': 0,
        'objects':{} 
        }

def show_stats():
    """Show object's model activities resume.
    At the end of an import for example.

    """
    sys.stdout.write('\n')
    sys.stdout.write('*'*79 + '\n')
    sys.stdout.write('* Objects activities :' + ' '*32 + 'Written Created Skipped *\n')
    sys.stdout.write('*'*79 + '\n')
    for model in STATS['objects'].keys():
        sys.stdout.write('%(name)-51s : %(written)7s %(created)7s %(skipped)7s' %
                STATS['objects'][model])
        sys.stdout.write('\n')
    sys.stdout.write('\n')

