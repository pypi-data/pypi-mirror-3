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
Fields can be used to configure columns/model's fields mapping.

"""
from inspect import stack, getargvalues
from constants_and_vars import ACTION_PATTERN, OERP, DB, USER, PWD

class Base(object):
    
    def __init__(self, column, callback, search, attributes):
        if not column or isinstance(column, int):
            self.column = column
        elif isinstance(column, list):
            if column:
                for index in column:
                    if not isinstance(index, int):
                        raise Exception('Column\'s `column` argument must be a list of int or int')
                self.column = column
            else:
                raise Exception('Column\'s `column` argument must be a list of int or int')
        else:
            raise Exception('Column\'s `column` argument must be a list of int or int')
        if callback and not callable(callback):
            raise Exception('Column\'s `callback` argument must be callable')
        self.callback = callback
        if not isinstance(search, bool):
            raise Exception('Column\'s `search` argument must be a boolean')
        self.search = search
        if attributes and not isinstance(attributes, list):
            raise Exception('Column\'s `search` argument must be a list')
        self.attributes = attributes
    
    def __call__(self):
        return ((self.column, self.callback, self.search), self.attributes)


class Column(Base):
    """ Specify the column number and special treatments from which the current
    model's field will be allocated to the object's creation.
    Also declares metadatas for each model's field defined in mapping, like
    ``required``, ``readonly`` attributes.
    
    .. note: Replaces tuples in model's field mapping

    Mapping example::
        
        >>> {
        ...     'model': {
        ...         'field': Column(column=0, callback=None, search=True),
        ...         } 
        ...     }

    :param column: The actual column number (mandatory)
    :type column: int
    :param callback: The actual callback function
    :type callback: function
    :param search: Search for same value before create object
    :type search: bool
    :param required: Is this field is required
    :type required: bool
    :param skip: Is this field is skippable
    :type skip: bool
    :param ignore: Is this field is ignorable (So object creation is skipped)
    :type ignore: bool
    :param replace: Is this field is replaceable (So it can be redifined)
    :type replace: bool
    :param noupdate: Is this field have not to be updated if existing in database
    :type noupdate: bool
    :param unique: Is this model's instance must be unique inside current model
    :type unique: bool

    """
    def __init__(self, column=None, callback=None, search=False,
            required=False, skip=False, ignore=False, replace=False,
            noupdate=False, unique=False):
        attributes = []
        # Getting the calling frame from stack
        frame = stack()[0][0]
        # Arguments passed to the method
        frame_args = getargvalues(frame)
        # Reformatting to kwargs arguments
        kwargs = frame_args.locals
        # Cleaning kwargs from args
        for item in ('column', 'callback', 'search', 'frame', 'action'):
            if item in kwargs:
                del kwargs[item]
        for arg in kwargs:
            if kwargs[arg] and arg in ACTION_PATTERN:
                attributes.append(ACTION_PATTERN[arg])
        return super(Column, self).__init__(column, callback, search, attributes)
        
class Relation(Base):
    """ Specify a relation field.
    Also declares metadatas like ``required``, ``readonly`` attributes.
    
    .. note: Replaces tuples in model's field mapping

    Mapping example::
        
        >>> {
        ...     'model': [
        ...         {
        ...             'field': Relation('REL_custom::model', search=True),
        ...             },
        ...         ],
        ...     'REL_custom::model': {
        ...         'field': Column(1),
        ...         }
        ...     }

    :param relation: The full name of the model which has to be related to field
    :type relation: str
    :param search: Search for same value before create object
    :type search: bool
    :param required: Is this field is required
    :type required: bool
    :param skip: Is this field is skippable
    :type skip: bool
    :param ignore: Is this field is ignorable (So object creation is skipped)
    :type ignore: bool
    :param replace: Is this field is replaceable (So it can be redifined)
    :type replace: bool
    :param noupdate: Is this field have not to be updated if existing in database
    :type noupdate: bool
    :param unique: Is this model's instance must be unique inside current model
    :type unique: bool

    """
    def _is_model(self, model):
        """Check model validity
        
        :returns: bool

        """
        res = True
        #res = OERP.execute(DB, USER, PWD,
        #        'ir.model', 'search', [('model', '=', model)])
        return bool(res)
    
    def _is_field(self, model, attr):
        """Check field validity
        
        :returns: bool

        """
        for pattern in ACTION_PATTERN.values():
            if attr.count(pattern):
                attr.replace(pattern, '')
        res = OERP.execute(DB, USER, PWD, model, 'fields_get')
        if attr in res:
            return True
        return False


    def __init__(self, relation, search=False, required=False, skip=False,
            noupdate=False, unique=False):
        if self._is_model(relation):
            callback = lambda *a: relation
        else:
            raise Exception('Model name `%s` is invalid.' % relation)
        # Getting the calling frame from stack
        frame = stack()[0][0]
        # Arguments passed to the method
        frame_args = getargvalues(frame)
        # Reformatting to kwargs arguments
        kwargs = frame_args.locals
        # Cleaning kwargs from args
        for item in ('column', 'callback', 'search', 'frame', 'action'):
            if item in kwargs:
                del kwargs[item]
        for arg in kwargs:
            if kwargs[arg] and arg in ACTION_PATTERN:
                self.action.append(ACTION_PATTERN[arg])
        return super(Relation, self).__init__(None, callback, search, [])


class Custom(Base):
    """ Specify a custom value for current field.
    
    .. note: Replaces tuples in model's field mapping

    Mapping example::
        
        >>> mapping = {
        ...     'model': {
        ...         'field': Custom('custom', search=True),
        ...         } 
        ...     }

    :param value: The value to apply.
    :type value: type
    :param search: Search for same value before create object
    :type search: bool

    """
    def __init__(self, value, search=False):
        attributes = []
        callback = lambda *a: value
        # Getting the calling frame from stack
        frame = stack()[0][0]
        # Arguments passed to the method
        frame_args = getargvalues(frame)
        # Reformatting to kwargs arguments
        kwargs = frame_args.locals
        # Cleaning kwargs from args
        for item in ('column', 'callback', 'search', 'frame', 'action'):
            if item in kwargs:
                del kwargs[item]
        for arg in kwargs:
            if kwargs[arg] and arg in ACTION_PATTERN:
                attributes.append(ACTION_PATTERN[arg])
        return super(Custom, self).__init__(None, callback, search, attributes)
        

