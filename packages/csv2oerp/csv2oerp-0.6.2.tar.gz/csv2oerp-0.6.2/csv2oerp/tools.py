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
Functions tools module.

"""
import os
import sys
import unicode_csv
from constants_and_vars import NOISE

def strip_accent(string):
    """ Replace accents from string with non accented char

    """
    for char, accent_list in NOISE.iteritems():
        for accent in accent_list:
            string.replace(accent, char)
    return string

def clean_line(line, encode_from='utf-8'):
    """ Encode a list in ``encode_from`` encoding

    """
    return [clean(col, encode_from) for col in line]

def clean_lines(lines, encode_from='utf-8'):
    """ Encode a list of list in ``encode_from`` encoding

    """
    return [clean_line(line, encode_from) for line in lines]

def clean(string, encode_from='cp1252'):
    """ Clean a string by removing returns and double quotes.

    """
    try:
        string = unicode(string)
    except:
        pass
    string.replace('\n', ' ').replace('"', '\'')
    try:
        string = (string[-1] in [val for val in NOISE['']]) and string[:-1] or string
    except IndexError:
        pass

    return string 

def generate_code(filenames=(), header=True, mode='stdout',  delimiter=',',
        quotechar='"', encoding='utf-8'):
    """Return a template's skeleton code

    .. versionadded: 0.5.2

    prerequisites: 
        
        Having a columns header to the CSV file
    
    
    :param filenames: Name tuple of filenames to generate the importation code from
    :type filename: tuple
    :param header: First line column's title or not
    :type header: bool
    :param stdout: Printing mode (``stdout``, ``file``)
    :type stdout: str
    
    """
    if mode != 'stdout':
        if os.path.isfile(mode):
            print('A file called `%s` already existed. Overwrites ?' % mode)

        f = open(mode, 'wb')
    else:
        f = sys.stdout

    # HEADERS + SOME CALLBACKS
    f.write("""#!/usr/bin/env python
# -*- coding: utf8 -*-
################################################################################
#
# Copyright (c) 2012 STEPHANE MANGIN. (http://le-spleen.net) All Rights Reserved
#                    Stephane MANGIN <stephane.mangin@freesbee.fr>
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
import csv2oerp
from csv2oerp import get_ids, get_id, to_boolean, to_date

# OpenERP configuration
host = 'XXX.XXX.XXX.XXX'
port = 8069
dbname = 'database'
user = 'admin'
pwd = 'admin'
csv2oerp.connect(host, port, user, pwd, dbname)

""")
    for filename in filenames:
        # Get file name without extention, replace space by underscore
        var = unicode(os.path.splitext(filename)[0].replace(' ', '_'))
        with open(filename, 'r') as f_csv:
            lines = list(unicode_csv.Reader(f_csv, delimiter=delimiter, quotechar=quotechar, encoding=encoding))
        #===================================================================
        # Header
        #===================================================================
        f.write(u"#" + u"="*79 + "\n")
        f.write(u"# %s\n" % var)
        f.write(u"#" + u"="*79 + "\n")
        #===================================================================
        # Mapping
        #===================================================================
        i = 0
        for item in lines[0]:
            f.write(u"# %s: %s\n" % (i, item))
            i += 1
        #===================================================================
        # Functionnal mapping
        #===================================================================
        f.write(u"%s = csv2oerp.Import()\n" % var)
        f.write(u"%s.set_filename_to_import(\n    '%s', '%s', '%s', '%s')\n" %\
                (var, filename, delimiter, quotechar, encoding))
        f.write(u"%s.set_mapping({\n" % var)
        f.write(u"    'model name': [\n")
        f.write(u"        {\n")
        i = 0
        for item in lines[0]:
            f.write(u"            '%s': (%s, None, False),\n" % (item, i))
            i += 1
        f.write(u"        },\n")
        f.write(u"    ],\n")
        f.write(u"})\n")
        f.write(u"\n")

    for filename in filenames:
        #===================================================================
        # Start lines
        #===================================================================
        var = unicode(os.path.splitext(filename)[0].replace(' ', '_'))
        f.write(u"%s.start()\n" % var)

    #=======================================================================
    # Stats
    #=======================================================================
    f.write(u"\n")
    f.write(u"# Show statistics\n")
    f.write(u"csv2oerp.show_stats()\n")
    if mode != 'stdout':
        f.close()
    return

