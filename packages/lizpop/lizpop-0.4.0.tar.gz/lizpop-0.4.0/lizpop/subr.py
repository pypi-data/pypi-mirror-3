#-*- coding: utf-8 -*-
# Copyright (c) 2012 Tetsu Takaishi.  All rights reserved.

from __future__ import division # 11/4 #=> 2.75
import config
if config.isdebug: print "Load subr as %s" % __name__ #debug

import sys, __builtin__
import math, cmath, operator, itertools, re
import traceback # debug

from mylist import Listable,Nil,isPair
import scheme
from scheme import Symbol, ScmList, Env, LspChar, SymbolBase, Keyword
from scheme import sy_quote, sy_unquote, sy_unquote_splicing
from scheme import LispError, LispCustomError, LispUnboundError
from scheme import LispWrongNumberOfArgsError, LispWrongTypeOfArgsError
from scheme import LispSyntaxError, LispLoadFileError
from scheme import lsp_string, scheme_subr
from inport import InPort

### Standard Macro Function #################
def and_macro(_,_e, args):
  if args is Nil : return True
  if args.cdr() is Nil: return args.car()
  # ('if (car args) (cons 'and (cdr args)) #f)
  return ScmList.make(
    #scheme.Boot.intern("if"), args.car(),
    scheme.sy_if, args.car(),
    ScmList( scheme.Boot.intern("and"), args.cdr()),
    False)

############## argument check ##############################
class TypeCheck:
  def __init__(self, fname, *args):
    (self.fname, self.args) = (fname, args)

  def check(self, *reqlst):
    if (len(reqlst) > 1) and (reqlst[-1] is True):
      reqlst = reqlst[0:-1] + (
        (reqlst[-2],) * (len(self.args) - len(reqlst) + 1) )
    #print "reqlst", reqlst # debug
    for (chk, arg) in itertools.izip(reqlst, self.args):
      if chk:
        expecting = chk(arg)
        if isinstance(expecting, basestring):
          raise LispWrongTypeOfArgsError(expecting, self.fname,
                                         mkform(self.fname, *(self.args)))
    return True

def mkform(fname, *args):
  "Return (fname . args) lisp form"
  return ScmList.make(Symbol(fname), *args)

def rqN(obj):
  "require number"
  if isnum(obj): return None
  return "number"

def rqI(obj):
  "require integer"
  if is_integer(obj): return None
  return "integer"

def rqS(obj):
  "require string"
  if isinstance(obj, basestring): return None
  return "string"

def rqC(obj):
  "require char"
  if isinstance(obj, LspChar): return None
  return "char"

def rqV(obj):
  "require vector"
  if isinstance(obj, list): return None
  return "vector"

def rqPr(obj):
  "require pair"
  if isPair(obj): return None
  return "pair"

def rqL(obj):
  "require pair or nil"
  if isinstance(obj, Listable): return None
  return "list"

if any( callable(obj) for obj in ("", u"", {}, [], 1, 1.1, 1L) ) :
  def isProcedure(obj):
    if any( isinstance(obj, typ)
            for typ in (str,unicode,dict,list,int,float,long) ):
      return False
    elif isinstance(obj, scheme.Closure):
      return not isinstance(obj, scheme.Macro)
    else: return callable(obj)
else:
  def isProcedure(obj):
    if isinstance(obj, scheme.Closure):
      return not isinstance(obj, scheme.Macro)
    else: return callable(obj)

# def isnum(obj):
#   return( (not isinstance(obj,bool)) and
#           any( isinstance(obj,tp) for tp in (int,float,long) ))
def isnum(obj):
  return( isinstance(obj, (int, float, long)) and
          (not isinstance(obj, bool)))

# def is_integer(obj):
#   return ( (not isinstance(obj,bool)) and
#            (isinstance(obj, int) or isinstance(obj, long) or
#             (isinstance(obj, float) and long(obj) == obj) ))
def is_integer(obj):
  return( (not isinstance(obj, bool)) and
          ( isinstance(obj, (int, long)) or
            (isinstance(obj, float) and (long(obj) == obj))) )

def ischar(obj): return isinstance(obj, scheme.LspChar)

def is_string(s): return isinstance(s, basestring)

### Standard Function ###############
def mkunsp(lspname, msg=None):
  if msg is None: msg = "Sorry, `%s is not supported" % lspname
  def _function(*args):
    raise LispCustomError(msg, lspname, mkform(lspname, *args))
  return _function

def chk_narg(length, args):
  "length is int or (min-length, max-length)"
  if isinstance(length, (int,long)):
    return len(args) == length

  # check minimum number of args
  if ( len(length) > 0 and isinstance(length[0], (int, long)) 
       and len(args) < length[0] ): return False

  # check maximum number of args
  if ( len(length) > 1 and isinstance(length[1], (int, long))
       and len(args) > length[1] ): return False
  return True
      
def makefunc(fname, pyfunc, chklen=None, reqlist=(), ):
  "Add argument check to PYFUNC, and return function"
  if reqlist and chklen is not None:
    #print "make makefunc %s check both" % fname # debug
    def _function(*args):
      if not chk_narg(chklen, args):
        raise LispWrongNumberOfArgsError(fname, mkform(fname, *args))
      TypeCheck(fname, *args).check(*reqlist)
      return pyfunc(*args)
  elif reqlist and chklen is None:
    #print "make makefunc %s check type only" % fname # debug
    def _function(*args):
      TypeCheck(fname, *args).check(*reqlist)
      return pyfunc(*args)
  elif (not reqlist) and chklen is not Not:
    #print "make makefunc %s check number only" % fname # debug
    def _function(*args):
      if not chk_narg(chklen, args):
        raise LispWrongNumberOfArgsError(fname, mkform(fname, *args))
      return pyfunc(*args)
  else:
    #print "make makefunc %s no check" % fname # debug
    def _function(*args):
      return pyfunc(*args)

  return _function

def equal(target,other):
  if eqv(target, other): return True
  if type(target) != type(other): 
    if isinstance(target, basestring) and isinstance(other, basestring):
      return target == other
    else: return False
  return (target == other)

# Rough implementation
# Note: The following case is not satisfy R5RS
#     eqv?(interned-symbol-A uninterned-symbol-A) -> #t
#     eq?(interned-symbol-A uninterned-symbol-A)  -> #f
def eqv(obj1, obj2):
  if obj1 is obj2: return True

  # when different type -> False
  if type(obj1) != type(obj2): return False

  # (string=? (symbol->string obj1) (symbol->string obj2)) if Symbol
  if isinstance(obj1, SymbolBase): return obj1.equal(obj2)
  if isinstance(obj1,Listable):return False
  if isinstance(obj1,basestring):return False
  if isinstance(obj1, list):return False
  return obj1 == obj2

# ll = ([1,2,3],[10,11,12],[21,22,23,34])
# for x,y,z in lists_each(*ll): print x,"-",y,"-",z
# lists = (List.make(1,2,3), List.make(10,11,12,13), List.make(20,21,22))
# List.from_iter( List.make(*x)  for x in lists_each(*lists) ).lispstr()
# =>'((1 10 20) (2 11 21) (3 12 22))'
def lists_each(*lists):
  itlist = [iter(L) for L in lists]
  try:
    while True:
      yield tuple( map(lambda it: it.next(), itlist) )
  except StopIteration: pass

# Can do also with `map`, without using `lists_each` ...?
@scheme_subr
def mapcar(lisp, env, func, *args):
  r'''(map PROC ITERABLE1 ITERABLE2 ...)
  [R5RS]

  Note:
    `map' and `for-each' work on any type of iterable.
    (This is an extension of Lizpop. )
    e.g.
      > (map (lambda (s) s) "abcd")
        ("a" "b" "c" "d")
      > (map + '(10 20 30) #(100 200 300)
                (<xrange> 1000 4000 1000))
        (1110 2220 3330)

  See Also: (help for-each)'''  
  if isProcedure(func):
    return ( ScmList.from_iter(
        (lisp.apply(env,func,arglist)[0] for arglist in
         (ScmList.from_iter(tp) for tp in lists_each(*args)) )
        ))
  else: raise LispCustomError("%s is not procedure." % func, "map")

@scheme_subr
def foreach(lisp, env, func, *args):
  r'''(for-each PROC ITERABLE1 ITERABLE2 ...)
  [R5RS]

  Note:
    `map' and `for-each' work on any type of iterable.
    (This is an extension of Lizpop. )
    e.g.
    > (for-each
        (lambda (n c) (format #t "~3D:~A\n" n c))
        '(1 2 3) #("A" "B" "C"))
      1:A
      2:B
      3:C
    > (for-each
        (lambda (n c) (format #t "~3D:~A\n" n c))
        (<xrange> 1 4) "ABC")
      1:A
      2:B
      3:C
    > 
  See Also: (help map)'''  
  if isProcedure(func):
    for arglist in (ScmList.from_iter(tp)
                    for tp in lists_each(*args)):
      lisp.apply(env,func, arglist)
    return None
  else:
    raise LispCustomError("%s is not procedure." % func, "foreach")

def setcar(pair, obj):
  if isPair(pair): pair.setcar(obj)
  else: raise LispWrongTypeOfArgsError("pair", "set-car!", pair)

def setcdr(pair, obj):
  if isPair(pair): pair.setcdr(obj)
  else: raise LispWrongTypeOfArgsError("pair", "set-cdr!", pair)

def list_append(*args):
  r'''(append LIST ...)
  [R5RS] Returns a list consisting of the elements of the 
  first list followed by the elements of the other lists.
  The resulting list is always newly allocated, except that 
  it shares structure with the last list argument. 
  The last argument may actually be any object; an improper 
  list results if the last argument is not a proper list.
  Examples:
   > (define lst1 '(1 2 3))
   > (define lst2 '(a b c))
   > (define lst3 '(x y z))
   > (define lst123 (append lst1 lst2 lst3))
   > lst123
   (1 2 3 a b c x y z)
   > (eq? (list-tail lst123 6) lst3)
   #t
   > (append lst123 '(4 . 5))
   (1 2 3 a b c x y z 4 . 5)
  See Also: (help append!) (help list-copy)'''
  if args == (): return Nil
  return ScmList.append(*args)

def list_nconc(*args):
  r'''(append! LIST ...)
  Returns a list consisting of the elements of the first list 
  followed by the elements of the other lists.
  LIST... except the last one may be altered.
  The last argument may actually be any object; an improper list
  results if the last argument is not a proper list.
  Examples:
   > (define lst1 '(1 2 3))
   > (define lst2 '(a b c))
   > (define lst3 '(x y z))
   > (append! lst1 lst2 lst3)
   (1 2 3 a b c x y z)  
   > lst1
   (1 2 3 a b c x y z) ;; lst1 is altered
   > lst2
   (a b c x y z) ;; lst2 is altered
   > lst3
   (x y z)  ;; lst3 is not altered
   ;; when the last argument is not list.
   > (append! lst1 'end)
   (1 2 3 a b c x y z . end)
   > lst1
   (1 2 3 a b c x y z . end)
   > lst2
   (a b c x y z . end)
   > lst3
   (x y z . end)
   > 
  See Also: (help append)'''
  if args == (): return Nil
  if isinstance(args[0], Listable):
    return args[0].nconc(*args[1:])
  elif len(args) == 1:
    return args[0]
  else :
    raise LispWrongTypeOfArgsError("list", "append!", ScmList.from_iter(args))

def list_reverse(lst):
  r'''(reverse LIST)
  [R5RS] Returns a newly allocated list consisting of 
  the elements of list in reverse order.
  See Also: (help reverse!)'''
  if not isinstance(lst, Listable):
    raise LispWrongTypeOfArgsError("list","reverse",lst)
  ret = Nil
  while isPair(lst):
    ret = ScmList(lst.car(), ret)
    lst = lst.cdr()
  return ret

def member(obj, lst, pred=lambda x,y: x is y, ewhere="memq"):
  ls = lst
  while isPair(ls):
    if pred(obj, ls.car()): return ls
    ls = ls.cdr()
  if ls == lst and ls is not Nil:
    raise LispWrongTypeOfArgsError("pair", ewhere, lst)
  return False

def assoc(obj, alist, pred=lambda x,y: x is y):
  for pair in alist:
    if(isPair(pair) and
        pred(obj, pair.car()) ): return pair
  return False

def delete(target, lst, isall=True):
  r'''(delete! ELT LIST . ALL?)
  Equivalent to 
   (delete-if! (lambda (x) (equal? x ELT)) LIST . ALL?)
  This is a destructive function.
  See Also: (help delete-if!)'''
  #return lst.delete(target, not isall)
  return lst.delete_if(lambda data: equal(target, data), not isall)

def list_copy(lst):
  r'''(list-copy LIST)
  Shallow copies LIST.
  examples:
   > (define lst '(1 2 3 . 4))
   #<none>
   > (list-copy lst)
   (1 2 3 . 4)
   > (equal? (list-copy lst) lst)
   #t
   > (eq? (list-copy lst) lst)
   #f
   > (append lst ())
   TypeError: in append: proper-list required
   >   
  See Also: (help append)'''
  if isinstance(lst, Listable): return lst.copy()
  raise LispWrongTypeOfArgsError("list", "list-copy", lst)

@scheme_subr
def try_finally(lisp, env, body, final):
  # Being called from other than `try-finally` macro is unexpected. 
  # Strictly, 
  #  apply_closure is used, so isProcedure(args) check is required ..?
  try:
    return lisp.apply_closure(body, Nil)[0]
  finally:
    lisp.apply_closure(final, Nil)

@scheme_subr
def try_catch(lisp, env, body, excbody):
  # Being called from other than `try-catch` macro is unexpected. 
  # Strictly, 
  #  apply_closure is used, so isProcedure(args) check is required ..?
  try:
    return lisp.apply_closure(body, Nil)[0]
  except BaseException, exc:
    return lisp.apply_closure(excbody, scheme.ScmList.make(exc))[0]

class LispContinuationException(BaseException):
  def __init__(self, value):
    self.value = value

@scheme_subr
def call_cc(lisp, env, proc):
  r'''
  [R5RS] (call-with-current-continuation PROC)
         (call/cc PROC)

  Restriction:
    Lizpop does not support full continuation.
    Lizpop's `call-with-current-continuation' is upward-only and 
    non-reentrant. So, it can be used for `non-local-exit', but 
    cannot be used for co-routines or backtracking.

  See Also: (help dynamic-wind) (help try-catch try-finally)'''
  cc = LispContinuationException(None)
  def continuation(*vallist):
    if cc:
      lval = len(vallist)
      if lval > 1: cc.value = vallist; # pass multi values to CC
      elif lval < 1: cc.value =  None
      else: cc.value = vallist[0]
      raise cc
    else:
      raise LispCustomError("Sorry, My poor call/cc is only `upwards`",
                            "call/cc")
  try:
    return (lisp.apply(env, proc, ScmList.make(continuation)))[0]
  except LispContinuationException, ex:
    if ex is cc:
      return cc.value
    raise ex
  finally:
    cc = None

def chktype_old(fname, expecting, pred, args): # not used 
  if not all(pred(x) for x in args):
    raise LispWrongTypeOfArgsError(expecting, fname, mkform(fname, *args))
  return True

def chktype(fname, expecting, pred, args):
  for x in args:
    if not pred(x):
      raise LispWrongTypeOfArgsError(expecting, fname, mkform(fname, *args))
  return True

def chktype1(fname, expecting, pred, arg):
  if not pred(arg):
    raise LispWrongTypeOfArgsError(expecting, fname, mkform(fname, arg))
  return True

def mkNfunc(lspname, pyfunc, length=None):
  return makefunc(lspname, pyfunc, length, (rqN, True))

# An error message will be raised, if a result is a 
# complex number. 
def mkZfunc(lspname, pyfunc, length=None):
  def _function(*args):
    z = pyfunc(*args)
    if z.imag == 0 :
      return z.real
    else:
      raise LispCustomError("complex number operations are not supported",
                            lspname, mkform(lspname, *args))
  return makefunc(lspname, _function, length, (rqN,True))

def plus(*args):
  chktype("+", "number", isnum, args)
  return reduce(lambda init,x: x + init, args, 0)

def minus(*args):
  chktype("-", "number", isnum, args)
  if len(args) == 1: return -args[0]
  else: return reduce(lambda init,x: init - x , args)

def asterisk(*args):
  chktype("*", "number", isnum, args)
  return reduce(lambda init,x: x * init, args,1)

def slash(*args):
  chktype("/", "number", isnum, args)
  #1 / args[0] if len(args) == 1 else reduce(lambda init,x: init / x, args),
  if len(args) == 1: return 1 / args[0]
  else: return reduce(lambda init,x: init / x, args)

# def argcheck_isnum(lisp, funcname, args):
#   if not all(isnum(n) for n in args):
#     raise scheme.LispError(funcname, "All arguments must be number,",
#                            ScmList(lisp.intern(funcname), ScmList.from_iter(args)))
# def maximum(lisp,_e, *args):
#   argcheck_isnum(lisp, "max", args)
#   return max(*args)
# 
# def minimum(lisp,_e, *args):
#   argcheck_isnum(lisp, "min", args)
#   return min(*args)

# z = ord("0") ; a = ord("a")
# [chr(z+n) for n in range(0,10)] + [chr(a+n) for n in range(0,26)]
_int2str_tab =[
  '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 
  'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 
  'u', 'v', 'w', 'x', 'y', 'z']
_str2int_tab = dict( (ch,n) for n,ch in enumerate(_int2str_tab))
def int2str(num, radix):
  radix = int(radix)
  if radix > len(_int2str_tab) : raise ValueError
  sign = "" ; sbuf = []
  if num < 0 :
    sign = "-"
    num = -num
  elif num == 0: return "0"
  while num > 0:
    sbuf.insert(0, _int2str_tab[num % radix])
    num = num // radix
  return sign + "".join(sbuf)

def str2int(snum, radix):
  radix = int(radix)
  if radix > len(_int2str_tab) : raise ValueError
  ntime = 1 ; result = 0
  if snum[0] == "-":
    ntime = -1
    snum = snum[1:]
  for ch in reversed(snum.lower()):
    nch = _str2int_tab[ch]
    if nch >= radix: raise ValueError
    result += (nch * ntime)
    ntime *= radix
  return result

# radix must be ( 1 < radix < 37)
# if S is float-string, support only when RADIX=10
def string2number(s, radix=10):
  if not isinstance(s, basestring):
    raise LispWrongTypeOfArgsError("string", "string->number", s)
  if not is_integer(radix):
    raise LispWrongTypeOfArgsError("integer", "string->number", radix)

  if (radix < 2) or  (radix > len(_int2str_tab)):
    raise LispCustomError("radix(%d) out of range" % radix,
                          "string->number")
  if radix == 10:
    ret = scheme.str2num(s)
    if ret is None: return False
    return ret
  try:
    return str2int(s, radix)
  except (ValueError, KeyError):
    return False

# radix must be ( 1 < radix < 37)
# if NUM is float, support only when RADIX=10
def number2string(num, radix=10):
  if not isnum(num):
    raise LispWrongTypeOfArgsError("number", "number->string", num)
  if not is_integer(radix):
    raise LispWrongTypeOfArgsError("integer", "number->string", radix)

  if (radix < 2) or  (radix > len(_int2str_tab)):
    raise LispCustomError("radix(%d) out of range" % radix,
                          "string->number")
  if isinstance(num, (int, long)):
    try:
      return unicode( int2str(num, radix) )
    except ValueError:
      return False
  elif isinstance(num, float) and (radix == 10):
    return unicode(num)
  else:
    return False

def quotient(x, y):
  # if( (x*y) < 0 );return -(abs(x) // abs(y))
  if( (cmp(x,0) * cmp(y,0)) < 0 ): return -(abs(x) // abs(y))
  else: return x // y  

def remainder(x,y):
  return x - ( quotient(x,y) * y)

def f_quotient(x, y):
  chktype("quotient", "integer", is_integer, (x,y))
  return quotient(x,y)

def f_remainder(x, y):
  chktype("remainder", "integer", is_integer, (x,y))
  return remainder(x, y)

def f_modulo(x, y):
  chktype("modulo", "integer", is_integer, (x,y))
  return x % y

def gcd_euclid(m, n):
  while( n != 0 ):
    r = m % n
    (m, n) = (n, r)
  return m

def lcm_euclid(m, n):
  gcd = gcd_euclid(m, n)
  if gcd == 0: gcd = 1
  return (m * n) // gcd

def f_gcd(*args):
  L = len(args)
  if L <= 0 : return 0
  chktype("gcd", "integer", is_integer, args)
  exact = all(isinstance(obj,(int, long)) for obj in args)
  if exact:
    return abs( reduce(lambda x,y: gcd_euclid(x,y), args, 0) )
  else:
    return float( abs( reduce(lambda x,y: gcd_euclid(x,y), args, 0) ) )

def f_lcm(*args):
  L = len(args)
  if L <= 0: return 1
  chktype("lcm", "integer", is_integer, args)
  return abs( reduce(lambda x,y: lcm_euclid(x,y), args, 1) )

def f_floor(x):
  if isinstance(x, (int, long)): return x
  return math.floor(x)

def f_ceiling(x):
  if isinstance(x, (int, long)): return x
  return math.ceil(x)

def f_truncate(x):
  if isinstance(x, (int, long)): return x
  if( x > 0 ): return math.floor(x)
  else: return -(math.floor(-x))

def f_round(x):
  if isinstance(x, (int, long)): return x
  return round(x)

def evenP(x):
  chktype1("even?", "integer", is_integer, x)
  return (x % 2) == 0

def oddP(x):
  chktype1("odd?", "integer", is_integer, x)
  return (x % 2) != 0

def f_log(x, base=math.e):
  chktype("log", "number", isnum, (x,base))
  #if (x  < 0) or (base < 0) :
  #  raise LispCustomError("complex number operations are not supported",
  #                        "log", ScmList.make(Symbol("log"), x, base))

  #if( x == 0 ): return(float("-inf"))
  #elif (base == 1): return(float("inf"))
  z = cmath.log(x, base)
  if(z.imag == 0): return z.real
  else:
    raise LispCustomError("complex number operations are not supported",
                          "log", mkform("log", x, base))

def mkCfunc(lspname, pyfunc, length=None):
  return makefunc(lspname, pyfunc, length, (rqC,True))

def mkCfunc_ic(lspname, pyfunc, length=None):
  def _function(*args):
    return pyfunc( *(ch.to_lcase() for ch in args) )
  return makefunc(lspname, _function, length, (rqC,True))

def mkSfunc(lspname, pyfunc, length=None):
  return makefunc(lspname, pyfunc, length, (rqS, True))

def mkSfunc_ic(lspname, pyfunc, length=None):
  def _function(*args):
    # return pyfunc( *( scheme.ascii_lower(s) for s in args) )
    return pyfunc( *( lsp_string(s).lower() for s in args) )
  return makefunc(lspname, _function, length, (rqS, True))

def mkSfunc2_ic(lspname, pyfunc,):  # Not using
  def _function(x,y, ascii=False):
    if ascii: ic = scheme.ascii_lower
    else: ic = unicode.lower
    return pyfunc( ic(lsp_string(x)) , ic( lsp_string(y) ) )
  return makefunc(lspname, _function, (2,3), (rqS, rqS))

def mkSfunc_cnv(lspname, pyfunc, length=None):
  def _function(*args):
    return pyfunc( *( lsp_string(s) for s in args) )
  return makefunc(lspname, _function, length, (rqS, True))

def string_ref(s, k):
  if isinstance(s, basestring):
    return LspChar(ord(s[k]))
  else:
    raise LispWrongTypeOfArgsError("string", "string-ref", mkform("string-ref", s, k))

def substring(s, start, end=None):
  if is_string(s):
    if end is None: end = len(s)
    return s[start:end]
  else:
    raise LispWrongTypeOfArgsError("string", "substring",
                                   mkform("substring", start, end))

def string_append(*args):
  chktype("string-append", "string", is_string, args)
  return reduce(lambda x,y: x + lsp_string(y), args, u"")

def string_to_list(s):
  chktype1("string->list", "string", is_string, s)
  #if not isinstance(s, basestring):
  #  raise LispWrongTypeOfArgsError("string", "string->list", s)
  return ScmList.from_iter(LspChar(ord(ch)) for ch in s)

def list_to_string(lst):
  if not all( isinstance(ch, LspChar) for ch in lst):
    raise LispCustomError("All arguments must be character", "list->string", lst)
  return reduce(lambda x,y: x + unicode(y) , lst, "")

def vector_length(v):
  if isinstance(v, list): return len(v)
  raise LispWrongTypeOfArgsError("vector", "vector-length", v)

def vector_ref(v, n):
  if isinstance(v, list): return v[n]
  raise LispWrongTypeOfArgsError("vector", "vector-ref", v)

def vector_set(v, k, obj):
  if isinstance(v, list): v[k] = obj
  else: raise LispWrongTypeOfArgsError("vector", "vector-set!", v)

def vector_fill(v, fill):
  if isinstance(v, list):
    for n in v: v[n] = fill
  else: raise LispWrongTypeOfArgsError("vector", "vector-set!", v)

import codecs, StringIO
def is_outport(p):
  if isinstance(p, (file, codecs.StreamWriter, codecs.StreamReaderWriter)):
    return hasattr(p, "mode")  and ( "w" in p.mode or "a" in p.mode)
  elif isinstance(p, StringIO.StringIO): return True
  return False

def is_port(p):
  return is_outport(p) or isinstance(p, InPort)

def open_infile(fname, error_where="open-input-file", embedded=False):
  if isinstance(fname, basestring) or isinstance(fname, Symbol):
    try:
      #return InPort( open(unicode(fname), "r") )
      return InPort( open(unicode(fname), "r"), embedded )
    except IOError, ex:
      raise LispCustomError(ex, error_where, fname)
  else:
    raise LispWrongTypeOfArgsError("string or symbol", error_where, fname)

def open_outfile(fname, mode="w", error_where="open-output-file"):
  if isinstance(fname, basestring) or isinstance(fname, Symbol):
    try:
      return open(fname, str(mode))
    except IOError, ex:
      raise LispCustomError(ex, error_where, fname)
  else:
    raise LispWrongTypeOfArgsError("string or symbol", error_where, fname)

@scheme_subr
def call_with_infile(lisp, env, filename, proc):
  r'''(call-with-input-file FILENAME PROC)
  [R5RS] Open FILENAME for input, and call PROC with one argument.
  (PROC PORT)  
    PORT -- The input port obtained by opening FILENAME.
    If PROC returns, then PORT is closed automatically.
  See Also: (help with-input-from-file)'''
  newport = open_infile(filename, "call-with-input-file")
  try:
    return (lisp.apply(env, proc, ScmList.make(newport)))[0]
  finally:
    newport.close()

@scheme_subr
def call_with_outfile(lisp, env, filename, proc, mode="w"):
  r'''(call-with-output-file FILENAME PROC . MODE)
  [R5RS] Open FILENAME for output, and call PROC with one argument.
  (PROC PORT)  
    PORT -- The output port obtained by opening FILENAME.
    If PROC returns, then PORT is closed automatically.
  MODE --- `string': indicating how the file is to be opened.
            "w" or "a"  default is "w"
            (not R5RS)
  See Also: (help with-output-to-file)'''
  newport = open_outfile(filename, mode, "call-with-output-file")
  try:
    return (lisp.apply(env, proc, ScmList.make(newport)))[0]
  finally:
    newport.close()

@scheme_subr
def with_infile(lisp, env, filename, thunk):
  r'''(with-input-from-file FILENAME THUNK)
  [R5RS] Call THUNK with no arguments, While evaluating THUNK, 
  `current-input-port' is set to FILENAME.
  See Also: (help call-with-input-file)'''
  newport = open_infile(filename, "with-input-from-file")
  inp_save = lisp.inport
  try:
    lisp.inport = newport
    return (lisp.apply(env, thunk, Nil))[0]
  finally:
    lisp.inport.close()
    lisp.inport = inp_save

@scheme_subr
def with_outfile(lisp, env, filename, thunk, mode="w"):
  r'''(with-output-to-file FILENAME THUNK . MODE)
  [R5RS] Call THUNK with no arguments, While evaluating THUNK, 
  `current-output-port' is set to FILENAME.
  MODE --- `string': indicating how the file is to be opened.
            "w" or "a"  default is "w"
            (not R5RS)
  See Also: (help call-with-output-file)'''
  newport = open_outfile(filename, mode, "with-output-to-file")
  outp_save = lisp.outport
  try:
    lisp.outport = newport
    return (lisp.apply(env, thunk, Nil))[0]
  finally:
    lisp.outport.close()
    lisp.outport = outp_save

@scheme_subr
def with_errfile(lisp, env, filename, thunk, mode="w"):
  r'''(with-error-to-file FILENAME THUNK . MODE)
  Call THUNK with no arguments, While evaluating THUNK, 
  `current-error-port' is set to FILENAME.
  MODE --- `string: indicating how the file is to be opened.
            "w" or "a"  default is "w"'''
  newport = open_outfile(filename, mode, "with-error-to-file")
  errp_save = lisp.errport
  try:
    lisp.errport = newport
    return (lisp.apply(env, thunk, Nil))[0]
  except Exception, err:
    exctype, evalue = sys.exc_info()[:2]
    lisp.error_out(err, exctype, evalue)
  finally:
    lisp.errport.close()
    lisp.errport = errp_save

@scheme_subr
def with_inport(lisp, env, newport, thunk):
  r'''(with-input-from-port INPORT THUNK)
  Call THUNK with no arguments, While evaluating THUNK, 
  `current-input-port' is set to INPORT.'''
  inp_save = lisp.inport
  try:
    lisp.inport = newport
    return (lisp.apply(env, thunk, Nil))[0]
  finally:
    lisp.inport = inp_save

@scheme_subr
def with_outport(lisp, env, newport, thunk):
  r'''(with-output-to-port OUTPORT THUNK)
  Call THUNK with no arguments, While evaluating THUNK, 
  `current-output-port' is set to OUTPORT.'''
  outp_save = lisp.outport
  try:
    lisp.outport = newport
    return (lisp.apply(env, thunk, Nil))[0]
  finally:
    lisp.outport = outp_save

@scheme_subr
def with_errport(lisp, env, newport, thunk):
  r'''(with-error-to-port ERRPORT THUNK)
  Call THUNK with no arguments, While evaluating THUNK, 
  `current-error-port' is set to ERRPORT.'''
  errp_save = lisp.errport
  try:
    lisp.errport = newport
    return (lisp.apply(env, thunk, Nil))[0]
  except Exception, err:
    exctype, evalue = sys.exc_info()[:2]
    lisp.error_out(err, exctype, evalue)
  finally:
    lisp.errport = errp_save

def close_inport(p):
  if isinstance(p, InPort): p.close()
  else:
    raise LispWrongTypeOfArgsError(u"input port", u"close-input-port")

def close_outport(p):
  if is_outport(p): p.close()
  else:
    raise LispWrongTypeOfArgsError(u"output port", u"close-output-port")

@scheme_subr
def write_char(lisp,_e, ch, p=None):
  if not ischar(ch):
    raise LispWrongTypeOfArgsError("char", "write-char",  mkform("write-char", ch))

  if not (p is None or is_outport(p)):
    raise LispWrongTypeOfArgsError("output-port", "write-char", 
                                   mkform("write-char", ch))
  lisp.disp(ch, p)

@scheme_subr
def flush_port(lisp,_e, p=None):
  r'''(flush . PORT)
  Flush PORT. if PORT is omitted, flush current-output-port.'''
  if p is None: p = lisp.outport
  if is_outport(p): p.flush()
  elif isinstance(p, InPort): p.stream.flush()
  else:
    raise LispWrongTypeOfArgsError("port", "flush", mkform("flush", p))

@scheme_subr
def read_line(lisp, _e, port=None):
  r'''(read-line . PORT)
  Reads one line from PORT and returns a string or `eof object`
  If PORT is omitted, reads from current-input-port.
  Examples:
   > (begin (read-char) (display "?: ") (read-line))
   ?: xyz
    => "xyz\n"
   > (define (mygrep regex file)
       (with-input-from-file file
         (lambda ()
           (let next-read ((line (read-line)))
             (if (not (eof-object? line))
                 (begin
                   (if (re-search regex line) (display line))
                   (next-read (read-line))))))))
   > (mygrep #/false$/ "/etc/passwd")
   sshd:x:*:*::/var/empty:/bin/false
   ......................
   >'''
  if port is None: port = lisp.inport
  line = port.get_line()
  if line == u"": return scheme.eof_object
  return line

import clformat
@scheme_subr
def cl_format(lisp,_e, p, *args):
  r'''
(format DESTINATION FMT ARG ...)
(format FMT ARG ... )
  Subset of CommonLisp's format function.
  DESTINATION
    #t -- The output is to the current output port, and None is returned.
    #f -- A formatted string is returned, and nothing is outputted. 
    port -- The output is to the `port'.
    DESTINATION can be omitted.
  FMT
    `string' containing format directives.

  Format Directive
    A directive consists of '~', parameters, flags, and a single
    character indicating what kind of directive this is.
    ~[Parameter-1],[Parameter-2],...[Parameter-n][Flags]Char
      Parameter 
        * integer  
        * 'character
        * V or v
           The parameter-value is taken from ARG...
      Flags
        atmark '@' and colon ':'
    Parameters and flags can be omitted.

  ~A
  ~mincol,colinc,minpad,padcharA
    Output without escape characters as `display' does.
    flag @ -- left pad
    examples:
     (format "[~A]" '(sym "str" 10 #\C)) ;-> "[(sym str 10 C)]"
     (format "[~10A]" '("a" b)) ;-> "[(a b)     ]"
     (format "[~10,,,'+A]" '("a" b)) ;-> "[(a b)+++++]"
     (format "[~10@A]" '("a" b)) ;-> "[     (a b)]"
     (format "[~V,,,V@A]" 12 #\_ '("a" b)) ;->  "[_______(a b)]"

  ~S
  ~mincol,colinc,minpad,padcharS
    Output with escape characters as `write' does.
    flag @ -- left pad
    examples
     (format "[~S]" '(sym "str" 10 #\C)) 
       => "[(sym \"str\" 10 #\\C)]"

  ~D
  ~mincol,padchar,commachar,comma-intervalD
    Decimal output
    flag @ -- number sign always
         : -- comma separated
    examples
      (format "<~D>" 12345678) ;-> "<12345678>"
      (format "<~@D>" 12345678) ;-> "<+12345678>"    
      (format "<~:D>" 12345678) ;-> "<12,345,678>"    
      (format "<~12,'_,' ,:D>" 12345678) ;-> "<__12 345 678>" 

  ~X
  ~mincol,padchar,commachar,comma-intervalX
    Hexadecimal output.
    flag @ -- number sign always
         : -- comma separated
    examples
      (format "<~X>" 12345678) ;-> "<BC614E>"
      (format "<~:X>" 12345678) ;-> "<BC6,14E>"

  ~O
  ~mincol,padchar,commachar,comma-intervalO
    Octal output
    flag @ -- number sign always
         : -- comma separated
    examples
      (format "<~O>" 12345678) ;-> "<57060516>"

  ~B
  ~mincol,padchar,commachar,comma-intervalB
    Binary output
    flag @ -- number sign always
         : -- comma separated
    examples
      (format "|~B|" 129) ;-> "|10000001|"
      (format "|~:B|" 129) ;-> "|10,000,001|"
      (format "|~12,'_,' ,:B|" 129) ;-> "|__10 000 001|"

  ~~
  ~n~
    Output N tildes.
    examples
      (format "(format ~~B 12) -> ~B" 12)
        -> "(format ~B 12) -> 1100"
      (format "~10~") ;-> "~~~~~~~~~~"

  ~*
  ~n*
    Jump N arguments
    flag : -- jumps N arguments backward.
         @ -- jump to the N'th argument (start at 0)
    examples
      (format "~A ~A ~*~A" 0 1 2 3) ;-> "0 1 3"
      (format "~A ~A ~:*~A" 0 1 2 3) ;-> "0 1 1"
      (format "~A ~A ~A ~A ~3:*~A" 0 1 2 3)
        => "0 1 2 3 1"
      (format "~A ~A ~A ~A ~2@*~A" 0 1 2 3)
        => "0 1 2 3 2"  '''
  port = None
  if isinstance(p, basestring):
    fmt = p; 
  elif isinstance(p, bool):
    if p is True:  port = lisp.outport
    fmt = args[0]
    args = args[1:]
  elif is_outport(p):
    port = p
    fmt = args[0]
    args = args[1:]
  else: 
    raise LispWrongTypeOfArgsError("port or string or boolean", "format",
                                   ScmList.from_iter( (p,) + args))

  # raise ValueError, CLFormatIndexError
  try:
    formatter = clformat.CLFormatter(fmt)
    result = formatter.format(args)
    if port:
      lisp.disp(result, port)
      return None
    else: return result
  except clformat.CLFormatIndexError:
    # traceback.print_exc() # debug
    raise LispCustomError("wrong number of fomat string arguments", 
                          "format", fmt)
  except clformat.CLFormatValueError, exc:
    # traceback.print_exc() # debug
    raise LispCustomError(exc.reason, "format", fmt)

def error(reason, *args):
  """(error REASON ARGS ...)
  Raise an error.
  REASON -- `string' or `symbol'
  ARGS   --  any scheme object"""
  raise LispError(reason, *args)

@scheme_subr
def load(lisp, _e, fname):
  '''(load FILE-PATH)
  Load program from FILE-PATH. 
  If FILE-PATH doesn't absolute-path and doesn't start with 
  "./" or "../", it is searched through the directories on 
  *load-path* variable

  See Also: (help *load-path*)'''
  loadpath = lisp.toplevel_env.lookup(lisp.intern(u"*load-path*"))
  if not isinstance(loadpath, Listable): loadpath = []
  fpath = scheme.get_loadpath(loadpath, fname)
  #print "fpath=", fpath # debug
  if not fpath:
    raise LispCustomError("cannot find file" ,"load", fname)
                          
  newport = open_infile(fpath, "load")
  saves = (lisp.toplevel_env, lisp.inport) # is no need???
  try:
    # lisp.inport = newport
    lisp.repl(prompt=None, readport = newport, errquit=True)
    return None
  except Exception:
    raise LispLoadFileError(newport.getname(), "load")
  finally:
    newport.close()  # --> See load-unlink-test.scm
    (lisp.toplevel_env, lisp.inport) = saves

@scheme_subr
def load_embedded(lisp, _e, fname):
  r'''(load-eml FILEPATH)
  Load EML(EMbedded Lizpop) code from FILEPATH.
  EML is Lizpop dialect for embedding Scheme code in text file.
  EML has the following simple specifications.
    * %>STRING<% is a new string literal, but escape sequences 
      in STRING (such as \n and \u3055) are not decoded.
    * Implicitly, '%>' is added to the beginning of the input-port.
    * Implicitly, '<%' is added to the end of the input-port.
    * '<%%' is replaced with '<%' in %>STRING<%
  Note: 
    These ideas are inspired by BRL(http://brl.sourceforge.net/).

  A simple example is this:
    $ cat hello.eml 
     <% (define message 
          (if (pair? *args*) (car *args*) "wonderful world")) %>
     Hello, <% message %>.
    $ python -O -m lizpop.run 
     > (load-eml "hello.eml")

     Hello, wonderful world.
     #<none>
     > (quit)

    $ python -O -m lizpop.run -eml hello.eml -- 'cruel world'

     Hello, cruel world.
    $ 

  More complex example.
    $ cat calc-gcd.eml
     <% (define title "GCD/LCM")
        (define (out . args) (for-each display args))
        (define data-list
          '((252 105) 
            (6132 9709 118041)
            (1030898 1027907 100697))) %>
     <html>
     <head><title><% title %></title></head>
     <body>
     <h3><% title %></h3>
     <% (for-each
          (lambda (nums)
            (out %>
             GCD of <%nums%> is <%(apply gcd nums)%>.<br />
             LCM of <%nums%> is <%(apply lcm nums)%>.<p/>
     <%      )) data-list) %>
     </body>
     </html>

    $ python -O -m lizpop.run -eml calc-gcd.eml

     <html>
     <head><title>GCD/LCM</title></head>
     <body>
     <h3>GCD/LCM</h3>

             GCD of (252 105) is 21.<br />
             LCM of (252 105) is 1260.<p/>

             GCD of (6132 9709 118041) is 511.<br />
             LCM of (6132 9709 118041) is 8971116.<p/>

             GCD of (1030898 1027907 100697) is 997.<br />
             LCM of (1030898 1027907 100697) is 107348439638.<p/>

     </body>
     </html>
   $
  See Also: (help load)'''
  loadpath = lisp.toplevel_env.lookup(lisp.intern(u"*load-path*"))
  if not isinstance(loadpath, Listable): loadpath = []
  fpath = scheme.get_loadpath(loadpath, fname)
  #print "fpath=", fpath # debug
  if not fpath:
    raise LispCustomError("cannot find file" ,"load", fname)
                          
  newport = open_infile(fpath, "load-embedded", embedded=True)
  saves = (lisp.toplevel_env, lisp.inport) # is no need???
  try:
    ## lisp.inport = newport
    # result = lisp.repl(prompt=None, writemode="raw", readport = newport)
    # if isinstance(result, Exception): return result
    # else: return None
    lisp.repl(prompt=None, writemode="raw", readport=newport, errquit=True)
    return None
  except Exception:
    raise LispLoadFileError(newport.getname(), "load-eml")
  finally:
    newport.close()  # --> See load-unlink-test.scm
    (lisp.toplevel_env, lisp.inport) = saves

def values(*args):
  L = len(args)
  if L > 1: return tuple(args) # return args 
  elif L >= 1:return args[0]
  # (call-with-values values (lambda args args)) ;-> ()
  else: return()

# def call_values(lisp, env, producer, consumer): # -> boot.scm
#   values = (lisp.apply(env, producer, Nil))[0]
#   if not isinstance(values, tuple):
#     values = (values,)
#   return (lisp.apply(env, consumer, ScmList.from_iter(values)))[0]
  
@scheme_subr
def interaction_env(lisp, env):
  "(interaction-environment)\n  [R5RS]\n  See Also: (help eval)"
  return lisp.toplevel_env

@scheme_subr
def current_env(lisp, env):
  r'''(current-environment)
  Returns the current environment (For debug use only).
  Example:
    > (define a 10)
    > (let ((a 100)) (eval 'a (interaction-environment)))
    10
    > (let ((a 100)) (eval 'a (current-environment)))
    100
  See Also: (help eval)'''
  return env

@scheme_subr
def builtin_env(lisp,env):
  r'''(built-in-environment)
  Returns the built-in environment.
  Note: the built-in environment is immutable.
  See Also: (help eval)'''
  return scheme.Boot.scheme_environment

@scheme_subr
def scheme_eval(lisp, current_env, sxp, env=None):
  r'''(eval EXPRESSION . ENV)
  [R5RS] Evaluates EXPRESSION in ENV.
  ENV is one of the following
     (interaction-environment) -- R5RS
     (built-in-environment) -- Lizpop built-in environment
     (current-environment) -- current environment
  If Env is omitted, then (interaction-environment) is used.
  NOTE: `scheme-report-environment' and `null-environment' 
        are not supported.

  Examples:
    > (define * +) ;; redefine * to + 
    > (* 10 20)
    30
    > (eval '(* 10 20) (interaction-environment))
    30
    > (eval '(* 10 20) (built-in-environment))
    200
    ;; built-in-environment is immutable!
    > (eval '(define aaa 100) (built-in-environment))
    ERROR: This environment is immutable .....
    >   
  See Also: 
    (help interaction-environment built-in-environment)'''
  if env is None: env = lisp.toplevel_env
  save_toplevel = lisp.toplevel_env
  try:
    if env == scheme.Boot.scheme_environment:
      lisp.toplevel_env = env
    lspobj = lisp.macro_expand(sxp, lisp.toplevel_env)
    return lisp.eval(lspobj, env)
  finally:
    lisp.toplevel_env = save_toplevel

def scheme_module():
  return scheme

@scheme_subr
def debugging(lisp, env, prompt="debug> "):
  r'''(debug . PROMPT)
  Enter REPL in the current environment.
  If PROMPT is omitted, the default is "debug> ".
  Examples:
   > (define (fact n)
       (debug "enter fact> ")
       (let loop ((x n) (acc 1))
         (if (< x 1) (begin (debug "exit fact> ") acc)
             (loop (- x 1) (* x acc)))))
   > (fact 40)
   enter fact> n
   40
   enter fact> (quit)
   exit fact> x
   0
   exit fact> acc
   815915283247897734345611269596115894272000000000
   exit fact> (quit)
   815915283247897734345611269596115894272000000000
   >'''
  saves = (lisp.toplevel_env, lisp.inport, lisp.outport, lisp.errport)
  try:
    lisp.inport = InPort(sys.stdin)
    lisp.outport = sys.stdout
    lisp.errport = sys.stderr
    lisp.repl(prompt=prompt, toplevel = env)
  finally:
    (lisp.toplevel_env, lisp.inport, lisp.outport, lisp.errport) = saves 

@scheme_subr
def boundp(lisp, env, sym):
  r'''(bound? SYMBOL)
  Return #t if SYMBOL is bound to any value.
  SYMBOL -- can be `symbol' or `string'.
  Examples:
   > (bound? '|set!|)
   #t
   > (bound? 'a)
   #f
   > (let ((a 100)) (bound? 'a))
   #t
   > (bound? 'a)
   #f'''
  #chktype1("bound?", "string", is_string, string)
  if is_string(sym): sym = lisp.intern(sym)
  elif not isinstance(sym, Symbol):
    raise LispWrongTypeOfArgsError("symbol or string", "bound?",
                                   mkform("bound?", sym))
  return env.lookup(sym) is not scheme.unbind

@scheme_subr
def gensym(lisp,env):
  lisp.gensym_seed += 1
  return Symbol("#*_^G%ld" % lisp.gensym_seed)

######## regex #########################################
def string2regex(string, flags=u""):
  r'''(string->regex STRING . FLAGS)
  Convert STRING to regular expression object.
  FLAGS -- `string' of regular expression flags.
        letters from the set('i', 'L', 'm', 's', 'u', 'x').
        i-- ignore case        m-- multi-line       s-- dot matches all
        u-- Unicode dependent  L-- locale dependent  x-- verbose
  e.g.
  > (define rx (string->regex "begin(.+)end" "is"))
  > rx
    #/begin(.+)end/is
  > (re-group (re-search rx "if begin\n a = 100\nend") 1)
    "\n a = 100\n"'''  
  if not isinstance(string, basestring):
    raise LispWrongTypeOfArgsError("string", "string->regex", 
                                   mkform("string->regex", string, flags))
  return re.compile(lsp_string(string), scheme.str2rxflag(flags))

def re_match(regex, string, *args):
  r"""(re-match REGEX STRING . POS ENDPOS)
  Mostly equivalent to `RegexObject.match' of Python's re-module, 
  except that it returns #f if the STRING does not match.
  REGEX -- Regular expression object, such as #/abc/i
  Examples:
   > (re-match #/abc/i "--Abcdef") ;=> #f
   > (re-match #/.*abc/i "--Abcdef") ;=> match
   > (re-search #/abc/i "--Abcdef") ;=> match
   
   > (define data "<h1>Regular Expression</H1>")
   > (begin (define m (re-match #/<(H\d)>(.+)<\/\1>/i data)) m)
     => <_sre.SRE_Match object>
   > (re-group-list m)
     => ("<h1>Regular Expression</H1>" "h1" "Regular Expression")
  See also: (re-search)"""
  ret = regex.match(string, *args)
  return False if ret is None else ret

def re_search(regex, string, *args):
  r"""(re-search REGEX STRING . POS ENDPOS)
  Mostly equivalent to `RegexObject.search' of Python's re-module,
  except that it returns #f if the STRING does not match.
  REGEX -- Regular expression object, such as #/abc/i
  Example:
   > (define data "Aug 14 08:08 - Sep 8 14:01 - Nov 12 17:26 -")
   > (let gettime ((pos 0) (result '()))
       (let ((m (re-search #/(\d+):(\d+)/ data pos)))
         (if m (gettime (re-end m) (cons (re-group m 1 2) result))
             result)))
     => (("17" "26") ("14" "01") ("08" "08"))
  See also: (re-match)"""
  ret = regex.search(string, *args)
  return False if ret is None else ret

def re_split(regex, string, *args):
  r"""(re-split REGEX STRING . MAXSPLIT=0)
  Mostly equivalent to `RegexObject.split' of Python's re-module,
  except that it returns lisp's list.
  Examples:
   > (re-split #/\W+/ "Words, words, words.")
    => ("Words" "words" "words" "")
   > (re-split #/(\W+)/ "Words, words, words.")
    => ("Words" ", " "words" ", " "words" "." "")
   > (re-split #/\W+/ "Words, words, words." 1)
    => ("Words" "words, words.")
   > (re-split #/(\W+)/ "...words, words...")
    => ("" "..." "words" ", " "words" "..." "")"""
  return ScmList.from_iter(regex.split(string, *args))

def re_findall(regex, string, *args):
  r"""(re-findall REGEX STRING . POS ENDPOS)
  Mostly equivalent to `RegexObject.findall' of Python's re-module,
  except that it returns lisp's list.
  Examples:
  > (re-findall #/\d+:\d+/ "Aug 14 08:08 - Sep 8 14:01 - Nov 12 17:26 -")
    => ("08:08" "14:01" "17:26")
  > (re-findall #/(\d+):(\d+)/ "Aug 14 08:08 - Sep 8 14:01 - Nov 12 17:26 -")
    => (("08" "08") ("14" "01") ("17" "26"))
  See also: (help re-finditer)"""
  return ScmList.from_iter(
    ScmList.from_iter(x) if isinstance(x, tuple) else x
    for x in regex.findall(string, *args))

def re_finditer(regex, string, *args):
  r"""(re-finditer REGEX STRING . POS ENDPOS)
  Equivalent to `RegexObject.finditer' of Python's re-module.
  Examples:
  > (for-each
     (lambda (m)
       (format #t "~2,'0D-~2,'0D: ~A\n"
               (re-start m) (re-end m) (re-group m 0)))
     (re-finditer  #/\w+ly/
        "He was carefully disguised but captured quickly by police."))
   07-16: carefully
   40-47: quickly
  See also: (help re-findall)"""
  return regex.finditer(string, *args)

def re_groupone(match_object, gnum):
  try:
    return lsp_string( match_object.group(gnum) )
  except IndexError:
    return False

def re_group(match_object, group=0, *group_numbers):
  r"""(re-group MATCH-OBJECT GROUP-NUMBER ...)
  Equivalent to Python re-module's `RegexObject.group'.
  If there is a single GROUP-NUMBER argument, 
     the result is a single string or #f .
  If there are multiple GROUP-NUMBER arguments, 
     the result is a scheme's list.
  Examples:
   > (re-group (re-match #/(\d+)\.(\d*)/ "123.45") 2) ;=> "45"
   > (re-group (re-match #/(\d+)\.(\d*)/ "123.45") 0 1 2 3) 
     => ("123.45" "123" "45" #f)
   > (define m (re-match #/(?P<first_name>\w+) (?P<last_name>\w+)/
                         "Malcom Reynolds"))
   > (re-group m "first_name")  ;=> "Malcom"
   > (re-group m "last_name")   ;=> "Reynolds"
   > (re-group m "middle_name") ;=> #f
  See also: (help re-group-list) """
  if group_numbers:
    return ScmList.from_iter(
      re_groupone(match_object, g) for g in (group,) + group_numbers)
  else:
    return re_groupone(match_object, group)

def re_groups(match_object):
  """(re-groups MATCH-OBJECT)
  Return a VECTOR containing all the subgroups (start at group-1) of the match.
  Equivalent to Python re-module's `MatchObject.groups(False)`
  See Also: (help re-group-list)"""
  return [ lsp_string(x) for x in match_object.groups(False) ]

def re_group_list(match_object):
  """(re-group-list MATCH-OBJECT)
  Return a LIST containing all the groups of the match.
  LIST is (group-0 group-1 group-2 ....)
  The group value that did not participate in the match => bind to #f
  Example:
   > (define m (re-match #/(\d+):(\d+):(\d*)/ "23:43:59"))
   > (re-groups m)
     #("23" "43" "59")
   > (re-group-list m)
     ("23:43:59" "23" "43" "59")
   > (re-group m 0 1 2 3)
     ("23:43:59" "23" "43" "59")
  See Also: (help re-group re-groups)"""
  return ScmList( re_groupone(match_object, 0),
                  ScmList.from_iter(
      lsp_string(x) for x in match_object.groups(False)) )

def re_group_assoc(match_object):
  return ScmList.from_iter(
    ScmList(lsp_string(k), lsp_string(v)) for (k, v) in match_object.groupdict(False).iteritems()
    )

def re_start(match_object, group=0):
  r"""(re-start MATCH-OBJECT . GROUP)
  Equivalent to `MatchObject.start' of Python's re-module.
  Example:
   > (define email "tony@tiremove_thisger.net")
   > (let ((m (re-search #/remove_this/ email)))
       (if m (string-append (substring email 0 (re-start m))
                            (substring email (re-end m)))
          #f))
    => "tony@tiger.net"
  See Also: (help re-end)"""
  return match_object.start(group)

def re_end(match_object, group=0):
  r"""(re-end MATCH-OBJECT . GROUP)
  Equivalent to `MatchObject.end' of Python's re-module.
  See Also: (help re-start)"""
  return match_object.end(group)

############ keyword ##################################
def search_keyword(kwd, kwdlist):
  while isPair(kwdlist) and isPair(kwdlist.cdr()) :
    if isinstance(kwdlist.car(), Keyword):
      if kwdlist.car().equal(kwd): return kwdlist
    else: return False
    kwdlist = kwdlist.cdr().cdr()
  return Nil

def get_keyword(kwd, kwdlist, fallback=False):
  r'''(get-keyword KEY KEY-VALUE-LIST . FALLBACK)
  Returns KEY's value from KEY-VALUE-LIST.
  If the KEY is not found, then returns FALLBACK.
  KEY -- `keyword symbol`
  KEY-VALUE-LIST -- (key value key2 value2 ...) 
  FALLBACK -- default is #f
  e.g:
    (get-keyword :two '(:one 1 :two 2 :three 3)) ;=> 2
    (get-keyword :zero '(:one 1 :two 2 :three 3)) ;=> #f
    (get-keyword :zero '(:one 1 :two 2 :three 3) -1) ;=> -1
  See Also: (help set-keyword! add-keyword! delete-keyword!)'''
  def _raiseError(expecting):
    raise LispWrongTypeOfArgsError(expecting, "get-keyword",
                                   mkform("get-keyword", kwd, kwdlist))
  if not isinstance(kwd, Keyword): _raiseError("keyword")
  if not isinstance(kwdlist, Listable): _raiseError("list")
  find = search_keyword(kwd, kwdlist)
  if isPair(find): return find[1]
  elif isinstance(find, Listable): return fallback
  else: _raiseError("keyword-list")

def set_keyword(kwd, val, kwdlist):
  r"""(set-keyword! KEY VAL KEY-VALUE-LIST)
  Change value in KEY-VALUE-LIST of KEY to VALUE, and 
  return old value.
  If KEY is not in KEY-VALUE-LIST, return #f.
  KEY -- `keyword symbol`
  KEY-VALUE-LIST -- (key value key2 value2 ...) 
                    KEY-VALUE-LIST is modified by side effects.
  Examples:
   > (define kvlst '(:year 2011 :month 10 :day 23))
   > (set-keyword! :year 1999 kvlst)
     => 2011
   > kvlst
     => (:year 1999 :month 10 :day 23)
   > (set-keyword! :hour 8 kvlst)
     => #f
  See Also: (help get-keyword add-keyword! delete-keyword!)"""
  def _raiseError(expecting):
    raise LispWrongTypeOfArgsError(expecting, "set-keyword!",
                                   mkform("set-keyword!", kwd, val, kwdlist))
  if not isinstance(kwd, Keyword): _raiseError("keyword")
  if not isinstance(kwdlist, Listable): _raiseError("list")
  find = search_keyword(kwd, kwdlist)
  if isPair(find):
    ret = find[1]
    find.cdr().setcar(val)
    return ret
  elif isinstance(find, Listable): return False
  else: _raiseError("keyword-list")

def add_keyword(kwd, val, kwdlist):
  r"""(add-keyword! KEY VAL KEY-VALUE-LIST)
  Change value in KEY-VALUE-LIST of KEY to VALUE.
  If KEY is not in KEY-VALUE-LIST, the new KEY/VAL pair is added.
  Return new or changed KEY-VALUE-LIST.
  KEY -- `keyword symbol`
  KEY-VALUE-LIST -- (key value key2 value2 ...) 
                    KEY-VALUE-LIST is modified by side effects.
  Examples:
  > (define kvlst '(:year 2011 :month 10 :day 23))
  > (define kvlst-new (add-keyword! :hour 21 kvlst)) ;; add :hour
  > kvlst-new
    => (:hour 21 :year 2011 :month 10 :day 23)
  > (eq? kvlst (cddr kvlst-new))
    => #t
  > (add-keyword! :year 1999 kvlst) ;; change :year
    => (:year 1999 :month 10 :day 23)
  > kvlst
    => (:year 1999 :month 10 :day 23)
  > kvlst-new
    => (:hour 21 :year 1999 :month 10 :day 23)
  > 
  See Also: (help get-keyword set-keyword! delete-keyword!)"""

  def _raiseError(expecting):
    raise LispWrongTypeOfArgsError(expecting, "add-keyword!",
                                   mkform("add-keyword!", kwd, val, kwdlist))
  if not isinstance(kwd, Keyword): _raiseError("keyword")
  if not isinstance(kwdlist, Listable): _raiseError("list")
  find = search_keyword(kwd, kwdlist)
  if isPair(find):
    find.cdr().setcar(val)
    return kwdlist
  elif isinstance(find, Listable): 
    return ScmList(kwd, ScmList(val, kwdlist))
  else: _raiseError("keyword-list")

def delete_keyword(kwd, kwdlist, isall=False):
  r'''(delete-keyword! KEY KEY-VALUE-LIST . ALL?)
  If KEY in KVLIST, KEY and VALUE will be deleted from KVLIST.
  KEY -- `keyword symbol`
  KEY-VALUE-LIST -- (key value key2 value2 ...) 
                    KEY-VALUE-LIST is modified by side effects.
  ALL?  -- #f: delete first match (default)
           #t: delete all match
  Examples:
   > (define kvlst '(:year 2011 :month 10 :day 23))
   > (define kvlst-new (delete-keyword! :month kvlst))
   > kvlst-new
     => (:year 2011 :day 23)
   > kvlst
     => (:year 2011 :day 23)
   > (define kvlst-new (delete-keyword! :year kvlst))
   > kvlst-new
     => (:day 23)
   > kvlst
     => (:year 2011 :day 23)
   ;; when key is not in kvlist
   > (delete-keyword! :z '(:a 1 :b 2 :c 3)) 
     => (:a 1 :b 2 :c 3)
   ;; delete first key :a from left
   > (delete-keyword! :a '(:a 1 :b 2 :c 3 :a 100))
     => (:b 2 :c 3 :a 100)
   ;; delete all key :a
   > (delete-keyword! :a '(:a 1 :b 2 :c 3 :a 100) #t)
     => (:b 2 :c 3)
  See Also: (help get-keyword set-keyword! add-keyword!)'''
  def _raiseError(expecting):
    raise LispWrongTypeOfArgsError(expecting, "delete-keyword!",
                                   mkform("delete-keyword!", kwd, kwdlist))
  if not isinstance(kwd, Keyword): _raiseError("keyword")
  if not isinstance(kwdlist, Listable): _raiseError("list")

  kwdlist = ScmList(False, kwdlist)
  top = kwdlist
  while isPair(kwdlist.cdr()):
    if isinstance(kwdlist.cdr().car(), Keyword):
      if kwdlist.cdr().car().equal(kwd): 
        kwdlist.setcdr(kwdlist.cdr().cdr().cdr())
        if not isall: return top.cdr()
    kwdlist = kwdlist.cdr().cdr()
  return top.cdr()

#########  python interface ############################
class PyExecException(Exception):  # not used
  def __init__(self, value): self.value = value

def py_exec(expr, *args):
  """(exec EXPR . GLOBAL-DICT LOCAL-DICT)
  Same as Python's `exec`."""
  if len(args) <= 0: exec expr
  elif len(args) == 1: exec expr in args[0]
  else: exec expr in args[0], args[1]
  return None

# ex.
#  (exec "import datetime; _return(datetime.date.today().strftime('%Y/%m/%d'))")
#   not used
def py_exec_return(expr, *args):
  exc = PyExecException(None)
  def _return(value):
    exc.value = value
    raise exc

  try:
    if len(args) <= 0: exec expr in globals(), locals()
    elif len(args) == 1: exec expr in args[0]
    else: exec expr in args[0], args[1]
  except PyExecException, ret:
    if ret is exc: return ret.value
    raise ret
  return None

#e.g. (define d (import "datetime"))
#    (call (attr d "datetime" "today"))
def attr(obj, *names):
  r"""(attr OBJECT NAME ....)
  Return the value of the named attributed of object.
  NAME --- can be `string` or `symbol` or `keyword-symbol`.
  (attr obj "name1" "name2") is equivalent to `obj.name1.name2` in Python.
  examples:
   > (define today (attr (import "datetime") 'date 'today))
   > (<type> today) ;=> <type 'datetime.date'>
   > (<callable> today) ;=> #t
   > (today) ;=> e.g. 2011-11-14
   > (map (lambda (at) (attr (today) at)) (list "year" 'month :day))
     => (2011 11 14)
  See also: (help attr? attr!)"""
  for name in names: obj = getattr(obj,unicode(name))
  return obj

def set_attr(obj, name, value):
  """(attr! OBJECT NAME VALUE)
  Set attribute value.
  This is equivalent to the Python expression `OBJECT.NAME = VALUE`.
  NAME --- can be `string` or `symbol` or `keyword-symbol`.
  See also: (help attr attr?)"""
  setattr(obj, unicode(name), value)
  return None

def invoke(obj, message, *args):
  """(invoke OBJ MESSAGE ARGS ... )
  Invokes the OBJ's method named MESSAGE with ARGS as positional arguments.
  The MESSAGE can be `string` or `symbol`.
  If you want to call with keyword arguments, use `invoke*` procedure.
  examples:
    ;; ",".join(["abc","def","efg"])
    > (invoke "," 'join '("abc" "def" "efg"))
     => "abc,def,efg"

    ;; os.getenv("LANG","C")
    > (invoke *os* 'getenv "LANG" "C") 
     => "ja_JP.UTF-8"

    ;; The same case using `attr`
    > ((attr "," 'join) '("abc" "def" "efg"))
     => "abc,def,efg" 
    > ((attr *os* 'getenv) "LANG" "C")
     => "ja_JP.UTF-8"

  See also: (help invoke* call)"""
  return (getattr(obj, str(message)))(*args)

def invoke_kwd(obj, message, *args):
  """(invoke* OBJ MESSAE PARG ... KWD VAL ...)
  Invokes the OBJ's method named MESSAGE with (PARG ...) as positional and 
  (KWD VAL ...) as keyword arguments.
  MESSAGE ---  `string` or `symbol`.
  KWD     ---  keyword-symbol 
  examples
    > (define *datetime* (attr (import "datetime") 'datetime))
    > (define dt (*datetime* 2011 10 20 14 30 ))
    > dt 
      => 2011-10-20 14:30:00
    > (invoke* dt 'replace 2012 :hour 3 :month 9)
      => 2012-09-20 03:30:00
  See also: (help call) (help invoke)"""
  return call(getattr(obj, str(message)), *args)

def call(func, *args):
  """(call FUNCTION PARG ... KWD VAL ...)
  Calls FUNCTION with (PARG ...) as positional and (KWD VAL ...) as 
 keyword arguments.
  KWD  ---  keyword-symbol
  e.g.
   > (define *datetime* (attr (import "datetime") 'datetime))
   > (*datetime* 2011 11 20)
     => 2011-11-20 00:00:00
   > (call *datetime* 2011 11 20 :minute 30 :hour 14 )  
     => 2011-11-20 14:30:00
   > (call *datetime* :month 11 :day 20 :year 2011 )
     => 2011-11-20 00:00:00
  See also: (help invoke) (help invoke*)"""
  dstart = -1
  dargs = {}
  for i, arg in enumerate(args):
    if isinstance(arg, Keyword):
      dstart = i
      break

  if dstart >= 0:
    dargs = dict(
      (str(args[id-1]), args[id]) for id in xrange(dstart+1, len(args), 2) )
    return func( *args[:dstart], **dargs)
  else:
    return func(*args)

def py_raise(exc, arg=None):
  '''(raise exc . arg=None)
     Raise exception.
     e.g. (raise <NameError> "HiThere")
          => NameError: HiThere'''
  if arg is None: raise exc
  else: raise exc, arg

# def pyhelp(obj):
#   """Syntax: (help obj)\n  equivalent to python's help(obj)"""
#   if isinstance(obj, unicode): obj = obj.encode("utf-8")
#   return help(obj)
  
def py_in(x, y):
  """(in? X Y)
  Same as `X in Y` in Python.
  e.g. 
    > (in? 'c '(a b c)) ;=> #t
    > (in? 'd #(a b c)) ;=> #f
    > (begin (define h (<dict> '(("one" 1) ("two" 2)))) h)
     => {u'two': 2, u'one': 1}
    > (list (in? "two" h)  (in? "three" h)) ;=> (#t #f)"""
  return x in y

def getslice(seq, start, end=None):
  '''(slice SEQ START END)
  Get the slice of SEQ from START to END.
  e.g. (slice #(1 2 3 4) 1 -1)           ;=> #(2 3)
       (slice #(1 2 3 4) #<none> -1)     ;=> #(1 2 3)
       (slice "abcd" 2 #<none>)          ;=> "cd"
  See also: (help slice!) and (help delslice!)'''
  return seq[start:end]

def setslice(seq, start, end, v):
  '''(slice! SEQ START END V)
  Set the slice of SEQ from index START to index END to the sequence V.
  e.g. (slice! #(1 2 3 4) 1 2 #(-2 -3 -4)) ;=> #(1 -2 -3 -4 3 4)
       (slice! #(1 2 3 4) -1 #<none> #(5 6 7)) ;=> #(1 2 3 5 6 7)
  See also: (help slice) and (help delslice!)'''
  seq[start:end] = v
  return seq

def delslice(seq, start, end):
  """(delslice! SEQ START END)
  Delete the slice of SEQ from index START to END.
  e.g. > (delslice! #(1 2 3 4) 1 3 ) ;=> #(1 4)
       > (delslice! #(1 2 3 4) -2 #<none>) ;=> #(1 2)
       ;; The same case using __builtin__ function
       > (let ((v #(1 2 3 4))) 
             (invoke *operator* 'delitem v (<slice> -2 #<none>)) v)
  See also: (help slice) and (help slice!)"""
  operator.delitem(seq, slice(start, end))
  return seq

def is_lambda(proc):
  r'''(lambda? OBJ)
  Returns #t if OBJ is lambda function.
  (if OBJ is Python's function, return #f)
  e.g.
    (lambda? (lambda (x) x)) ;=> #t
    (procedure? (lambda (x) x)) ;=> #t
    (lambda? <open>) ;=> #f
    (procedure? <open>) ;=> #t'''
  return (isinstance(proc, scheme.Closure) and
          not (isinstance(proc, scheme.Macro)) )

@scheme_subr
def to_callable(lisp, _e, proc):
  r'''(@callable PROC)
  Convert Scheme lambda function to Python's callable.
  Example:
  > (<sorted>
     '(Parsley sage rosemary and THYME)
     (@callable
      (lambda (a b)
        (<cmp> (string-upcase (symbol->string a))
               (string-upcase (symbol->string b))))))
   => #(and Parsley rosemary sage THYME)'''
  if isProcedure(proc):
    if callable(proc):
      if scheme.is_scheme_subr(proc):
        # Please use (@callable (lambda args (apply proc args)))
        raise LispCustomError("Sorry, cannot convert %s to python's function" % proc,
                              "@callable")
      return proc
    _e = None
    def pyfunc(*args):
      return (lisp.apply_closure(proc, ScmList.from_iter(args)))[0]
    return pyfunc
  else:
    raise LispWrongTypeOfArgsError("closure function", "@callable",
                                   mkform("@callable", proc))

def sprintf(fmt, *args):
  '''(sprintf fmt . args ...)
     Same as the C sprintf().
     e.g. (sprintf "PI=%0.5f" (* (atan 1) 4)) ;=> \"PI=3.14159\"'''
  def iscnv(obj):
    return any( isinstance(obj, typ)
                for typ in (basestring, list, dict,
                            SymbolBase, Listable, LspChar, bool))
  return( fmt % tuple(scheme.sxp2text(o) if iscnv(o) else o
                      for o in args)  )

# def string_str(string, encoding=u"utf-8"):
#   '''Procedure: (string->str string . encoding="utf-8")
#   Convert string to byte string'''
#   chktype1("string->str", "string",
#            lambda s: isinstance(s, unicode), string)
#   return string.encode(encoding, "replace")

def string2bytes(string, encoding=u"utf-8"):
  '''(string->bytes STRING . ENCODING="utf-8")
  Convert string(`unicode' in python2) to bytes(`str' in python2).
  (If STRING is a bytes, do nothing and return STRING)
  Examples:         
    > (<type> (string->bytes "abc"))
    <type 'str'>
    > (define japanese "\u65e5\u672c\u8a9e")
    > (<type> japanese)
    <type 'unicode'>
    ;; unicode => byte-string
    > (define japanese-euc (string->bytes japanese "euc-jp"))
    > (isa?  japanese-euc <str>)
    #t
    ;; byte-string => unicode
    > (<type> (bytes->string japanese-euc "euc-jp"))
    <type 'unicode'>
    > (equal? (bytes->string japanese-euc "euc-jp") japanese)
    #t
    > 
  See Also: (help bytes->string)'''
  if isinstance(string, unicode):
    return string.encode(encoding, "replace")
  elif isinstance(string, basestring):
    return string
  else: 
    raise LispWrongTypeOfArgsError("string", "string->bytes",
                                   mkform("string->bytes", string))

def bytes2string(bstr, decoding=u"utf-8"):
  '''(bytes->string BYTES . DECODING="utf-8")
  Convert bytes(`str' in python2) to string(`unicode' in python2).
  (If BYTES is a unicode, do nothing and return BYTES)
  Note:
    When DECODING == utf-8, you can use (string-append BYTES) instead.
  Examples:         
    > (<type> (bytes->string (<str> "abc")))
    <type 'unicode'>
    > (define japanese "\u65e5\u672c\u8a9e")
    ;; unicode => byte-string
    > (define japanese-euc (string->bytes japanese "euc-jp"))
    > (<type> japanese-euc)
    <type 'str'>
    ;; byte-string => unicode
    > (<type> (bytes->string japanese-euc "euc-jp"))
    <type 'unicode'>
    > (equal? (bytes->string japanese-euc "euc-jp") japanese)
    #t
    > (define japanese-u8 (string->bytes japanese "utf-8"))
    ;; byte-string => unicode (using string-append)
    > (<type>  (string-append japanese-u8))
    <type 'unicode'>
    > (equal? (string-append japanese-u8) japanese)
    > #t
  See Also: (help string->bytes)'''
  if isinstance(bstr, str):
    return bstr.decode(decoding, "replace")
  elif isinstance(bstr, unicode):
    return bstr
  else: 
    raise LispWrongTypeOfArgsError("<str>", "bytes->string",
                                   mkform("bytes->string", bstr))

import time
def sys_time(): return time.time()
