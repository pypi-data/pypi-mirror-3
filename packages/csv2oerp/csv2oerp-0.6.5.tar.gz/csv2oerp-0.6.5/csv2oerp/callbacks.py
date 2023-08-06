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

How to use::

    Import the callback method and call it properly into the callback argument of
    a column type object, such as `Column`, `Relation`, `Custom`.

Concretlty, it's such as simple as that::

    >>> from csv2oerp.callbacks import cb_method
    >>> mapping = {
    ...         'res.parter_address': {
    ...                 'partner_id': Column(25, callback=cb_method('res.partner', 'name'))
    ...             }
    ...     }


"""
from constants_and_vars import STATS
import unicode_csv
from datetime import datetime

def get_line_from_table(csv_file, value, column, separator=',', quote='"', header=True):
    """Search for an equivalence between value from column ``col_referer``
    and ``value`` value, and return value from column ``col_return`` index at
    the same line as matching pair ``col_referer`` values.

    :param csv_file: The name of the CSV file to search into 
    :type csv_file: str
    :param value: The value to test
    :type value: type
    :param col_referer: The number of the column to compare to ``value``
    :type col_referer: int
    :param col_return: he number of the column to return if matches
    :type col_return: int
    :param separator: The CSV separator
    :type separator: str
    :param quote: The CSV quote
    :type quote: str
    :param header: CSV file has header
    :type header: bool
    :returns: list

    """

    res = []
    with open(csv_file, 'r') as f:
        filereader = unicode_csv.Reader(f, delimiter=separator, quotechar=quote)
        for line in filereader:
            if header:
                header = False
                continue
            if line[column] == value:
                res.append(line)
    
    return res

def search_table(csv_file, value, col_referer=0, col_return=1, 
        separator=',', quote='"', header=True):
    """Search for an equivalence between value from column ``col_referer``
    and ``value`` value, and return value from column ``col_return`` index at
    the same line as matching pair ``col_referer`` values.

    :param csv_file: The name of the CSV file to search into 
    :type csv_file: str
    :param value: The value to test
    :type value: type
    :param col_referer: The number of the column to compare to ``value``
    :type col_referer: int
    :param col_return: he number of the column to return if matches
    :type col_return: int
    :param separator: The CSV separator
    :type separator: str
    :param quote: The CSV quote
    :type quote: str
    :param header: CSV file has header
    :type header: bool
    :returns: list

    """

    res = []
    with open(csv_file, 'r') as f:
        filereader = unicode_csv.Reader(f, delimiter=separator, quotechar=quote)
        for item in filereader:
            if header:
                header = False
                continue
            if item[col_referer] == value:
                res.append(item[col_return])
    
    return res

def get_value_from_table(csv_file, col_referer=0, col_return=1,
        separator=',', quote='"', header=True):
    """Search for an equivalence between value from column ``col_referer`` index
    and and value from ``args[3]``, and return value from column ``col_return``
    index at the same line as matching pair ``col_referer`` values.
    
    .. note::
        
        This function is the search_table callback interface

    >>> 'address': Column(3, get_value_from_table('address.csv', 0, 1))
    
    :param csv_file: The name of the CSV file to search into 
    :type csv_file: str
    :param col_referer: The number of the column to compare to ``args[3]``
    :type col_referer: int
    :param col_return: he number of the column to return if matches
    :type col_return: int
    :param separator: The CSV separator
    :type separator: str
    :param quote: The CSV quote
    :type quote: str
    :param header: CSV file has header
    :type header: bool
    :returns: list

    """
    def _get_value_from_table(self, model, field, value, line):
        return search_table(csv_file, value, col_referer, col_return,
                separator, quote, header)

    return _get_value_from_table

def get_ids(model, fields, op='&'):
    """Return ``model`` which one or more ``fields`` matched column ``value``
   
    >>> 'partner_ids': Column(56, get_ids('res.partner.address', ['street', 'street2'], op='|'))
    [100, 102]
    
    :param args: lambda args (ie: [self, model ,field, content, line])
    :type args: list
    :param model: The name of the model to search into
    :type model: str
    :param field: The name of the model's field
    :type field: str
    :param value: The value to compare to
    :type value: str
    :returns: list

    """
    def _get_ids(self, b_model, b_field, b_value, b_line):
        search = []
        try:
            b_value = str(b_value).strip()
        except Exception:
            pass
        i = 1
        for field in fields:
            if i != len(fields):
                search.append(op)
                i += 1
            search.append((field, '=', b_value))

        try:
            res = self.server.execute(self.db, self.uid, self.pwd,
               model, 'search', search)
        except RuntimeError:
            return self._get_ids(b_model, b_field, b_value, b_line)
        if not res:
            self._logger.error(u"'%s' not found in fields %s from %s" %
                    (b_value, fields, model), extra=STATS[self._id])
        return res
    
    return _get_ids

def get_id(model, fields, op='&'):
    """Return ``model`` which one or more ``fields`` matched column ``value``
   
    >>> 'address_ids': (21, get_ids('res.partner', ['name']))
    [99]
    
    :param args: lambda args (ie: [self, model ,field, content, line])
    :type args: list
    :param model: The name of the model to search into
    :type model: str
    :param field: The name of the model's field
    :type field: str
    :param value: The value to compare to
    :type value: str
    :returns: int

    """
    def _get_id(*args):
        res = get_ids(model, fields, op)(*args)
        return res and res[0] or False
    
    return _get_id

def get_objects(model, fields, op='&'):
    """Return ``model`` instance which ``fields``'s value matched ``value``
    
    >>> 'parent_name': Column(2, get_objects('res.partner.address', ['ref'])[0]['name'])
    ['Toto']
    
    :param model: The name of the model to search into
    :type model: str
    :param fields: The name of the model's field
    :type fields: str
    :param value: The value to compare to
    :type value: str
    :returns: list

    """

    def _get_objects(self, b_model, b_field, b_value, b_line):
        return self.server.execute(self.db, self.uid, self.pwd,
               model, 'read', get_id(model, fields, op))

    return _get_objects

def get_field(model, fields, field, op='&'):
    """Return ``model``'s ``field`` field which ``fields``'s value matched ``value``
    
    >>> 'parent_name': Column(2, get_field('res.partner.address', ['ref'], 'name')
    ['Toto']
    
    :param model: The name of the model to search into
    :type model: str
    :param fields: The name of the model's field
    :type fields: str
    :param field: The desire field's value to returned
    :type field: str
    :param value: The value to compare to
    :type value: str
    :returns: dict

    """
    
    def _get_field(*args):
        res = get_objects(model, fields, op=op)(*args)
        res = res and res[0]
        return res and field in res and res[field]

    return _get_field

def get_fields(model, fields, op='&'):
    """Return ``model`` instance which one or more ``fields`` matched column ``value``
    
    >>> 'parent_name': Column(2, get_fields('res.partner.address', ['ref']))
    'Toto'
    
    :param model: The name of the model to search into
    :type model: str
    :param fields: The name of the model's field
    :type fields: str
    :param value: The value to compare to
    :type value: str
    :returns: list

    """

    def _get_fields(self, b_model, b_field, b_value, b_line):
        ids = get_ids(model, fields, op)(self, b_model, b_field, b_value, b_line)
        res = self.server.execute(self.db, self.uid, self.pwd, model, 'read', ids)
        return res

    return _get_fields

def to_boolean(true='1', false='0', none=''):
    """Return a boolean depending from the input value.
    
    >>> 'field': Column(2, to_boolean('Y', 'N', ''))
    
    :param mode: First char will be used if value is True and second if False
    :type mode: str
    :param true_values: The name of the model to search into
    :type true_values: str
    :param false_values: The name of the model's field
    :type false_values: str
    :returns: bool (or str)

    """
    def _to_boolean(self, model, field, value, line):
        if value == str(true):
            return True
        elif value == str(false):
            return False
        elif value == str(none):
            return None

    return _to_boolean

def to_date(formatted='%Y-%m-%d'):
    """Check for a valid date and convert if needed before returning the value

    >>> 'inserted_date': Column(6, to_date())
    
    :param formatted: Format of this date
    :type formatted: str
    :returns: str

    """
    def _to_date(self, model, field, value, line):
        date = value
        try:
            date = str(value.split('\n')[0])
        except:
            pass
        if date in ('0000-00-00', '0000/00/00', '00-00-0000', '00/00/0000', ''):
            return ''
        date = datetime.strptime(date, formatted)
        return date.strftime('%Y-%m-%d')

    return _to_date

def city_cedex(res=None, cedex_code=False):
    """Check if a cedex code is in the town name.
    Return the relative string to ``res`` argument
    
    from 'Paris Cedex 9'
    >>> 'city':  Column(6, city_cedex('city'))
    'PARIS'
    >>> 'cedex': Column(6, city_cedex('cedex'))
    'CEDEX 9'
    
    :param res: Relative string returned
    :type res: str
    :param cedex_code: Returns only code or full code ('6', 'CEDEX 6')
    :type cedex_code: str
    :returns: str or tuple

    """
    def _city_cedex(self, model, field, value, line):
        string = value.upper()
        cedex = ""

        if string.count('CEDEX'):
            string = string.split('CEDEX')[0].strip(' ')
            try:
                cedex = "CEDEX %s" % int(string.split('CEDEX')[1].strip(' '))
            except IndexError:
                cedex = "CEDEX"
            except ValueError:
                cedex = 'CEDEX'
        if res == 'city':
            return string
        elif res == 'cedex':
            return cedex
        else:
            return (string, cedex)

    return _city_cedex


