#-*- coding: utf-8 -*-
# Scheme interpreter in Python.
# Copyright (c) 2012 Tetsu Takaishi.  All rights reserved.
#

from __future__ import division # 11/4 #=> 2.75
import config
if config.isdebug: print "Load scheme as %s" % __name__ #debug

import sys, re, os, math, gc, cmath, operator, StringIO
import mylist
from mylist import Listable,Nil,isPair, List
import traceback

LIZPOP_VERSION = u"0.4.0"

def str2num(s):
  for foo in (int,float,long):
    try:
      return foo(s)
    except ValueError: pass
  return None

class mydict(dict):
  def __getattr__(self,name):return self[name]
  def set(self, name,value):
    "Set name:value, and return value"
    self[name] = value
    return value

def set_return(map,name,value):
  map[name] = value
  return value

def str2rxflag(s):
  "Convert string to regex flags"
  def c2flag(c):
    if(c == "i"): return re.IGNORECASE
    elif(c == "m"): return re.MULTILINE
    elif(c == "s"): return re.DOTALL
    elif(c == "u"): return re.UNICODE
    elif(c == "L"): return re.LOCALE
    elif(c == "x"): return re.VERBOSE
    else: return 0
  return reduce( lambda flg,c: flg | c2flag(c), s, 0)

def rxflag2str(flag):
  s = ""
  if flag & re.IGNORECASE : s += "i"
  if flag & re.MULTILINE : s += "m"
  if flag & re.DOTALL : s += "s"
  if flag & re.UNICODE : s += "u"
  if flag & re.LOCALE : s += "L"
  if flag & re.VERBOSE : s += "x"
  return s

def is_regex(obj, _sample=re.compile("@_@")):
  return isinstance(obj, type(_sample))

def str2rx(pattern, flags=0, _cache={}):
  # if isinstance(flags, (str, unicode))
  if isinstance(flags, basestring) : flags = str2rxflag(flags)
  rx = _cache.get((pattern, flags),None)
  if rx is None:
    rx = re.compile(pattern,flags)    
    _cache[(pattern,flags)] = rx
  return rx

def makepath(parent, subpath):
  return os.path.normpath(os.path.join(parent, subpath))

def isapply_loadpath(path):
  "Is apply *load-path* for (load path) ?"
  # check absolute path
  if os.path.isabs(os.path.normpath(os.path.expanduser(path))):
    return False
  # check ./ or ../
  #   (do not call normpath, normpath trims "." )
  for c in (os.curdir, os.pardir):
    if c:
      if os.sep and path.startswith(c + os.sep):
        return False
      if os.altsep and path.startswith(c + os.altsep):
        return False
  return True

def get_loadpath(path_list, script_path):
  if not isapply_loadpath(script_path):
    script_path = os.path.normpath(os.path.expanduser(script_path))
    if os.path.isfile(script_path):return script_path
    return False
  #
  for path in path_list:
    path = makepath(os.path.expanduser(path), script_path)
    #print "path=",path # debug
    if os.path.isfile(path): return path
  return False

def ascii_upper(s):
  return re.sub(r"([a-z]+)", lambda m:m.group(1).upper(), s)

def ascii_lower(s):
  return re.sub(r"([A-Z]+)", lambda m:m.group(1).lower(), s)

def lsp_string(s):
  if isinstance(s, str): return( s.decode("utf-8", "replace") )
  else: return s

def lsp_string_new(s):
  if isinstance(s, str): return( s.decode("utf-8", "replace") )
  else: return unicode(s)

# ex for Env
#  i = Interpreter(); e = Env(None,[[i.intern("a"),"abc"], [i.intern("b"),"brief"]])
#  u"a" in e #=> False
#  Symbol("a") in e #=> False
#  i.intern("a") in e #=> True
# class Symbol(unicode):  
#   def __eq__(self,other): return self is other
#   def __hash__(self): return id(self) # too slow for dict key !!!
#   def __ne__(self,other): return not self.__eq__(other)
#   def equal(self,other):
#     return (isinstance(other,Symbol) and
#             unicode(self) == unicode(other))
pass # ignore comment when help 
class SymbolBase(object):
  def __init__(self,name): self.name=unicode(name)
  def getname(self): return self.name
  def __len__(self): return self.name.__len__()
  def __str__(self): return self.name.__str__()
  def __unicode__(self): return self.name
#  def __getattr__(self,name):
#    print "send %s to name attribute" % name
#    return getattr(self.name,name)
  
# def intern(name, symbol_table):
#   sym = self.symbol_table.get(name)
#   if sym : return sym
#   return set_return(self.symbol_table, name, Symbol(name))

class Symbol(SymbolBase):
  def equal(self,other):
    return (isinstance(other,Symbol) and
            unicode(self) == unicode(other))

class Keyword(SymbolBase):
  def equal(self,other):
    return (isinstance(other,Keyword) and
            unicode(self) == unicode(other))
  
#class ScmList(Listable):
class ScmList(List):
  r'''Note:
      All elements of ScmList must be a mylist.List object except for
      the termination.'''
  def __init__(self, data, link=Nil):
    self._car = data
    self._cdr = link

  def car(self): return self._car
  def cdr(self): return self._cdr
  def isNil(self): return False
  def setcar(self,data): self._car = data
  def setcdr(self,link): self._cdr = link

  # Use Symbol#equal() method when compare Symbols
  def __eq__(self, other):
    #print "%s's __eq__ called" % self.__class__.__name__ #debug
    if not isinstance(self, type(other)): return False
    alist = self ; blist = other
    while isPair(alist) and isPair(blist):
      if alist is blist : return True   # for circular list
      (acar, bcar) = (alist.car(), blist.car())
      if( (acar == bcar) or
          (isinstance(acar,SymbolBase) and acar.equal(bcar)) ):
        alist = alist.cdr()
        blist = blist.cdr()
      else: return False
    # if isPair(alist) or isPair(blist): return False
    return ( (alist == blist) or
             (isinstance(alist,SymbolBase) and  alist.equal(blist)) )

  def map_p(self, proc):
    top = ScmList(None)
    ret = top; lst = self
    #while lst is not Nil: #
    while isinstance(lst,List):
      ret._cdr =  ScmList(proc(lst._car)) 
      ret = ret._cdr ; lst = lst._cdr
    return top._cdr

  def each(self):
    lst = self
    while isinstance(lst, List):
      yield lst._car
      lst = lst._cdr

  def __len__(self):
    lst = self ; lng = 0
    while isinstance(lst, List):
      lng += 1 ; lst = lst._cdr
    return lng

def scmcar(x):
  if isPair(x): return x.car()
  raise LispWrongTypeOfArgsError("pair", "car", x)

def scmcdr(x):
  if isPair(x): return x.cdr()
  raise LispWrongTypeOfArgsError("pair", "cdr", x)

eof_object = Symbol("#<eof>")
#comment_object = Symbol("#<comment>")
#undef = Symbol("#<undef>")
undef = None
unbind = Symbol("#<unbind>")  # For Env, intern, not binding symbol-table

# e.g.  LspChar(u"#\\u3055") LspChar(u"#\\newline") LspChar(u"#\ ")
class LspChar(object):
  name2int_tab = dict(
    (unicode(k), ord(v) if isinstance(v,basestring) else v) for k,v in
    (("space"," "), ("newline","\n"), ("nl","\n"), ("lf","\n"),
     ("return","\r"), ("cr","\r"), ("tab","\t"), ("ht","\t"),
     ("page","\f"), ("escape","\033"), ("esc", "\x1b"),
     ("delete","\x7f"), ("del", "\x7f"), ("null",0),) )

  int2name_tab = dict( [ (name2int_tab.get(k), k) for k in
                       ("space", "newline","return","tab", "page","escape","delete","null") ])
  @staticmethod
  def name2int(name):
    "e.g. #\space => 32"
    name = unicode(name)
    if not re.match(r"#\\", name):return None
    word = name[2:]
    if len(word) == 1: return ord(word)
    lword = word.lower()
    if lword in LspChar.name2int_tab:
      return LspChar.name2int_tab[lword]
    m = re.match(r"[ux]([0-9a-f]+)",lword)
    if m: return int(m.group(1),16)
    return None
  def __init__(self,name):
    if isinstance(name,basestring):
      val = LspChar.name2int(name)
      if val is None: raise ValueError
    else: val = int(name)
    unichr(val) # test unicode conver, raise ValueError
    self.data = val
  def __hash__(self): return int.__hash__(self.data)
  def __cmp__(self, other): return cmp(self.data, other)
  def __repr__(self):
    if self.data in LspChar.int2name_tab:
      return u"#\\" + LspChar.int2name_tab[self.data]
    elif (31 < self.data) and (self.data < 127 ):
      return u"#\\" + unichr(self.data)
    elif self.data < 256:
      return u"#\\x%02x" % self.data
    elif self.data < 65536: # 2 ** 16
      return u"#\\u%04x" % self.data
    else:
      return u"#\\u%08x" % self.data
  def __unicode__(self): return unichr(self.data)
  #def __str__(self): return unichr(self.data).encode("utf-8")
  
  def is_ascii(self): return self.data < 128

  # These method handles only ascii character
  def is_alphabetic(self, ascii_only=False):
    return (not ascii_only or self.is_ascii()) and unicode(self).isalpha()
  def is_numeric(self,ascii_only=False):
    return (not ascii_only or self.is_ascii()) and unicode(self).isdigit()
  def is_whitespace(self, ascii_only=False):
    return (not ascii_only or self.is_ascii()) and unicode(self).isspace()
  def is_ucase(self, ascii_only=False):
    return (not ascii_only or self.is_ascii()) and unicode(self).isupper()
  def is_lcase(self, ascii_only=False):
    return (not ascii_only or self.is_ascii()) and unicode(self).islower()

  # These method handles only ascii character
  def to_lcase(self, ascii_only=False):
    if (not ascii_only or self.is_ascii()):
      return type(self)( ord( unicode(self).lower() ) )
    else: return type(self)(self.data)
  def to_ucase(self, ascii_only=False):
    if (not ascii_only or self.is_ascii()):
      return type(self)( ord( unicode(self).upper() ) )
    else: return type(self)(self.data)

  def to_i(self): return self.data

#class MultiValue(tuple):  Not use
#  def __str__(self):
#    return "#<values %s>" % tuple.__str__(self)

_mydebug = False

class Env(dict):
  # e.g. e = Env(None, zip(["one","two","three"],[1,2,3]), four=4, five=5)
  def __init__(self, parent, *args, **kwargs):
    self.parent = parent
    dict.__init__(self,*args, **kwargs)
  
  #e.g. 
  # i = Interpreter(); e = Env(None,[[i.intern("a"),"abc"], [i.intern("b"),"brief"]])
  # ee = Env(e); ee[i.intern("c")] = "Cando"
  # ee.lookup(i.intern("a")); ee.lookup(i.intern("c")); ee.lookup(i.intern("d"))
  pass
  def lookup(self,key):
    val = self.get(key,unbind)
    if val is not unbind: return val
    elif self.parent is not None: return self.parent.lookup(key)
    else: return unbind

  def bind(self,key,value): self[key] = value

  def set_d(self,key,value):
    "For scheme set! syntax"
    val = self.get(key,unbind)
    if val is not unbind: self[key] = value
    elif self.parent is None:
      raise LispUnboundError(key)
    else:
      self.parent.set_d(key, value)

  def allkeys(self, acc=[]):
    acc = acc + self.keys()
    if self.parent is None: return acc
    else : return self.parent.allkeys(acc)

  if _mydebug:
    def __setitem__(self,key,value):
      if not isinstance(key, unicode):
        print "Warning: key %s is not unicode" % key
        key = unicode(key, encoding="utf-8")
      dict.__setitem__(self,key,value)

class ScmReportEnv(Env):
  def __init__(self, parent, *args, **kwargs):
    self.frozen = False
    Env.__init__(self, parent, *args, **kwargs)

  def bind(self,key,value):
    if self.frozen:
      raise LispError(
        "This environment is immutable, so `%s' cannot be bound to." % key)
    self[unicode(key)] = value
  def lookup(self,key): return Env.lookup(self,unicode(key))
  def set_d(self,key,value):
    if self.frozen:
      raise LispError("`%s is immutable binding" % key)
    Env.set_d(self, unicode(key), value)

def sxp2text(lspobj,raw=True):
  "Convert Lisp S-expression to unicode text"
  if isinstance(lspobj, SymbolBase):
    if isinstance(lspobj, Keyword):return u":" + lspobj.name
    return lspobj.name
  elif isinstance(lspobj, basestring):
    if raw: return lsp_string(lspobj)
    return (u'"' +
            # unicode(lspobj.encode("utf-8","replace").encode("string_escape"),"utf-8") +
            Interpreter.uni_escape(lsp_string(lspobj)) + 
            u'"')
  elif isinstance(lspobj,ScmList):
    (left, right) = lspobj.split_tail()
    return(u"(" +
           u" ".join( sxp2text(obj,raw) for obj in left) +
           (u")" if right is Nil else " . %s)" % sxp2text(right, raw)) )
#    return ( "(" +
#             " ".join( (sxp2text(obj,raw) for obj in lspobj) ) + ")")
  elif lspobj is Nil: return u"()"
  elif isinstance(lspobj,bool):
    return u"#t" if lspobj else u"#f"
  elif isinstance(lspobj, list):
    return( u"#(" + 
            u" ".join(sxp2text(obj, raw) for obj in lspobj) + u")")
  elif lspobj is None:
    return u"" if raw else u"#<none>"
  elif isinstance(lspobj,LspChar) and (not raw):
    return lspobj.__repr__()
  elif is_regex(lspobj):
    return Interpreter.rxobj2token(lspobj, raw)
  elif isinstance(lspobj, type):
    # Python 2.5, 
    #   if lspobj has __unicode__ method, `unicode( type )` try type.__unicode__()
    return str(lspobj).decode("utf-8")
  else: return unicode(lspobj)

TXT = sxp2text

def trunc(s):
  if len(s) >= 90 : s = s[:81] + " ..."
  return s

def _RAISE(exp): raise (exp)

class LispException(Exception):pass
class LispQuitException(Exception):pass
class LispError(LispException):
  def __init__(self, reason, *options):
    (self.reason, self.options) = (unicode(reason), options)
  def __unicode__(self):
    msg = u"ERROR: " + self.reason
    if self.options:
      msg = (msg + u" - " +
             trunc(u" ".join(TXT(opt, False) for opt in self.options)) )
    return msg
  
class LispCustomError(LispError):
  def __init__(self, reason=u"",  where=u"",  *options):
    (self.reason, self.where, self.options) = (
      unicode(reason), unicode(where), options)
  def __unicode__(self):
    if self.where:
      msg = u"ERROR in %s: %s" % (TXT(self.where), self.reason)
      if self.options:
        msg = (msg + u" - " +
               trunc(u" ".join(TXT(opt, False) for opt in self.options)))
      return msg
    else: return LispError.__unicode__(self)

class LispUnboundError(LispError):
  def __init__(self, symbol, *options):
    LispError.__init__(self,
                       u"Variable %s is not bound" % TXT(symbol,True),
                       *options)

class LispWrongNumberOfArgsError(LispCustomError):
  def __init__(self, where=u"", *options):
    LispCustomError.__init__(self,u"Wrong number of arguments", where, *options)

class LispWrongTypeOfArgsError(LispCustomError):
  def __init__(self, expect=u"",  where=u"", *options):
    reason = "Wrong type of arguments"
    if expect: reason = reason + (u" (expecting %s)" % expect)
    LispCustomError.__init__(self,reason, where, *options)

class LispSyntaxError(LispCustomError):
  def __init__(self, where=u"", *options):
    LispCustomError.__init__(self,u"Invalid Syntax", where, *options)

class LispLoadFileError(LispCustomError):
  def __init__(self, srcname=u"", where=u"load", *options):
    LispCustomError.__init__(self, "'" + srcname + "'", where, *options)

class LispEOFError(EOFError):
  def __init__(self, errmsg=u""):
    self.errmsg = errmsg
  def __unicode__(self):
    return u"ERROR: Unexpected EOF -- " + self.errmsg

class Closure(object):
  #_begin = Symbol(u"#<closure's-begin>") #Must be unintern 
  def __init__(self, vargs, bodies, env):
    # self.vargs = vargs;
    if isinstance(vargs, Listable):
      if vargs is Nil:
        (self.vargs, self.varg_rest) = (Nil, Nil)
        self.bind = self._bind_nil
      else:
        (self.vargs, self.varg_rest) = vargs.split_tail()
        if self.varg_rest is Nil:
          self.bind = self._bind_pure
        else:
          self.bind = self._bind_nopure
    else:
      (self.vargs, self.varg_rest) = (Nil, vargs)
      self.bind = self._bind_sym
    self.lng_vargs = len(self.vargs)

    if isinstance(bodies.car(), basestring) and isPair(bodies.cdr()):
      self._scheme_doc = bodies.car()
      bodies = bodies.cdr()
    #self.body = ScmList(Closure._begin, bodies)
    if bodies.cdr() is Nil:
      self.body = bodies.car()
    else:
      # self.body = ScmList(Boot.intern("begin"), bodies)
      self.body = ScmList(sy_begin, bodies)
    self.env = env

  def _bind_nil(self,rargs):
    if len(rargs) > 0 : raise LispWrongNumberOfArgsError("Closure", rargs)
    return Env(self.env, {})

  def _bind_pure(self,rargs):
    if self.lng_vargs == len(rargs):
      return Env(self.env, zip(self.vargs, rargs))
    raise LispWrongNumberOfArgsError("Closure", rargs)

  def _bind_sym(self,rargs):
    return Env(self.env, {self.varg_rest:rargs})

  def _bind_nopure(self,rargs):
    if self.lng_vargs > len(rargs):
      raise LispWrongNumberOfArgsError("Closure", rargs) # 0.3.2
    e = Env(self.env, zip(self.vargs, rargs))
    e.bind(self.varg_rest, rargs.nthcdr(self.lng_vargs))
    return e

  def _bind_all(self,rargs): # not used now
    "Bind closure vargs to real args, and return new Env"
    if self.varg_rest is Nil:
      if self.vargs is Nil:
        if len(rargs) > 0 : raise LispWrongNumberOfArgsError("Closure", rargs)
        return Env(self.env, {})
      elif self.lng_vargs == len(rargs):
        return Env(self.env, zip(self.vargs, rargs))
      raise LispWrongNumberOfArgsError("Closure", rargs)
    elif self.vargs is Nil:
      return Env(self.env, {self.varg_rest:rargs})
    else:
      if self.lng_vargs > len(rargs):
        raise LispWrongNumberOfArgsError("Closure", rargs) # 0.3.2
      e = Env(self.env, zip(self.vargs, rargs))
      e.bind(self.varg_rest, rargs.nthcdr(self.lng_vargs))
      return e

class Macro(object):pass

class ClosureMacro(Closure, Macro):pass

class PyMacro(Macro):
  def __init__(self, func): self.func = func
  def expand(self, lisp, env, arglist):
    return self.func(lisp, env, arglist)

class Primitive: # Implementation TORIAEZU
  def __init__(self,name): self.name = name
  def __call__(self, *args): return self
  def __str__(self): return "primitive function %s" % self.name

class Syntax(object):
  def __init__(self,name): self.name = name
  def __str__(self): return "#<syntax %s>" % self.name

# Even if evaluates(__call__) these objecs many times, they return themselves. 
p_apply = Primitive("apply") 
_syntax_names = (u"begin", u"if", u"define", u"define-macro", u"lambda",
                 u"quote", u"unquote",u"unquote-splicing",
                 u"or", u"set!",)
(sy_begin, sy_if, sy_define, sy_defmacro, sy_lambda,
 sy_quote, sy_unquote, sy_unquote_splicing,
 sy_or, sy_set,
 ) = (Syntax(name) for name in _syntax_names)
_syntax_dict = dict(
  zip(_syntax_names,
      (sy_begin, sy_if, sy_define, sy_defmacro,sy_lambda,
       sy_quote, sy_unquote, sy_unquote_splicing,
       sy_or, sy_set,
       )))

#e.g.
# [(x,y) for x, y in each_slice(xrange(4))] #=> [(0, 1), (1, 2), (2, 3)]
# [(x,y) for x, y in each_slice(xrange(4),-1)] #=> [(-1, 0), (0, 1), (1, 2), (2, 3)]
# all( (x < y for x,y in each_slice((2,10,13,10,20,22))) )
# Check: yield 10,20... is not executed
def each_slice(iterable, *defaults):
  it = iter(iterable)
  if defaults : x = defaults[0]
  else: x = it.next()
  for y in it:
    #print "yield",y # debug
    yield(x,y);
    x = y
    

def scheme_subr(func):
  "Mark FUNC to call with scheme info"
  func._scheme_subr = True
  return func

def is_scheme_subr(func):
  return hasattr(func, "_scheme_subr")

from inport import InPort
import subr
from subr import makefunc, rqI, rqN
from subr import mkNfunc, mkZfunc
from subr import mkCfunc, mkCfunc_ic
from subr import mkSfunc, mkSfunc_ic, mkSfunc_cnv

import __main__
import __builtin__
import exceptions
class Boot(object):
  symbol_table = {} # symbol's intern table when boot() was run
  scheme_environment = ScmReportEnv(
    None,
    {
      u"apply":p_apply,
      u"and":PyMacro(subr.and_macro),

      u"boolean?":lambda x: isinstance(x, bool),
      u"exact?":lambda x: (not isinstance(x,bool)) and isinstance(x, (int, long)),
      u"inexact?":lambda x:isinstance(x, float),
      u"number?":subr.isnum,  u"integer?":subr.is_integer,
      u"real?":subr.isnum, # MADA toriaezu
      u"zero?":makefunc("zero?", lambda n: n == 0, 1, (rqN,)),
      u"positive?":makefunc("positive?", lambda n: n > 0, 1, (rqN,)),
      u"negative?":makefunc("negative?", lambda n: n < 0, 1, (rqN,)),
      u"even?":subr.evenP, u"odd?":subr.oddP,
      u"max":max, u"min":min,
      #u"+":lambda _,_e,*args:reduce(lambda init,x: x + init, args,0),
      #u"-":lambda _,_e,*args: -args[0] if len(args) == 1 else reduce(lambda init,x: init - x, args),
      u"+":subr.plus, u"-":subr.minus, u"*":subr.asterisk, u"/":subr.slash,
      u"<":lambda *args:all( (x < y for x,y in each_slice(args)) ),
      u">":lambda *args:all( (x > y for x,y in each_slice(args)) ),
      u"<=":lambda *args:all( (x <= y for x,y in each_slice(args)) ),
      u">=":lambda *args:all( (x >= y for x,y in each_slice(args)) ),
      u"=":lambda  *args:all( (x == y for x,y in each_slice(args)) ),
      u"inexact->exact":subr.mkunsp("inexact->exact"),
      u"exact->inexact":subr.mkunsp("exact->inexact"),
      u"string->number":subr.string2number, u"number->string":subr.number2string,
      u"quotient":subr.f_quotient, u"remainder":subr.f_remainder, u"modulo":subr.f_modulo,
      u"gcd":subr.f_gcd, u"lcm":subr.f_lcm,
      u"floor":subr.f_floor, u"ceiling":subr.f_ceiling,
      u"truncate":subr.f_truncate, u"round":subr.f_round,
      u"sqrt":mkZfunc("sqrt",cmath.sqrt,1), u"abs":abs,
      u"exp":mkNfunc("exp", math.exp,1), u"log":subr.f_log,
      u"sin":mkNfunc("sin", math.sin,1), u"asin":mkZfunc("asin", cmath.asin,1),
      u"cos":mkNfunc("cos", math.cos,1), u"acos":mkZfunc("acos", cmath.acos,1),
      u"tan":mkNfunc("tan", math.tan,1), u"atan":mkNfunc("atan", math.atan,1),
      u"expt":mkNfunc("expt", operator.pow,2),

      u"char?":subr.ischar,
      u"char=?":mkCfunc("char=?",operator.eq, 2),
      u"char<?":mkCfunc("char<?",operator.lt, 2), u"char<=?":mkCfunc("char<=?",operator.le, 2),
      u"char>?":mkCfunc("char>?",operator.gt, 2), u"char>=?":mkCfunc("char>=?",operator.ge, 2),
      u"char-ci=?":mkCfunc_ic("char-ci=?",operator.eq, 2),
      u"char-ci<?":mkCfunc_ic("char-ci<?",operator.lt, 2),
      u"char-ci<=?":mkCfunc_ic("char-ci<=?",operator.le, 2),
      u"char-ci>?":mkCfunc_ic("char-ci>?",operator.gt, 2),
      u"char-ci>=?":mkCfunc_ic("char-ci>=?",operator.ge, 2),
      u"char-alphabetic?":mkCfunc("char-alphabetic?", LspChar.is_alphabetic, 1),
      u"char-numeric?":mkCfunc("char-numeric?", LspChar.is_numeric, 1),
      u"char-whitespace?":mkCfunc("char-whitespace?", LspChar.is_whitespace, 1),
      u"char-upper-case?":mkCfunc("char-upper-case?", LspChar.is_ucase, 1),
      u"char-lower-case?":mkCfunc("char-lower-case?", LspChar.is_lcase, 1),
      u"char->integer":mkCfunc("char->integer", LspChar.to_i, 1),
      u"integer->char":makefunc("integer->char", LspChar, 1, (rqI,)),
      u"char-upcase":mkCfunc("char-upcase", LspChar.to_ucase,1),
      u"char-downcase":mkCfunc("char-downcase", LspChar.to_lcase,1),

      u"string?":lambda obj: isinstance(obj, unicode),
      u"make-string":lambda k, ch=LspChar("#\space"): unicode(ch)[0] * k, # Not R5RS
      u"string":lambda *args: subr.list_to_string(args),
      u"string-length":mkSfunc(u"string-length", len, 1), u"string-ref":subr.string_ref, 
      u"string-set!":subr.mkunsp("string-set!"), # string-set! is not supported
      u"string=?":mkSfunc("string=?", operator.eq, 2),
      u"string<?":mkSfunc("string<=?", operator.lt, 2), u"string<=?":mkSfunc("string<=?", operator.le, 2),
      u"string>?":mkSfunc("string>=?", operator.gt, 2), u"string>=?":mkSfunc("string>=?", operator.ge, 2),
      # u"string-ci=?":subr.mkSfunc2_ic("string-ci=?", operator.eq),
      u"string-ci=?":mkSfunc_ic("string-ci<=?", operator.eq,2),
      u"string-ci<?":mkSfunc_ic("string-ci<=?", operator.lt,2),
      u"string-ci<=?":mkSfunc_ic("string-ci<=?", operator.le, 2),
      u"string-ci>?":mkSfunc_ic("string-ci>=?", operator.gt, 2),
      u"string-ci>=?":mkSfunc_ic("string-ci>=?", operator.ge, 2),
      u"substring":subr.substring, u"string-append":subr.string_append,
      # string-copy: for compatibility only, string is immutable
      u"string-copy":mkSfunc("string-copy", lsp_string_new,1), #for compatibility only
      u"string-fill!":subr.mkunsp("string-fill!"), # string-fill! is not supported
      u"string->list":subr.string_to_list, u"list->string":subr.list_to_string,
      u"string-upcase":mkSfunc_cnv("string-upcase", unicode.upper,1), #not R5RS
      u"string-downcase":mkSfunc_cnv("string-downcase", unicode.lower,1), #not R5RS
      u"length":len,
      u"list":lambda *args:ScmList.from_iter(args),  
      u"cons":ScmList,
      u"null?":lambda x: x is Nil,
      u"pair?":lambda x: isinstance(x,ScmList), 
      u"list?":mylist.isProperList,
      #u"car":lambda _,_e,x:
      #  _RAISE(LispWrongTypeOfArgsError("pair", "car")) if x is Nil else x.car(),
      #u"cdr":lambda _,_e,x:
      #  _RAISE(LispWrongTypeOfArgsError("pair", "cdr")) if x is Nil else x.cdr(),
      u"car":scmcar, u"cdr":scmcdr,
      u"cadr":lambda x: x.ref(1), u"cddr":lambda x: x.nthcdr(2),
      u"caar":lambda x: scmcar( scmcar(x) ),
      u"cdar":lambda x: scmcdr( scmcar(x) ),
      u"set-car!":subr.setcar, u"set-cdr!":subr.setcdr,
      u"list-ref":lambda lst, n: lst.ref(n), 
      u"list-tail":lambda lst, n: lst.nthcdr(n), 
      u"append":subr.list_append, u"append!":subr.list_nconc,
      u"reverse":subr.list_reverse, u"reverse!":lambda lst: lst.nreverse(), 
      u"make-list":lambda k, fill=None: ScmList.from_iter([fill] * k),  # Not R5RS
      u"memq":lambda obj,lst: subr.member(obj,lst),
      u"memv":lambda obj,lst: subr.member(obj,lst, subr.eqv, "memv"),
      u"member":lambda obj,lst: subr.member(obj,lst, subr.equal, "member"),
      u"assq":lambda obj,alst: subr.assoc(obj,alst),
      u"assv":lambda obj,alst: subr.assoc(obj,alst, subr.eqv),
      u"assoc":lambda obj,alst: subr.assoc(obj,alst, subr.equal),
      u"procedure?":subr.isProcedure,
      u"map":subr.mapcar,
      u"for-each":subr.foreach,
      u"it->list":ScmList.from_iter, #NOT R5RS
      u"delete!":subr.delete, #Not R5RS
      u"list-copy":subr.list_copy, #Not R5RS (SRFI-1)

      u"eq?":lambda x,y: x is y,  
      u"equal?":subr.equal,
      u"eqv?":subr.eqv,
      u"not":lambda x: x is False,
      u"symbol?":lambda x: isinstance(x,Symbol),
      u"symbol->string":lambda s: unicode(s), # MADA: must be immutable string 
      u"string->symbol":scheme_subr(lambda lisp,_e, s: lisp.intern(s)), # MADA: error check
      u"vector?":lambda x: isinstance(x,list), 
      u"vector->list":ScmList.from_iter,
      u"list->vector":list,
      u"make-vector":lambda k, fill=None: [fill] * k,
      u"vector":lambda *args: list(args), u"vector-length":subr.vector_length,
      u"vector-ref":subr.vector_ref, u"vector-set!":subr.vector_set,
      u"vector-fill!":subr.vector_fill,

      u"port?":subr.is_port,
      u"input-port?":lambda p: isinstance(p, InPort),
      u"output-port?":subr.is_outport,
      u"eof-object?":lambda o: o is eof_object,
      u"current-input-port":scheme_subr(lambda lsp,_e: lsp.inport),
      u"current-output-port":scheme_subr(lambda lsp,_e: lsp.outport),
      u"current-error-port":scheme_subr(lambda lsp,_e: lsp.errport),
      u"call-with-input-file":subr.call_with_infile,
      u"call-with-output-file":subr.call_with_outfile,
      u"with-input-from-file":subr.with_infile,
      u"with-output-to-file":subr.with_outfile,
      u"with-error-to-file":subr.with_errfile,
      u"with-input-from-port":subr.with_inport,
      u"with-output-to-port":subr.with_outport,
      u"with-error-to-port":subr.with_errport,
      u"open-input-file":lambda name: subr.open_infile(name),
      u"open-output-file":lambda name, mode="w": subr.open_outfile(name, mode),
      u"close-input-port":subr.close_inport, u"close-output-port":subr.close_outport,
      u"read":scheme_subr(lambda lsp,_e, p=None: lsp.read(p)),
      u"write":scheme_subr(lambda lsp,_,o,p=None: lsp.write(o,p)),
      u"display":scheme_subr(lambda lsp,_,o,p=None: lsp.disp(o,p)),
      u"newline":
        scheme_subr(lambda lsp,_,p=None:(lsp.outport if p is None else p).write("\n")),
      u"write-char":subr.write_char,
      u"read-char":scheme_subr(lambda lsp,_e, p=None: lsp.read_char(False, p)),
      u"peek-char":scheme_subr(lambda lsp,_e, p=None: lsp.read_char(True, p)),
      u"char-ready?":scheme_subr(lambda lsp,_e, p=None, tmout=0: lsp.is_char_ready(p, tmout)),
      u"format":subr.cl_format,  u"read-line":subr.read_line, # NOT R5RS

      u"call-with-current-continuation":subr.call_cc, u"call/cc":subr.call_cc, 
      u"values":subr.values, ### u"call-with-values":subr.call_values,
      u"interaction-environment":subr.interaction_env,
      u"built-in-environment":subr.builtin_env, #NOT R5RS
      u"current-environment":subr.current_env,  #NOT R5RS
      u"null-environment":subr.mkunsp("null-environment"), 
      u"scheme-report-environment":subr.mkunsp("scheme-report-environment"),
      u"eval":subr.scheme_eval,

      u"error":subr.error, u"load":subr.load, 
      u"load-eml":subr.load_embedded,
      u"debug":subr.debugging, u"bound?":subr.boundp, #NOT R5RS
      u"*<try-finally>*":subr.try_finally, u"*<try-catch>*":subr.try_catch,
      u"quit":lambda : _RAISE(LispQuitException), #Not R5RS
      u"lambda?":subr.is_lambda, #Not R5RS

      u"regex?":lambda x: is_regex(x),
      u"string->regex":subr.string2regex,
      u"re-match":subr.re_match, u"re-search":subr.re_search,
      u"re-split":subr.re_split, u"re-findall":subr.re_findall,
      u"re-finditer":subr.re_finditer,
      u"re-escape":lambda s: re.escape( lsp_string(s)),
      u"re-group":subr.re_group, u"re-groups":subr.re_groups,
      u"re-group-list":subr.re_group_list, # u"re-group-length":lambda rx: rx.groups,
      u"re-group-assoc":subr.re_group_assoc,
      u"re-start":subr.re_start, u"re-end":subr.re_end,

      u"keyword?":lambda x: isinstance(x,Keyword),
      u"string->keyword":scheme_subr(lambda lisp,_e, s: lisp.intern_kwd(s)),
      u"keyword->string":lambda s: unicode(s),
      u"get-keyword":subr.get_keyword, u"set-keyword!":subr.set_keyword,
      u"add-keyword!":subr.add_keyword, u"delete-keyword!":subr.delete_keyword,

      u"flush":subr.flush_port,
      u"exit":lambda arg=0: sys.exit(arg),
      ### u"pyeval":eval,
      u"exec":subr.py_exec,
      #### u"py-globals":globals,  u"py-locals":locals,
      u"import":__import__,
      u"attr":subr.attr, u"attr!":subr.set_attr, 
      u"attr?":lambda o,x: hasattr(o, unicode(x)),
      u"invoke":subr.invoke,  u"invoke*":subr.invoke_kwd, 
      u"call":subr.call,
      ### u"call":lambda func, *args: func(*args), 
      u"in?":subr.py_in,
      ### u"bltin":subr.bltin,
      u"isa?":isinstance, u"raise":subr.py_raise, 
      # u"item":subr.item, u"item!":subr.setitem,
      u"item":operator.getitem, u"item!":operator.setitem, u"delitem!":operator.delitem,
      u"slice":subr.getslice, u"slice!":subr.setslice, u"delslice!":subr.delslice,
      u"@callable":subr.to_callable, u"none?":lambda x: x is None,
      u"@gc":lambda : gc.collect(),
      u"sys-time":subr.sys_time,  u"sprintf":subr.sprintf, u"gensym":subr.gensym,
      #u"string->str":subr.string_str,
      u"string->bytes":subr.string2bytes, u"bytes->string":subr.bytes2string,
      
      u"*builtin*":__builtin__, u"*sys*":sys, u"*os*":os, u"*math*":math,
      u"*re*":re, u"*operator*":operator, u"*scheme*":subr.scheme_module(),

      u"*version*":LIZPOP_VERSION,

      u"symbol-keys": scheme_subr(lambda lsp,env: lsp.toplevel_env.allkeys()), # for debug

      # u"unset!":lambda lisp,env,text: env.__delitem__(lisp.intern(text)),  #debug
      }
    )

  # add syntax to scheme_environment
  scheme_environment.update(_syntax_dict) 

  # bind __builtin__ type to <typename>
  #scheme_environment.update(
  #  (u"<" + key + u">", val) for key, val in 
  #  filter(lambda (k,v) : isinstance(v,type), vars(__builtin__).items())  )

  # bind exceptions to <exceptions-name>
  #scheme_environment.update(
  #  (u"<" + key + u">", val) for key, val in 
  #  filter(lambda (k,v) : isinstance(v,type) and issubclass(v, BaseException),
  #         exceptions.__dict__.items() )  )

  # bind all __builtin__ var to <var>
  scheme_environment.update(
    (u"<" + key + u">", val) for key, val in vars(__builtin__).items())

  # bind lisp exceptions to <exceptions-name>
  scheme_environment.bind(u"<LispError>", LispError)

  @classmethod
  def intern(klass,name):
    sym = klass.symbol_table.get(name,None) # better?? None -> unbind 
    if sym is not None: return sym # better?? None -> unbind 
    return set_return(klass.symbol_table, name, Symbol(name))

  @staticmethod
  def boot(force=False, extsources=[]): # Call this the first time only
    if Boot.scheme_environment.frozen and not force:
      raise UserWarning("Already booted")
    Boot.dir = os.path.dirname( os.path.abspath(__file__) ) 
    bootsrc = os.path.join(Boot.dir,"boot.scm")
    srclist = [bootsrc] + extsources
    lisp = Interpreter(isboot=True)
    Boot.symbol_table = lisp.symbol_table
    Boot.scheme_environment.frozen = False
    # Make extra document
    import defdoc
    defdoc.make()
    Boot.scheme_environment.bind(u"*lizpop-defdoc*", defdoc)
    # Read booting scheme sources
    for src in srclist:
      if os.path.isfile(src):
        rport = None
        try:
          rport = InPort(open(src, "r"))
          # read boot.scm
          lisp.repl(prompt=None, toplevel=Boot.scheme_environment,
                    readport=rport)
        finally:
          if rport: rport.close() # No need? GC will close
      else:
        sys.stderr.write("WARNING: Booting source(%s) is not find\n" % src)
    lisp = None # need?
    # Freeze scheme_environment
    Boot.scheme_environment.frozen = True
# End of Boot define 

class Interpreter(object):

  # INPORT, OUTPORT, and ERRPORT are default of (current-input-port), 
  # (current-output-port), (current-error-port).
  # If these value are None, these will be bound to stdin, stdout, 
  # and stderr.
  def __init__(self, inport=None, outport=None, errport=None, isboot=False):
    self.symbol_table = {}
    self.kwdsym_table = {}
    self.interaction_env = Env(Boot.scheme_environment)
    self.toplevel_env = self.interaction_env
    # self.current_env = self.interaction_env
    self.gensym_seed = 0

    if not inport :
      # self.inport = InPort( codecs.getreader("UTF-8")(sys.stdin, errors="replace") )
      self.inport = InPort(sys.stdin)
    elif isinstance(inport, basestring) :
      # self.inport = InPort( codecs.open(inport,"r", encoding='UTF-8', errors="replace") )
      self.inport = InPort( open(inport,"r") )
    elif isinstance(inport, InPort): self.inport = inport
    else: self.inport = InPort(inport)

    if not outport:
      self.outport = sys.stdout
    elif isinstance(outport, basestring) :
      self.outport = open(outport,"w")
    else: self.outport = outport

    if not errport:
      self.errport = sys.stderr
    elif isinstance(errport, basestring) :
      self.errport = open(errport,"w")
    else: self.errport = errport

    self.quotes_table = {
      u"'":self.intern("quote"), u"`":self.intern("quasiquote"),
      u",":self.intern("unquote"), u",@":self.intern("unquote-splicing")}

    if not isboot:
      # bind self to *interpreter* 
      self.bind_toplevel("*interpreter*", self)
      # bind *load-path*
      loadpath = ["."]
      if "LIZPOP_LOAD_PATH" in os.environ:
        loadpath = os.environ["LIZPOP_LOAD_PATH"].split(os.pathsep)
      self.bind_toplevel("*load-path*", ScmList.from_iter(loadpath))
      #self.toplevel_env.bind(self.intern("*load-path*"),
      #                       ScmList.from_iter(loadpath))

  def intern(self,name):
    sym = self.symbol_table.get(name, None)  # better?? None -> unbind 
    if sym is not None: return sym  # # better?? None -> unbind 
    return set_return(self.symbol_table, name, Symbol(name))

  def intern_kwd(self,name):
    kwd = self.kwdsym_table.get(name, None) # better?? None -> unbind 
    if kwd is not None: return kwd # better?? None -> unbind 
    return set_return(self.kwdsym_table, name, Keyword(name))

  def bind_toplevel(self, key, value): # key is string or symbol
    if not isinstance(key, Symbol): key = self.intern(key)
    self.toplevel_env.bind(key, value)

  def lookup_toplevel(self, key, default=unbind):
    "For accessing from python code"
    if not isinstance(key, Symbol): key = self.intern(key)
    ret = self.toplevel_env.lookup(key)
    if ret is unbind: return default
    else: return ret

  def write(self, lspobj, port=None):
    if port is None: port = self.outport
    port.write(sxp2text(lspobj,False).encode("utf-8", "replace"))

  def write_nl(self, lspobj, port=None):
    self.write(lspobj, port)
    (self.outport if port is None else port).write("\n"),

  def disp(self, lspobj, port=None):
    if port is None: port = self.outport
    port.write(sxp2text(lspobj).encode("utf-8","replace"))

  def disp_nl(self, lspobj, port=None):
    self.disp(lspobj, port)
    (self.outport if port is None else port).write("\n"),

  def read_char(self, peep=False, port=None):
    if port is None: port = self.inport
    ch = port.get_char(peep)
    if ch == u"" : return eof_object
    return LspChar(ord(ch))

  def is_char_ready(self, port=None, timeout=0):
    if port is None: port = self.inport
    return port.isready(timeout)

  @staticmethod
  def uni_unescape(s):
    "Decode escape sequence in S(unicode), and return decoded unicode string"
    return re.sub(r'[\040-\176]+', lambda m:m.group(0).decode("unicode_escape"), s)

  # Check unicode_escape
  if u'\'"\n\t\\\u3055'.encode("unicode_escape") != '\'"\\n\\t\\\\\\u3055':
    raise AssertionError

  @staticmethod
  def uni_escape(s):
    "S(unicode) =>  escape sequence unicode"
    s = s.encode("unicode_escape").decode("utf-8")
    return re.sub('"', r'\"', s, 0)

  def read(self,port=None):
    if port is None: port = self.inport
    try:
      return self.read_token(port, None) 
    except EOFError, eof: 
      if isinstance(eof, LispEOFError):
        if self.outport:
          self.outport.write(unicode(eof) + "\n")
      return eof_object

  def read_list(self, port, list_ahead, dot_ahead, isvec=False):
    try:
      while True:
        token = port.get_token()
        # if token == u";": continue
        if token == u")":
          if isvec: return list_ahead
          else: return list_ahead.nreverse(dot_ahead)
        elif dot_ahead is not Nil:
          raise LispCustomError("Expected ')', but got %s" % token, "reader")
        elif token == ".":
          if isvec: raise LispCustomError("Unexpected dot", "reader")
          dot_ahead = self.read_token(port)
        elif isvec:
          list_ahead.append(self.read_token(port, token))
        else:
          list_ahead = ScmList(self.read_token(port, token), list_ahead)
    except EOFError, eof:
      if not isinstance(eof,LispEOFError):
        if isvec: raise LispEOFError("reading vector literal")
        else: raise LispEOFError("reading list literal")
      else : raise eof

  def read_token(self, port, token=None):
    if token is None : token = port.get_token()
    if token == u"(": return self.read_list(port,Nil,Nil)
    elif token == u"#(": return self.read_list(port,list(),Nil,True)
    elif token == u")": raise LispSyntaxError("reader", "Unexpected ')'")
    elif token == u".": raise LispSyntaxError("reader", "unexpected dot")
    # elif token == u";": return comment_object
    elif token in self.quotes_table:
      return ScmList.make(self.quotes_table[token], self.read_token(port,None))
    return self.token2atom(token)

  sharp_constants = {"t":True, "T":True, "f":False, "F":False,
                     # "<eof>":eof_object,
                     "<none>":None, "<undef>":None,}
  def token2atom(self,token):
    if token[0] == u'"': 
      #return unicode(token[1:-1].encode("utf-8", "replace").decode("string_escape"),"utf-8")
      return Interpreter.uni_unescape(token[1:-1])
    elif token[0] == u'#':
      if token[1:] in Interpreter.sharp_constants:
        return Interpreter.sharp_constants[token[1:]]
      #if token == "#t" or token == "#T": return True
      #elif token == "#f" or token == "#F": return False
      elif token[1] == "/":  # #/regex/ token
        return Interpreter.token2rxobj(token)
      elif token[1] == "\\": # character token 
        try: return LspChar(token)
        except ValueError:
          raise LispSyntaxError("reading character literal", token)
      elif token.startswith('#"""'): # non escape string (for embedded scheme)
        return token[4:-3]
      else: raise LispSyntaxError("reading # prefix literal", token)
    elif token[0] == u":": # keyword
      #if token[1] == u"|"  # index error when ":"
      if token.startswith(u'|',1) : # vertical bar keyword atom
        s = re.sub(r'\\\|',  "|", token[2:-1])
        return self.intern_kwd(Interpreter.uni_unescape(s))
      return self.intern_kwd(token[1:])
    elif token[0] == u'|': # vertical bar symbol atom
      s = re.sub(r'\\\|',  "|", token[1:-1])
      return self.intern(Interpreter.uni_unescape(s))
    else:
      num = str2num(token)
      if num is not None: return num
    # Symbol atom
    return self.intern(token)

  @staticmethod
  def escape_regex(s):
    "Escape regex pattern string, for using lisp writer"
    def _escape(ch):
      code = ord(ch)
      if 31 < code and code < 127:
        if ch == u"/": return u"\\/"
        return ch
      elif code < 256: # when control code
        return u"\\x%02x" % code
      else:            # when 2 byte
        return u"\\u%04x" % code
    return u"".join( _escape(ch) for ch in s )

  @staticmethod
  def unescape_regex(s):
    "Unescape regex pattern string, for using lisp reader"
    s = re.sub(r"\\/", "/", s)  # convert \/ to /
    # convert \uHHHH -> unicode
    def _convert(m):
      bs = m.group(1)
      if (len(bs) % 2) == 0: return m.group(0) # when len(\ sequence) is even
      # return bs[0:-1] + (u"\\u" + m.group(2)).decode("unicode_escape")
      return bs[0:-1] + unichr(int(m.group(2), 16))
    s = re.sub(r'(\\+)u([0-9A-Fa-f]{4})', _convert, s)
    return s
    
  @staticmethod
  def token2rxobj(token):
    "regex toke => regex object"
    lastslash = token.rfind(u"/")
    if lastslash >= 2:
      # pattern = re.sub(r"\\/", "/", token[2:lastslash])
      pattern = Interpreter.unescape_regex(token[2:lastslash])
      flag = str2rxflag( token[lastslash+1 : ] )
      return re.compile(pattern, flag)
    else:
      raise LispCustomError("Program Error", "token2rxobj")

  @staticmethod
  def rxobj2token(rxobj, raw=True):
    pattern = lsp_string( rxobj.pattern )
    #if not raw: pattern = Interpreter.uni_escape(pattern)
    if raw:
      # only \ escape when raw mode display
      pattern = re.sub("/", r"\/", pattern)
    else: 
      pattern = Interpreter.escape_regex(pattern)
    return u"#/" + pattern + u"/" + rxflag2str(rxobj.flags)

  def eval(self, exp, env):
    while True:
      if isinstance(exp, Symbol): # Symbol
        v = env.lookup(exp)
        if v is not unbind:return v
        raise LispUnboundError(exp)
      elif not isinstance(exp, ScmList): # numeric, string, bool, nil, None ...
        return exp

      # ScmList object
      top = exp.car(); rest = exp.cdr(); 
      if isinstance(top, Syntax): # (#<syntax-xx>  ....)
        if top is sy_begin:   # begin
          while rest.cdr() is not Nil:
            self.eval(rest.car(), env)
            rest = rest.cdr()
          exp = rest.car()  
          continue
        elif top is sy_quote: return(rest.car()) # quote
        elif top is sy_if:      # if
          exp = exp.cdr()
          if self.eval(rest.car(), env) is not False:
            exp = rest.cdr().car()
          else: exp = rest.ref(2)
          continue  # For tail recursive
        elif top is sy_lambda: # (lambda arg b b2 ...)
          return Closure(rest.car(), rest.cdr(), env)
        elif top is sy_define:  # define
          sym = rest.car()
          env.bind(sym, self.eval(rest.ref(1), env))
          return None
        elif top is sy_or:      # (or ...)
          while rest.cdr() is not Nil:
            retval = self.eval(rest.car(), env)
            if retval is not False : return retval
            rest = rest.cdr()
          exp = rest.car() 
          continue # for tail recursive
        elif top is sy_set:    # (set! sym value)
          sym = rest.car()
          #if isinstance(sym, Symbol): # better to expander?? MADA
          env.set_d(sym, self.eval(rest.ref(1), env))
          return None
          #else: raise LispSyntaxError("eval",exp)
        else: raise LispSyntaxError("eval",exp)
      # end of if-Syntax

      func = unbind
      if isinstance(top,Symbol): # (symbol ....)
        func = env.lookup(top) # symbol eval
        if func is unbind:
          raise LispUnboundError(top)

      # (function ...) or ((lambda () ...) ...)
      if func is unbind: func = self.eval(top,env) # when top != symbol
      #func = self.eval(top,env) # eval top of scheme-list
      # eval all arguments
      # rargs = ScmList.from_iter((self.eval(body, env) for body in rest)) #v0.3.1
      # rargs = ScmList.from_iter([self.eval(body, env) for body in rest]) #v0.3.2
      #rargs = rest.map(lambda body: self.eval(body, env)) # v0.3.2
      rargs = rest.map_p(lambda body: self.eval(body, env)) # v0.3.2
      if func is p_apply:
        while True:
          func = rargs.car()
          rargs = rargs.ref(1)
          if func is not p_apply: break
      if isinstance(func, Closure):  # apply closure
        #if isinstance(func, Macro) and not expanding:
        # sxpRaise(topval,LispInvalidProcedure)
        if isinstance(func, ClosureMacro):
          raise LispCustomError("Invalid procedure", "eval", exp)
        (exp, env) = (func.body, func.bind(rargs))
        # if exp is None: return undef # IRANAI? 
      elif callable(func):           # python function
        if is_scheme_subr(func):
          return func(self,env,*rargs)
        else:
          return func(*rargs)
      else: raise LispSyntaxError("eval", exp)

  #def apply_dynamic(self, closure, rargs, parent_env): #
  # CAUTUION: Not use this in self.eval !!!
  def apply_closure(self, closure, rargs):
    """apply closure with real-arglist and return (eval-value, new-env)"""
    env = closure.bind(rargs)
    #if body is Nil: return(None, env) # did in eval(), No use,
    return (self.eval(closure.body, env), env)

  def apply(self, env, func, rargs):
    if func is p_apply:
      while True:
        func = rargs.car()
        rargs = rargs.ref(1)
        if func is not p_apply: break
    if isinstance(func, Closure):  # apply closure
      return self.apply_closure(func, rargs)
    elif callable(func):           # python function
      if is_scheme_subr(func):
        return (func(self,env,*rargs),env)
      else:
        return (func(*rargs),env)
    else: raise LispCustomError("%s is not callable" % sxp2text(func),
                                "Interpreter#apply")

  def macro_expand(self, form, env):
    def expand_forms(formlist,ev):
      if isPair(formlist):
        return formlist.map(lambda fm: self.macro_expand(fm,ev) )
      else:
        return Nil

    ## Not try below yet,
    ##   because,  > (define a if) > (begin (define a 100) a) ;-> <syntax if> 
    # if isinstance(form, Symbol):
    #  v = env.lookup(form)
    #  if isinstance(v, Syntax): return v
    #  return form

    if not isinstance(form, ScmList): return form
    top = form.car()
    if isinstance(top,Symbol): # (symbol ....)
      topval = env.lookup(top) # symbol eval
      if isinstance(topval, (Syntax, Macro)):
        form = ScmList(topval, form.cdr()) # goto syntax processing
      else:
        rest = expand_forms(form.cdr(), env)
        return ScmList(top, rest)
    # end of Symbol

    top = form.car(); rest = form.cdr(); 
    if isinstance(top, Syntax):
      if top is sy_if:        # (if test e1 e2)
        length = rest.length(4)  # rest.length(maximum=4)
        if length == 2 :
          rest = ScmList.append(rest, ScmList(undef) ) # when (if test e1)
        elif length != 3 :
          raise LispWrongNumberOfArgsError("expander", form)
        return ScmList(top, expand_forms(rest, env))

      elif top is sy_quote: return form   # (quote xxx)
      elif top is sy_set:   # (set! sym val) 
        if rest.length(3) != 2:
          raise LispWrongNumberOfArgsError("expander",form)
        if not isinstance(rest.car(), Symbol):
          raise LispSyntaxError("expander", form)
        return ScmList(top, ScmList(rest.car(), expand_forms(rest.cdr(),env)))

      elif (top is sy_define or
            top is sy_defmacro) : # (define ..) or (define-macro)
        if isinstance(rest.car(), ScmList):
          # (define (foo x y) b ...) => 
          # (define f (lambda (x y) b ...))
          form = ScmList(top,
                         ScmList(rest.car().car(),
                                 ScmList( ScmList(sy_lambda,
                                                  ScmList(rest.car().cdr(), rest.cdr())) ) ))
          # form.setcdr( ScmList(rest.car().car(),
          #                      ScmList( ScmList(self.intern("lambda"),
          #                                      ScmList(rest.car().cdr(), rest.cdr())) ) ))
          rest = form.cdr()
          #print "define convert to %s" % sxp2text(form,False) # debug
        if rest.length(3) != 2:
          raise LispWrongNumberOfArgsError("expander",form)
        if not isinstance(rest.car(), Symbol):
          raise LispSyntaxError("expander", form)
     
        if top is not sy_defmacro: # when define
          return ScmList(top, ScmList(rest.car(), expand_forms(rest.cdr(),env)))
        # when define-macro, register macro
        if env is not self.toplevel_env:
          # define-macro must be on toplevel environment
          raise LispCustomError("define-macro must be on toplevel environment",
                                "expander", form)
        lambbody =  expand_forms(rest.cdr(),env)
        (sym,lamb) = (rest.car(), lambbody.car())
        env.bind(sym,ClosureMacro(lamb.ref(1), lamb.cdr().cdr(), env))
        return undef

      elif (top is sy_begin and rest is Nil):  # (begin) => (begin undef)
        return undef

      elif (top is sy_lambda):    # (lambda (p ...) body body2 ...)
        if rest.length(2) < 2 : raise LispSyntaxError("expander",form)
        (param, bodies) = (rest.car(), rest.cdr())
        if isinstance(param, ScmList): 
          # MADA dot pair 
          if not all( (isinstance(p,Symbol) for p in param ) ):
            raise LispSyntaxError("expander", form)
        elif not (isinstance(param, Symbol) or param is Nil):
          raise LispSyntaxError("expander",form)
        # make dummy closure for (lambda (begin,if) ...)
        dmylamb = Closure(param, Nil, env)
        dmyenv = dmylamb.bind(ScmList.from_iter([True] * len(param))
                              if isinstance(param,ScmList) else Nil)
        #can be replaced??  MADA
        # dmyenv = dmylamb.bind(param if isinstance(param,ScmList) else Nil)
        return ScmList(top, ScmList(rest.car(), expand_forms(bodies, dmyenv)))

      elif top is sy_or and rest is Nil:   #(or) => #f
        return False

      elif top is sy_unquote or top is sy_unquote_splicing:
        # outside quasiquote
        raise LispCustomError(u"`%s` appeared outside quasiquote" % top.name,
                               u"macro expander", form)
      return ScmList(top, expand_forms(form.cdr(), env))
    # end-of if-Symbol

    if isinstance(top, Macro):   # Expand (macro arg ....)
      if not mylist.isProperList(rest):
        raise LispCustomError(u"Macro argument must be proper list" ,u"expander", rest)
      if isinstance(top, ClosureMacro):
        #print "macro-in:",sxp2text(top,False) # macro debug
        (form, _ev) = self.apply_closure(top, rest)
        #print "macro-out:",sxp2text(form,False) # macro debug
        # (virtial-args is macro-name, syntax-name) and (recursive macro) MADA
        # Tail recursion optimization?? MADA
        return self.macro_expand(form,env)
      else: # When PyMacro(python macro)
        return self.macro_expand(top.expand(self, env, rest), env)

    return form.map(lambda exp: self.macro_expand(exp,env))
    
  def error_out(self, err, exctype, value):
    if self.errport:
      if isinstance(err, LispException):
        self.errport.write(unicode(err).encode("utf-8","replace") + "\n")
      else:
        self.errport.write(exctype.__name__ + ": " +  str(value) + "\n")
    
  # READPORT must be <file> or <InPort> or None
  # If READPORT is None , READPORT is bound to self.inport.
  # WRITEMODE:
  #   True  ---- The result will be outputted using (write ...)
  #   "raw" ---- The result will be outputted using (display ...)
  #   False ---- No result will be outputted
  #   default 
  #     writemode = True if PROMPT or (PROMPT == ""),  else False
  # ERRQUIT 
  #   True --- if some error occurred then print the error and re-raise this error
  #   False -- if some error occurred then print the error and continue REPL
  # If TOPLEVEL is None, (interaction-environment) will be used
  def repl(self,prompt=False, toplevel = None, readport = None,
           writemode = None, errquit=False):
    if toplevel is not None:
      self.toplevel_env = toplevel

    if readport is None:
      readport = self.inport
    # elif isinstance(readport, basestring): open(..) #=> how close?, realy GC will close?
    # elif isinstance(readport, file) #=> codecs.getreader() is not file
    elif not isinstance(readport, InPort): 
      readport = InPort(readport)

    if not self.outport:
      prompt = False
      writemode = False

    if writemode is None:
      writemode = bool(prompt) or (prompt == "")

    #if errquit is None:
    #  errquit = not readport.stream.isatty()

    wfunc = lambda lsp, x: None
    if writemode:
      if writemode == "raw":
        wfunc = type(self).disp
      else:
        wfunc = type(self).write_nl

    lspobj = None
    retobj = None
    while True:
      try:
        if prompt:
          self.outport.write(prompt) ; self.outport.flush()
        lspobj = self.read(readport)
        if lspobj is eof_object:
          #if writemode: self.outport.write("EOF\n") # debug
          break
        # elif lspobj == comment_object: continue
        # print "reader end", sxp2text(lspobj) # debug
        lspobj = self.macro_expand(lspobj, self.toplevel_env)
        # print "macro expander end", sxp2text(lspobj) # debug
        retobj = self.eval(lspobj, self.toplevel_env)
        #if retobj is not None: wfunc(self, retobj)
        wfunc(self, retobj)
    
      except LispQuitException: break
      except (Exception, KeyboardInterrupt), err:
        if isinstance(err, KeyboardInterrupt):
          #print "catch ^C" # debug
          if not readport.stream.isatty():
            #print "raise ^C" # debug
            raise err
        # retobj = err # ?????
        #traceback.print_exc()
        if self.errport:
          if config.istraceback:
            # traceback
            tblist = traceback.format_tb(sys.exc_info()[2])
            for tbstr in tblist: self.errport.write(tbstr)
          exctype, evalue = sys.exc_info()[:2]
          self.error_out(err, exctype, evalue)
        if errquit: raise err
      # End-of-try
    # End-of-while
    #print "Exit repl" # debug
    return retobj

  def srepl(self, text, prompt=False, toplevel=None, writemode=None,
            errquit=True):
    "REPL , readport is TEXT-string"
    if isinstance(text, unicode):
      text = text.encode("utf-8", "replace") # convert to byte-string
    return self.repl( prompt=prompt, toplevel=toplevel, 
                      readport=StringIO.StringIO(text),
                      writemode=writemode, errquit=errquit)


