# -*- coding: utf-8 -*-
import scheme
from scheme import Boot

class ExDoc:
  table = {}
  toplevel_bind_const = object()
  def __init__(self, name, doc, bind=None):
    self.name = name
    self.doc = doc
    self.bind = bind
    if self.bind is None:
      self.bind = Boot.scheme_environment.lookup(name)
    ExDoc.table[name] = self
 
  def is_toplevel_bind(self):
    return self.bind == ExDoc.toplevel_bind_const

def adddoc_lambda(name, doc):
  Boot.scheme_environment.lookup(name)._scheme_doc = doc

def make():
  for name in ("and", "begin", "if", "define", "lambda", "quote",
               "unquote", "unquote-splicing", "or", "set!",
               "newline"):
    adddoc_lambda(name, "\n  [R5RS]")

  adddoc_lambda("none?", '''(none? OBJ)
  Same as `OBJ is None` in Python.
  e.g. (none? (if #f #t)) ;=> #t''')

  adddoc_lambda("quit","(quit)\n  Terminates Read-Eval-Print-Loop.")

  adddoc_lambda("attr?",'''(attr? OBJECT NAME)
  If NAME is an attribute of OBJECT, then returns #t,  else returns #f.
  NAME -- can be `string` or `symbol` or `keyword-symbol`.
  examples:  
   > (define *datetime* (import "datetime"))
   > (define d ((attr *datetime* 'date) 2000 11 14))
   > d ;=> 2000-11-14
   > (attr? d 'year) ;=> #t
   > (attr? d 'hour) ;=> #f
   > (attr? ((attr *datetime* 'datetime) 2000 11 14) "hour") ;=> #t
  See also: (help attr attr!)''')

  adddoc_lambda("regex?", '''(regex? OBJECT)
  Returns #t if OBJECT is a regular expression object.''')

  adddoc_lambda("re-escape", r'''(re-escape STRING)
  Same as re.escape(STRING) in Python.
  e.g.
    > (string->regex (re-escape "[*info*] +100"))
    #/\[\*info\*\]\ \+100/''')
  
  adddoc_lambda("string->keyword", r'''(string->keyword STRING)
  Returns a keyword with the name STRING.''')

  adddoc_lambda("keyword->string", r'''(keyword->string KEYWORD-SYMBOL)
  Transforms KEYWORD-SYMBOL into a string.''')

  adddoc_lambda("keyword?", r'''(keyword? OBJ)
  Returns #t if OBJ is a keyword symbol.''')

  adddoc_lambda("define-macro", r'''
  (define-macro NAME LAMBDA-FORM)
  (define-macro (NAME . ARGS) FORM ...)
  Define NAME as a macro.
  e.g.
   > (define-macro (+= var num)
       `(begin (set! ,var (+ ,var ,num)) ,var))
   > (define a 100)
   > (+= a 5)
   105
   > (+= a 10)
   115
   > a
   115
   > 
   ;; Will act like while loop
   > (define-macro (while condition . bodies)
       (let ((loop (gensym)) (ret (gensym)))
         `(call/cc
           (lambda (break)
             (let ,loop ((,ret #f))
                  (if ,condition
                      (,loop (call/cc (lambda (next) ,@bodies)))
                      ,ret))))))
   > (define (scanlist lst)
       (let ((result '()))
         (reverse!
          (while (pair? lst)
                 (case (car lst)
                   ((END) (break result))
                   ((SKIP IGNORE)
                    (set! lst (cdr lst))
                    (next result))
                   (else (set! result (cons (car lst) result))
                         (set! lst (cdr lst))
                         result))))))
   > (scanlist '(1 2 SKIP 3 4 IGNORE SKIP 5 6 END 7 8))
   (1 2 3 4 5 6)''')

  adddoc_lambda("open-output-file",  r'''(open-output-file FILENAME . MODE)
  [R5RS] Open a file for output.
  FILENAME -- the file name
  MODE -- `string: indicating how the file is to be opened.
           "w" or "a"  default is "w"
           (not R5RS)''')

  adddoc_lambda("open-input-file",  r'''(open-input-file FILENAME)
  [R5RS] Open a file for input.''')

  adddoc_lambda("current-input-port", r'''(current-input-port)
  [R5RS] Returns the current input port''')
  adddoc_lambda("current-output-port", r'''(current-input-port)
  [R5RS] Returns the current output port''')
  adddoc_lambda("current-error-port", r'''(current-input-port)
  [R5RS] Returns the current error port''')

  adddoc_lambda("exit", r'''(exit . ARG=0)
  Same as `sys.exit(ARG)' in Python.''')

  adddoc_lambda("make-list", r'''(make-list LEN . INIT)
  Creates a proper list of LEN elements, If INIT is 
  provided, all elements in the list are initialized 
  to INIT.
  Examples:
   > (make-list 3)
   (#<none> #<none> #<none>)
   > (make-list 10 'A)
   (A A A A A A A A A A)''')

  adddoc_lambda("reverse!",r'''(reverse! LIST)
  Reverses the order of elements in LIST by modifying 
  cdr pointers.
  Returns the reversed list.
  Examples:
   > (define lst '(a b c d))
   > (reverse! lst)
   (d c b a)
   > lst
   (a)
  See Also: (help reverse)''')

  adddoc_lambda("string-downcase", r'''(string-downcase STRING)
  Converts STRING to lower case and returns that.
  See Also: (help string-upcase)''')
  adddoc_lambda("string-upcase", r'''(string-downcase STRING)
  Converts STRING to upper case and returns that.
  See Also: (help string-downcase)''')

  adddoc_lambda("string-copy", r'''[R5RS] (string-copy STRING) 
  Restriction:
    Lizpop string objects are implemented as Python unicode objects
    which are immutable.
    So, `string-set!' and `string-fill!' are not implemented, and 
    `string-copy' may return itself without returning a copy. ''')

  for fname in ("string-set!", "string-fill!"):
    adddoc_lambda(fname, r'''
  Not Supported:
    Lizpop string objects are implemented as Python unicode objects
    which are immutable.
    So, `string-set!' and `string-fill!' are not implemented, and 
    `string-copy' may return itself without returning a copy. ''')

  for fname in ("scheme-report-environment", "null-environment"):
    adddoc_lambda(fname, r'''
  Not Supported:
    `scheme-report-environment' and `null-environment' procedures
     are not implemented. Instead, The following procedures can be 
     used as the 2nd argument of `eval'. 
        * (interaction-environment) -- R5RS
        * (built-in-environment) -- Lizpop built-in environment
        * (current-environment) -- current environment
  See Also: (help eval) (help built-in-environment)''')

  adddoc_lambda("char-ready?", r'''(char-ready? . PORT TIMEOUT)
  [R5RS] Returns #t if a character is ready on the PORT and 
  returns #f otherwise.
  PORT    -- a input port, the default is (current-input-port)
  TIMEOUT -- time-out in seconds(tha default is 0).
             this argument is Lizpop's extension.
  Note:
    This procedure is implemented by using Python's select-module, 
    so, it may not work on on Windows.

  Example:
    ;; wait for 5 seconds until return key is pressed.
    > (begin (read-char) 
           (if (char-ready? (current-input-port) 5)
               (read-char) #f ))
    #\newline ''')

  ExDoc("*version*", "Version number of Lizpop.")

  ExDoc("*args*",  
        r'''
  The list of command line arguments passed to a Scheme script.
  e.g. 
    $ python -O -m lizpop.run -- abc xyz
    > *args*
    ("abc" "xyz")''', ExDoc.toplevel_bind_const) # *args* is toplevel bind

  ExDoc("*load-path*", 
        r'''
  List of directories to search for scheme source files to load.

  Note: LIZPOP_LOAD_PATH
    You can set *load-path* by the LIZPOP_LOAD_PATH environment variable.
    Each path is separated by `os.pathsep', such as ":" for unix.
  Example:
    $ env LIZPOP_LOAD_PATH=".:~/mylisp" python -O -m lizpop.run
    > *load-path*
    ("." "~/mylisp")
  See Also: (help load)''', ExDoc.toplevel_bind_const) #load-path is toplevel bind

  ExDoc("*program-name*", r'''
  The script file name passed to the interpreter.
  If no script, this variable is bound to "lizpop".'''
        , ExDoc.toplevel_bind_const) # *program-name* is toplevel bind

  ExDoc("item", '''(item A B)
  Return the value of A at index B.  Same as A[B] in Python.
  e.g.  (item #(\"A\" \"B\" \"C\") 1) ;=> \"B\"
        (item \"ABCD\" -1) ;=> \"D\"
        (item \"ABCD\" (<slice> 1 #<none>)) ;=> \"BCD\"''')

  ExDoc("item!", '''(item! A B C)
  Set the value of A at index B to C.  Same as A[B] = C in Python.
  e.g. (let ((v #(100 200 300))) (item! v 1 -200) v) 
       => #(100 -200 300)''')

  ExDoc("delitem!", '''(delitem! A B)
  Remove the value of A at index B.  Same as del A[B].
  e.g. (let ((v #(1 2 3 4))) (delitem! v 0) v) ;=> #(2 3 4)
       (let ((v #(1 2 3 4))) (delitem! v (<slice> 2 #<none>)) v ) 
       => #(1 2)''')

  ExDoc("isa?", '''(isa? OBJ TYPE)
  Same as `isinstance(OBJ, TYPE)` in Python.
  e.g.  (isa? \"abc\" <unicode>) ;=> #t
        (isa? (current-output-port) <file>) ;=> #t''')

  ExDoc("it->list",'''(it->list ITERABLE)
  Convert ITERABLE to a list.
  e.g. 
  rang -> list
    (it->list (<xrange> 1 5)) ;=> (1 2 3 4)
  tuple -> list
    (define tp (<tuple> #(1 2 3 4)))
    tp ;=> (1, 2, 3, 4)
    (it->list tp) ;=> (1 2 3 4)''')

  ExDoc("import", '''(import NAME . GLOBALS LOCALS FROMLIST LEVEL)
  Import module.
  Same as (<__import__> NAME . GLOBALS LOCALS FROMLIST LEVEL).
  examples:
   > (begin (define *datetime* (import "datetime")) *datetime*)
     => <module 'datetime' from ...>
   > (invoke (attr *datetime* 'date) 'today) 
     => e.g. 2011-09-10
   > (begin (define *curses* (import "curses.ascii")) *curses*)
     => <module 'curses' from ....>
   > (define *curses-ascii* (attr *curses* 'ascii))
   > *curses-ascii*
     => <module 'curses.ascii' from ...>
   > (attr *curses-ascii* 'ESC) 
     => 27
  See also:  (help <__import__>)''')

  ExDoc("abs", "(abs X)\n  [R5RS] Returns the absolute value.")

  ExDoc("max", "(max X ...)\n  [R5RS] Same as `max(X ...)' in Python.")
  ExDoc("min", "(min X ...)\n  [R5RS] Same as `min(X ...)' in Python.")

  ExDoc("length", r'''(length SEQ)
  [R5RS] Same as `len(SEQ)' in Python.
  Examples:
   > (length '(1 2 3 . a)) ;; R5RS
   3
   > (length #(1 2 3))  ;; not R5RS
   3
   > (length "abcde")   ;; not R5RS
   5
   > (length (<xrange> 10)) ;; not R5RS
   10''')

  ExDoc("vector->list", r'''(vector->list VECTOR)
  [R5RS] Converts VECTOR to a list.
  See Also: (help list->vector)''')
  ExDoc("list->vector", r'''(list->vector LIST)
  [R5RS] Converts LIST to a vector.
  See Also: (help vector->list)''')


