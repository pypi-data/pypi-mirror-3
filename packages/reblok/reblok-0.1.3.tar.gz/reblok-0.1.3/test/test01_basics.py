#!/usr/bin/env python
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
__version__ = "$Revision$"
__date__    = "$Date$"
__license__ = "GPLv3"

import unittest
from reblok import Parser, namespaces as ns, opcodes as op

class TestReblokBasics(unittest.TestCase):
	def __init__(self, *args, **kwargs):
		unittest.TestCase.__init__(self, *args, **kwargs)
		self.parser = Parser()

	def walk(code):
		return self.parser.walk(code)

	def test_01arithmetic(self):
		tree = self.parser.walk(lambda u: u + 5)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.ADD, (op.VAR, 'u', ns.LOCAL), (op.CONST , 5))]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: u - 5)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.SUB, (op.VAR, 'u', ns.LOCAL), (op.CONST , 5))]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: u * 5)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.MUL, (op.VAR, 'u', ns.LOCAL), (op.CONST , 5))]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: u / 5)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.DIV, (op.VAR, 'u', ns.LOCAL), (op.CONST , 5))]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: u % 5)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.MOD, (op.VAR, 'u', ns.LOCAL), (op.CONST , 5))]],
				[('u', op.UNDEF)], None, None, [], {}
		])
	
	def test_02cmp(self):
		tree = self.parser.walk(lambda u: u == 5)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA, [
				[op.RET,
					(op.EQ,
						(op.VAR  , 'u', ns.LOCAL),
						(op.CONST, 5)
				)]],
				[('u', op.UNDEF)], None, None, [], {}]
		)

		tree = self.parser.walk(lambda u: u != 5)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.NEQ, (op.VAR, 'u', ns.LOCAL), (op.CONST , 5))]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		# <> and != are same operator
		tree = self.parser.walk(lambda u: u <> 5)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.NEQ, (op.VAR, 'u', ns.LOCAL), (op.CONST , 5))]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: u > 5)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.GT, (op.VAR, 'u', ns.LOCAL), (op.CONST , 5))]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: u < 5)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.LT, (op.VAR, 'u', ns.LOCAL), (op.CONST , 5))]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: u >= 5)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.GEQ, (op.VAR, 'u', ns.LOCAL), (op.CONST , 5))]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: u <= 5)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.LEQ, (op.VAR, 'u', ns.LOCAL), (op.CONST , 5))]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: u is 5)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.ID, (op.VAR, 'u', ns.LOCAL), (op.CONST , 5))]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: u is not 5)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.NID, (op.VAR, 'u', ns.LOCAL), (op.CONST , 5))]],
				[('u', op.UNDEF)], None, None, [], {}
		])

	def test_03bool(self):
		tree = self.parser.walk(lambda u: u or True)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.OR, (op.VAR, 'u', ns.LOCAL), (op.CONST , True)]]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: True or u)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.OR, (op.CONST , True), (op.VAR, 'u', ns.LOCAL)]]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: u and True)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.AND, (op.VAR, 'u', ns.LOCAL), (op.CONST , True)]]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: True and u)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.AND, (op.CONST , True), (op.VAR, 'u', ns.LOCAL)]]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: not u)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.NOT, (op.VAR, 'u', ns.LOCAL))]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: not u or True)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.OR, (op.NOT, (op.VAR, 'u', ns.LOCAL)), (op.CONST , True)]]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: not (u or True))
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.NOT, [op.OR, (op.VAR, 'u', ns.LOCAL), (op.CONST , True)])]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: not u and True)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.AND, (op.NOT, (op.VAR, 'u', ns.LOCAL)), (op.CONST , True)]]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: not (u and True))
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.NOT, [op.AND, (op.VAR, 'u', ns.LOCAL), (op.CONST , True)])]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: a or b and c)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.OR, (op.VAR, 'a', ns.GLOBAL), [op.AND, (op.VAR, 'b', ns.GLOBAL), (op.VAR, 'c', ns.GLOBAL)]]]],
				[('u', op.UNDEF)], None, None, ['a', 'b', 'c'], {}
		])

		tree = self.parser.walk(lambda u: a or (b and c))
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.OR, (op.VAR, 'a', ns.GLOBAL), [op.AND, (op.VAR, 'b', ns.GLOBAL), (op.VAR, 'c', ns.GLOBAL)]]]],
				[('u', op.UNDEF)], None, None, ['a', 'b', 'c'], {}
		])

		tree = self.parser.walk(lambda u: (a or b) and c)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.AND, [op.OR, (op.VAR, 'a', ns.GLOBAL), (op.VAR, 'b', ns.GLOBAL)], (op.VAR, 'c', ns.GLOBAL)]]],
				[('u', op.UNDEF)], None, None, ['a', 'b', 'c'], {}
		])

		tree = self.parser.walk(lambda u: a and b or c)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.OR, [op.AND, (op.VAR, 'a', ns.GLOBAL), (op.VAR, 'b', ns.GLOBAL)], (op.VAR, 'c', ns.GLOBAL)]]],
				[('u', op.UNDEF)], None, None, ['a', 'b', 'c'], {}
		])

		tree = self.parser.walk(lambda u: a and (b or c))
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.AND, (op.VAR, 'a', ns.GLOBAL), [op.OR, (op.VAR, 'b', ns.GLOBAL), (op.VAR, 'c', ns.GLOBAL)]]]],
				[('u', op.UNDEF)], None, None, ['a', 'b', 'c'], {}
		])

		tree = self.parser.walk(lambda u: a and b or c and d)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.OR, 
					[op.AND, (op.VAR, 'a', ns.GLOBAL), (op.VAR, 'b', ns.GLOBAL)], 
					[op.AND, (op.VAR, 'c', ns.GLOBAL), (op.VAR, 'd', ns.GLOBAL)]
				]]],
				[('u', op.UNDEF)], None, None, ['a', 'b', 'c', 'd'], {}
		])

		tree = self.parser.walk(lambda u: a or b and c or d)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.OR, 
					(op.VAR, 'a', ns.GLOBAL), 
					[op.OR, 
						[op.AND, (op.VAR, 'b', ns.GLOBAL), (op.VAR, 'c', ns.GLOBAL)],
						(op.VAR, 'd', ns.GLOBAL)]
				]]],
				[('u', op.UNDEF)], None, None, ['a', 'b', 'c', 'd'], {}
		])


	def test_04list(self):
		tree = self.parser.walk(lambda a,b: (1, plop, a.name, "Zzz", b))
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.TUPLE, [
					(op.CONST, 1), (op.VAR, 'plop', ns.GLOBAL), 
					(op.ATTR, (op.VAR, 'a', ns.LOCAL), 'name'),
					(op.CONST, 'Zzz'), (op.VAR, 'b', ns.LOCAL)])]],
				[('a', op.UNDEF), ('b', op.UNDEF)], None, None, ['plop'], {}
		])

		tree = self.parser.walk(lambda a,b: [1, 'plop', True, 3.14, foo])
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.LIST, [
					(op.CONST, 1), (op.CONST, 'plop'), (op.CONST, True), (op.CONST, 3.14), (op.VAR, 'foo', ns.GLOBAL)])]],
				[('a', op.UNDEF), ('b', op.UNDEF)], None, None, ['foo'], {}
		])

		tree = self.parser.walk(lambda u: u[0])
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.AT, (op.VAR, 'u', ns.LOCAL), (op.CONST, 0))]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: u[:])
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.SLICE, (op.VAR, 'u', ns.LOCAL), None, None)]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: u[1:])
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.SLICE, (op.VAR, 'u', ns.LOCAL), (op.CONST, 1), None)]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: u[:1])
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.SLICE, (op.VAR, 'u', ns.LOCAL), None, (op.CONST, 1))]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: u[5:2])
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.SLICE, (op.VAR, 'u', ns.LOCAL), (op.CONST, 5), (op.CONST, 2))]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: a in b)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.IN, (op.VAR, 'a', ns.GLOBAL), (op.VAR, 'b', ns.GLOBAL))]],
				[('u', op.UNDEF)], None, None, ['a', 'b'], {}
		])

		tree = self.parser.walk(lambda u: a not in b)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.NIN, (op.VAR, 'a', ns.GLOBAL), (op.VAR, 'b', ns.GLOBAL))]],
				[('u', op.UNDEF)], None, None, ['a', 'b'], {}
		])

	
	def test_05dict(self):
		tree = self.parser.walk(lambda u: {'name': 'doe', 'age': 42})
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.DICT, [
					((op.CONST, 'name'), (op.CONST, 'doe')),
					((op.CONST, 'age') , (op.CONST, 42))
				])]],
				[('u', op.UNDEF)], None, None, [], {}
		])


	def test_06attr(self):
		tree = self.parser.walk(lambda u: u.name)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.ATTR, (op.VAR, 'u', ns.LOCAL), 'name')]],
				[('u', op.UNDEF)], None, None, [], {}
		])


	def test_07funcall(self):
		tree = self.parser.walk(lambda u: u.lower())
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.CALL, (op.ATTR, (op.VAR, 'u', ns.LOCAL), 'lower'), [], {}, None, None]]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: u.lower(a))
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.CALL, 
					(op.ATTR, (op.VAR, 'u', ns.LOCAL), 'lower'), [(op.VAR, 'a', ns.GLOBAL)], {}, None, None]]],
				[('u', op.UNDEF)], None, None, ['a'], {}
		])

		tree = self.parser.walk(lambda u, v: u.lower(v, 'b', 3))
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.CALL, 
					(op.ATTR, (op.VAR, 'u', ns.LOCAL), 'lower'), 
					[(op.VAR, 'v', ns.LOCAL), (op.CONST, 'b'), (op.CONST, 3)], {}, None, None]]],
				[('u', op.UNDEF), ('v', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u, v: u.lower(v, name='b'))
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.CALL, 
					(op.ATTR, (op.VAR, 'u', ns.LOCAL), 'lower'), 
					[(op.VAR, 'v', ns.LOCAL)], {(op.CONST, 'name'): (op.CONST, 'b')}, None, None]]],
				[('u', op.UNDEF), ('v', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u, v: u.lower(*v, **a))
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.CALL, 
					(op.ATTR, (op.VAR, 'u', ns.LOCAL), 'lower'), [], {}, (op.VAR, 'v', ns.LOCAL), (op.VAR, 'a', ns.GLOBAL)]]],
				[('u', op.UNDEF), ('v', op.UNDEF)], None, None, ['a'], {}
		])


	def test_08string(self):
		tree = self.parser.walk(lambda u: "::" + u)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.ADD, (op.CONST, '::'), (op.VAR, 'u', ns.LOCAL))]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: ":: %s" % u)
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.MOD, (op.CONST, ':: %s'), (op.VAR, 'u', ns.LOCAL))]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		tree = self.parser.walk(lambda u: "%s, %d, %s" % (u.name, u.age, "female"))
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.MOD, (op.CONST, '%s, %d, %s'), (op.TUPLE, [ 
					(op.ATTR, (op.VAR, 'u', ns.LOCAL), 'name'),
					(op.ATTR, (op.VAR, 'u', ns.LOCAL), 'age'),
					(op.CONST, 'female')
				]))]],
				[('u', op.UNDEF)], None, None, [], {}
		])
	
	def test_09import(self):
		def func():
			import sys
			import sys as system

			from sys import *
			from sys import stdin, stdout
			from sys import stdin as input, stdout
			from os.path import basename

		tree = self.parser.walk(func)
		self.assertEqual(tree,
			[op.FUNC, 'func', [
				[op.IMPORT, 'sys', []                                    , None    , (op.CONST, -1)],	
				[op.IMPORT, 'sys', []                                    , 'system', (op.CONST, -1)],	
				[op.IMPORT, 'sys', [('*', None)]                         , None    , (op.CONST, -1)],	
				[op.IMPORT, 'sys', [('stdin', None), ('stdout', None)]   , None    , (op.CONST, -1)],	
				[op.IMPORT, 'sys', [('stdin', 'input'), ('stdout', None)], None    , (op.CONST, -1)],	
				[op.IMPORT, 'os.path', [('basename', None)]              , None    , (op.CONST, -1)],	
				[op.RET, (op.CONST, None)]
			], [], None, None, [], {}
		])


	def test_10list(self):
		tree = self.parser.walk(lambda x: x in [1,2])
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, (op.IN, (op.VAR, 'x', ns.LOCAL), (op.CONST, (1,2)))]],
				[('x', op.UNDEF)], None, None, [], {}
		])

		def fnc():
			l = [1,2]
			return x in l
		tree = self.parser.walk(fnc)
		self.assertEqual(tree,
			[op.FUNC, 'fnc', [
					(op.SET, (op.VAR, 'l', ns.LOCAL), (op.LIST, [(op.CONST, 1), (op.CONST, 2)])),
					[op.RET, (op.IN, (op.VAR, 'x', ns.GLOBAL), (op.VAR, 'l', ns.LOCAL))]
				], [], None, None, ['x'], {}
		])

	def test_11loop(self):
		def fnc():
			for i in xrange(10):
				if i > 5:
					break
				print i
		tree = self.parser.walk(fnc)
		self.assertEqual(tree,
			[op.FUNC, 'fnc', [
				[op.FOR, (op.VAR, 'i', ns.LOCAL), 
					[op.CALL, (op.VAR, 'xrange', ns.GLOBAL), [(op.CONST, 10)], {}, None, None],
					[
						[op.IF, (op.GT, (op.VAR, 'i', ns.LOCAL), (op.CONST, 5)), [(op.BREAK,)],	[]],
						(op.PRINT, None, [(op.VAR, 'i', ns.LOCAL), (op.CONST, '\n')])
					], None],
				[op.RET, (op.CONST, None)]
			], [], None, None, ['xrange'], {}
		])


	def test_12print(self):
		def printall():
			#NOTE: when python compiler find *print* instructions following each others,
			# it merge it to have only on print call in bytecode 
			# base types, variable, function result
			print 10, (1+2), "pouët", False, a, foo()
			# % operator
			print "%d - %s\n %s" % (24, "Zzzz", True)
			# .format() method
			print "{1} -- {2}".format(a, b)

			# no newline
			z=1 # just to be sure have a new print instruction
			print "blablabla",

			# out stream
			z=1
			print >>myfile, "hoho", 17
			# as output stream is different, should produce a separate print instruction
			print >>otherfile, "bar", u"fôo"

		tree = self.parser.walk(printall)
		self.assertEqual(tree,
			[op.FUNC, 'printall', [
					(op.PRINT, None, [
						# 1st print
						(op.CONST, 10), 
						(op.CONST, 3), 
						(op.CONST, 'pouët'), 
						(op.CONST, False),
						(op.VAR, 'a', ns.GLOBAL),
						[op.CALL, (op.VAR, 'foo', ns.GLOBAL), [], {}, None, None],
						(op.CONST, '\n'),
						# 2d print
						(op.MOD, (op.CONST, "%d - %s\n %s"), (op.TUPLE, [(op.CONST, 24), (op.CONST, "Zzzz"), (op.CONST, True)])),
						(op.CONST, '\n'),
						# 3d print
						[op.CALL, (op.ATTR, (op.CONST, "{1} -- {2}"), 'format'), [(op.VAR, 'a', ns.GLOBAL), (op.VAR, 'b', ns.GLOBAL)], {}, None, None],
						(op.CONST, '\n'),
					]),

					(op.SET, (op.VAR, 'z', ns.LOCAL), (op.CONST, 1)),
					(op.PRINT, None, [(op.CONST, "blablabla")]),

					(op.SET, (op.VAR, 'z', ns.LOCAL), (op.CONST, 1)),
					(op.PRINT, (op.VAR, 'myfile', ns.GLOBAL), [(op.CONST, 'hoho'), (op.CONST, 17), (op.CONST, '\n')]),

					(op.PRINT, (op.VAR, 'otherfile', ns.GLOBAL), [(op.CONST, 'bar'), (op.CONST, u'fôo'), (op.CONST, '\n')]),

					[op.RET, (op.CONST, None)]
				], [], None, None, ['a', 'b', 'foo', 'myfile', 'otherfile'], {}
		])


	def test_13delete(self):
		# delete a variable
		c = False
		def func(b):
			a = 23
			# DELETE_FAST
			del a
			# DELETE_FAST
			del b
			# DELETE_GLOBAL
			global c
			del c
		tree = self.parser.walk(func)
		self.assertEqual(tree,
			[op.FUNC, 'func',
				[(op.SET, (op.VAR, 'a', ns.LOCAL), (op.CONST, 23)),
				 (op.DEL, (op.VAR, 'a', ns.LOCAL)),
				 (op.DEL, (op.VAR, 'b', ns.LOCAL)),
				 (op.DEL, (op.VAR, 'c', ns.GLOBAL)),
				 [op.RET, (op.CONST, None)]
				], [('b', '<undef>')], None, None, ['c'], {}
		])


	def test_14unpackseq(self):
		# simple unpack
		def func():
			global b
			(a, b, c[0]) = (10, 11, 12)
		tree = self.parser.walk(func)
		self.assertEqual(tree, 
			[op.FUNC, 'func',
				[(op.SET, (op.TUPLE, 
					 ((op.VAR, 'a', ns.LOCAL), 
						(op.VAR, 'b', ns.GLOBAL), 
						(op.AT, (op.VAR, 'c', ns.GLOBAL), (op.CONST, 0))
					 )), (op.CONST, (10, 11, 12))),
				 [op.RET, (op.CONST, None)]
				], [], None, None, ['b', 'c'], {}
		])
			# unpack in loop
		def func():
			global b

			l = ((1,2), (3,4))
			for (a, b) in l:
				c = 0
		tree = self.parser.walk(func)
		self.assertEqual(tree,
			[op.FUNC, 'func',
				[(op.SET, (op.VAR, 'l', ns.LOCAL), (op.TUPLE, [(op.CONST, (1,2)), (op.CONST, (3,4))])),
				 [op.FOR, (op.TUPLE, ((op.VAR, 'a', ns.LOCAL), (op.VAR, 'b', ns.GLOBAL))), (op.VAR, 'l', ns.LOCAL),
					 [(op.SET, (op.VAR, 'c', ns.LOCAL), (op.CONST, 0))], None],
				 [op.RET, (op.CONST, None)]
				], [], None, None, ['b'], {}
		])


	def test_15set(self):
		def func():
			foo = 'bar'
			global bis
			bis = 'bille'

			array[42] = 3.14
		tree = self.parser.walk(func)
		self.assertEqual(tree,
			[op.FUNC, 'func',
				[(op.SET, (op.VAR, 'foo', ns.LOCAL) , (op.CONST, 'bar')),
				 (op.SET, (op.VAR, 'bis', ns.GLOBAL), (op.CONST, 'bille')),
				 (op.SET, (op.AT , (op.VAR, 'array', ns.GLOBAL), (op.CONST, 42)), (op.CONST, 3.14)),
				 [op.RET, (op.CONST, None)]
				], [], None, None, ['array', 'bis'], {}
		])

	def test_16try(self):
		#CASE #1: no finally clause, except match all
		def case1():
			try:
				a=1
			except:
				print 'failure'
		tree = self.parser.walk(case1)
		self.assertEqual(tree,
			[op.FUNC, 'case1',
				[[op.TRYCATCH, None, 
					[(op.SET, (op.VAR, 'a', ns.LOCAL), (op.CONST, 1))], 
					[(op.PRINT, None, [(op.CONST, 'failure'), (op.CONST, '\n')])], 
					None],
				 [op.RET, (op.CONST, None)]
				], [], None, None, [], {}
		])


		# CASE #2: except with named exception
		def case2():
			try:
				a=1
			except ValueError:
				print 'failure'

		tree = self.parser.walk(case2)
		self.assertEqual(tree,
			[op.FUNC, 'case2',
				[[op.TRYCATCH,
					((op.VAR, 'ValueError', ns.GLOBAL), None), 
					[(op.SET, (op.VAR, 'a', ns.LOCAL), (op.CONST, 1))], 
					[(op.PRINT, None, [(op.CONST, 'failure'), (op.CONST, '\n')])], 
					None],
				 [op.RET, (op.CONST, None)]
				], [], None, None, ['ValueError'], {}
		])

		# CASE #3: except defined, but without instructions
		#   - except clause must be empty list ([])
		#   - while finally clause must be None
		def case3():
			try:
				a=1
			except ValueError:
				pass

		tree = self.parser.walk(case3)
		self.assertEqual(tree,
			[op.FUNC, 'case3',
				[[op.TRYCATCH,
					((op.VAR, 'ValueError', ns.GLOBAL), None), 
					[(op.SET, (op.VAR, 'a', ns.LOCAL), (op.CONST, 1))], 
					[],
					None],
				 [op.RET, (op.CONST, None)]
				], [], None, None, ['ValueError'], {}
		])

		# CASE #4: except, with exception set in variable
		def case4():
			try:
				a=1
			except ValueError, e:
				print e

		tree = self.parser.walk(case4)
		self.assertEqual(tree,
			[op.FUNC, 'case4',
				[[op.TRYCATCH,
					((op.VAR, 'ValueError', ns.GLOBAL), (op.VAR, 'e', ns.LOCAL)), 
					[(op.SET, (op.VAR, 'a', ns.LOCAL), (op.CONST, 1))], 
					[(op.PRINT, None, [(op.VAR, 'e', ns.LOCAL), (op.CONST, '\n')])], 
					None],
				 [op.RET, (op.CONST, None)]
				], [], None, None, ['ValueError'], {}
		])

		# CASE #5: same as #4, but with global variable
		def case5():
			global e
			try:
				a=1
			except ValueError, e:
				print e

		tree = self.parser.walk(case5)
		self.assertEqual(tree,
			[op.FUNC, 'case5',
				[[op.TRYCATCH,
					((op.VAR, 'ValueError', ns.GLOBAL), (op.VAR, 'e', ns.GLOBAL)), 
					[(op.SET, (op.VAR, 'a', ns.LOCAL), (op.CONST, 1))], 
					[(op.PRINT, None, [(op.VAR, 'e', ns.GLOBAL), (op.CONST, '\n')])], 
					None],
				 [op.RET, (op.CONST, None)]
				], [], None, None, ['ValueError', 'e'], {}
		])


		# CASE #10: finally clause
		def case10():
			try:
				a=1
			finally:
				print 'passed'

		tree = self.parser.walk(case10)
		self.assertEqual(tree,
			[op.FUNC, 'case10',
				[[op.TRYCATCH,
					None,
					[(op.SET, (op.VAR, 'a', ns.LOCAL), (op.CONST, 1))], 
					None,
					[(op.PRINT, None, [(op.CONST, 'passed'), (op.CONST, '\n')])]
				 ], 
				 [op.RET, (op.CONST, None)]
				], [], None, None, [], {}
		])

		# CASE #11: except+finally
		def case11():
			try:
				a=1
			except Exception, e:
				print e
			finally:
				print a

		tree = self.parser.walk(case11)
		self.assertEqual(tree,
			[op.FUNC, 'case11',
				[[op.TRYCATCH,
					((op.VAR, 'Exception', ns.GLOBAL), (op.VAR, 'e', ns.LOCAL)), 
					[(op.SET, (op.VAR, 'a', ns.LOCAL), (op.CONST, 1))],
					[(op.PRINT, None, [(op.VAR, 'e', ns.LOCAL), (op.CONST, '\n')])], 
					[(op.PRINT, None, [(op.VAR, 'a', ns.LOCAL), (op.CONST, '\n')])]
				 ], 
				 [op.RET, (op.CONST, None)]
				], [], None, None, ['Exception'], {}
		])

		# CASE #12: except+finally (no exception)
		def case12():
			try:
				a=1
			except:
				print 'fail'
			finally:
				print a

		tree = self.parser.walk(case12)
		self.assertEqual(tree,
			[op.FUNC, 'case12',
				[[op.TRYCATCH,
					None,
					[(op.SET, (op.VAR, 'a', ns.LOCAL), (op.CONST, 1))],
					[(op.PRINT, None, [(op.CONST, 'fail'), (op.CONST, '\n')])], 
					[(op.PRINT, None, [(op.VAR, 'a', ns.LOCAL), (op.CONST, '\n')])]
				 ], 
				 [op.RET, (op.CONST, None)]
				], [], None, None, [], {}
		])

		# CASE #13: except+finally (empty code)
		def case13():
			try:
				a=1
			except:
				pass
			finally:
				pass

		tree = self.parser.walk(case13)
		self.assertEqual(tree,
			[op.FUNC, 'case13',
				[[op.TRYCATCH,
					None,
					[(op.SET, (op.VAR, 'a', ns.LOCAL), (op.CONST, 1))],
					[],
					[]
				 ], 
				 [op.RET, (op.CONST, None)]
				], [], None, None, [], {}
		])



	def test_20funcdef(self):
		tree = self.parser.walk(lambda u: foo())
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.CALL, (op.VAR, 'foo', ns.GLOBAL), [], {}, None, None]]],
				[('u', op.UNDEF)], None, None, ['foo'], {}
		])

		# with positional args
		tree = self.parser.walk(lambda u: foo(42, bar))
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.CALL, (op.VAR, 'foo', ns.GLOBAL), [(op.CONST, 42), (op.VAR, 'bar', ns.GLOBAL)], {}, None, None]]],
				[('u', op.UNDEF)], None, None, ['bar', 'foo'], {}
		])


	def test_25ifelse(self):
		# uniline if:else
		tree = self.parser.walk(lambda u: u if True else 'bar')
		self.assertEqual(tree,
			[op.FUNC, op.LAMBDA,
				[[op.RET, [op.IF, (op.CONST, True), [(op.VAR, 'u', ns.LOCAL)], [(op.CONST, 'bar')]]]],
				[('u', op.UNDEF)], None, None, [], {}
		])

		# uniline if:else, result set to a variable
		def func():
			c = a if a else b
			return c
		tree = self.parser.walk(func)
		self.assertEqual(tree,
			[op.FUNC, 'func', [
				(op.SET, (op.VAR, 'c', ns.LOCAL),
					[op.IF, (op.VAR, 'a', ns.GLOBAL), [(op.VAR, 'a', ns.GLOBAL)], [(op.VAR, 'b', ns.GLOBAL)]]
				),
				[op.RET, (op.VAR, 'c', ns.LOCAL)]],
				[], None, None, ['a','b'], {}
		])

		# if:elif:else
		def func():
			if a:
				pass
			elif b:
				pass
			else:
				pass
		tree = self.parser.walk(func)
		self.assertEqual(tree,
			[op.FUNC, 'func', [
					[op.IF, (op.VAR, 'a', ns.GLOBAL), 
						[],
						[[op.IF, (op.VAR, 'b', ns.GLOBAL), [], []]]
					],
					[op.RET, (op.CONST, None)]
				],
				[], None, None, ['a','b'], {}
			])

		# 
		def func():
			a = True

			if a:
				b = 1
			else:
				b = 'plop'
		
			c = 7
		tree = self.parser.walk(func)
		self.assertEqual(tree,
			[op.FUNC, 'func', [
				(op.SET, (op.VAR, 'a', ns.LOCAL), (op.CONST, True)),
				[op.IF, (op.VAR, 'a', ns.LOCAL), 
					[(op.SET, (op.VAR, 'b', ns.LOCAL), (op.CONST, 1))],
					[(op.SET, (op.VAR, 'b', ns.LOCAL), (op.CONST, 'plop'))]
				],
				(op.SET, (op.VAR, 'c', ns.LOCAL), (op.CONST, 7)),
				[op.RET, (op.CONST, None)]
			],
			[], None, None, [], {}
		])

		#
		def func():
			foo()

			if a:
				b = 42
			c
		tree = self.parser.walk(func)
		self.assertEqual(tree,
			[op.FUNC, 'func', [
				[op.CALL, (op.VAR, 'foo', ns.GLOBAL), [], {}, None, None],
				[op.IF, (op.VAR, 'a', ns.GLOBAL), 
					[(op.SET, (op.VAR, 'b', ns.LOCAL), (op.CONST, 42))], 
					[]
				],
				[op.RET, (op.CONST, None)]
			],
			[], None, None, ['a','c','foo'], {}
		])


if __name__ == '__main__':
	unittest.main()

