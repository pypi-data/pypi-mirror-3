Abstract Syntax Tree
====================

reblok create an AST (Abstract Syntax Tree) from python bytecode.
But this AST is different from the official python one (describe at `http://docs.python.org/library/ast.html`)

a reblok AST is a list of node, which can be either: 
* an instruction (affectation, return, conditional branch, ...), 
* a definition (function), 
* an accessor (object attribute, array index, array range, dictionary value)
* a variable
* a constant literal (integer, boolean, None, ...)

Accessors, variables and literals cannot be finals (e.g must be *included* into another node).
Technically, a node is a tuple of 2 elements at least; where first is the opcode, followed by its arguments

Literal string is quoted ('blue firefly'); null value, integers, floats and booleans are represented with their raw value (respectively: None, 1, 2.45, True).
Variables are written without quotes.


ADD
...
**(ADD, left, right)**

Arithmetic *addition*: left + right

NOTE: in a string context (both left and right are resolving to strings), ADD stands for **string concatenation**

Example::

  print 1.142 + 0.476
  >>> 1.618

  (PRINT, [(ADD, (CONST, 1.142), (CONST, 0.476)), (CONST, '\n')])

  print 'leonardo' + ' Da Vinci'
  >>> leonardo Da Vinci

  (PRINT, None, [(ADD, (CONST, 'leonardo'), (CONST, ' Da Vinci')), (CONST, '\n')])

AND
...
**(AND, left, right)**

Boolean *and*: left and right

Example::

  if(hour > 17 and light is False): 
    lighton()

  (IF, 
    (AND, 
      (GT, (VAR, 'hour'), (CONST, 17)), 
      (IS, (VAR, 'light'), (CONST, False))
    ), 
    [(CALL, 'lighton', (), {}, None, None)], 
    []
  )

AT
..
**(AT, mylist, (CONST, 10))**

List item accessor.
3d item (list index) MAY be a *CONST*, *VARIABLE*, ...

Example::

  colors[3]

  (AT, (VAR, 'colors'), (CONST, 3))

ATTR
....
**(ATTR, myobject, 'myattr')**

Object attribute.

Example::

  print captain.age
  >>> 63

  (PRINT, None, [(ATTR, (VAR, captain), 'age'), (CONST, '\n')])

BREAK
.....
**(BREAK,)**

Break a loop

Example::

  for i in xrange(10):
    break

  (FOR, 
    (VAR, 'i'), 
    (CALL, (VAR, 'xrange'), [(CONST, 10)], {}, None, None),
    [(BREAK,)],
    None
  )


CALL
....
**(CALL, function, args, kwargs, vaargs, kwvaargs)**

Function call
function MUST BE either *VAR*, *ATTR*, *AT*
args is a list of positional arguments (if no arguments, args is an empty list)
kwargs is a dictionary of named arguments (where key is argument name and value argument default value)
vaargs point to the variable positional arguments list. If None, the function does not accept undeclared positional arguments, else vaargs is set to argument name)
kwvaargs point to the variable named arguments list. If None the function does not accept undeclared named arguments, else kwvaargs is set to argument name)

NOTE: 

Example::

  car.run(speed=45, **kwargs)
  >>> Car is now running at 45km

  (CALL, (ATTR, (VAR, car), run), (), {'speed': 45}, None, 'kwargs')

CONST
.....
**(CONST, 'Three witches watch three Swatch watches. Which witch watch which Swatch watch?')**

Constant literal. MAY be string (single quoted), integer, float, boolean, None,
tuple

Example::

  color = 'red'
  age   = 27
  blond = True
  countries = ('France', 'Spain', 'Belgium')

  [
    (SET, (VAR, 'color'), (CONST, 'red')),
    (SET, (VAR, 'age'),   (CONST, 27)),
    (SET, (VAR, 'blond'), (CONST, True)),
    (SET, (VAR, 'countries'), (CONST, ('France', 'Spain', 'Belgium')))
  ]

DEL
...
**(DEL, (VAR, 'foo'))**

Delete a variable

Example::
  foo = 'bar'
  del foo

  [
    (SET, (VAR, 'foo'), (CONST, 'bar')),
    (DEL, (VAR, 'foo'))
  ]

DICT
....
**(DICT, [initvals])**

Create a new dictionary with initial values (list of key/value tuples)

Example::

  students = {'pierre': 19, 'hélène': 18}

  (SET, (VAR, 'students'), (DICT, [('pierre', 19), ('hélène', 18)]))

DIV
...
**(DIV, left, right)**

Arithmetic division: left / right

Example::

  print 1024/2
  >>> 512

  (PRINT, None, [(DIV, (CONST, 1024), (CONST, 2))), (CONST, '\n')])

EQ
...
**(EQ, left, right)**

Boolean *equality*: left == right

Example::
  
  print carot == potatoes
  >>> False

  (PRINT, None, [(EQ, (VAR, 'carot'), (VAR, 'potatoes')), (CONST, '\n')])

FOR
...
**(FOR, loopvar, arglist, instrs, ret)**

*foreach* 
arglist is the list we iter, loopvar is the inner variable for each iteration.
instrs is the loop instructions list
ret is the returned list (list comprehension), else None

Note::
  loopvar is either a variable (VAR) or a TUPLE of variables


Example::

  for student in class.students:
    student.note = 0

  (FOR, 
    (VAR, 'student'), 
    (ATTR, (VAR, 'class'), 'students'), 
    [(SET, (ATTR, (VAR, 'student'), 'note'), (CONST, 0))], 
    None
  )

  for (start, len) in statistics:
    print 'start %d, len %d' % (start, len)

  (FOR
    (TUPLE, [(VAR, 'start'), (VAR, 'len')]),
    (VAR, 'statistics'),
    [(PRINT, None, [(MOD, (CONST, 'start %d, len %d'), (TUPLE, [(VAR, 'start'), (VAR, 'len')]))])],
    None
  )

FUNC
....
**(FUNC, name, [instructions], (args), vaargs, vakwargs, globals, derefs)**

Function definition:
# *name* is the function name. special value '<lambda>' means we declare a lambda
function
# args is the list of function arguments. Each one is set as a tuple (variable
name, default value), where default value is opcodes.UNDEF when there is no default
value for this argument
# vaargs is the name of the "positional variable arguments" variable (None if not
set)
# globals is the list of global variables used in the function
# derefs is the list of derefs variables used in the function  (is set to None if no deref variables as used)


Example::

  def alice_rabbit(hour, *args):
    print "I'm late, I'm late, it's %d O'clock!"

  alice_rabbit(10)
  >> I'm late, I'm late, its 10 O'clock;

  [
    (FUNC,
      'alice_rabbit',
      [(PRINT, None, [(CONST, 'I\'m late, I\'m late, it\'s %d O\'clock!'), (CONST, '\n')], (RET, None)]
      ((hour, UNDEF)),
      'args',
      None
    ),
    (CALL, 'alice_rabbit', (10), {}, None, None)
  ]


GEQ
...
**(GET, left, right)**

Boolean *greater-or-equal*: left >= right

Example::

  print dog >= cat
  >>> True

  (PRINT, None, [(GEQ, (VAR, 'dog'), (VAR, 'cat')), (CONST, '\n')])

GT
...
**(GT, left, right)**

Boolean *greater-than*: left > right

Example::

  print elephant > mouse
  >>> True

  (PRINT, None, [(GT, (VAR, 'elephant'), (VAR, 'mouse')), (CONST, '\n')])

IF
..
**(IF, condition, [iftrue-instructions], [iffalse-instructions])**

Conditional statement.

Example::

  if me.age < 18:
    me.drink = False
  else:
    me.drive = True

  (IF, 
    (LT, (ATTR, (VAR, 'me'), 'age'), (CONST, 18)),
    [(SET, (ATTR, (VAR, 'me'), 'drink'), (CONST, False))],
    [(SET, (ATTR, (VAR, 'me'), 'drive'), (CONST, True))]
  )

IMPORT
......
**(IMPORT, module, (identifiers), alias, level)**

Import modules.
alias is None is no alias set for module
idenfitiers is a tuple of (identifier, alias) where alias may be None

NOTE: 
* if alias is set (not None), identifiers must be empty, and vice versa
* is identifier is '*', alias MUST be None and the MUST not have other identifiers set

Examples::

  import sys

  (IMPORT , 'sys', (), None, -1)


  import sys as system

  (IMPORT, 'sys', (), 'system', -1)


  from sys import stdin as input, stdout

  (IMPORT, 'sys', (('stdin', 'input'), ('stdout', None)), None, -1)


  from os.path import basename

  (IMPORT, 'os.path', (('basename', None)), None, -1)

IN
..
**(IN, arg, list)**

sets operation: *arg* in *list* list.
Return a boolean

Example::

  'new-orleans' in usa

  (IN, ('CONST', 'new-orleans'), (VAR, 'usa'))

INVERT
......
**(INVERT, arg)**

Bitwise inverse of *arg* number

Example::
  
  print ~10
  >>> -11

  (PRINT, None, [(INVERT, (CONST, 10)), (CONST, '\n')])

LIST
....
**(LIST, [values])**

Build a list.

Example::

  colors = ['red', 'blue', 'white', 'cyan']

  (SET, (VAR, 'colors'), (LIST, [(CONST, 'red'), (CONST, 'blue'), (CONST, 'white'), (CONST, 'cyan')]))

LEQ
...
**(LEQ, left, right)**

Boolean **lower or equal**: *left <= right*

Example::

  dwarf <= small_person

  (LEQ, (VAR, 'dwarf'), (VAR, 'small_person'))

LT
..
**(LT, left, right)**

Boolean *lower than* operation: *left < right*

Example::

  dwarf < giant

  (LT, (VAR, 'dwarf'), (VAR, 'giant'))

MINUS
...
**(MINUS, arg)**

Negation:

Example::

  b = -a

  (SET, (VAR, 'b'), (MINUS, (VAR, 'a')))

MOD
...
**(MOD, left, right)**

Arithmetic **modulo**: *left % right*

NOTE: *MOD* is also used as print formatting

Examples::

  remains = 11 % 2
  >>> remains === 1

  (SET, (VAR, 'remains'), (MOD, (CONST, 11), (CONST, 2)))


  print "%s is %d years old" % ('The captain', 86)
  >>> The captain is 86 years old

  (PRINT, None, [(MOD, (CONST, '%s is %d years old'), [(CONST, 'The captain'), (CONST, 86)]), (CONST, '\n')])

MUL
...
**(MUL, left, right)**

Arithmetic operation: *left* * *right*.
NOTE: one of *left* or *right* may resolve to a string. In this case, the result is the string repeated *peer* times

Example::

  print 6 * 7
  >>> 42

  (PRINT, None, [(MUL, (CONST, 6), (CONST, 7)), (CONST, '\n')])

  print 'no, ' * 4
  >>> no, no, no, no

  (PRINT, None, [(MUL, (CONST, 'no, '), (CONST, 4)), (CONST, '\n')])

NEQ
...
**(NEQ, left, right)**

Boolean comparison: *left* not equal *right*

Example::

  if night != day:
    pass

  (IF, (NEQ, (VAR, 'night'), (VAR, 'day')), [], [])

NIN
...
**(NIN, arg, list)**

sets operation: *arg* not in *list* list.
Return a boolean

Example::

  'orleans' not in usa

  (NIN, ('CONST', 'orleans'), (VAR, 'usa'))

NOT
...
**(NOT, arg)**

Boolean negation.
*arg* **MUST** be *CONST*, *VAR*, *ATTR*, *AT* or *CALL*; and resolve to boolean value

Example::

  night = !day

  (SET, (VAR, 'night'), (NOT, (VAR, 'day')))

OR
...
**(OR, left, right)**

Boolean *or* operation. *left* and *right* MUST be *CONST*, *VAR*, *ATTR*, *AT* or *CALL*; and resolve to boolean value

Example::

  meal = cheese or dessert

  (SET, 'meal', (OR, (VAR, 'cheese'), (VAR, 'dessert')))

PLUS
....
**(PLUS, arg)**

Get *`arg`* positive value

Example::

  prefix = +33

  (SET, (VAR, a), (PLUS, 33))


PRINT
.....
**(PRINT, stream, [nodes])**

Print a list of *nodes* in *stream* output stream

Note: if stream set to None, means printing to default output stream

Example::

  print "captain is", 86, "aged old"

  (PRINT, None, [(CONST, 'captain is'), (CONST, 86), (CONST, ('aged old'))])


  print >>sys.stdout, "captain is", 86, "aged old"

  (PRINT, (ATTR, (VAR, 'sys'), 'stdout'), [(CONST, 'captain is'), (CONST, 86), (CONST, ('aged old'))])


  print >>outfile, "tic tac toe"

  (PRINT, (VAR, 'outfile'), [(CONST, 'tic tac toe')])


RET
...
**(RET, arg)**

Return a value. a return instruction is placed into a function, or as the last node in main list

Example:

  return captain.age

  (RET, (ATTR, (VAR, 'captain'), 'age'))

SET
...
**(SET, (VAR, 'myvar'), 999)**

Variable affectation
2d item MUST be a settable instruction: *Variable*, *At*, ... 

Example::

  popcorn   = 472
  depth[10] = 3.14
  (name, age) = ('doe', 21)

  [
    (SET, (VAR, 'popcorn'), (CONST, 472)),
    (SET, (AT, (VAR, 'depth'), (CONST, 10)), (CONST, 3.14)),
    (SET, (TUPLE, [(VAR, 'name'), (VAR, 'age')]), (TUPLE, [(CONST, 'doe'), (CONST, 21)]))
  ]

SLICE
...
**(SLICE, list, start, end)**

*list* is either a **LIST**, **VAR**, **ATTR**, or a **CALL** node
*start* is a signed integer or None value
*end* is a signed integer or None value 
(NOTE: both *start* and *end* can be None. Thus we get the entire list)

Example::

  primes = [1, 3, 5, 7]
  print primes[1:-2]
  >>> [3,5]

  [
    (SET, (VAR, primes), (LIST, [1, 3, 5, 7])),
    (PRINT, None, [(SLICE, (VAR, 'primes'), 1, -2), (CONST, '\n')])
  ]


SUB
...
**(SUB, left, right)**

mathematical operation: substraction.
*left* and *right* MUST BE *CONST*, *VAR*, *ATTR*,  *AT* or *CALL*; and may resolve to an integer or a float

Example::

 result = beer_cnt - 1

 (SET, (VAR, 'result'), (SUB, (VAR, 'beer_cnt'), 1))

TRY
...
**(TRY, (Exception, except-variable), try-clause, except-clause, finally-clause)**

try: except: finally: statement

* if except clause is not present, 2d value (exception+variable) is None, as except-clause
* if neither exception nor except variable as set in expect clause, 2d argument is None
* if finally clause is not present, finally-clause is None
* if except clause is empty (`pass`), except-clause is empty list
* if finally clause is empty (`pass`), finally-clause is empty list

Example::

 try:
   a = 1
 except ValueError, e:
   print e
 finally
   print 'pass'

 (TRY, ((VAR, 'ValueError'), (VAR, 'e')), [(SET, (VAR, 'a'), (CONST, 1))], [(PRINT, None, [(VAR, 'e'), (CONST, '\n')])], [(PRINT, None, [(CONST, 'pass'), (CONST, '\n')])])


 try:
   a = 1
 except:
   pass

 (TRY, None, [(SET, (VAR, 'a'), (CONST, 1))], [], None)

TUPLE
....
**(TUPLE, [values])**

Build a tuple (static-length list).

Example::

  colors = ('red', 'blue', 'white', 'cyan')

  (SET, (VAR, 'colors'), (TUPLE, [(CONST, 'red'), (CONST, 'blue'), (CONST, 'white'), (CONST, 'cyan')]))

VAR
...
**(VAR, name)**

Variable.

Example::

  name = 'john doe'
  print name
  >>> john doe

  [
    (SET, (VAR, 'name'), (CONST, 'john doe')),
    (PRINT, None, [(VAR, 'name'), (CONST, '\n')])
  ]


