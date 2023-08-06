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
Unicode CSV reader and writer rewriting.

"""

import csv

def _is_null(string):
    return str(string) in ('False', '0', 'NULL', 'null') and '' or string

class Reader:
    """Return an unicode CSV reader

    """
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        self.reader = csv.reader(f, dialect=dialect, **kwds)
        self.encoding = encoding

    def next(self):
        row = self.reader.next()
        return [unicode(_is_null(s), self.encoding) for s in row]

    def __iter__(self):
        return self

class Writer:
    """Return a unicode writer

    """
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        self.writer = csv.writer(f, dialect=dialect, **kwds)
        self.encoding = encoding

    def writerow(self, row):
        self.writer.writerow([_is_null(s).encode("utf-8") for s in row])

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

