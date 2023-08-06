;; -*- coding: utf-8; indent-tabs-mode: nil; -*-
;;
;; Lizpop's boot-up source
;; Copyright (c) 2012 Tetsu Takaishi.  All rights reserved.

;; (display "load boot.scm\n") ;; debug

;; (define-macro and
;;   (lambda args 
;;    (if (null? args) #t
;;        (if (null? (cdr args)) (car args)
;;         (list 'if (car args)
;;               (cons 'and (cdr args)) #f)))))


;; R5RS `cond` sample
;; (define-syntax cond
;;   (syntax-rules (else =>)
;;     ((cond (else result1 result2 ...))
;;      (begin result1 result2 ...))
;;     ((cond (test => result))
;;      (let ((temp test))
;;        (if temp (result temp))))
;;     ((cond (test => result) clause1 clause2 ...)
;;      (let ((temp test))
;;        (if temp
;;            (result temp)
;;            (cond clause1 clause2 ...))))
;;     ((cond (test)) test)
;;     ((cond (test) clause1 clause2 ...)
;;      (let ((temp test))
;;        (if temp
;;            temp
;;            (cond clause1 clause2 ...))))
;;     ((cond (test result1 result2 ...))
;;      (if test (begin result1 result2 ...)))
;;     ((cond (test result1 result2 ...)
;;            clause1 clause2 ...)
;;      (if test
;;          (begin result1 result2 ...)
;;          (cond clause1 clause2 ...)))))
(define-macro (cond exp . forms)
  (define (cond-error)
    (error "cond" "Syntax error" (cons exp forms)))
  (if (or (null? exp) (not (list? exp))) (cond-error)
      (if (eqv? (car exp) 'else)
          ;; (cond (else result1 result2 ...))
          (if (null? forms) 
              (cons 'begin (cdr exp))
              (cond-error))

          (if (null? (cdr exp))
              (if (null? forms)
                  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                  ;; (car exp) ;; (cond (test)) ->  test
                  ;;((lambda (temp) ;; (cond (test) clause1 clause2 ...)
                  ;;   (list 'let (list (list temp (car exp)))
                  ;;       (list 'if temp temp
                  ;;             (cons 'cond forms)))) (gensym)))
                  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                  ;; (car exp) ;; (cond (test)) ->  test
                  (list 'or (car exp) #<undef>)  ;; (cond (test)) -> (or test (begin))
                  ;; (cond (test) clause1 clause2 ...)
                  (list 'or (car exp) (cons 'cond forms))
                  )
          
              (if (and (eqv? (cadr exp) '=>) (= (length exp) 3))
                  ;; (cond (test => foo) clause ....)
                  (if (null? forms) ;; (cond (test => foo))
                      ((lambda (temp)
                         ;; `(let ((,temp ,(car exp)))
                         ;;    (if ,temp (,(list-ref exp 2) ,temp)))
                         (list 'let (list (list temp (car exp)))
                               (list 'if temp (list (list-ref exp 2) temp)))
                         ) (gensym))
                      ((lambda (temp)
                         ;; `(let ((,temp ,(car exp)))
                         ;; (if ,temp (,(list-ref exp 2) ,temp)
                         ;;    (cond ,@forms)))
                         (list 'let (list (list temp (car exp)))
                               (list 'if temp (list (list-ref exp 2) temp)
                                     (cons 'cond forms)))
                         ) (gensym))
                      )
                  ;;
                  (if (null? forms)
                      ;; (cond (test result1 result2 ...))
                      (list 'if (car exp) (cons 'begin (cdr exp)))
                      ;; (cond (test result1 result2 ...) clause1 clause2 ...)
                      (list 'if (car exp) (cons 'begin (cdr exp))
                            (cons 'cond forms)))
              )))))

;; MyGuide:  `(a ,(+ 1 2) (2 3)) => (cons 'a (cons (+ 1 2) (cons (quote (2 3)) ())))
;; Note:
;;   Do not use eq? , use eqv? instead, for ScmReportEnv implementation.
(define-macro (quasiquote form)
  "\n  [R5RS]"
  (define (QQ nest form)
    (cond ((pair? form)
           (cond ((eqv? (car form) 'unquote)
                  ;; `,(foo a b) -> (unquote (foo a b))
                  (if (= nest 0) (car (cdr form))
                      (list 'cons (list 'quote 'unquote)
                            (QQ (- nest 1) (cdr form)))))
                 ((eqv? (car form) 'quasiquote) 
                  ;; ``(e ...) -> (quasiquote (e ...))
                  (list 'cons (list 'quote (car form))
                        (QQ (+ nest 1) (cdr form))))
                 ((and (pair? (car form))
                       (eqv? (car (car form)) 'unquote-splicing))
                  ;; `(,@(a b ..) ...) -> ((unquote-splicing (a b ...)) ...)
                  (if (= nest 0)
                      (if (null? (cdr form))
                          (list 'append (car (cdr (car form))))
                          (list 'append (car (cdr (car form))) (QQ nest (cdr form))))
                      (list 'cons
                            (list 'list(list 'quote 'unquote-splicing)
                                  (QQ (- nest 1) (car (cdr (car form)))))
                            (QQ nest (cdr form)))))
                 (else
                  (list 'cons (QQ nest (car form))
                        (QQ nest (cdr form)))))
           )
          ((vector? form)
           (list 'list->vector (QQ nest (vector->list form))))
          (else ;; (quote ()) -> ()
           (list 'quote form))))

  (QQ 0 form))

;; (define-syntax let  ;; R5RS sample
;;   (syntax-rules ()
;;     ((let ((name val) ...) body1 body2 ...)
;;      ((lambda (name ...) body1 body2 ...)
;;       val ...))
;;     ((let tag ((name val) ...) body1 body2 ...)
;;      ((letrec ((tag (lambda (name ...)
;;                       body1 body2 ...)))
;;         tag)
;;       val ...))))
(define-macro (let exp . bodies)
  (if (list? exp)
      `((lambda
            ,(map car exp)
          ,@bodies) ,@(map cadr exp))
      (if (and (symbol? exp) (pair? bodies) (list? (car bodies)))
          `((letrec ((,exp (lambda ,(map car (car bodies))
                            ,@(cdr bodies))))
              ,exp) ,@(map cadr (car bodies)))
          (error "let" "illegal syntax" (cons exp bodies))
          )))

;; (define-syntax let* ;; R5RS sample
;;   (syntax-rules ()
;;     ((let* () body1 body2 ...)
;;      (let () body1 body2 ...))
;;     ((let* ((name1 val1) (name2 val2) ...)
;;        body1 body2 ...)
;;      (let ((name1 val1))
;;        (let* ((name2 val2) ...)
;;          body1 body2 ...)))))
(define-macro (let* exp . bodies)
  (if (null? exp) `(let () ,@bodies)
      (if (and (pair? exp) (list? (car exp))
               (pair? (cdr (car exp))) (null? (cddr (car exp))))
          `(let (,(car exp))
             (let* ,(cdr exp) ,@bodies))
          (error "let*" "illegal syntax" exp))))

(define-macro (letrec plst . bodies)
  `(let 
       ,(map (lambda (p) (list (car p) #<undef>)) plst)
     ,@(map (lambda (p) `(set! ,(car p) ,(cadr p))) plst)
     (let ()  ;; for top define (no need with current `define` implementation)
       ,@bodies)))

;; letrec: gensym version
;; (define-macro (letrec plst . bodies)
;;   (let ((tmplst (map (lambda (p) (gensym)) plst)))
;;   `(let 
;;     ,(map (lambda (p) (list (car p) #f)) plst)
;;     (let
;;      ,(map (lambda (tp p) 
;;           (list tp (cadr p))) tmplst plst)
;;      ,@(map (lambda (tp p) (list 'set! (car p) tp)) tmplst plst)
;;      (let () ;; 
;;        ,@bodies)))))

;; R5RS sample
;; (define-syntax case
;;   (syntax-rules (else)
;;     ((case (key ...)
;;        clauses ...)
;;      (let ((atom-key (key ...)))
;;        (case atom-key clauses ...)))
;;     ((case key
;;        (else result1 result2 ...))
;;      (begin result1 result2 ...))
;;     ((case key
;;        ((atoms ...) result1 result2 ...))
;;      (if (memv key '(atoms ...))
;;          (begin result1 result2 ...)))
;;     ((case key
;;        ((atoms ...) result1 result2 ...)
;;        clause clauses ...)
;;      (if (memv key '(atoms ...))
;;          (begin result1 result2 ...)
;;          (case key clause clauses ...)))))
(define-macro (case key . bodies)
  (cond ((pair? key)
         (let ((tmp (gensym)))
           `(let ((,tmp ,key))
              (case ,tmp ,@bodies))))
        ((null? (cdr bodies))
         (cond ((eqv? (caar bodies) 'else)
                `(begin ,@(cdar bodies)))
               ((list? (caar bodies))
                `(if (memv ,key (quote ,(caar bodies)))
                     (begin ,@(cdar bodies))))
               (else (error "case" "illegal syntax" (car bodies)))))
        ((list? (caar bodies))
         `(if (memv ,key (quote ,(caar bodies)))
              (begin ,@(cdar bodies))
              (case ,key ,@(cdr bodies))))
        (else (error "case" "Illegal syntax" (car bodies)))))

(define-macro (try-finally body handler)
  "(try-finally BODY HANDLER)
   This macro is equivalent to the following Python statement.
      try: BODY
      finally: HANDLER
   Examples:
     > (try-finally
        (begin (display \"Hello world. \" ) 'RETURN)
        (display \"Goodbye world.\\n\"))
     Hello world. Goodbye world.
     RETURN
     > (try-finally
         (begin (display \"Hello world. \" ) 
              (raise <KeyboardInterrupt>) 'RETURN)
         (display \"Goodbye world.\\n\"))
     Hello world. Goodbye world.
     KeyboardInterrupt: 
   See also: (help try-catch raise error)"
  `(*<try-finally>* (lambda () ,body) (lambda () ,handler)))

(define-macro (try-catch body . handlers)
  "(try-catch BODY HANDLER ...)
  Handling exceptions.
  Each HANDLER has the form: (var exception-type exp ...)
  e.g. 
  (try-catch body
        (exobj <ValueError> exp exp2 ...)
        (exobj <TypeError>> exp exp2 ...))
  This is equivalent to the following Python statement.
      try: body
      except ValueError as exobj: 
        exp; exp2; ...
      except TypeError as exobj:
        exp; exp2; ...

  Examples:
    > (try-catch
       (begin (display \"He\") (<open> \"notexist.file\") (display \"llo\"))
       (ex <IOError> (display \"Error\\n\") #f))
      HeError
      #f
    > (define (divide x y)
        (try-catch (/ x y)
                   (e <LispError>
                      (format #t \"Lisp error: ~A\\n\" e) #f)
                   (e <ArithmeticError>
                      (format #t \"ArithmeticError type:~A ~A\\n\"
                              (attr (<type> e) '__name__) e) 
                      #f)
                   (ex <Exception> 
                      (display \"Unknown error\\n\")
                      (raise ex) ;; re-raise the exception
                      )))
    > (divide 1.5 2.0) ;=>   0.75
    > (divide 1.5 \"2.0\")
    Lisp error: ERROR in /: Wrong type of arguments.........
    #f
    > (divide 1.5 0.0)  ;; not support `+inf.0`
    ArithmeticError type:ZeroDivisionError float division
    #f
  See also: (help try-finally error raise)"
  (define (catch-body var newvar type explist )
    `((isa? ,var ,type)
      (let ((,newvar ,var)) ,@explist))
    )
  (let ((tmp (gensym)))
    `(*<try-catch>*
      (lambda () ,body)
      (lambda (,tmp)
        (cond ,@(map
                 (lambda (hd)
                   (catch-body tmp (car hd) (cadr hd) (cddr hd))) handlers)
              (else (raise ,tmp)))))
    ))

(define (dynamic-wind before body after)
  "[R5RS] (dynamic-wind BEFORE THUNK AFTER) 

  Restriction:
    Lizpop does not support full continuation.
    Lizpop's dynamic-wind can be used for non-local-exit only.   

  See Also: (help call-with-current-continuation)
            (help try-catch)"
  (before)
  (try-finally (body) (after)))

(define (call-with-values producer consumer)
  (let ((mvalue (producer)))
    (if (isa? mvalue <tuple>)
        (apply consumer 
               (invoke (attr *scheme* 'ScmList) 'from_iter mvalue))
        (consumer mvalue))))

(define-macro (delay exp)
  (define make-promise ;; R5RS sample 
    (lambda (proc)
      (let ((result-ready? #f)
            (result #f))
        (lambda ()
          (if result-ready?
              result
              (let ((x (proc)))
                (if result-ready?
                    result
                    (begin (set! result-ready? #t)
                           (set! result x)
                           result))))))))
  `(,make-promise (lambda () ,exp)))

(define (force promise) (promise))

;;(do ((<var> <init> <step>) ...)
;;    (<test> <result> ...)
;;    (body ...))
(define-macro (do bindlist test . body)
 (let ((varlist (map car bindlist))
       (initlist (map cadr bindlist))
       (steplist (map (lambda (bind)
                       (if (pair? (cddr bind))
                           (list-ref bind 2) (car bind))) bindlist))
       (_loop (gensym)))
   `(letrec ((,_loop (lambda ,varlist
                       (if ,(car test)
                           (begin ,@(cdr test))
                           (begin ,@body
                                  ;; (,_loop ,@(steplist))
                                  (,_loop . ,steplist))))))
      (,_loop . ,initlist))))

;;;;;;;;;;;;;;;;;;  not R5RS ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(define-macro (when test . body)
  "(when TEST BODY ...)
  If TEST yields true value, eval BODY... sequentially and 
  return value of last one. Otherwise, return None.
  See Also: (help unless)"
  `(if ,test (begin . ,body)))

(define-macro (unless test . body)
  "(unless TEST BODY ...)
  If TEST yields #f, eval BODY... sequentially and 
  return value of last one. Otherwise, return None.
  See Also: (help when)"
  `(if ,test (begin (if #f #f)) (begin . ,body)))

(define (delete-if! pred lst . all? )
  "(delete-if PREDICATE LIST . ALL?)
  If ALL? is true value or omitted, 
   Deletes all elements from LIST that (PREDICATE element) 
   returns true value
  else
   Deletes the first element from LIST that (PREDICATE element) 
   returns true value
  This is a destructive function.
  Examples:
   > (define lst '(1 2 3 4 5 6))
   > (delete-if! odd? lst)
   (2 4 6)
   > lst
   (1 2 4 6)
  See Also: (help delete!)"
  (invoke lst 'delete_if (@callable pred)
          (if (pair? all?) (not (car all?)) #f)))

(define (open-output-string)
  "(open-output-string)
  Open string port for output.
  This function is implemented using Python's StringIO module.
  Example: 
   > (define p (open-output-string))
   > (with-output-to-port p (lambda () (display '(1 2 3))))  
   > (string-append (get-output-string p)) ;=> \"(1 2 3)\"
   > (close-output-port p)
  See Also: (help get-output-string with-output-to-string)"
  ((attr (import "StringIO") "StringIO")))

(define (get-output-string p)
  "(get-output-string SPORT)
   Get string value from SPORT.
   SPORT -- string port
   The return value is a byte-string not a unicode.
   See Also: (help get-output-string with-output-to-string)"
  (invoke p 'getvalue))

(define (with-output-to-string thunk)
  "(with-output-to-string THUNK)
  Call THUNK with no arguments, While evaluating THUNK, 
  `current-output-port' is set to string-port.
  Return a byte-string value.
  Example:
   > (string-append  ;; convert to unicode
       (with-output-to-string 
          (lambda () (display '(1 2 \"abc\")) (newline))))
   > \"(1 2 abc)\\n\"
  See Also: (help open-output-string get-output-string)"
  (let ((p (open-output-string)))
    (try-finally
     (begin (with-output-to-port p thunk)
            (get-output-string p))
     (close-output-port p))))

;;;;; help tool ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(define (help:type obj)
  (cond ((lambda? obj) "Closure")
        ((isa? obj (attr *scheme* 'PyMacro)) "Macro")
        ((isa? obj (attr *scheme* 'Macro)) "Macro")
        ((procedure? obj) "Procedure")
        ((isa? obj (attr *scheme* 'Syntax)) "Syntax Object")
        ((isa? obj <unicode>) "String Object")
        ((isa? obj <list>) "Vector Object")
        ((char? obj) "Character Object")
        ((symbol? obj) "Symbol Object")
        ((keyword? obj) "Keyword Symbol")
        ((pair? obj) "List Object")
        ((null? obj) "Empty List")
        ((number? obj) "Number Object")
        ((boolean? obj) "Boolean Object")
        (else (format "~A" (<type> obj)))))

(define (help:object obj . opts)
  (letrec ((_bool (lambda (o) (and (<bool> o) o)))
           (_attr (lambda (o att)
                    (and (attr? o att) (_bool (attr o att)))))
           (name (and (pair? opts) (car opts)))
           )
    (add-keyword!
     :name name
     (cond 
      ((attr? obj '_scheme_doc)
       `(:obj-type ,(help:type obj) :doc-type lizpop
                   :doc-string ,(_attr obj '_scheme_doc)))
      ((isa? obj (attr *scheme* 'Closure))
       `(:obj-type ,(help:type obj) :doc-type lizpop :doc-string #f))
      ((and (<callable> obj) (_attr obj '__module__)
            (re-match #/lizpop\./ (_attr obj '__module__)))
       `(:obj-type ,(help:type obj) :doc-type lizpop
                   :doc-string ,(_attr obj '__doc__)))
      ((none? obj) '())
      (else `(:obj-type ,(help:type obj) :doc-type python 
                        :doc-string ,(or (_attr obj '__doc__) "")
                        :object obj))
      ))
    ))

(define (help:symbol sym)
  (if (not (symbol? sym)) (error "Wrong type of arguments (expecting symbol)"))
  (letrec ((extable (attr *lizpop-defdoc* 'ExDoc 'table))
           (exdoc (lambda (name)
                    (and (in? name extable)
                         (let ((exd (item extable name))
                               (bind (eval (string->symbol name))))
                           (and (or (eq? (attr exd 'bind) bind)
                                    (invoke exd 'is_toplevel_bind))
                                (attr exd 'doc)))))) )
    (let ((docstr (exdoc (symbol->string sym))))
      (if docstr `(:name (symbol->string sym)
                         :obj-type ,(help:type (eval sym))
                         :doc-type lizpop :doc-string ,docstr)
          (help:object (eval sym) (symbol->string sym))))))

(define (help:summary hinfo)
  (letrec ((docstr (get-keyword :doc-string hinfo))
           (trunc (lambda (s len)
                    (if (> (string-length s) len)
                        (string-append
                         (substring s 0 (max (- len 4) 0)) " ...")
                        s))))
    (if docstr
        (let ((str (re-gsub #/\s+/ " "
                            (re-gsub #/^\s+/ "" docstr))))
          (if (string=? str "") "" (trunc str 50)))
        "Not documented.")))

(define (help:print obj hinfo)
  (let ((otype (get-keyword :doc-type hinfo #f)))
    (cond ((eqv? otype 'lizpop)
           (format #t "~A: ~A\n\n" 
                   (or (get-keyword :obj-type hinfo) "Unknown-Type")
                   (or (get-keyword :doc-string hinfo) "Not documented.")))
          ((none? obj) (display "None\n"))
          (else
           (format #t "=> (<help> ~A)\n" (or (get-keyword :name hinfo) ""))
           (<help> obj))
          )))

;; e.g.  (help item item! slice slice! help-list)
(define-macro (help . names)
  "(help VARIABLE ...)
  Show help on VARIABLE
  Examples:
    > (help invoke)
      Procedure: (invoke OBJ MESSAGE ARGS ... )
      ............................................
    > (help map)
      Procedure: (map PROC ITERABLE1 ITERABLE2 ...)
        Note:
          `map' and `for-each' work on any type of iterable.
          (This is an extension of Lizpop. )
        ............................................

  If VARIABLE is a regular expression object, then list the symbols
  bound to the top-level environment with a given pattern.
  (same as the `help-list` function)
  e.g.
   > (help #/^call/)
     call
         Procedure          (call FUNCTION PARG ... KWD VAL ...) Calls FUN ...
     call-with-current-continuation
         Procedure          [R5RS] (call-with-current-continuation PROC) ( ...

  See Also: (help help-list)"
  (if (pair? names)
      (if (pair? (cdr names))
          `(begin (help ,(car names)) (help . ,(cdr names)))
          (let ((name (car names)))
            (if (regex? name)
                `(help-list ,name)
                `(help:print
                  ,name
                  ,(if (symbol? name) `(help:symbol (quote ,name))
                       `(help:object ,name))))))
      ;; (help) => (help help)
      '(help help)))

(define help:privates
  (<set> '("*<try-catch>*"  "*<try-finally>*" "help:object" "help:privates"
           "help:print" "help:summary" "help:symbol" "help:type")))
(define (help-list . pattern)
  "(help-list . PATTERN)
  List the symbols bound to the top-level environment.
  PATTERN -- searching regex-pattern
  e.g. > (help-list)  
         => All the symbols will be listed. 
       > (help-list #/^<.+>/) 
          =>   <ArithmeticError>
                    Procedure   Assertion failed.
               <AssertionError>
                    Procedure   Attribute not found.
               <BaseException>
                    Procedure   Common base class for all exceptions
               ...................................."
  (if (and (pair? pattern) (not (regex? (car pattern))))
      (format (current-error-port)
              "Wrong type of arguments (expecting regular-expression object) - ~S\n"
              (car pattern))
      (begin
        (if (null? pattern) (format #t "--- The list of all symbols ---\n")
            (format
             #t "--- The List of symbols matching the given pattern ---\n"))
        (for-each
         (lambda (name)
           (let ((name (format "~A" name)))
             (if (and (not (in? name help:privates))
                      (or (null? pattern)
                          (re-search (car pattern) name)))
                 (let ((hinfo (help:symbol (string->symbol name))))
                   (let ((type (get-keyword :obj-type hinfo "Unknown-Type"))
                         (summary (help:summary hinfo)))
                     (format #t "~A\n    ~18A ~A\n" name type summary))))))
         (<sorted> (symbol-keys))))))

;;;;;;;;;;;;;;;;; python's if  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(define-macro (@if test ex . else)
  "(@if TEST CONSEQUENT . ALTERNATE)
   Simulate Python's if statement.
   Same as `(if (<bool> TEST) CONSEQUENT ALTERNATE)'.
   Example: 
    > (map (lambda (x) (@if x #t #f)) '(\"\" #() ()))
    (#f #f #f)"
  `(if (<bool> ,test) ,ex . ,else))
;;  `(if (not (invoke *operator* 'not_ ,test))
;;       ,ex ,@else))

;; Return __builtin__ variable vector
;; (define (builtin-vars)
;;   (<filter>
;;    (@callable (lambda (v) (bound? v)))
;;    (map (lambda (v) (format "<~A>" v)) (invoke (<vars> *builtin*) 'keys))))

(define (re-gsub re repl string)
  "(re-gsub REGEX REPL STRING)
  Replaces all matches for REGEX with REPL in STRING.
  Returns a new string containing the replacements.
  Equivalent to (re-sub REGEX REPL STRING 0).
  REPL -- can be `string` or `procedure`.

  Examples:
   > (re-gsub #/abc/i \"xyz\" \"abc-abc\") ;=> \"xyz-xyz\"
   > (re-gsub #/(abc)/i \"<\\\\1>\" \"ABC-Abc\") ;=> \"<ABC>-<Abc>\"

   > (define (m->upcase m) (string-upcase (re-group m)))
   > (re-gsub #/[a-z]+/ m->upcase \"12ab-cd-xyz\") ;=>  \"12AB-CD-XYZ\"
  See Also: (help re-sub)"
  (invoke re "sub" (if (lambda? repl) (@callable repl) repl)
          string 0))

(define (re-sub re repl string . count)
  "(re-sub REGEX REPL STRING . COUNT=1)
  Replaces matches for REGEX with REPL in STRING.
  Returns a new string containing the replacements.
  Equivalent to `RegexObject.sub(REPL, STRING, COUNT)` of 
  Python's re-module.
  REPL -- can be `string` or `procedure`.

  Examples:
   > (re-sub #/abc/i \"xyz\" \"abc-abc\") ;=> \"xyz-abc\"
   > (re-sub #/abc/i \"xyz\" \"abc-abc\" 0) ;=> \"xyz-xyz\"

   > (re-sub #/(abc)/i \"<\\\\1>\" \"ABC-Abc\" 0) ;=> \"<ABC>-<Abc>\"

   > (define (m->upcase m) (string-upcase (re-group m)))
   > (re-sub #/[a-z]+/ m->upcase \"12ab-cd-xyz\" )  ;=>  \"12AB-cd-xyz\"
   > (re-sub #/[a-z]+/ m->upcase \"12ab-cd-xyz\" 2) ;=>  \"12AB-CD-xyz\"
   > (re-sub #/[a-z]+/ m->upcase \"12ab-cd-xyz\" 0) ;=>  \"12AB-CD-XYZ\"
  See Also: (help re-gsub)"
  (invoke re "sub" (if (lambda? repl) (@callable repl) repl)
          string (if (pair? count) (car count) 1)))

;; Returns the first COUNT elements of list LST
;; e.g. (list-take '(1 2 3 4 5) 3) ;-> (1 2 3)
;;     (list-take '(1 2 3 4 5) 7) ;-> (1 2 3 4 5 #f #f)
;;     (list-take '(1 2 3 4 5) 7 0) ;-> (1 2 3 4 5 0 0)
(define (list-take lst count . fill)
  (let ((fill (if (pair? fill) (car fill) #f)))
    (let loop ((lst lst) (count count) (result '()))
      (if (> count 0)
          (if (pair? lst) (loop (cdr lst) (- count 1) (cons (car lst) result))
              (loop lst (- count 1) (cons fill result)))
          (reverse! result)))))

(define-macro (re-let match-expr vars . body)
  "(re-let EXPR (VAR ...) BODY ...)
  Evaluates EXPR, and if it's result is regex-MatchObject, then binds 
  VAR... to the matched group values, then evaluates BODY... .
  If `group-length` < `VAR-length`, the remainder of VARS is bound to #f.
  Examples:
  > (re-let (re-match #/(http|https|ftp):\\/\\/([-.\w]+?)\\/(.*)$/i 
                     \"http://docs.python.org/modindex.html\")
           (url protocol domain)
           (list url protocol domain))
    => (\"http://docs.python.org/modindex.html\" \"http\" \"docs.python.org\")

  > (re-let (re-match #/(http|https|ftp):\\/\\/([-.\w]+?)\\/(.*)$/i 
                     \"http://docs.python.org/modindex.html\")
           (url protocol domain path query)
           (list url protocol domain path query))
    => (\"http://docs.python.org/modindex.html\" \"http\" \"docs.python.org\" 
        \"modindex.html\" #f)
  "
  (if (pair? match-expr)
      (let ((tmp-match (gensym)))
        `(let ((,tmp-match ,match-expr))
           (re-let ,tmp-match ,vars . ,body)))
      (let ((tmp-groups (gensym)))
        `(if (and ,match-expr (attr? ,match-expr 'groups))
            (apply
             (lambda ,vars
               ,@body)
             (let ((,tmp-groups (re-group-list ,match-expr)))
               (list-take ,tmp-groups ,(length vars) #f))
             )
            #f))))

;; For any test

