.. -*-mode: rst; coding: utf-8;  -*-

====================
Interfaces to Python
====================

Contents
=========
  * `Lizpop data types <=> Python data types`_
  * `Built-In attributes`_
  * `To import Python module in Lizpop`_
  * `To call Python functions from a Scheme interpreter`_
  * `How to access Python objects from Scheme interpreter`_
  * `Data Type Conversion`_
  * `Exception Handling`_
  * `Convert Scheme closure to Python's callable.`_
  * `How to run Scheme code from Python.`_


Lizpop data types <=> Python data types 
=========================================

  ================      ========================
  Lizpop                Python
  ================      ========================
  string                unicode-string
  number                long, int, float
  boolean               bool
  vector                list
  multiple value        tuple
  symbol                lizpop.scheme.Symbol
  keyword symbol        lizpop.scheme.Keyword
  list                  lizpop.scheme.ScmList 
  empty list            lizpop.mylist.NilCell
  character             lizpop.scheme.LspChar
  input-port            lizpop.inport.InPort
  output-port           file , StringIO.StringIO
  ================      ========================

Built-In attributes
===================

``<ATTRIBUTE-NAME>`` variable is bound to the built-in attributes in
Python (e.g. <sorted>, <tuple>, <EOFError>).

For example::

  > (<map> <type> `#(100 #f "scheme-string" ,(<str> "byte-string")))
  #(<type 'int'> <type 'bool'> <type 'unicode'> <type 'str'>)

  > (<sorted> #("xyz" "abc" "123" "ABC") <cmp>)
  #("123" "ABC" "abc" "xyz")

You can see all the built-in attributes using ``(help-list #/^<.+>$/)``. ::

  > (help-list #/^<.+>$/)
   <ArithmeticError>
       Procedure          Base class for arithmetic errors.
   <AssertionError>
       Procedure          Assertion failed.
   ..................................................................
   ..................................................................

To import Python module in Lizpop
=================================

Please use ``import`` procedure.

Example::

  > (define *urllib2* (import "urllib2"))
  > (for-each (lambda (line) (format #t "~A\n" line))
             (invoke *urllib2* 'urlopen "http://python.org/"))
   <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML ..................
   ..............................................................

The following modules are built into the interpreter beforehand. ::

  *sys*  *os*  *re*  *math*  *operator*


To call Python functions from a Scheme interpreter
==================================================

**To call functions with positional arguments.**

  (FUNCTION-OBJ ARG ...)    

  examples::

    > (<zip> '(1 2 3) '(100 200 300))
    #((1, 100) (2, 200) (3, 300))
    > (define *glob* (import "glob"))
    > ((<getattr> *glob* "glob") "*.scm")
     #("test.scm" "boot.scm" "hello.scm")   
    > ((attr *glob* 'glob) "*.py") ;; same as ((<getattr> ...) )
     #("hoge.py" "run.py")   

**To call functions with keyword arguments**

  (call FUNCTION-OBJ PARG ... KWD VAL ... )

  example::

    ;; Same as `print calendar.calendar(2012, w=3, m=2)'
    > (define *cal* (import "calendar"))
    > (display (call (attr *cal* 'calendar) 2012 :w 3 :m 2))
                January                          February
      Mon Tue Wed Thu Fri Sat Sun      Mon Tue Wed Thu Fri Sat Sun
                                1                1   2   3   4   5
        2   3   4   5   6   7   8        6   7   8   9  10  11  12
        9  10  11  12  13  14  15       13  14  15  16  17  18  19
      .......................................................

  For more info, run ``(help call)``.


How to access Python objects from Scheme interpreter
====================================================

**To access attributes of an object:**

  :Procedure (attr OBJECT NAME ...):
     Return the value of the named attributed of object.

     (attr obj 'name1 'name2) 
     is equivalent to ```obj.name1.name2'`` in Python.

  :Procedure (attr! OBJECT NAME VALUE):
     Set attribute value.

     (attr! obj 'name value)
     is equivalent to the Python expression ```obj.name = value'``.

  :Procedure (attr? OBJECT NAME):
    If NAME is an attribute of OBJECT, then return #t, else return #f.

  Examples::

    ;; Wrapper of Python's `type' function
    > (define (make-type name base-list dict-assq)
        (<type> (<str> name) (<tuple> base-list)
              (<dict> dict-assq)))

    ;; Make a simple class
    > (define myclass
        (make-type "MyClass" (list <object>) '(("a" 1) ("b" 2))))
    > (attr myclass '__name__)
    "MyClass"
    > (attr myclass '__dict__)
    {u'a': 1, u'b': 2, '__dict__': ....}

    ;; Make an instance of MyClass
    > (define myobj (myclass))
    > (isa? myobj myclass)  ;; equal to (<isinstance> myobj myclass)
    #t

    ;; List attribute values
    > (map (lambda (name) (if (attr? myobj name)
                            (attr myobj name) #f)) '(a b c))
    (1 2 #f)
    > (attr! myobj 'c "abc") ;; Set attribute
    > (map (lambda (name) (if (attr? myobj name)
                            (attr myobj name) #f)) '(a b c))
    (1 2 "abc")
    > (attr myobj 'c 'upper) ;; get upper method
    <built-in method upper of unicode object at 0x81650e0>
    > ((attr myobj 'c 'upper)) ;; call upper method
    "ABC"
    > 

**To invoke methods of an object:**

  :Procedure (invoke OBJ MESSAGE ARGS ... ):

     Invokes the OBJ's method named MESSAGE with ARGS as positional arguments.

     Examples::

       > (invoke "abc" 'upper)
       "ABC"
       > (define *glob* (import "glob"))
       > (invoke *glob* 'glob "*.scm")
        #("test.scm" "boot.scm" "hello.scm")   

  :Procedure (invoke* OBJ MESSAGE PARG ... KWD VAL ...):

     Invokes the OBJ's method named MESSAGE with (PARG ...) as positional and 
     (KWD VAL ...) as keyword arguments. ::

       MESSAGE ---  `string` or `symbol`.
       KWD     ---  `keyword-symbol`

     Example::

       > (define *cal* (import "calendar"))
       > (display (invoke* *cal* 'calendar 2014 :w 3 :m 2))
                 January                          February
       Mon Tue Wed Thu Fri Sat Sun      Mon Tue Wed Thu Fri Sat Sun
                 1   2   3   4   5                            1   2
         6   7   8   9  10  11  12        3   4   5   6   7   8   9
        13  14  15  16  17  18  19       10  11  12  13  14  15  16
        20  21  22  23  24  25  26       17  18  19  20  21  22  23
        27  28  29  30  31               24  25  26  27  28
       ....................................................................
       ....................................................................

  For more info, run ``(help invoke)`` and ``(help invoke*)``

**To access a sequence**

  Get or set an item:
    Please run ``(help item item! delitem! in? )`` to see its help message.

  Slice:
    Please run ``(help slice slice! delslice!)``,

  Examples::

    > (begin (define hash (<dict> '(("one" 1) ("two" 2)))) hash)
    {u'two': 2, u'one': 1}
    > (item hash "one")
    1
    > (in? "three" hash)
    #f
    > (item! hash "three" 3)
    > (in? "three" hash)
    #t
    > (item hash "three")
    3
    > (map (lambda (x) x) (invoke hash 'keys))
    ("three" "two" "one")
    > (map (lambda (items)
	   (call-with-values (lambda () items) cons))
	 (invoke hash 'iteritems))
    (("three" . 3) ("two" . 2) ("one" . 1))

    > (define v '#(100 200 300))
    > (item! v 1 (- (item v 1)))
    > v
    #(100 -200 300)
    > (slice! v -1 4 #(-300 400 500))
    #(100 -200 -300 400 500)
    > (delslice! v #<none> -2)
    #(400 500)


Data Type Conversion
======================

* **iterable object**
   
  Procedure **it->list** converts Python's iterator to Scheme's list. ::

    > (it->list (<xrange> 10))
    (0 1 2 3 4 5 6 7 8 9)

    > (it->list (invoke (<dict> '((a 1) (b 2) (c 3))) 'iterkeys))
    (b a c)

    > (it->list "abcd")
    ("a" "b" "c" "d")

  **map** and **for-each** work on any type of iterable. ::

    > (map (lambda (s) s) "abcd")
    ("a" "b" "c" "d")

    > (for-each
        (lambda (n c) (format #t "~3,'0D:~A\n" n c))
           (<xrange> 1 4 ) "ABC")
    001:A
    002:B
    003:C

* **tuple**

  Scheme's list/vector => tuple ::

    > (<tuple> '(1 2 3))
    (1, 2, 3)

    > (<tuple> #(1 2 3))
    (1, 2, 3)

  tuple => Scheme's list ::

    > (begin (define tuple (<tuple> (<xrange> 1 5))) tuple) 
    (1, 2, 3, 4)

    > (it->list tuple)
    (1 2 3 4)
    > (apply list tuple)
    (1 2 3 4)
    > (map (lambda (x) x) tuple)
    (1 2 3 4)

* **dict**

  Scheme's list/vector => dict ::

    > (<dict> '(("a" 100) ("b" 200) ("c" 300)))
    {u'a': 100, u'c': 300, u'b': 200}

    > (<dict> #(#("a" 100) #("b" 200) #("c" 300)))
    {u'a': 100, u'c': 300, u'b': 200}

    > (<dict> (<zip> '("a" "b" "c") '(100 200 300)))
    {u'a': 100, u'c': 300, u'b': 200}

  dict => Scheme's assoc list ::

    > (begin (define dict (<dict> '(("a" 100) ("b" 200) ("c" 300)))) dict)    
    {u'a': 100, u'c': 300, u'b': 200}

    > (map it->list (invoke dict 'items)) 
    (("a" 100) ("c" 300) ("b" 200))
    > (equal? (<dict> (map it->list (invoke dict 'items))) dict)
    #t

* **set**

  Scheme's list/vector => set ::

    > (<set> '(1 2 3 2 3))
    set([1, 2, 3])
    > (<set> #(1 2 3 2 3))
    set([1, 2, 3])

    > (invoke (<set> '(0 1 2 3)) 'union '(2 3 4 5))
    set([0, 1, 2, 3, 4, 5])


  set => Scheme's list ::

    > (it->list (<set> '(1 2 3 2 3)))
    (1 2 3)

* **unicode-string and bytes-string**
  
  Lizpop's string is Python's unicode-string.

  Procedure **string->bytes** converts Scheme's string to bytes-string.

  Procedure **bytes->string** converts bytes-string  to Scheme's string.

  For more info, please run ``(help string->bytes)`` and ``(help bytes->string)``.

Exception Handling
==================

**Macro: (try-catch BODY HANDLER ...)**

  Each HANDLER has the form: ``(var exception-type exp ...)``

  e.g. ::

    (try-catch body
          (exobj <ValueError> exp exp2 ...)
          (exobj <TypeError>> exp exp2 ...))

  This is equivalent to the following Python statement. ::

    try: body
    except ValueError as exobj: 
      exp; exp2; ...
    except TypeError as exobj:
      exp; exp2; ...

**Macro: (try-finally BODY HANDLER)**

  This macro is equivalent to the following Python statement. ::

    try: BODY
    finally: HANDLER

**Procedure: (raise EXC . ARG=None)**

  Raise exception

**Example**::

  > (define (test-exception error?)
	(try-finally
	 (try-catch
	  (if error? (raise <NameError> "Hi there") #t)
	  (exc <NameError> (format #t "Catch error: ~A\n" exc) #f))
	 (format #t "Executing finally clause\n")
	 ))

  > (test-exception #f)
  Executing finally clause
  #t
  > (test-exception #t)
  Catch error: Hi there
  Executing finally clause
  #f

Convert Scheme closure to Python's callable.
============================================

:Procedure: (@callable PROC)

Examples::

  ;; ** A simple example **
  > (<filter>
     (@callable (lambda (obj) (and (number? obj) (> obj 0))))
     '(1 100 -10 "200" 0  #t 2000))
  #(1 100 2000)  

  ;; ** Similar to Python class definition **
  > (define (make-type name base-list dict-assq)
      "Make new type"
      (<type> (<str> name) (<tuple> base-list)
              (<dict> dict-assq)))

  > (define *html-parser* (attr (import "HTMLParser") "HTMLParser"))

  > (define make-myparser
      (letrec ((->list (lambda (tuple-of-vec) 
                         ;; convert #((a,b)...) to '((a . b) ...)
                         (map (lambda (tuple)
                                (cons (item tuple 0) (item tuple 1)))
                                tuple-of-vec))))
        (make-type "MyParser" (list *html-parser* <object>) 
                   `(("handle_starttag"
                      ,(@callable
                        (lambda (self tag attrs)
                          (format #t "Beginning of a ~A tag\n\tattrs:~S\n"
                                  (string-upcase tag) (->list attrs)))))
                     ("handle_endtag"
                      ,(@callable
                        (lambda (self tag)
                          (format #t "End of a ~A tag\n" (string-upcase tag)))))
                     ))))

  > (define p (make-myparser))

  > (define html "<div id='navi'>
       <a href='doc.html' target='_blank'>Document</a>
       <a href='home.html'>Home</a>Document</a></div>")

  > (invoke p 'feed html)
  Beginning of a DIV tag
          attrs:(("id" . "navi"))
  Beginning of a A tag
          attrs:(("href" . "doc.html") ("target" . "_blank"))
  End of a A tag
  ...........................................................
  ...........................................................
  > 

For more info, run ``(help @callable)``.

How to run Scheme code from Python.
====================================

You can use the s-expression code from Python in the following way:

1. Import Lizpop module. ::

    >>> import lizpop.scheme

2. Boot Scheme. ::

    >>> lizpop.scheme.Boot.boot()

    (This function has to be called at the first time only.)

3. Make Scheme-Interpreter object. ::

    >>> anInterpreter = lizpop.scheme.Interpreter()

4. Call ``repl()`` or ``srepl()``. ::

    # Evaluate s-expressions from a File. 
    >>> anInterpreter.repl(readport=FILE) 

    # Evaluate s-expressions from a text string.
    >>> anInterpreter.srepl(STRING) 

Examples::

  # A sample source file
  $ cat fact.scm
  (define (fact n)
    (let loop ((x n) (acc 1))
      (if (< x 1) acc (loop (- x 1) (* x acc)))))
  $
  $ python
  >>> import lizpop.scheme

  # Boot 
  >>> lizpop.scheme.Boot.boot() # call this the first time only

  # Make a scheme interpreter.
  >>> lisp = lizpop.scheme.Interpreter()

  # Evaluate s-expressions using lisp.srepl(STRING)
  >>> lisp.srepl('''(vector (gcd 1232 42 21) (lcm 1232 42 21))''')
  [7, 3696]
  >>> lisp.srepl('''(define (hello msg) (format "Hello ~A" msg))''')
  >>> lisp.srepl('''(hello "friend")''')
  u'Hello friend'

  # Load fact.scm using `lisp.repl(readport=FILE)'
  >>> from __future__ import with_statement # (only python 2.5)
  >>> with open("fact.scm") as f: lisp.repl(readport=f)
  ... 
  # Run (fact 100) using `list.srepl(STRING)'
  >>> ret = lisp.srepl('(fact 100)')
  >>> print ret
  933262154439441526816992388562667004907159682643816214...........
  >>> 

