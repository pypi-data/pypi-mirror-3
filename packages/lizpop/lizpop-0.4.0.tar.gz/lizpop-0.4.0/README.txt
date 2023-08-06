======
Lizpop 
======

Lizpop is Scheme interpreter in Python.
    
Installation
============

Requirements:

  Lizpop requires Python 2.5 or later, but does not work in Python3.

To install:

  Simply run ``python setup.py install``. 

  e.g. ::

  $ tar zxvf lizpop-0.4.0.tar.gz 
  $ cd lizpop-0.4.0
  $ sudo python setup.py install

Usage
=====
To run interactively::

  $ python -O -m lizpop.run

To run a Scheme script in a file::

  $ python -O -m lizpop.run yourfile.scm

For more info about command-line options::

  $ python -O -m lizpop.run -h

Features
========

Subset of Scheme R5RS

  See the `Restrictions`_ section for more details.

Has interfaces to Python

  e.g. ::

    $ cat helloworld.py 
    def hello(s="world"):
      return u"Hello %s!" % s.capitalize()

    $ python -O -m lizpop.run
    > (define *helloworld* (import "helloworld"))
    > (define hello (attr *helloworld* 'hello))
    > (hello "friends")
    "Hello Friends!"


  For more details, See the **IFPY.rst** file in this package.

Regular Expression literal.

  The following literal is a Regular Expression Object. ::

    #/PATTERN/FLAGS
      PATTERN:   Regular expression pattern
      FLAGS:     Regular expression flags.
        i-- ignore case  m-- multi-line  s-- dot matches all
        u-- Unicode dependent  L-- locale dependent  x-- verbose

  Examples ::

    ;; A simple matching
    > (re-search #/(\d+):(\d+)/ "Aug 14")  ;; not match
    #f 
    > (re-search #/(\d+):(\d+)/ "Aug 14 08:30") ;; match
    <_sre.SRE_Match object at ...>

    ;; Get subgroup
    > (re-group (re-search #/(\d+):(\d+)/ "Aug 14 08:30") 1 2)
    ("08" "30")

    ;; Replace string
    > (re-gsub #/<(\/?)h\d>/i "<\\1H3>" "<h1>Features:</h1>")
    "<H3>Features:</H3>"
    > 

  For more info, run ``help`` procedure. ::
 
    e.g.   
    > (help-list #/(^re-)|(regex)/)
    > (help re-match re-search re-group re-gsub)

Supports multi-byte characters

  Only utf-8 encoding now.

EML(EMbedded Lizpop)

  EML is a template language for embedding Lizpop code in text file.

  EML has the following simple specifications.

  * ``%>STRING<%`` is a new string literal, but escape sequences 
    in STRING (such as \\n and \\u3055)  are not decoded.

  * Implicitly, ``%>`` is added to the beginning of the input-port.

  * Implicitly, ``<%`` is added to the end of the input-port.

    Note: These ideas are inspired by BRL ( http://brl.sourceforge.net/ ).

  To run EML, use ``-eml`` as command line option. ::

    e.g. 
    python -m lizpop.run -eml yourfile.eml

  A simple example ::

    $ cat gcdlcm.eml
    <% (define numlist (map string->number *args*)) %>
    GCD of <% numlist %> is <%(apply gcd numlist)%>.
    LCM of <% numlist %> is <%(apply lcm numlist)%>.

    $ python -m lizpop.run -eml gcdlcm.eml -- 1533 37303 4307
    GCD of (1533 37303 4307) is 73.
    LCM of (1533 37303 4307) is 6602631.

  For more examples: 

    please run ``(help load-eml)`` to see its help message.

  Note: ```lizpop + apache2 + mod_wsgi```

    See the ``wsgi_sample/application.wsgi`` file included in this package.

Help function

  Lizpop has a help-function, it displays documentation for the given
  procedures or macros.

  Usage: 

    (help var ...)

    (help-list regex-pattern)

    e.g. ::

      > (help invoke)
      Procedure: (invoke OBJ MESSAGE ARGS ... )
        Invokes the OBJ's method named MESSAGE with ARGS ...
        .........................................................

  However, for now, the help documentation is provided only for the
  Python-Interface related functions.

  For more info, run ``(help)`` and ``(help help-list)``.

  **Note**:
    I'm not good at English. So help messages may include some
    errors or unnatural expressions in English.

Restrictions
============

Hygienic macros are not supported.

  ``define-syntax`` ``syntax-rules``, and ``let-syntax`` are not implemented.

  Instead, traditional(non-hygienic) macros can be used.
    => run ``(help define-macro)``

Strings are not mutable.

  Lizpop strings are implemented as Python unicode-string objects
  which are immutable. so, ``string-set!`` and ``string-fill!`` don't work.

``call/cc`` and ``dynamic-wind`` are only partially implemented.

  Lizpop does not support full continuation.

  Lizpop's ``call-with-current-continuation`` is upward-only and
  non-reentrant. So, it can be used for non-local-exit, but cannot
  be used for co-routines or backtracking.

Complex numbers and Fractional numbers are not supported.

``null-environment`` and ``scheme-report-environment`` are not implemented.

    For more info, run (help eval).

