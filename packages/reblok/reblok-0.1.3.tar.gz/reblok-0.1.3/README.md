Reblok
======

[Reblok](http://devedge.bour.cc/wiki/Reblok) build an Abstract Syntax Tree (AST) back from python bytecode.


###Requirements:
* [byteplay](http://pypi.python.org/pypi/byteplay)

###Compatility:
*	python 2.[5-6] (NOT python 2.7, see [Notes](#notes) bellow)

* Has not been tested with python3,
*	Should work with [pypy](http://pypy.org), although some specific opcodes are not handled (see
	[Pypy special opcodes](http://codespeak.net/pypy/dist/pypy/doc/interpreter-optimizations.html#special-bytecodes)).

###Installation
	easy_install reblok

or

	wget http://devedge.bour.cc/resources/reblok/src/reblok.latest.tar.gz
	tar xvf reblok.latest.tar.gz
	cd reblok-* && ./setup.py install

Documentation
-------------

You can found reblok opcodes documentation at [http://devedge.bour.cc/resources/reblok/doc/sources/ast.html](http://devedge.bour.cc/resources/reblok/doc/sources/ast.html)

Example
-------

	>>> from reblok import Parser
	>>> add = lambda x: x + 1
	>>> ast = Parser().walk(add)
	>>> print ast
	['function', '<lambda>', [['ret', ('add', ('var', 'x', 'local'), ('const', 1))]], [('x', '<undef>')], None, None, [], {}]

Notes<a id="notes"/>
-----

reblok is not compatible with python 2.7 at the moment as JUMP\_IF\_FALSE and JUMP\_IF\_TRUE opcodes are replaced by new POP\_JUMP\_IF\_FALSE, POP\_JUMP\_IF\_TRUE, JUMP\_IF\_FALSE\_OR\_POP and
JUMP\_IF\_TRUE\_OR\_POP opcodes.<br/>
Will be fixed in a future release.

Not yet handled opcodes:
 * POP_JUMP_IF_TRUE      (py2.7)
 * POP_JUMP_IF_FALSE     (py2.7)
 * JUMP_IF_FALSE_OR_POP  (py2.7)
 * JUMP_IF_FALSE_OR_TRUE (py2.7)

About
-----

*Reblok* is licensed under GNU GPL v3.<br/>
It is developped by Guillaume Bour &lt;guillaume@bour.cc&gt;
