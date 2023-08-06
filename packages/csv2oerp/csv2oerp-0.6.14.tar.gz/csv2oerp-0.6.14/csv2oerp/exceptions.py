#!/usr/bin/env python
# -*- coding: utf8 -*-
##############################################################################
#
# Copyright (c) 2012 STEPHANE MANGIN. (http://le-spleen.net) All Rights Reserved
#                    Stéphane MANGIN <stephane.mangin@freesbee.fr>
# Copyright (c) 2012 OSIELL SARL. (http://osiell.com) All Rights Reserved.
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
# as published by the Free Software Foundation; either version 2
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
##############################################################################

"""
Exceptions used in csv2oerp.

"""

from constants_and_vars import STATS

class RequiredFieldError(BaseException):
    """Exception used when a column index has not be found 
    
    """
    def __init__(self, model, field, value=None, line=None, logger=None):
        """
        :param model: Object model
        :type model: str
        :param field: Field required
        :type field: str

        """
        if line is None:
            msg = "Required field '%s' has null value ('%s') at line %s. Skipping."\
                    % (model, field, value, line)
        else:
            msg = field
        #if logger:
        #    logger.info("<%-20s> %s" % (model, msg), extra=STATS)
        super(RequiredFieldError, self).__init__(msg)


class ColumnIndexError(IndexError):
    """Exception used when a column index has not be found 
    
    """
    def __init__(self, model, field=None, value=None, column=None, logger=None):
        """
        :param model: Object model
        :type model: str
        :param msg: Message to be printed
        :type msg: str

        """
        if column is None:
            msg = "Invalid column index found for field '%s'('%s') at column %s"\
                    % (model, field, value, column)
        else:
            msg = field
        #if logger:
        #    logger.info("<%-20s> %s" % (model, msg), extra=STATS)
        super(ColumnIndexError, self).__init__(msg)


class SkipLineException(BaseException):
    """Exception used when a subfunction need to skip a entire particular line
    
    Usefull into lambda statement with field definition

    """
    def __init__(self, model, field=None, value=None, line=None, logger=None):
        """
        :param model: Object model
        :type model: str
        :param msg: Message to be printed
        :type msg: str

        """
        if line is None:
           msg = "Skipped line for field '%s'('%s') at line %s"\
                % (field, value, line)
        else:
            msg = field
        #if logger:
        #    logger.info("<%-20s> %s" % (model, msg), extra=STATS)
        super(SkipLineException, self).__init__(msg)


class SkipObjectException(BaseException):
    """Exception used when a subfunction need to skip a particular object
    
    Usefull into lambda statement with field definition

    """
    def __init__(self, model, field=None, value=None, line=None, logger=None):
        """
        :param model: Object model
        :type model: str
        :param msg: Message to be printed
        :type msg: str

        """
        global STATS
        if line is None:
            msg = "Skipped object for field '%s'('%s') at line %s"\
                    % (field, value, line)
        else:
            msg = field
        if logger:
            if 'line_num' not in STATS:
                STATS['line_num'] = -2 
            logger.info("<%-20s> %s skipped" % (model, msg), extra=STATS)
        super(SkipObjectException, self).__init__(msg)

