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

import sys, traceback
import opcodes as op
"""
	Rebuild python source code from an AST tree
"""

class MetaReblok(type):
	UNARY  = {
		op.MINUS : '-',
		op.PLUS  : '+',
		op.NOT   : 'not ',	
		op.INVERT: '~',
	}

	BINARY = {
		op.IN  : 'in',
		op.NIN : 'not in',

		op.AND : 'and',
		op.OR  : 'or',

		op.EQ  : '==',
		op.NEQ : '!=',
		op.LT  : '<',
		op.GT  : '>',
		op.GEQ : '>=',
		op.LEQ : '<=',
		op.ID  : 'is',
		op.NID : 'is not',

		op.ADD : '+',
		op.SUB : '-',
		op.MUL : '*',
		op.DIV : '/',
		op.MOD : '%',
	}
	
	def __new__(cls, name, bases, dct):
		klass = type.__new__(cls, name, bases, dct)

		for name, op in MetaReblok.UNARY.iteritems():
			setattr(klass, 'do_%s' % str(name).lower().replace(' ','_'), klass._unaryop(op))

		for name, op in MetaReblok.BINARY.iteritems():
			setattr(klass, 'do_%s' % str(name).lower().replace(' ','_'), klass._binaryop(op))

		return klass


class Reblok(object):
	__metaclass__ = MetaReblok
	
	def __init__(self, ident='\t', output=sys.stdout):
		self.depth  = 0
		self.ident  = ident	
		self.output = output

	def run(self, tree):
		"""Rebuild source code from AST tree
		"""
		for instr in tree:
			self._dispatch(instr)

	def _print(self, code, newline=True):
		"""Print code with depth*ident prefixed (to respect python code indentation)
		"""
		print >>self.output, "%s%s" % (self.ident*self.depth, code),
		if newline:
			print >>self.output

	def _dispatch(self, instr, **kwargs):
		"""dispatch AST instructions into callbacks

			instr[0] is the opcode. dispatch call a function named "do_opcode()"
		"""
		try:
			return getattr(self, 'do_%s' % instr[0].lower().replace(' ', '_'))(instr, **kwargs)
		except Exception, e:
			traceback.print_exc()
			print e
			import pprint; pprint.pprint(instr)
			sys.exit(1)

	# OPCODES CALLBACKS #

	### CONST,VAR ###
	def do_const(self, instr, **kwargs):
		"""Constant

			(op.CONST, 42)
		"""
		if instr[1] is None:
			return 'None'
		elif isinstance(instr[1], str):
			return "'%s'" % instr[1].replace('\n', '\\n')

		return str(instr[1])
	
	def do_var(self, instr, **kwargs):
		"""Variable
	
			(op.VAR, 'foo', ns.GLOBAL)
		"""
		return instr[1]
	
	def do_attr(self, instr, **kwargs):
		"""Attribute
	
			(op.ATTR, (op.VAR, 'foo', ns.LOCAL), 'bar')
		"""
		return "%s.%s" % (self._dispatch(instr[1], **kwargs), instr[2])
	
	def do_at(self, instr, **kwargs):
		"""List/Dict item
	
			(op.AT, (op.VAR, 'foo', ns.LOCAL), (op.CONST, 10))
		"""
		return "%s[%s]" % (self._dispatch(instr[1]), self._dispatch(instr[2]))
	
	def do_slice(self, instr, **kwargs):
		"""List slice
	
			(op.SLICE, (op.VAR, 'foo', ns.GLOBAL), (op.CONST, 10), None)
		"""
		return "%s[%s:%s]" % (
			self._dispatch(instr[1], **kwargs),
			'' if instr[2] is None else self._dispatch(instr[2]), 
			'' if instr[3] is None else self._dispatch(instr[3])
		)
	
	### BINARY OPERATORS ###
	@staticmethod
	def _unaryop(op):
		def _format(self, instr, **kwargs):
			return op+self._dispatch(instr[1])
		
		return _format

	@staticmethod
	def _binaryop(op):
		def _format(self, instr, **kwargs):
			return ' '.join([self._dispatch(instr[1]), op, self._dispatch(instr[2])])
		
		return _format

	### LISTS ###
	def do_list(self, instr, **kwargs):
		ret = "[%s]" % (', '.join([self._dispatch(i, noprint=True) for i in instr[1]]))
		if 'noprint' not in kwargs:
			self._print(ret)
	
		return ret

	def do_tuple(self, instr, **kwargs):
		ret = "(%s)" % (', '.join([self._dispatch(i, noprint=True) for i in instr[1]]))
		if 'noprint' not in kwargs:
			self._print(ret)

		return ret
	
	### VARIABLE SET ###
	def do_set(self, instr, **kwargs):
		self._print("%s = %s" % (self._dispatch(instr[1], noprint=True), self._dispatch(instr[2], noprint=True)))

	### RETURN ###	
	def do_ret(self, instr, **kwargs):
		# we ignore return instruction if we are outside function
		if self.depth == 0:
			return
		self._print("return %s" % self._dispatch(instr[1], noprint=True))
	
	### IMPORT ###	
	def do_import(self, instr, **kwargs):
		if len(instr[2]) == 0:
			self._print("import %s" % instr[1], False)
	
			if instr[3] is not None:
				self._print("as %s" % instr[3], False)
			self._print('', True)
		else:
			self._print("from %s import %s" % (instr[1], ', '.join([m[0]+'' if m[1] is None else 'as '+m[1] for m in instr[2]])))

	### FUNCTION ###	
	def do_function(self, instr, **kwargs):
		if instr[1] == 'lambda':
			ret = 'lambda %s: %s' % (', '.join([arg[0] for arg in instr[3]]), self._dispatch(instr[2][0][1], noprint=True))
	
			if 'noprint' not in kwargs:
				print ret
			return ret
	
		self._print("")
		self._print("def %s(%s):" % (instr[1], ','.join([arg[0] for arg in instr[3]])))
		self.depth += 1
	
		# global variables
		if len(instr[6]) > 0:
			self._print("global %s" % ','.join(instr[6]))

		for instr in instr[2]:
			self._dispatch(instr)
		self.depth -= 1

		return ""
	
	### BRANCHS ###
	def do_if(self, instr, **kwargs):
		if 'noprint' in kwargs:
			return "%s if %s else %s" % (self._dispatch(instr[2][0], noprint=True), self._dispatch(instr[1], noprint=True), self._dispatch(instr[3][0], noprint=True))
	
		self._print('');
		self._print("if %s:" % (self._dispatch(instr[1])))
		self.depth += 1
	
		for instr in instr[2]:
			self._dispatch(instr)
	
		self.depth -= 1
	
	def do_call(self, instr, **kwargs):
		_args=""
		if instr[4] is not None:
			_args = ", **%s" % self._dispatch(instr[4], noprint=True)
	
		_kwargs=""
		if instr[5] is not None:
			_kwargs = ", **%s" % self._dispatch(instr[5], noprint=True)
	
		named = ', '.join(["%s=%s" % (self._dispatch(k, noprint=True)[1:-1], self._dispatch(instr[3][k], noprint=True)) for k in instr[3].keys()])
		if len(named) > 0:
			named = ', %s' % named
	
		ret = "%s(%s%s%s%s)" % (\
				self._dispatch(instr[1], noprint=True), 
				', '.join([self._dispatch(x, noprint=True) for x in instr[2]]), 
				named,_args, _kwargs)
	
		if 'noprint' not in kwargs:
			self._print(ret)
	
		return ret

	### PRINT ###	
	def do_print(self, instr, **kwargs):
		stream = instr[1]
		if stream is not None:
			stream = self._dispatch(stream, noprint=True)

		if stream is None or stream == "sys.stdout":
			stream = ""
		else:
			stream = " >>", stream
	
		if instr[2][-1] == ('const', '\n'):
			instr[2].pop()
		self._print("print%s %s" % (stream, ', '.join([self._dispatch(x, noprint=True) for x in instr[2]])))
	
	### FOR LOOP ###	
	def do_for(self, instr, **kwargs):
		# list comprehension
		if len(instr[3]) == 1 and instr[3][0][0] == 'append':
			ret = "[%s for %s in %s]" % (self._dispatch(instr[3][0][2]), instr[1], self._dispatch(instr[2], noprint=True))
	
			if 'noprint' not in kwargs:
				self._print(ret)
			return ret
	
		self._print("for %s in %s:" % (self._dispatch(instr[1], noprint=True), self._dispatch(instr[2], noprint=True)))
		self.depth += 1
		
		for instr in instr[3]:
			self._dispatch(instr)
		self.depth -= 1

		return ""

	def do_break(self, instr, **kwargs):
		self._print("break")

	def do_del(self, instr, **kwargs):
		self._print("del %s" % self._dispatch(instr[1], noprint=True))

	# Exceptions handling (try-except-finally)
	def do_try(self, instr, **kwargs):
		self._print("try:")
		self.depth += 1
	
		for i in instr[2]:
			self._dispatch(i)
		self.depth -= 1

		if instr[3] is not None:
			ex = 'except'
			if instr[1] is not None:
				exname = instr[1][0]
				if exname is not None:
					ex += ' '+self._dispatch(exname, noprint=True)

					if instr[1][1] is not None:
						ex += ', '+self._dispatch(instr[1][1], noprint=True)

			self._print(ex+':')
			self.depth += 1

			for i in instr[3]:
				self._dispatch(i)
			self.depth -= 1

		if instr[4] is not None:
			self._print('finally:')
			self.depth += 1

			for i in instr[4]:
				self._dispatch(i)
			self.depth -= 1


