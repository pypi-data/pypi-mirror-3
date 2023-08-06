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

def get_ids(args, model, field):
    """Return ``model`` which ``fields``'s value matched ``args[3]`` value
   
    >>> 'partner_ids': Column(56, get_ids('res.partner.address', 'city'))
    
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
    def _get_ids(self, model, field, value, line):

        try:
            value = value.strip()
        except:
            pass
        res = self.search(model, {field: value}, [field])
        if not res:
            self.logger.warning(u'get_ids(%s, %s): No object found for value `%s` on model' %
                    (model, field, value), extra=STATS)
        return res

    return _get_ids

def get_id(model, field):
    """Return ``model`` which ``fields``'s value matched ``args[3]`` value
   
    >>> 'address_ids': (21, get_ids('res.partner', 'city'))
    
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
        res = get_ids(model, field)(*args)
        return res and res[0] or False
    
    return _get_id


def to_boolean(mode='on',
        true_values=('O', 'Y', '1', 'o', 'y', 'true', 'True'),
        false_values=('0', 'N', '2', 'n', 'false', 'False')):
    """Return a boolean depending from the input value.
    
    >>> 'field': Column(2, to_boolean()
    
    :param mode: lambda args (ie: [self, model ,field, content, line])
    :type mode: list
    :param true_values: The name of the model to search into
    :type true_values: str
    :param false_values: The name of the model's field
    :type false_values: str
    :returns: bool (or str)

    True values::

        'O', 'Y', '1', 'o', 'y', 'true', 'True'

    False values::

        '0', 'N', '2', 'n', 'false', 'False'

    """
    def _to_boolean(self, model, field, value, line):
        return (value in true_values and True)\
                or (value in false_values and False)\
                or (value and True or False)

    return _to_boolean

def to_date():
    """Check for a valid date and convert if needed before returning the value

    >>> 'inserted_date': Column(6, to_date())
    
    :returns: str

    """
    def _to_date(self, model, field, value, line):
        date = value
        try:
            date = str(value.split('\n')[0])
        except:
            pass
        if date == '0000-00-00':
            return ''
        else:
            return date

    return _to_date

