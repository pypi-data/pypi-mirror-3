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
__version__ = "$Revision: 270 $"
__date__    = "$Date: 2011-10-06 08:20:41 +0200 (jeu. 06 oct. 2011) $"
__license__ = "GPLv3"


# opcode constants

## list
LIST      = 'list'
TUPLE     = 'tuple'
AT        = 'at'
SLICE     = 'slice'
IN        = 'in'
NIN       = 'not in'

## dict
DICT      = 'dict'
ATTR      = 'attr'

## 
CONST     = 'const'
VAR       = 'var'
SET       = 'set'
DEL       = 'del'

## function
FUNC      = 'function'
CALL      = 'call'

## boolean ops
AND       = 'and'
OR        = 'or'
NOT       = 'not'
INVERT    = 'invert'

EQ        = 'eq'
NEQ       = 'neq'
LT        = 'lt'
GT        = 'gt'
LEQ       = 'leq'
GEQ       = 'geq'
ID        = 'id'
NID       = 'nid'

## arithmetic ops
MINUS     = 'positive'
PLUS      = 'negative'

ADD       = 'add'
SUB       = 'sub'
MUL       = 'mul'
DIV       = 'div'
MOD       = 'mod'

##
RET       = 'ret'
IF        = 'if'
FOR       = 'for'
BREAK     = 'break'
TRYCATCH  = 'try'

## IMPORT 
IMPORT    = 'import'
PRINT     = 'print'
CONVERT   = 'convert'

UNDEF     = '<undef>'
LAMBDA    = '<lambda>'

## temp. Do not use outside of reblok
MARKER_MAP      = 'marker::map'
MARKER_IFFALSE  = 'marker::iffalse'
MARKER_IFTRUE   = 'marker::iftrue'
MARKER_JUMP     = 'marker::jump'
MARKER_POPTOP   = 'marker::poptop'
MARKER_EXCEPT   = 'marker::except'
