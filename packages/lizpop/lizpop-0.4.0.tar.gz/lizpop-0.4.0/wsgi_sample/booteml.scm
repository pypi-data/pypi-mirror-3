;; -*- coding: utf-8 -*-
;; CAUTION:
;;  All the symbols defined here are bound to built-in-environment,
;;  not interaction-environment. 
;;  So, a interaction-environment variable such as *environ* and *form* 
;;  cannot be looked up from here.
;;  In macro:
;;      If you want to output interaction-environment symbol, 
;;      use  (string->symbol symbol-name) .
;;

;; Convert <str> to <unicode>"
(define UNI string-append)

(define (x->string obj)
  (cond ((isa? obj <basestring>) (string-append obj)) ;; convert unicode
	((keyword? obj) (keyword->string obj))
	(else (format "~A" obj))))

(define (string-join strlist term) (invoke term 'join strlist))

(define (each-hash proc hash)
  (for-each
   (lambda (tuple) (proc (item tuple 0) (item tuple 1)))
   (invoke hash 'iteritems)))

(define (map-hash proc hash)
  (map
   (lambda (tuple) (proc (item tuple 0) (item tuple 1)))
   (invoke hash 'iteritems)))

(define (each-keyword foo kwlst)
  (and (pair? kwlst) (pair? (cdr kwlst))
       (begin (foo (car kwlst) (cadr kwlst))
	      (each-keyword foo (cddr kwlst)))))

(define (map-keyword foo kwlst)
  (reverse!
   (let lp ((kwlst kwlst) (result '()))
     (if (and (pair? kwlst) (pair? (cdr kwlst)))
	 (lp (cddr kwlst) (cons (foo (car kwlst) (cadr kwlst)) result))
	 result))))

(define *cgi* (import "cgi"))
(define (htesc s )
  "HTML escape"
  (re-gsub #/"/ ; " -> &quote
	   "&quot;" (invoke *cgi* 'escape (x->string s))))

(define *urllib* (import "urllib"))

(define (url-encode string . encoding)
  (string-append
   (invoke *urllib* 'quote_plus (apply string->bytes (cons string encoding)))))
(define (url-decode string . encoding)
  (invoke (invoke *urllib* 'unquote_plus (<str> string))
	  'decode (if (pair? encoding) (car encoding) "utf-8") "replace"))

(define (hash->query-string hash . encoding)
  (let ((enc (if (pair? encoding) (car encoding) "utf-8")))
    (string-join
     (map-hash (lambda (k vlst)
		 (string-join
		  (map (lambda (v)
			 (string-append (url-encode (x->string k) enc) "="
					(url-encode (x->string v) enc)))
		       (if (or (list? vlst) (vector? vlst) (isa? vlst <tuple>))
			   vlst (cons vlst))) "&" ))
	       hash)
     "&")))

(define (printf fmt . args)
  "print with format to sys.stdout"
  (with-output-to-port (attr *sys* 'stdout) 
    (lambda ()
      (apply format `(#t ,fmt . ,args)))))

(define (eml . strlist)
  "Procedure: (eml STRING ...)
   Display strlist"
  (display (apply string-append strlist)))

(define (emlf fmt . strlist)
  (apply format `(#t ,fmt . ,strlist)))

(define (eml-include file . args)
  "(eml-include FILE . NAME VALUE ...)"
  (if (pair? args)
      (let ((req (eval (string->symbol "request"))))
	(apply req (cons "setdata" args))))
  (load-eml file))

(define (eml-query a-query key . fallback)
  "Procedure: (eml-query A-QUERY KEY . FALLBACK=\"\")
   Get query parameter with KEY.
   Return the first value associated with form field KEY.
   A-QUERY ---- cgi.FieldStorage object, such as (request 'query)"
  (let ((v (invoke a-query 'getfirst (x->string key) #<none>)))
    (if (none? v) (if (pair? fallback) (car fallback) "")
	(x->string v))))

(define-macro (query key . fallback)
  "Macro: (query key . fallback=\"\")
   Equivalent to (eml-query (request 'query) key . fallback)"
  `(eml-query (,(string->symbol "request") 'query ) ,key . ,fallback))

(define (eml-query/list a-query key . fallback)
  "Procedure: (eml-query/list QUERY KEY . FALLBACK='() )
   Get query parameter with KEY.
   Return the list of values associated with form field KEY.
   QUERY   ---- cgi.FieldStorage object, such as (request 'query)"
  (let ((v (map x->string
		(vector->list (invoke a-query 'getlist (x->string key) )))))
    (if (null? v) (if (pair? fallback) (car fallback) v)
	v)))
(define-macro (query/list key . fallback)
  "Macro: (query/list key . fallback='())
   Equivalent to (eml-query/list (request 'query) key . fallback)"
  `(eml-query/list (,(string->symbol "request") 'query ) ,key . ,fallback))

(define (eml-each-query proc a-query)
  "Procedure: (eml-each-query proc a-query)
   Applies proc for each form fields.
   PROC --- (lambda (key value-list) ... )
   a-query   ---- cgi.FieldStorage object, such as (request 'query)"
  (for-each (lambda (key)
	      (proc (UNI key) (eml-query/list a-query key)))
	    (invoke a-query 'keys)))
(define-macro (each-query proc)
  "Macro: (each-query proc)
   Equivalent to (eml-each-query proc (request 'query))"
  `(eml-each-query ,proc (,(string->symbol "request") 'query )))

(define (eml-map-query proc a-query)
  "Procedure: (eml-each-query proc a-query)
   Applies proc for each form fields, and returns a list of the result
   PROC --- (lambda (key value-list) ... )
   a-query   ---- cgi.FieldStorage object, such as (request 'query)"
  (map (lambda (key)
	 (proc (UNI key) (eml-query/list a-query key)))
       (invoke a-query 'keys)))

(define-macro (map-query proc)
  "Macro: (map-query proc)
   Equivalent to (eml-map-query proc (request 'query))"
  `(eml-map-query ,proc (,(string->symbol "request") 'query )))


(define-macro (request-data . args)
  "Macro: (request-data NAME . FALLBACK=#f)
   get RequestContext data associated with NAME.
   Equivalent to (request 'getdata . NAME FALLBACK).
   ex. (request-data! :mode \"exec\" :show?  #t)
       (request-data  :mode) ;-> \"exec\"
       (request-data) ;-> {u'show?':True, u'mode':u'exec'}"
  `(,(string->symbol "request") 'getdata . ,args))

(define-macro (request-data! . args)
  "Macro: (request-data name value . name2 value2 ...)
   set RequestContext data.
   Equivalent to (request 'setdata name value).
   ex. (request-data! :mode \"exec\" :show?  #t)
       (request-data  :mode) ;-> \"exec\"
       (request-data) ;-> {u'show?':True, u'mode':u'exec'}"
  `(,(string->symbol "request") 'setdata . ,args))

(define (forward uri . args)
  (let ((req (eval (string->symbol "request"))))
    (if (pair? args)
	(apply req (cons "setdata" args)))
    (req "forward" uri)))

;; (define (eml-quit-request req)
;;   ((attr req "quit")))
;; (define-macro (quit-request)
;;   `(eml-quit-request (,(string->symbol "request"))))

(define (redirect url)
  (forward "/redirect" "redirect-url" url))

(define *wsgiref-util* (attr (import "wsgiref.util") 'util))
(define (eml-request-uri env . query?)
  (UNI (invoke* *wsgiref-util* 'request_uri env
	       :include_query (and (pair? query?) (car query?) #t))))
(define-macro (request-uri . query?)
  `(eml-request-uri (,(string->symbol "request") 'environ) . ,query?))

