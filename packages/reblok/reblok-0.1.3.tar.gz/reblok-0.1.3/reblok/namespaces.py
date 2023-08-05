# -*- coding: utf8 -*-
"""
    reblok, python decompiler, AST builder
    Copyright (C) 2010-2011, Guillaume Bour <guillaume@bour.cc>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 3.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
__author__  = "Guillaume Bour <guillaume@bour.cc>"
__version__ = "$Revision: 246 $"
__date__    = "$Date: 2011-07-09 22:33:13 +0200 (sam. 09 juil. 2011) $"
__license__ = "GPLv3"

GLOBAL = 'global'
LOCAL  = 'local'
DEREF  = 'deref'
NAME   = 'name'
