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

"""
  Python bytecode instructions are listed here: http://docs.python.org/library/dis.html#python-bytecode-instructions

	TOS == Top Of Stack
"""
import sys, types
import byteplay as byte
import opcodes
import namespaces

def is_STORE(opcode):
	return opcode in (byte.STORE_NAME, byte.STORE_FAST, byte.STORE_GLOBAL,
			byte.STORE_DEREF)


class CodeGenerator(object):
	"""Opcodes generator
		
		we allow to preview (predict) the next code line without unstacking.
		We also allow unstacking opcode out of main iterator loop.
	"""
	def __init__(self, code):
		self.code = code
		self.i    = 0

	def __iter__(self):
		self.i = 0

		while self.i < len(self.code):
			yield self.code[self.i]; self.i += 1

		return

	def predict(self, at=1):
		"""
			we want to predict the at'th next code line, skipping SetLineno fake instructions
		"""
		i    = self.i + 1
		step = 0

		while i < len(self.code) and step < at:
			if self.code[i][0] == byte.SetLineno:
				i += 1; continue

			i    += 1
			step += 1

		return self.code[i-1] if i < len(self.code) else (None, None)

	def nexthop(self):
		i = self.i + 1
		while i < len(self.code) and self.code[i][0] == byte.SetLineno:
			i += 1

		self.i = i
		return self.code[i] if i < len(self.code) else None


class Parser(object):
	"""Analyse python opcode, and convert it to an Abstract Syntax Tree
	"""
	def __init__(self):
		pass

	def walk(self, code):
		"""Main parser loop
		"""
		c = byte.Code.from_code(code.func_code if hasattr(code, 'func_code') else code)
		#print c.code#; return
		#print c.args, c.freevars, c.newlocals, c.varargs, c.varkwargs
		#print code.func_code.co_varnames, code.func_code.co_freevars,	code.func_code.co_cellvars, code.func_closure

		ast, _globals = self._walk(c.code)
		if not isinstance(code, types.FunctionType):
			return ast

		dftval = code.func_defaults if code.func_defaults is not None else ()
		diff   = len(c.args) - len(dftval)
		args = [(c.args[i], dftval[i-diff] if i >= diff else opcodes.UNDEF) for i in xrange(len(c.args))]

		oparg = code.func_name

		kwvararg = args.pop()[0] if c.varkwargs else None
		vararg   = args.pop()[0] if c.varargs else None

		freevars = {}
		for i in xrange(len(code.func_code.co_freevars)):
			freevars[code.func_code.co_freevars[i]] = code.func_closure[i].cell_contents
		#TODO: cellvars

		return [opcodes.FUNC, code.func_name, ast, args,  vararg, kwvararg, _globals, freevars]

	def _walk(self, code):
		self.covargs = {}
		self.stack   = []
		self.jumps   = {}

		self.globals = {}

		self.code    = CodeGenerator(code)
		for opcode, attr in self.code:
			#print opcode, attr
			if isinstance(opcode, byte.Label): # jump destination
				attr   = opcode
				opcode = 'LABEL'

			if not hasattr(self, 'do_%s' % opcode):
				assert False, "opcode %s not implemented" % opcode

			getattr(self, 'do_%s' % opcode)(attr)
			#print self.stack

		return self.stack, sorted(self.globals.keys())

	def do_SetLineno(self, attr):
		""" ignore """
		pass

  ### STACK OPERATIONS ###
	def do_POP_TOP(self, attr):
		"""Unstack TOS opcode"""
		self.stack.pop()

	def do_DUP_TOP(self, attr):
		"""Duplicate stack-top and stack it up"""
		self.stack.append(self.stack[-1])

	def do_ROT_TWO(self, attr):
		""""""
		self.stack.append(self.stack.pop(-2))

		opcode, arg = self.code.predict()
		if opcode in [byte.PRINT_ITEM_TO, byte.PRINT_NEWLINE_TO]:
			self.code.nexthop()
			getattr(self, 'do_%s' % opcode)(arg)

			# inverse rotation
			self.stack.append(self.stack.pop(-2))

	### ###
	def do_LOAD_CONST(self, attr):
		"""Stack up constant (untyped)"""
		self.stack.append((opcodes.CONST, attr))

	def do_LOAD_GLOBAL(self, attr):
		"""Stack up global variable.
			
			Special variables 'True' and 'False' are casted to constants
		"""
		if   attr == 'True':
			self.stack.append((opcodes.CONST, True))
		elif attr == 'False':
			self.stack.append((opcodes.CONST, False))
		elif attr == 'None':
			self.stack.append((opcodes.CONST, None))
		else:
			self.stack.append((opcodes.VAR, attr, namespaces.GLOBAL))
			self.globals[attr] = None

	def do_LOAD_FAST(self, attr):
		"""Stacking up local variable"""
		self.stack.append((opcodes.VAR, attr, namespaces.LOCAL))

	def do_DELETE_FAST(self, attr):
		""" """
		self.stack.append((opcodes.DEL, (opcodes.VAR, attr, namespaces.LOCAL)))

	def do_DELETE_GLOBAL(self, attr):
		self.globals[attr] = None
		self.stack.append((opcodes.DEL, (opcodes.VAR, attr, namespaces.GLOBAL)))

	def do_LOAD_ATTR(self, attr):
		"""Stacking up attribute

			Attribute owner is top-of-stack value (unstaked and set as attribute arg)
		"""
		self.stack.append((opcodes.ATTR, self.stack.pop(), attr))

	def do_STORE_ATTR(self, attr):
		self.stack.append((opcodes.SET, (opcodes.ATTR, self.stack.pop(), attr), self.stack.pop()))

	def do_LOAD_NAME(self, attr):
		self.stack.append((opcodes.VAR, attr, namespaces.NAME))

	def do_DELETE_NAME(self, attr):
		self.stack.append((opcodes.DEL, (opcodes.VAR, attr, namespaces.NAME)))

	def do_RETURN_VALUE(self, attr):
		"""Return TOS value (popped from stack)

			If RETURN opcode is followed by a LABEL (jump destination) then a POP_TOP,
			POP_TOP is ignored:
				i.e: in a 'if: else:' structure, a return at the end of 'if' branch is
				followed by LABEL + POP_TOP.
				This last one is use to unstack if condition at 'else' starting branch.
				As we still unstacked it at 'if' start, we must not unstack it twice
				(the bad element will be unstacked)
		"""
		# in some strange case, python make a legitim return followed
		# by a "return None"
		if len(self.stack) == 1 or self.stack[-2][0] != opcodes.RET:
			self.stack.append([opcodes.RET, self.stack.pop()])
		elif self.stack[-1][0] in (opcodes.CONST, opcodes.VAR):
			self.stack.pop()

		_next = self.code.predict()
		if _next is not None and isinstance(_next[0], byte.Label):
			self.do_LABEL(self.code.nexthop()[0])

			if self.code.predict()[0] == byte.POP_TOP:
				self.code.nexthop()

		# if RETURN is followed by a JUMP, this last is ignored
		# we found such construction on code compiled with compiler.compileFile:
		#
		# if a:
		#  return b
		# else
		#  ...
		#elif _next[0] == byte.JUMP_FORWARD:
		#	self.code.nexthop()

		"""
			ret a if a else b
		"""
		"""Unary if:else:
			We made a unique instruction (ret (ifelse)) from a (ifelse, (ret), (ret))
		"""
		if len(self.stack) > 1 and self.stack[-1][0] == opcodes.RET and\
			 self.stack[-2][0] == opcodes.IF and len(self.stack[-2][2]) > 0 and \
			 self.stack[-2][2][0][0] == opcodes.RET:
			ret = self.stack.pop()
			self.stack[-1][3] = [ret[1]]
			self.stack[-1][2] = [self.stack[-1][2][0][1]]

			ret[1] = self.stack.pop()
			self.stack.append(ret)

	def do_STORE_FAST(self, attr, sub=False):
		"""Affect TOS value to attr variable
		
			If called from UNPACK_SEQUENCE (sub=True), we are only interested in variable definition
		"""
		var = (opcodes.VAR, attr, namespaces.LOCAL)
		if sub:
			return var

		self.stack.append((opcodes.SET, var, self.stack.pop()))

	def do_STORE_NAME(self, attr):
		self.stack.append((opcodes.SET, (opcodes.VAR, attr), self.stack.pop()))

	def do_STORE_GLOBAL(self, attr, sub=False):
		"""
			If called from UNPACK_SEQUENCE (sub=True), we are only interested in variable definition
		"""
		var = (opcodes.VAR, attr, namespaces.GLOBAL)
		self.globals[attr] = None
		if sub:
			return var

		self.stack.append((opcodes.SET, var, self.stack.pop()))

	### LISTS ###

	def do_BUILD_TUPLE(self, attr):
		"""Build a list (in fact a tuple == static list)
		
			attr is the number of elements to unstack and append to the list
		"""
		elts = self.stack[-attr:]
		del self.stack[-attr:]

		self.stack.append((opcodes.TUPLE, elts))

	def do_BUILD_LIST(self, attr):
		"""Build a list

			attr is the number of elements to unstack and append to the list
			attr may be zero value (empty list)
		"""
		if attr == 0:
			self.stack.append((opcodes.LIST, []))
			return

		self.stack.append((opcodes.LIST, self.stack[-attr:]))
		del self.stack[-attr-1:-1]

	def do_STORE_SUBSCR(self, attr, sub=False):
		var = (opcodes.AT, self.stack.pop(-2), self.stack.pop())
		if sub:
			return var

		self.stack.append((opcodes.SET, var,	self.stack.pop()))

	def do_BINARY_SUBSCR(self, attr):
		""" list[10] 
		
			Access nth element in list.
			  . nth  is TOS
			  . list is TOS-1
		"""
		self.stack.append((opcodes.AT, self.stack.pop(-2), self.stack.pop()))

	def do_SLICE_0(self, attr):
		"""
			neither start or stop argument == whole list slice
			
			list[:]
		"""
		self.stack.append((opcodes.SLICE, self.stack.pop(), None, None))

	def do_SLICE_1(self, attr):
		"""
			only start argument (on top of stack)
			
			list[5:]
		"""
		self.stack.append((opcodes.SLICE, self.stack.pop(-2), self.stack.pop(), None))

	def do_SLICE_2(self, attr):
		"""
			only start argument (on top of stack)
			
			list[:10]
		"""
		self.stack.append((opcodes.SLICE, self.stack.pop(-2), None, self.stack.pop()))

	def do_SLICE_3(self, attr):
		"""
			only start argument (on top of stack)
			
			list[5:10]
		"""
		self.stack.append((opcodes.SLICE, self.stack.pop(-3), self.stack.pop(-2), self.stack.pop()))

	def do_LIST_APPEND(self, attr):
		# MAY BE a variable (don't know the typeof)
		#assert self.stack[-2][0] == opcodes.LIST 
		value = self.stack.pop()

		# replace specific opcode by standard CALL to 'append' function
		#self.stack.append([opcodes.APPEND, self.stack.pop(), value])
		self.stack.append([opcodes.CALL, (opcodes.ATTR, self.stack.pop(), 'append'),
			(value,), {}, None, None])

	def do_UNPACK_SEQUENCE(self, attr, sub=False):
		"""
			opcode= UNPACK_SEQUENCE 2

			UNPACK_SEQUENCE members may be: STORE_FAST, STORE_GLOBAL, STORE_SUBSCR

			UNPACK_SEQUENCE may be "loop variable" of FOR_ITER.
			In this case, sub is True, and we return TUPLE as target loop variable
		"""
		#if not sub:
		#	src = self.stack.pop()
		dst = []
		for i in xrange(attr):
			opcode, arg = self.code.nexthop()
			#assert opcode in (byte.STORE_FAST, byte.STORE_GLOBAL)
			#NOTE: STORE_SUBSCR is precedeed by variable name and index position (LOAD_XXX)
			while opcode not in (byte.STORE_FAST, byte.STORE_GLOBAL, byte.STORE_SUBSCR):
				getattr(self, 'do_%s' % opcode)(arg)
				opcode, arg = self.code.nexthop()

			dst.append(getattr(self, 'do_%s' % opcode)(arg, sub=True))

		dst = (opcodes.TUPLE, tuple(dst))
		if sub:
			return dst
		self.stack.append((opcodes.SET, dst, self.stack.pop()))


	### FUNCTIONS ###

	def do_CALL_FUNCTION(self, attr, vaarg=None, vakwarg=None):
		"""
		
			attr: function arguments count (taken from top stack)
				low byte  = num. of positional parameters
				high byte = num. of keyword parameters
		"""
		highb = attr >> 8
		lowb  = attr - (highb << 8)

		kwargs = {}
		if highb > 0:
			for i in xrange(-1, -highb*2-1, -2):
				kwargs[self.stack[i-1]] = self.stack[i]
			del self.stack[-highb*2:]

		args = []
		if lowb > 0:
			args = self.stack[-lowb:]
			del self.stack[-lowb:]
		
		self.stack.append([opcodes.CALL, self.stack.pop(), args, kwargs, vaarg, vakwarg])

		#
		if self.code.predict()[0] == byte.POP_TOP:
			self.code.nexthop()

	def do_CALL_FUNCTION_VAR(self, attr):
		args = self.stack.pop()
		self.do_CALL_FUNCTION(attr, vaarg=args)

	def do_CALL_FUNCTION_KW(self, attr):
		kwargs = self.stack.pop()
		self.do_CALL_FUNCTION(attr, vakwarg=kwargs)

	def do_CALL_FUNCTION_VAR_KW(self, attr):
		args, kwargs = self.stack.pop(-2), self.stack.pop()
		self.do_CALL_FUNCTION(attr, args, kwargs)

	def do_MAKE_FUNCTION(self, attr):
		"""
			function definition
		"""
		assert self.stack[-1][0] == opcodes.CONST and\
			   isinstance(self.stack[-1][1], byte.Code)

		# get function content and decode it
		opcode, func = self.stack.pop()
		xfunc, _globals = Parser()._walk(func.code)
		###

		dftval = []
		if attr > 0:
			dftval = self.stack[-attr:]
			del self.stack[-attr:]

		diff = len(func.args) - len(dftval)
		args = [(func.args[i], dftval[i-diff] if i >= diff else opcodes.UNDEF) for i in xrange(len(func.args))]

		opcode, oparg = self.code.predict()
		if opcode in [byte.STORE_NAME, byte.STORE_FAST]:
			self.code.nexthop()
		else:
			# 'lambda' is a reserved word, users can't use it a function name
			oparg = '<lambda>'

		kwvararg = args.pop()[0] if func.varkwargs else None
		vararg   = args.pop()[0] if func.varargs else None

		#TODO: handle freevars and cellvars

		self.stack.append([opcodes.FUNC, oparg, xfunc, args, vararg, kwvararg, _globals, {}])

	def do_STORE_DEREF(self, attr):
		self.stack.append((opcodes.SET, (opcodes.VAR, attr, namespaces.DEREF), self.stack.pop()))

	def do_LOAD_DEREF(self, attr):
		self.stack.append((opcodes.VAR, attr, namespaces.DEREF))

	def do_LOAD_CLOSURE(self, attr):
		self.stack.append((opcodes.VAR, attr))

	def do_MAKE_CLOSURE(self, attr):
		opcode, func = self.stack.pop()
		xfunc, _globals = Parser()._walk(func.code)

		_derefs  = self.stack.pop()
		assert _derefs[0] == opcodes.LIST
		_derefs = [var[1] for var in _derefs[1]]

		dftval = []
		if attr > 0:
			dftval = self.stack[-attr:]
			del self.stack[-attr:]

		diff = len(func.args) - len(dftval)
		args = [(func.args[i], dftval[i-diff] if i >= diff else None) for i in xrange(len(func.args))]

		opcode, oparg = self.code.predict()
		if opcode in [byte.STORE_NAME, byte.STORE_FAST]:
			self.code.nexthop()
		else:
			# 'lambda' is a reserved word, users can't use it a function name
			oparg = '<lambda>'
	
		self.stack.append([opcodes.FUNC, oparg, xfunc, args, func.varargs,
			func.varkwargs, _globals, _derefs])

	### NUMBER OPS ###

	def do_UNARY_POSITIVE(self, attr):
		self.stack[-1] = (opcodes.PLUS, self.stack[-1])

	def do_UNARY_NEGATIVE(self, attr):
		self.stack[-1] = (opcodes.MINUS, self.stack[-1])

	def do_BINARY_ADD(self, attr):
		"""
		  Note: is also used for string concatenation ('a'+'b' == 'ab')
		"""
		self.stack[-1] = (opcodes.ADD, self.stack.pop(-2), self.stack[-1])

	def do_BINARY_SUBTRACT(self, attr):
		self.stack[-1] = (opcodes.SUB, self.stack.pop(-2), self.stack[-1])

	def do_BINARY_DIVIDE(self, attr):
		self.stack[-1] = (opcodes.DIV, self.stack.pop(-2), self.stack[-1])

	def do_BINARY_MULTIPLY(self, attr):
		self.stack[-1] = (opcodes.MUL, self.stack.pop(-2), self.stack[-1])

	def do_BINARY_MODULO(self, attr):
		self.stack[-1] = (opcodes.MOD, self.stack.pop(-2), self.stack[-1])

	def do_INPLACE_ADD(self, attr):
		target = self.stack[-2]
		self.do_BINARY_ADD(attr)
		self.stack.append(('set', target, self.stack.pop()))

	def do_INPLACE_SUBTRACT(self, attr):
		target = self.stack[-2]
		self.do_BINARY_SUBTRACT(attr)
		self.stack.append(('set', target, self.stack.pop()))

	def do_INPLACE_DIVIDE(self, attr):
		target = self.stack[-2]
		self.do_BINARY_DIVIDE(attr)
		self.stack.append(('set', target, self.stack.pop()))

	def do_INPLACE_MULTIPLY(self, attr):
		target = self.stack[-2]
		self.do_BINARY_MULTIPLY(attr)
		self.stack.append(('set', target, self.stack.pop()))

	def do_INPLACE_MODULO(self, attr):
		target = self.stack[-2]
		self.do_BINARY_MODULO(attr)
		self.stack.append(('set', target, self.stack.pop()))

	def do_UNARY_INVERT(self, attr):
		self.stack[-1] = (opcodes.INVERT, self.stack[-1])

	### DICT ###

	def do_BUILD_MAP(self, attr):
		"""
			attr = number of items in dict
			
			BUILD_MAP 2
			...
		"""
		self.stack.append((opcodes.DICT, []))

	def do_STORE_MAP(self, attr):
		"""
			call for each key/value couple
			
			LOAD_ATTR name
			LOAD_CONST joe
			STORE_MAP None
		"""
		self.stack[-3][1].append((self.stack.pop(), self.stack.pop()))


	### BOOLEAN OPS ###

	COMPARE_MAP = {
		'is'             : opcodes.ID,
		'is not'         : opcodes.NID,
		'=='             : opcodes.EQ,
		'!='             : opcodes.NEQ,
		'>'              : opcodes.GT,
		'<'              : opcodes.LT,
		'>='             : opcodes.GEQ,
		'<='             : opcodes.LEQ,
		'in'             : opcodes.IN,
		'not in'         : opcodes.NIN,

		#try:except exception comparison
		'exception match': opcodes.MARKER_EXCEPT
	}

	def do_COMPARE_OP(self, attr):
		"""boolean operation"""
		if self.COMPARE_MAP[attr] == opcodes.MARKER_EXCEPT:
			"""except: COMPARE_OP is followed by:
					- JUMP_IF_FALSE
					- POP_TOP (*2)
					- STORE_NAME
					- POP_TOP

				and precedeed by a 
					- DUP_TOP
					- LOAD_NAME Exception
			"""
			self.stack.pop(-2)

			assert self.code.predict()[0] == byte.JUMP_IF_FALSE
			jmp = self.code.nexthop()
			
			while self.code.predict()[0] == byte.POP_TOP:
				self.code.nexthop()
			# STORE_XXX (facultative)
			if is_STORE(self.code.predict()[0]):
				opcode, attr = self.code.nexthop()
				getattr(self, 'do_%s' % opcode)(attr)

				while self.code.predict()[0] == byte.POP_TOP:
					self.code.nexthop()

				store = self.stack.pop()
			else:
				store = (None, None, self.stack.pop())
			self.stack[-1][1] = (store[2], store[1])

			node = self.jumps.setdefault(jmp[1], [])
			node.insert(0, self.stack[-1])
			return

		self.stack[-1] = (self.COMPARE_MAP[attr], self.stack.pop(-2), self.stack[-1])

	def do_UNARY_NOT(self, attr):
		top = self.stack.pop()
		if top[0] == opcodes.MARKER_IFFALSE:
			if len(top[2]) != 1:
				raise Exception()

			top[0] = opcodes.AND
			top[2] = top[2][0]
		elif top[0] == opcodes.MARKER_IFTRUE:
			if len(top[2]) != 1:
				raise Exception()

			top[0] = opcodes.OR
			top[2] = top[2][0]

		self.stack.append((opcodes.NOT, top))


	### PRINTSCREEN ###

	def do_UNARY_CONVERT(self, attr):
		"""
			`plop` is the old notation for repr(plop)
		"""
		self.stack[-1] = (opcodes.CALL, (opcodes.VAR, 'repr', namespaces.GLOBAL), (self.stack[-1],), {},
				None, None)

	def do_PRINT_ITEM(self, attr):
		self.__print(self.stack.pop())

	def do_PRINT_NEWLINE(self, attr):
		self.__print((opcodes.CONST, '\n'))

	def __print(self, arg):
		stream = None #(opcodes.ATTR, (opcodes.VAR, 'sys'), 'stdout')

		if len(self.stack) > 0 and\
			 self.stack[-1][0]    == opcodes.PRINT and\
			 self.stack[-1][1]    == stream:
			self.stack[-1][2].append(arg)
		else:
			self.stack.append((opcodes.PRINT,	stream, [arg]))

	def do_PRINT_ITEM_TO(self, attr):
		stream = self.stack.pop()
		args   = [self.stack.pop()]

		self.__print_to(stream, args)

	def do_PRINT_NEWLINE_TO(self, attr):
		args   = [(opcodes.CONST, '\n')]
		stream = self.stack.pop()

		self.__print_to(stream, args)

	def __print_to(self, stream, args):
		while len(self.stack) > 0 and\
 			    self.stack[-1][0] == opcodes.PRINT and\
					self.stack[-1][1] == stream:
			nargs = self.stack.pop()[2]
			nargs.extend(args)
			args = nargs
		
		self.stack.append((opcodes.PRINT, stream, args))


	### IMPORTS ###
	def do_IMPORT_NAME(self, attr):
		level = self.stack[-2]
		del self.stack[-2:]

		name = None
		if self.code.predict()[0] in [byte.STORE_NAME, byte.STORE_FAST]:
			null, name = self.code.nexthop()
			if name == attr:
				name = None

		self.stack.append([opcodes.IMPORT, attr, [], name, level])

	def do_IMPORT_STAR(self, attr):
		assert self.stack[-1][0] == opcodes.IMPORT
		self.stack[-1][2].append(('*', None))

	def do_IMPORT_FROM(self, attr):
		assert self.stack[-1][0] == opcodes.IMPORT

		alias = None
		if self.code.predict()[0] in [byte.STORE_NAME, byte.STORE_FAST]:
			null, alias = self.code.nexthop()
			if alias == attr:
				alias = None

		if self.code.predict()[0] == byte.POP_TOP:
			self.code.nexthop()

		self.stack[-1][2].append((attr, alias))

	### CONDITIONAL/UNCONDITIONAL JUMPS (if, else) ###
	"""
	def do_POP_JUMP_IF_FALSE(self, attr):
		print self.stack
		raise Exception
	"""
	def do_JUMP_IF_FALSE(self, attr):
		jmp = [opcodes.AND, self.stack[-1], None]
		# POP_TOP must not stack ou our AND instr, but its 1st argument
		if self.code.predict()[0] == byte.POP_TOP:
			self.code.nexthop()
			self.do_POP_TOP(None)
		else:
			self.stack.pop()

		self.stack.append(jmp)

		node = self.jumps.setdefault(attr, [])
		node.insert(0, jmp)

	def do_JUMP_IF_TRUE(self, attr):
		jmp = [opcodes.OR, self.stack[-1], None]
		# POP_TOP must not stack ou our AND instr, but its 1st argument
		if self.code.predict()[0] == byte.POP_TOP:
			self.code.nexthop()
			self.do_POP_TOP(None)
		else:
			self.stack.pop()
		self.stack.append(jmp)

		node = self.jumps.setdefault(attr, [])
		node.insert(0, jmp)

	def do_JUMP_ABSOLUTE(self, attr):
		if isinstance(self.code.predict()[0], byte.Label):
			jmp = [opcodes.MARKER_JUMP, attr]
			self.stack.append(jmp)

			self.do_LABEL(self.code.nexthop()[0])

			if self.code.predict()[0] == byte.POP_TOP:
				self.code.nexthop()
		else:
			assert False

		node = self.jumps.setdefault(attr, [])
		self.jumps[attr].insert(0, self.stack[-1])

	def do_JUMP_FORWARD(self, attr):
		#_next = self.code.predict()
		#if isinstance(_next[0], byte.Label): # jump destination
		if isinstance(self.code.predict()[0], byte.Label):
			jmp = [opcodes.MARKER_JUMP, attr]
			self.stack.append(jmp)

			self.do_LABEL(self.code.nexthop()[0])

			#if self.code.predict()[0] == byte.POP_TOP:
			while self.code.predict()[0] == byte.POP_TOP:
				self.code.nexthop()
		#elif _next[0] == byte.END_FINALLY:

		if self.code.predict()[0] == byte.END_FINALLY:
			# just eat the END_FINALLY
			self.code.nexthop(); return
		#else:
		#	assert False

		node = self.jumps.setdefault(attr, [])
		#self.jumps[attr].insert(0, self.stack[-1])
		# prevent from having both the same instr. following each other in link jumps list
		if len(node) == 0 or node[0] != self.stack[-1]:
			node.insert(0, self.stack[-1])

		#print '>>', self.jumps

	### LIST/LIST COMPREHENSION ###
	def do_SETUP_LOOP(self, attr):
		pass

	def do_POP_BLOCK(self, attr):
		pass

	### TRY/EXCEPT/FINALLY ###
	def do_SETUP_FINALLY(self, attr):
		block = [opcodes.TRYCATCH, None, None, None, True]
		self.stack.append(block)

		node = self.jumps.setdefault(attr, [])
		node.insert(0,  block)


	def do_SETUP_EXCEPT(self, attr):
		"""
			attr is the position (label) where starts the except clause

			opcode args:
				. except Exception and variable
				. try block
				. except block
				. finally block
		"""
		#print 'except', attr
		# if we have both except: and finally: blocs, 
		# SETUP_EXCEPT follows SETUP_FINALLY
		if len(self.stack) > 0 and self.stack[-1][0] == opcodes.TRYCATCH and\
			 self.stack[-1][4] == True:
			block = self.stack[-1]
			block[-2] = True
		else:
			block = [opcodes.TRYCATCH, None, None, True, None]	
			self.stack.append(block)

		node = self.jumps.setdefault(attr, [])
		node.insert(0, block)

	def do_END_FINALLY(self, attr):
		tryb = None
		for i in xrange(len(self.stack)-1,-1,-1):
			if self.stack[i][0] == opcodes.TRYCATCH:
				tryb = self.stack[i];	break

		#if tryb is None or tryb[-1] is not True:
		if tryb is None or not (tryb[-1] is True or isinstance(tryb[-1], list) and
				len(tryb[-1]) == 0):
			#raise Exception
			return

		pos = self.stack.index(tryb)
		tryb[-1] = self.stack[pos+1:]
		del self.stack[pos+1:]



	### LOOPS/ITERATIONS ###
	def do_BREAK_LOOP(self, attr):
		self.stack.append((opcodes.BREAK,))

	def do_GET_ITER(self, attr):
		"""
			param 1: loop variable
			param 2: loop argument
			param 3: loop instructions
			param 4: returned list (for list comprehensions, None else)
		"""
		cond = self.stack.pop()
		ret  = None

		if len(self.stack) > 0 and self.stack[-1][0] == opcodes.SET and\
				(self.stack[-1][1][1].startswith('_[') or self.stack[-1][1][1].startswith('$list')):
			assert self.stack[-2][0] == opcodes.LIST and len(self.stack[-2][1]) == 0
			del self.stack[-2]

			ret = self.stack.pop()[1][1]

		self.stack.append([opcodes.FOR, None, cond, None, ret])

	def do_FOR_ITER(self, attr):
		"""
			FOR_ITER opcode is followed by the loop variable, which may be:
				. a STORE_XXX opcode
				. a UNPACK_SEQUENCE
		"""
		assert self.stack[-1][0] == opcodes.FOR
		
		node = self.jumps.setdefault(attr, [])
		self.jumps[attr].insert(0, self.stack[-1])

		# get loop variable
		opcode, arg = self.code.nexthop()
		if opcode not in (byte.STORE_FAST, byte.STORE_GLOBAL, byte.UNPACK_SEQUENCE):
			#NOTE: STORE_SUBSCR is precedeed by variable name and index position (LOAD_XXX)
			while opcode != byte.STORE_SUBSCR:
				getattr(self, 'do_%s' % opcode)(arg)
				opcode, arg = self.code.nexthop()

		self.stack[-1][1] = getattr(self, 'do_%s' % opcode)(arg, sub=True)

	def do_LABEL(self, label):
		#print 'LBL=', label
		if label not in self.jumps:
			print >>sys.stderr, " *** flashback label ***", label
			return
			

		for instr in self.jumps[label]:
			#print instr
			#import pprint; pprint.pprint(self.stack)
			i = self.stack_index(instr)
			if i is None:
				print >>sys.stderr, " *** instruction not found ***", self.stack, instr; continue

			do_iter = True

			if instr[0] == opcodes.IF:
				assert instr[3] is None

				instr[3] = self.stack[i+1:]
				del self.stack[i+1:]
				top = self.stack.pop()
				do_iter = False

			if do_iter:
				prev = self.stack.pop()
			while do_iter:
				top = self.stack.pop() if len(self.stack) > 0 else None

				# TRY/EXCEPT
				if instr[0] == opcodes.TRYCATCH:
					idx = -1
					if instr[2] is None:
						#assert prev[0] == opcodes.MARKER_JUMP
						idx = 2
					elif instr[3] in (True, None):
						idx = 3
					elif instr[4] in (True, None):
						idx = 4

					#print ">>", instr, idx, prev, top, self.stack
					blok = self.stack[i+1:]
					if top is not None and top != instr:
						blok.append(top)
					if prev != instr and prev[0] != opcodes.MARKER_JUMP and not\
						 (prev[0] == opcodes.CONST and prev[1] is None):
						blok.append(prev)

					if len(blok) > 0 or instr[idx] is True:
						instr[idx] = blok

					if len(self.stack) > 0:
						self.stack.pop() # unstack for() temporary
					top = instr


				elif prev[0] == opcodes.MARKER_JUMP and\
					 instr[0] == opcodes.FOR:
					assert instr[3] is None

					instr[3] = self.stack[i+1:]
					del self.stack[i+1:]
					instr[3].append(top)

					self.stack.pop() # unstack for() temporary
					top = instr


				elif prev[0] == opcodes.MARKER_JUMP or\
				   prev[0] == opcodes.RET:
					assert instr[0] in (opcodes.AND, opcodes.OR) and instr[2] is None

					if instr[0] == opcodes.OR:
						# or == not and
						instr[1] = [opcodes.NOT, instr[1]]

					pclone  = list(prev)
					prev[0] = opcodes.IF
					prev[1] = instr[1]
					# unstack from index i (excluded) to top
					prev.extend([self.stack[i+1:], None])
					del self.stack[i+1:]
					if pclone[0] == opcodes.RET:
						prev[2].append(pclone)

					self._update_refs(top, prev)
					if top != instr:
						prev[2].append(top)
						self._update_refs(instr, prev)
				
						if len(self.stack) > 0:
							self.stack.pop() # unstack instr as replaced by prev

					top   = prev
					instr = prev
					
				elif top[0] in [opcodes.AND, opcodes.OR] and top[2] is None:
					if prev[0] in [opcodes.AND, opcodes.OR] and prev[2] is None:
						"""
							top  = or(a, None)
							prev = and(b, None)

							=> top = and(or(a, b))
						"""

						top[2]  = prev[1]
						prev[1] = top
						top     = prev # prevent swap

						self._update_refs(top[1], top)
						if instr == top[1]: # old top
							instr = top
			
					elif prev[0] == opcodes.IF:
						top[2]   = prev[1]
						prev[1] = top
						top     = prev

						self._update_refs(top[1], top)
						if instr == top[1]: # old top
							instr = top
					else:
						"""
							top  = or(a, None)
							prev = b

							=> top = or(a, b)
						"""
						top[2]   = prev
						self._update_refs(prev, top)

				if top == instr:
					break;

				prev = top

			self.stack.append(top)
			if self.code.predict()[0] == byte.POP_TOP:
				# skip pop_top
				self.code.nexthop()

	def stack_index(self, instruction):
		for i in xrange(len(self.stack)):
			if id(instruction) == id(self.stack[i]):
				return i
				
		return None

	def _update_refs(self, old, new):
		"""
			Must be optimized
		"""
		for key, jumps in self.jumps.iteritems():
			if old not in jumps:
				continue

			jumps = [new if j is old else j for j in jumps]
			jumps.reverse()
			j2    = []

			for i in xrange(len(jumps)):
				if jumps[i] in jumps[i+1:]:
					continue

				j2.insert(0, jumps[i])
				
			# we may have duplicates, and should remove them
			# we can't use set because values are also list (error TypeError: unhashable type:
			# 'list')
			
			self.jumps[key] = j2

	### CLASS ###
	def do_LOAD_LOCALS(self, attr):
		""" Used for classes definition
			Ignore from now as we do not support classes yet
		"""
		pass

	def do_BUILD_CLASS(self, attr):
		pass

