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
csv2oerp is intended to be used to simplify data migration from CSV to OpenERP.

"""

import os
import sys
import xmlrpclib
import copy
import logging
import time
import logging.handlers
from copy import copy
from copy import deepcopy
from optparse import OptionParser
import exceptions
from pprint import pformat
import tools
import fields
import unicode_csv

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

def set_global_connection(host=HOST, port=PORT, user=USER, pwd=PWD, dbname=DB):
    """Set globals constants needed to initialize a connection to openerp

    .. deprecated:: 0.5.3
       Use :func:`connect` instead.
    
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

    .. versionadded:: 0.5.3

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


class Import_session(object):
    """Main class which provides the functionnal part of the importation process.
    
    .. note:: `sys.argv` integrated provides a command line parser.

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

    def __init__(self, **kw):
        
        # Unique id of this import
        self._id = str(time.time())
        
        # Pass args to sys.argv
        self._arg_treatments()
        self._syslog_mode = False
        self._columns_mapping = {}
        self._processed_lines = None
        self._server = None
        self._uid = None
        self._preconfigure = None
        self._relationnal_prefix = 'REL_'
        self._current_mapping = None
        self._lang = 'fr_FR'
        self._encoding = 'utf-8'
        self._logger = None
        
        # Importation options
        self._offset = 'offset' in kw and kw['offset'] or self._opts.offset
        self._limit = 'limit' in kw and kw['limit'] or self._opts.limit
        self.quiet = 'quiet' in kw and kw['quiet'] or self._opts.quiet
        self.verbose = 'verbose' in kw and kw['verbose'] or self._opts.verbose
        self.debug = 'debug' in kw and kw['debug'] or self._opts.debug
        
        # Open socket
        self._host = self._opts.host
        self._port = self._opts.port
        self._db = self._opts.dbname
        self._user = self._opts.username
        self._pwd = self._opts.password
        
        # Global statistics
        STATS[self._id] = {
            'importfile': None,
            'actual_line': 0,
            'col_num': 0,
            'line_num': 0,
            'errors': 0,
            'warnings': 0,
            'line_skipped': 0,
            'line_done': 0,
            'object_skipped': 0,
            'object_created': 0,
            'object_written': 0
            }

    #===========================================================================
    # Command line argument method
    #===========================================================================
    def _arg_treatments(self):
        parser = OptionParser()
        parser.add_option("-o", "--offset",
                action="store",
                type="int",
                dest="offset",
                default=0,
                help="Offset (Usually used for header omission, default=1)")
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
        (self._opts, args) = parser.parse_args()

    def __del__(self):
        """ Cleanly clear socket and files connections

        """
        # TODO: NOT FUNCTIONNAL
        try:
            self._server.close()
            del self._server
        except Exception:
            pass

    def start(self, *args, **kwargs):
        """Start the importation process

        """
        # Initialize logger
        if not self._logger:
            self.set_logger()
        
        # Initialize connection to OpenERP
        self._open_connection()
        
        # Check for mapping errors
        self.check_mapping()

        # Finally launch the import
        return self._launch_import(*args, **kwargs)
    
    #===========================================================================
    # Accessors
    #===========================================================================
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
        """ Return the current password for this session.

        """
        return self._pwd
    
    @property
    def lines(self):
        """Getting all lines from CSV parser.
        
        :returns: list

        """
        return deepcopy(list(self._lines()))

    @property
    def offset(self):
        """Getting line offset start.

        """
        return self._offset

    @property
    def limit(self):
        """Getting treatment line limitation.

        """
        return self._limit
    
    @property
    def mapping(self):
        """Getting columns mapping configuration.

        """
        return self._columns_mapping

    @property
    def lang(self):
        """Getting current language.

        """
        return self._lang

    def set_mapping(self, mapping):
        """ Columns mapping configuration.

        See ``Creation of your Columns mapping`` for further details.
        
        """
        STATS[self._id]['importfile'] = self._filename
        self._current_mapping = mapping

    def set_lang(self, code='fr_FR'):
        """ Set current lang
        
        :param code: The standardized code of a language
        :type code: str

        """
        self._lang = code
    
    def set_logger(self, name=None, syslog=False):
        """ Configure and initialize the logger facility

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
        if syslog or self._syslog_mode:
            self._hdlr = logging.handlers.SysLogHandler(
                address=self._syslog_mode,
                facility=logging.handlers.SysLogHandler.LOG_USER
            )
        else:
            self._hdlr = logging.FileHandler(logfile)

        # Format du logger
        STATS[self._id]['importfile'] = self._filename
        formatter = logging.Formatter(FORMAT)
        self._hdlr.setFormatter(formatter)
        self._logger.addHandler(self._hdlr)
        if self.debug:
            self._logger.setLevel(logging.DEBUG)
        else:
            self._logger.setLevel(logging.INFO)
        
        if not self.quiet:
            if self.verbose:
                logging.basicConfig(format=FORMAT)
    
        self._logger.info("Logger set to '%s'" % basename, extra=STATS[self._id])
        return True

    def set_file_to_import(self, filename, delimiter=',', quotechar='"', encoding='utf8'):
        """ Set the CSV file to use.
    
        .. deprecated:: 0.5.3
           Use :func:`set_input_file` instead.

        """
    
    def set_input_file(self, filename, delimiter=',', quotechar='"', encoding='utf8'):
        """ Set the CSV file to use.
        
        .. versionadded:: 0.5.3

        """
        global STATS
        self._filename = filename
        STATS[self._id]['importfile'] = self._filename
        self._separator = delimiter
        self._quote = quotechar
        self._encoding = encoding
        # Initialize logger
        if not self._logger:
            self.set_logger()
        return True
    
    set_filename_to_import = set_input_file

    def _name_get(self, model, id_=False, data={}):
        if not id_ and data:
            return 'name' in data and data['name']\
                or 'nom' in data and data['nom']\
                or 'surname' in data and data['surname']\
                or 'prenom' in data and data['prenom']\
                or 'state' in data and data['state']\
                or 'etat' in data and data['etat']\
                or 'value' in data and data['value']\
                or 'valeur' in data and data['valeur']\
                or 'id' in data and data['id']\
                or data.itervalues().next()
        elif id_:
            try:
                return self.execute(self.db, self.uid, self.pwd, model, 'name_get', id_)
            except:
                pass
        
        return "NONAME"

    def set_preconfigure_script(self, filename):
        """ Declare a parrallel script which will be called before importation.

        It must implement a main method which take in params the instance of 
        Import class, it will be able to use all facilities from Import class.

        It must return a list of lines (lines already list too)

        """
        self._preconfigure = filename

    def set_syslog(self, arg=True):
        """ Set if syslog must be used instead of a log file.

        """
        self._syslog_mode = arg

    def get_line_from_index(self, line_num):
        """ Retrieve lines which have value at column

        :param line_num: The index of line
        :type line_num: value
        :returns: tuple

        """
        i = 1
        for line in self.lines:
            if i == int(line_num):
                return line
            i += 1
        raise IndexError
    
    def get_lines_from_value(self, column, value):
        """ Retrieve lines which have value at column

        :param column: The column index
        :type column: int
        :param value: The value to compare from
        :type value: value
        :returns: tuple

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
        try:
            url = 'http://%s:%s/xmlrpc/' % (self.host, self.port)
            sock_common = xmlrpclib.ServerProxy(url + 'common', allow_none=True)
            self._uid = sock_common.login(self.db, self.user, self.pwd)
            self._server = xmlrpclib.ServerProxy(url + 'object', allow_none=True)
        except Exception as error:
            self._logger.error("connection problem : %s" % error, extra=STATS[self._id])
            sys.exit(EXIT_ERROR)
        
    def connect(self, host=HOST, port=PORT, user=USER, pwd=PWD, dbname=DB):
        """Set constants needed to initialize a connection to OpenERP.

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

        """
        self._host = host
        self._port = port
        self._user = user
        self._pwd = pwd
        self._db = dbname

    #===========================================================================
    # Search and Get methods
    #===========================================================================
    def search(self, model, criteria, context):
        """Return a list of IDs of records matching the given criteria
        in ``data`` parameter, ``data`` must be of the form ``{'name': 'Agrolait'}``.
        ``search`` define wich must be of the form ``['name', 'firstname']``

        >>> self._search('res.partner', {'name': 'Agrolait'}, ['name'])
        [3]

        :param model: Name of the OERP class model
        :type model: str
        :param data: Data dictionnary to transmit to OERP create/write method
        :type data: dict
        :param search: List of fields to be used for search
        :type search: list
        :returns: a list of IDs
        
        """
        return NotImplemented

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
                content += " "+STATS[self._id]['actual_line'][ind]
        elif column is not None:
            try:
                content = STATS[self._id]['actual_line'][column]
            except IndexError:
                raise exceptions.ColumnIndexError(model,
                        'Invalid column index `%s`' % column, self._logger)
        else:
            content = callback
        return content
    
    def _search(self, model, data, search=None):
        global STATS
        STATS[self._id]['importfile'] = self._filename
        if search is None:
            search = []
        if not data:
            return [] 
        res = []
        list_search = []
        self._logger.debug('<%-25s> search:%s' % (model, search),
                extra=STATS[self._id])

        for item in search:
            if item in data.keys():
                list_search.append((item, '=', data[item]))

        self._logger.debug('<%-25s> list_search:%s' % (model, list_search),
                extra=STATS[self._id])

        for (item, sign, val) in copy(list_search):
            if val in ("", " ", None):
                list_search = []

        if list_search:
            res = self.server.execute(self.db, self.uid, self.pwd, model,
                    'search', list_search, 0, False, False, {'lang': self.lang})
            self._logger.debug('<%-25s> search result %s' % (model, res),
                    extra=STATS[self._id])
        
        return res

    #===========================================================================
    # Relations methods
    #===========================================================================
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
                    res = self._search(model.split('::')[1], data, search)
                    if res\
                    and self.mapping[each_model]['CREATED::id'] in res:
                        self._logger.debug('<%20s> UNIQUE Replacement' %\
                                model, extra=STATS[self._id])
                        return self.mapping[each_model]['CREATED::id']
        return False

    def _create_relation(self, line, model):
        """Launch a sub function to import the new relation id

        """
        id_ = False
        try:
            data_rels = self.mapping[model]
        except:
            raise Exception("'%s' relation not found !" % model)

        if not isinstance(data_rels, list):
            data_rels = [data_rels]
        
        for data_rel in data_rels:
            if 'CREATED::id' in data_rel:
                id_ = data_rel['CREATED::id']
            else:
                if 'CREATED::search' in data_rel:
                    search_rel = data_rel['CREATED::search']
                else:
                    try:
                        search_rel = self._convert(line, model, data_rel)
                    except exceptions.SkipObjectException:
                        self._logger.info("<%-20s> Object skipped" % model, extra=STATS[self._id])
                        STATS['objects'][model]['skipped'] += 1
                        STATS[self._id]['object_skipped'] += 1
                        return False
                
                # If relation is unique inside actual model
                if _get_special_actions(model)['unique']:
                    id_ = self._unique_relation(model, data_rel, search_rel)
                # If relation is not updating
                elif _get_special_actions(model)['noupdate']:
                    id_ = self._noupdate_relation(model, data_rel, search_rel)
                
                if not id_:
                    (state, model, id_) = self._create(model,
                            data_rel, search_rel)
                data_rel['CREATED::id'] = id_
        return id_

    #===========================================================================
    # Inline actions
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
                        raise exceptions.SkipLineException('%s is required' % key.split('::')[1])
                    else:
                        # rename key becomed unusefull
                        data[key.split('::')[1]] = data[key]
                        del data[key]
                    self._logger.debug('<%-25s> processing %s=%s' % (model, key,
                        returned_value), extra=STATS[self._id])
                else:
                    content = self._get_content(model, column, callback)
                    if content:
                        data[key.split('::')[1]] = data[key]
                        del data[key]
                        self._logger.debug('<%-25s> processing %s=%s' % (model,
                            key, content), extra=STATS[self._id])
                    else:
                        raise exceptions.SkipLineException(model)


    def _replace_line(self, line, data, model):
        """Dynamic method to modify/replace current field by another one(s)

        .. warning:: DO NOT WORK WITHOUT HEAVY BUGS

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
                            key), extra=STATS[self._id])
                        for item, value in returned_value.iteritems():
                            self._logger.debug('<%-25s> modifying "%s" to %s' %\
                                    (model, item, value), extra=STATS[self._id])
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
                        content), extra=STATS[self._id])

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
                        raise exceptions.SkipObjectException(model)
                    else:
                        # Finally remove key unusefull and create new one with
                        # correct tuple without callback
                        content = (column, None, searchable)
                        data[key.split('::')[1]] = content
                        del data[key]
                        self._logger.debug('<%-25s> processing %s=%s' % (model,
                            key, returned_value), extra=STATS[self._id])
                else:
                    self._logger.debug('<%-25s> processing %s=%s' % (model, key,
                        content), extra=STATS[self._id])
    
    def _route_line(self, line, data, model):
        for key, value in data.items():
            if key.startswith(ACTION_PATTERN['router']):
                (column, callback, searchable) = value
                content = self._get_content(model, column, callback)
                if callback is not None:
                    returned_value = self._get_callback(line, model, callback,
                            key, content)
                    if returned_value:
                        raise exceptions.SkipObjectException(model)
                    else:
                        # Finally remove key unusefull and create new one with
                        # correct tuple without callback
                        content = (column, None, searchable)
                        if key.split('::')[1] != '':
                            data[key.split('::')[1]] = content
                        del data[key]
                        self._logger.debug('<%-25s> processing %s=%s' % (model,
                            key, returned_value), extra=STATS[self._id])
                else:
                    self._logger.debug('<%-25s> processing %s=%s' % (model, key,
                        content), extra=STATS[self._id])
    
    #===========================================================================
    # Models and fields verifications
    #===========================================================================
    def _is_model(self, model):
        """Check model validity
       
        .. versionadded: 0.5.1

        :returns: bool

        :returns: bool

        """
        res = self.server.execute(self.db, self.uid, self.pwd,
                'ir.model', 'search', [('model', '=', model)])
        return bool(res)
    
    def _is_model_defined(self, model):
        """Return if model is in the mapping

        .. versionadded: 0.5.1

        """
        return model in [mod.count['::'] and mod.split('::')[0] or mod for mod in self.mapping.keys()]

    def _is_readonly(self, model ,field):
        """Check field requirability
        
        .. versionadded: 0.5.3

        :returns: bool

        """
        res = self.server.execute(self.db, self.uid, self.pwd, model, 'fields_get')
        if 'readonly' in res:
            return True
        return False

    def _is_required(self, model ,field):
        """Check field requirability
        
        .. versionadded: 0.5.3

        :returns: bool

        """
        res = self.server.execute(self.db, self.uid, self.pwd, model, 'fields_get')
        if 'required' in res:
            return True
        return False

    def _is_field(self, model, attr):
        """Check field validity
        
        .. versionadded: 0.5.1

        :returns: bool

        """
        for pattern in ACTION_PATTERN.values():
            if attr.count(pattern):
                attr.replace(pattern, '')
        res = self.server.execute(self.db, self.uid, self.pwd, model, 'fields_get')
        if attr in res:
            return True
        return False

    def check_mapping(self):
        """Check mapping for semantics errors.http://www.openerp.com/forum/topic31343.html
        Also check for required and readonly fields.

        """
        mapping = deepcopy(self._current_mapping)
        title = "Errors occured during mapping check :\n___________________\n\n"
        res = ""
        # Mapping must be iterable throught pair of item
        if not hasattr(mapping, 'iteritems'):
            res += "\t* Mapping must be iterable throught pairs of item\n\n"
        else:
            for model, columns in mapping.iteritems():
                # Check if model exist
                if model.startswith(self._relationnal_prefix):
                    model = model.split('::')[1]
                    columns = [columns]
                    self._logger.info("Checking relationnal model '%s' ..." % model, extra=STATS[self._id])
                elif model.startswith('NO_CREATE'):
                    model = model.split('::')[1]
                    self._logger.info("Checking model (without creation) '%s' ..." % model, extra=STATS[self._id])
                elif model.startswith('NO_UPDATE'):
                    model = model.split('::')[1]
                    self._logger.info("Checking model (without update) '%s' ..." % model, extra=STATS[self._id])
                else:
                    self._logger.info("Checking model '%s' ..." % model, extra=STATS[self._id])
                if not self._is_model(model):
                    res += "\t* '%s' does not exist, \n\n" % model
                    continue
                
                # Check if value is a well formed tuple
                for obj in columns:
                    if not hasattr(obj, 'iteritems'):
                        res += "\t* List of fields must be iterable throught\
pairs of item and objects (non relationnal) must be in a list.\n\n"
                    else:
                        for attr, tuple_val in deepcopy(obj).iteritems():
                            self._logger.debug("Checking field '%s'" % attr,
                                    extra=STATS[self._id])
                            for patt in ACTION_PATTERN.values():
                                if attr.count(patt):
                                    attr = attr.split('::')[1]
                            
                            if attr != 'id' and attr and not self._is_field(model, attr):
                                res += "\t* '%s' '%s' does not exist, \n\n" %\
                                        (model, attr)
                                continue
                            try:
                                if callable(tuple_val):
                                    tuple_val = tuple_val()[0]
                                (column, lambda_func, searchable) = tuple_val
                                if column is None and not callable(lambda_func):
                                    res += "\t* You must indicate either a column\
number or a function or both in a field definition, \n\n"
                            except:
                                res += "\t* '%s' '%s' definition is not well\
formed, \n\n" % (model, attr)

                            required = self._is_required(model, attr)
                            obj[attr] = (column, lambda_func, searchable, required)

        if res != "":
            raise Exception(title + res)
        else:
            return True
    

    #===========================================================================
    # Creation methods
    #===========================================================================
    def create(self, model, data, search=None):
        """Object's automatic and abstracted creation from model

        Logged public method
        
        :param model: Name of the OERP class model
        :type model: str
        :param data: Data dictionnary to transmit to OERP create/write method
        :type data: dict
        :param search: List of fields to be used for search
        :type search: list
        :returns: int 
        
        """
        if search is None:
            search = []
        if not data:
            return []
        (state, model, id_) = self._create(model, data, search)
        return id_

    def _create(self, model, data, search=None):
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
        
        """
        global STATS
        STATS[self._id]['importfile'] = self._filename
        update = True
        if 'CREATED::search' in data:
            search = data['CREATED::search']
            data.pop('CREATED::search')
        create = True
        if model.count('NO_UPDATE'):
            update = False
        if model.count('NO_CREATE'):
            create = False
        if model.count('::'):
            model = model.split('::')[1]
        res = [False]
        error = None
        state = 'old'

        # Manage null values
        for attr, value in data.items():
            try:
                data[attr] = value.strip(' \t\n\r\r\n')
            except:
                pass
            if not data[attr]:
                del data[attr]

        search = self._search(model, data, search)

        if 'CREATED::id' in data and data['CREATED::id']:
            res = [int(data['CREATED::id'])]
            del data['CREATED::id']
            self._logger.info("<%-25s> ALREADY%s" % (model, res),
                    extra=STATS[self._id])
        else:
            if 'id' in data:
                search = [int(data['id'])]
                del data['id']

            self._logger.debug('<%-25s> data:%s' % (model, data),
                    extra=STATS[self._id])

            # If data is empty SKIPPED
            if not data:
                self._logger.warning("<%-25s> Null values" % model,
                        extra=STATS[self._id])
                STATS['objects'][model]['skipped'] += 1
                res = [False]
            else:
                try:
                    if not search:
                        state = "new"
                        if create:
                            res = [self.server.execute(self.db,
                                self.uid, self.pwd, model, 'create', data,
                                {'lang': self.lang})]
                            self._logger.info("<%-25s> CREATE%s" % (model, res),
                                    extra=STATS[self._id])
                            STATS[self._id]['object_created'] += 1
                            STATS['objects'][model]['created'] += 1
                        else:
                            self._logger.info("<%-25s> NO CREATE %s" % (model,
                                self._name_get(model, data=data)),
                                extra=STATS[self._id])

                    else:
                        state = 'old'
                        res = search
                        if update:
                            self.server.execute(self.db,
                                self.uid, self.pwd, model, 'write', res, data,
                                {'lang': self.lang})
                            self._logger.info("<%-25s> UPDATE%s"% (model, res),
                                    extra=STATS[self._id])
                            STATS[self._id]['object_written'] += 1
                            STATS['objects'][model]['written'] += 1
                        else:
                            self._logger.info("<%-25s> NO UPDATE %s" % (model,
                                self._name_get(model, res[0])),
                                extra=STATS[self._id])
                    
                except xmlrpclib.Fault as err:
                    try:
                        error = unicode(err.faultString.split('\n')[-2])
                    except:
                        error = unicode(err.faultString + (err.faultCode or ''))\
                            or 'Unknown error (xmlrplib.Fault)'
                except Exception as err:
                    error = unicode(err) or 'Unknown error (Exception)'
        if error:
            res = [False]
            state = 'none'
            self._logger.error("<%-25s> id:%s %s" %\
                    (model, search, error), extra=STATS[self._id])
            self._logger.debug("<%-25s> id:%s|state:%s|%s" %\
                (model, search, state, pformat(data)), extra=STATS[self._id])
            STATS[self._id]['warnings'] += 1
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
        global STATS

        try:
            search = self._convert(line, model, self.mapping[model])
            self._columns_mapping[model]['search'] = search
        except exceptions.SkipObjectException:
            self._logger.info("<%-20s> Object skipped" % model, extra=STATS[self._id])
            STATS['objects'][model]['skipped'] += 1
            STATS[self._id]['object_skipped'] += 1
            return False
        return True
    

    #===========================================================================
    # Column's value retreiver and process launcher
    #===========================================================================
    def _register_models(self):
        """ Keeping objects actions to stats further

        .. versionadded: 0.6

        """
        for model in self._current_mapping.iterkeys():
            if model.count('::'):
                model = model.split('::')[1]
            if model not in STATS['objects']:
                STATS['objects'][model] = {
                        'name': model, 
                        'written': 0,
                        'created': 0,
                        'skipped': 0,
                        'error': 0,
                        }

    def _lines(self):
        """Reader a line generator from self.filename. Apply offset and limit
        restriction.
        
        .. versionadded: 0.6

        .. note: Call th preconfigure script and execute if any.

        """
        if self._filename is None:
            raise Exception("File to import has not been set !")
        with open(self._filename, 'r') as f:

            # Getting lines to import
            ucsv = unicode_csv.Reader(f, delimiter=self._separator, quotechar=self._quote)
            self._processed_lines = tools.clean_lines(ucsv)
            self._logger.info("Lines: %s" % int(len(self._processed_lines)),
                    extra=STATS[self._id])

            # Applying `offset` limitation
            if self._offset:
                self._processed_lines = self._processed_lines[self._offset:]
                STATS[self._id]['line_skipped'] += self._offset
                self._logger.info("Offset: %s" % self.offset, extra=STATS[self._id])
            
            # Applying `limit` limitation
            self._processed_lines = self._limit and self._processed_lines[:self._limit] or self._processed_lines
            self._logger.info("Limit: %s" % int(len(self._processed_lines)),
                    extra=STATS[self._id])
            if self._preconfigure:
                script_to_import, script_extention = os.path.splitext(self._preconfigure)
                if script_extention == '.py':
                    self._processed_lines = __import__(script_to_import).main(self)

            # Init line incrementor
            STATS[self._id]['line_num'] = self._offset
           
            # LINE ITERATION
            #===============================================================
            for line in self._processed_lines:
                yield line

        raise StopIteration

    def _convert(self, line, model, data, encoding="UTF-8"):
        """Search for vals in line

        """
        global STATS
        search = []
        ToRemove = []
        
        if 'CREATED::search' in data.iterkeys():
            self._logger.debug('<%-25s> previous search:%s' % (model,
                data['CREATED::search']), extra=STATS[self._id])
            return data['CREATED::search']
        
        # Record function functionnality integration and type verification
        #=======================================================================
        for field, column in deepcopy(data).iteritems():

            if isinstance(column, fields.BaseField):
                # Result of Column call
                new_tuple, actions = column()
                if actions:
                    del data[field]
                    field = "%s::%s" % (','.join(actions).upper().strip(','), field)

                data[field] = new_tuple

            elif not isinstance(column, tuple):
                raise Exception('Field\'s column definition must be tuple\
 or Column class')

        # Exceptions if any
        #=======================================================================
        self._skip_line(line, data, model, type_='skip')
        self._skip_line(line, data, model, type_='required')
        self._ignore_object(line, data, model)
        self._replace_line(line, data, model) 
        self._route_line(line, data, model) 

        # Main process loop
        #=======================================================================
        for item, tuple_val in data.iteritems():

            # Relationnal key, do not process until remove the prefix
            current_model = model

            if current_model.startswith(self._relationnal_prefix)\
                    or current_model.startswith('NO_UPDATE')\
                    or current_model.startswith('NO_CREATE'):
                current_model = model.split('::')[1]
            
            column = -1 # Default
            searchable = False
            try:
                required = False
                (column, callback, searchable) = tuple_val
            except:
                (column, callback, searchable, required) = tuple_val
            STATS[self._id]['col_num'] = int(bool(column))
            
            content = self._get_content(model, column, callback)
            
            if callback is not None:
                if callable(callback):
                    content = self._get_callback(line, current_model, callback,
                            item, content)
                else:
                    STATS[self._id]['errors'] += 1
                    self._logger.error('callback must be a function',
                            extra=STATS[self._id])
                    raise exceptions.SkipLineException()

                # If result is a relation, so launch relation creation function
                if isinstance(content, str) and content.startswith("REL_"):
                    self._logger.debug('<%-25s> ==REL %s==' % (model, content),
                            extra=STATS[self._id])
                    content = self._create_relation(line, content)
                    self._logger.debug('<%-25s> ==END %s==' % (model, content),
                            extra=STATS[self._id])

            elif column is None:
                STATS[self._id]['errors'] += 1
                self._logger.error('callback is mandatory',
                        extra=STATS[self._id])
                raise exceptions.SkipLineException()
            #else:
            #    self._logger.error('Callback or columns is mandatory.',
            #        extra=STATS[self._id])
            
            self._logger.debug('<%-25s> process %s=%s' % (model, item, content),
                    extra=STATS[self._id])
                
            # Add this item to search criteria
            if searchable:
                search.append(item)

            # Manage null values
            #===================================================================
            try:
                data[item] = content.strip(' \t\n\r\r\n')
            except:
                data[item] = content
            #Cleaning dict items with null value
            if data[item] not in (0, '0') and not data[item]:
                if required:
                    raise exceptions.RequiredFieldError(
                        '%s %s field is required. Skipped.' % (model, item))
                ToRemove.append(item)

        # Cleaning data from given attributes
        for item in ToRemove:
            del data[item]
        
        # Adding this to indicate that this field has been loaded
        data['CREATED::search'] = search
        return search
    
    def _launch_model_import(self):
        """Start model importation.

        """
        for model, datas in self.mapping.items():

            try:
                
                if model.startswith(self._relationnal_prefix):
                    continue

                for data in datas:
                    search = self._convert(STATS[self._id]['line_num'],
                            model, data)
                    (state, model, id) = self._create(model,
                            data, search)
            
            except exceptions.RequiredFieldError as error:
                # Required field not found
                continue
            except exceptions.SkipObjectException as error:
                self._logger.info("<%-20s> Object skipped" % model, extra=STATS[self._id])
                STATS['objects'][model]['skipped'] += 1
                STATS[self._id]['object_skipped'] += 1
                # Next object
                continue
            except exceptions.SkipLineException as error:
                self._logger.info("<%-20s> Line skipped(%s)" % (model, error), extra=STATS[self._id])
                STATS[self._id]['line_skipped'] += 1
                # Next line
                break 
            
#                       except exceptions.NotConsistentError as error:
#                           self._logger.info("""
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
#            """ % (error, STATS[self._id]['line_num'], model, state, search,
#                        pformat(data)), extra=STATS[self._id])
            #except Exception as error:
            #    STATS[self._id]['errors'] += 1
            #    LOGGER.error("%s %s" % (model, error),extra=STATS[self._id])
            finally:
                # Keep line incrementation
                STATS[self._id]['line_done'] = STATS[self._id]['line_num']
    
            # END OBJECTS ITERATION
            #===========================================================
            #self._logger.info("next line", extra=STATS[self._id])

    def _launch_import(self, *args, **kwargs):
        """Main function that launch the importation process

        """
        global STATS 
        exit = False
        # Checking mapping
        if self._current_mapping is None:
            raise Exception("No mapping has been defined, use 'setMapping' first !")
            exit(1)
        
        STATS[self._id]['importfile'] = self._filename
        if not self.quiet:
            sys.stdout.write('\n')
            sys.stdout.write('*'*79 + '\n')
            sys.stdout.write('* Processing %-64s *\n' % self._filename)

        # Instanciate connection
        if DB and not self.db:
            self.set_connection(HOST, PORT, USER, PWD, DB)
        elif not DB and self.db:
            pass
        elif not DB and not self.db:
            raise Exception('You have to configure a connection to an existing OpenERP instance.')
        
        # Register models on global statistics
        self._register_models()
        
        #=======================================================================
        # Open file, call preconfigure if given in arg
        #=======================================================================
        try:
            for line in self.lines:
                # Keeping stats 
                STATS[self._id]['actual_line'] = line
                STATS[self._id]['line_num'] += 1
                
                # Instanciate a dictionnary which will receive values
                # from CSV line according to columns mapping
                self._columns_mapping = deepcopy(self._current_mapping)
                self._logger.debug('+++++ NEW LINE +++++',
                        extra=STATS[self._id])
                self._launch_model_import()

            self._logger.info("END import", extra=STATS[self._id])
            
        except KeyboardInterrupt:
            self._logger.error('CTRL^C caught !', extra=STATS[self._id])
            exit = True

        finally:
            if not self.quiet:
                sys.stdout.write('*'*79 + '\n')
                sys.stdout.write('Object Skipped %(object_skipped)11s' %
                        STATS[self._id])
                sys.stdout.write(' | Line Skipped %(line_skipped)11s' %
                        STATS[self._id])
                sys.stdout.write(' | Total Errors %(line_skipped)10s' %
                        STATS[self._id])
                sys.stdout.write('\n')
                sys.stdout.write('Object Created %(object_created)11s' %
                        STATS[self._id])
                sys.stdout.write(' | Line Done    %(line_done)11s' %
                        STATS[self._id])
                sys.stdout.write(' | Total Warnings%(line_skipped)9s' %
                        STATS[self._id])
                sys.stdout.write('\n')
                sys.stdout.write('Object Written %(object_written)11s' %
                        STATS[self._id])
                sys.stdout.write('\n')
                
            STATS[self._id] = {
                'importfile': None,
                'actual_line': 0,
                'line_num': 0,
                'col_num': 0,
                'errors': 0,
                'warnings': 0,
                'line_skipped': 0,
                'line_done': 0,
                'object_skipped': 0,
                'object_created': 0,
                'object_written': 0,
                }

            if exit:
                del self
                sys.exit(1)
        
        return True
    
    #===========================================================================
    # Public methods
    #===========================================================================
    def log(self, level, msg, line=None, model=None):
        """Allow to use the internal logger to log special message outside of
        the importation process.

        """
        global STATS
        STATS[self._id]['importfile'] = self._filename
        if level not in ('debug', 'info', 'warning', 'error'):
            raise Exception("logger, invalid level")
        old_line = STATS[self._id]['line_num']
        if line:
            STATS[self._id]['line_num'] = line
        if not self._logger:
            self.set_logger()
        getattr(self._logger, level)("CP %s%s" % (model and '<%-25s> ' %\
                model or '', msg), extra=STATS[self._id])
        STATS[self._id]['line_num'] = old_line



def purge_stats():
    """Re-initialize objects activities resume

    """
    global STATS
    STATS = {
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

