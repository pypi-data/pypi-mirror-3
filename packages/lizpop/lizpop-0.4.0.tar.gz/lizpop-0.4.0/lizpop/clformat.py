# -*- coding: utf-8 -*-
# `(format)` procedure source
# Copyright (c) 2012 Tetsu Takaishi.  All rights reserved.

import re

import scheme
from scheme import LspChar,sxp2text
import subr
from subr import isnum

# Different of `split:
#   Returns [string, (tuple matched group), string, .....]
# e.g. rx = re.compile(r"~(.*?)([AS])", re.IGNORECASE)
#     mysplit(rx, "abc~1,2Adef~2Sxyz")
#     => ['abc', ('~1,2A', '1,2', 'A'), 'def', ('~2S', '2', 'S'), 'xyz']
pass
def mysplit(rx, data):
  (pos, result) = (0, [])
  while True:
    m = rx.search(data, pos)
    if m:
      if m.start() > pos: result.append(data[pos:m.start()])
      result.append( (m.group(0),) + m.groups() )
      pos = m.end()
    else:
      s = data[pos:]
      if s != "" : result.append(s)
      if result == []: return [""]
      return result

class CLFormatIndexError(scheme.LispException):pass
class CLFormatValueError(scheme.LispError):pass

class CLFormatter(object):
  def __init__(self, fmt):
    # rx = re.compile(r"~(.*?)([ASDXOB~*])", re.IGNORECASE)
    rx = re.compile(r"~((?:'.|.)*?)([ASDXOB~*])", re.IGNORECASE)
    fmtlist = mysplit(rx,fmt)
    self.formats = map( 
      lambda x : CLFormat.create(x[2],x[1]) if isinstance(x, tuple) else x,
      fmtlist)
    
  def format(self, args):
    fargs = CLFormatArgs(args)
    slist = map(
      lambda f: f.apply(fargs) if isinstance(f, CLFormat) else f,
      self.formats)
    return u"".join(slist)

class CLFormatArgs(object):
  def __init__(self, args):
    self.args = args
    self.position = 0

  def get(self):
    try:
      self.position += 1
      return self.args[self.position - 1]
    except IndexError:
      raise CLFormatIndexError

  def setpos(self, pos):
    if pos < 0 or pos > len(self.args):
      raise CLFormatIndexError
    self.position = pos

  def setipos(self, ipos):
    self.setpos(self.position + ipos)

class CLFormat(object):
  def __init__(self,operator, params,flagset):
    self.operator = operator
    self.params = params
    self.flagset = flagset

  @staticmethod
  def str2params(sdata):
    "Convert format parameter string to (parameter-list, flag-set)"
    def _error():
      raise CLFormatValueError("Illegal format parameter -- %s" % sdata)

    # Find flags
    (sparam, sflag) = (sdata, u"")
    rx = re.search(r"[^']([:@]{1,2})$",  u" " + sdata)
    if rx:
      (sparam, sflag) = (sdata[0:rx.start(1) - 1], rx.group(1))
    #print "(sparam, sflag)=", (sparam, sflag) # debug
    flagset = set(sflag)
    if len(flagset) != len(list(sflag)): # "@@" or "::"
      _error()
    
    params = re.findall(r"((?:(?:',)|(?:[^,]))*),",  sparam + ",")
    # parameter's entities check
    #if not all(re.match(r"(('.)|[0-9vV])*$",data)
    #           for data in params): _error()
    if not all(re.match(r"(('.)|[vV]|([0-9]*))$",data)
               for data in params): _error()

    return (params, flagset) 

  @staticmethod
  def nparam(data, fargs, fallback=0):
    if data == "": return fallback
    elif data == "v" or data == "V" :
      obj = fargs.get()
      if isnum(obj) : return obj
      else: return fallback
    elif data[0] == "'" : return fallback
    return int(data)

  @staticmethod
  def cparam(data, fargs, fallback=u" "):
    if data == "": return fallback
    elif data == "v" or data == "V" :
      obj = fargs.get()
      if isinstance(obj, LspChar) : return unicode(obj)
      else: return fallback
    elif data[0] == "'" : return unicode(data[1])
    return fallback

  @staticmethod
  def create(operator, pdata):
    creator = {"a":CLFormat_A, "A":CLFormat_A, "s":CLFormat_S, "S":CLFormat_S,
               "d":CLFormat_D, "D":CLFormat_D, "x":CLFormat_D, "X":CLFormat_D,
               "o":CLFormat_D, "O":CLFormat_D, "B":CLFormat_B, "b":CLFormat_B,
               "~":CLFormat_Tilde, "*":CLFormat_Asterisk,
               }
    if operator in creator:
      (params, flagset) = CLFormat.str2params(pdata)
      return creator[operator](operator, params, flagset)
    raise CLFormatValueError("Illegal format operator -- %s" % operator)

  @staticmethod
  def padtext(text, mincol=0, colinc=1, minpad=0, padchar=u" ", is_right=False):
    if minpad >= 1:
      if is_right:
        text = (padchar * minpad) + text
      else:
        text = text + (padchar * minpad)

    L = len(text)
    morepad = mincol - L
    if morepad > 0:
      L = L + (((morepad - 1) // colinc + 1) * colinc)
    if is_right:
      return text.rjust(L,padchar)
    else:
      return text.ljust(L,padchar)

class CLFormat_A(CLFormat):

  def isRight(self):
    return "@" in self.flagset

  def apply(self, fargs, raw=True):
    (mincol, colinc, minpad, padchar) = ( 0, 1, 0, u" ")
    try:
      mincol = max(0, CLFormat.nparam(self.params[0], fargs, 0))
      colinc = max(1, CLFormat.nparam(self.params[1], fargs, 1))
      minpad = max(0, CLFormat.nparam(self.params[2], fargs, 0))
      padchar = CLFormat.cparam(self.params[3], fargs, u" ")
    except IndexError: pass
    
    data = sxp2text(fargs.get(), raw)
    return CLFormat.padtext(data, mincol, colinc, minpad, padchar,
                            self.isRight())

class CLFormat_S(CLFormat_A):
  def apply(self, fargs):
    return CLFormat_A.apply(self, fargs, False)


class CLFormat_D(CLFormat):
  def inttext(self, obj):
    fmtdic = {"d":u"%ld", "D":u"%ld", "x":u"%lx", "X":u"%lX", "o":u"%lo", "O":u"%lo"}
    num = long(obj)
    return( u"+" if num >= 0 else u"-", fmtdic[self.operator] % abs(num) )

  @staticmethod
  def do_comma(nstr, comma_char=u",", interval=3):
    if interval < 1 : return nstr
    slist = []
    while True:
      if len(nstr) <= interval:
        slist.insert(0, nstr)
        break
      slist.insert(0, nstr[-interval: ])
      nstr = nstr[: -interval]
    return comma_char.join(slist)

  def apply(self, fargs):
    (mincol, padchar, commachar, comma_interval) = ( 0, u" ", u",", 3)
    try:
      mincol = max(0, CLFormat.nparam(self.params[0], fargs, 0))
      padchar = CLFormat.cparam(self.params[1], fargs, u" ")
      commachar = CLFormat.cparam(self.params[2], fargs, u",")
      comma_interval = max(0, CLFormat.nparam(self.params[3], fargs, 3))
    except IndexError: pass

    obj = fargs.get()
    if not isnum(obj):
      return CLFormat.padtext(sxp2text(obj),
                              mincol=mincol, padchar=padchar, is_right=True);
    (sign, text) = self.inttext(obj)
    if ":" in self.flagset:
      # insert comma character
      text = CLFormat_D.do_comma(text, commachar, comma_interval)

    if sign == "-" or ("@" in self.flagset) :
      text = sign + text

    if mincol >= 1:
      return CLFormat.padtext(text,
                              mincol=mincol, padchar=padchar, is_right=True);
    else:
      return text

class CLFormat_B(CLFormat_D):
  hexdic = {
    '0':u'0000', '1':u'0001', '2':u'0010', '3':u'0011', 
    '4':u'0100', '5':u'0101', '6':u'0110', '7':u'0111', 
    '8':u'1000', '9':u'1001', 'A':u'1010', 'B':u'1011', 
    'C':u'1100', 'D':u'1101', 'E':u'1110', 'F':u'1111' }
  def inttext(self, obj):
    num = long(obj)
    xstr = "%lX" % abs(num)
    bstr = u"".join( map(lambda x: CLFormat_B.hexdic[x], xstr )  )
    bstr = re.sub("^0+", u"", bstr)
    if bstr == "" : bstr = u"0"
    return( u"+" if num >= 0 else u"-", bstr)

class CLFormat_Tilde(CLFormat):
  def apply(self, fargs):
    count = 1
    try:
      count = max(0, CLFormat.nparam(self.params[0], fargs, 1))
    except IndexError: pass
    return "~" * count

class CLFormat_Asterisk(CLFormat):
  def __init__(self,operator, params,flagset):
    CLFormat.__init__(self,operator, params,flagset)
    if self.flagset == set("@:"):
      raise CLFormatValueError("Illegal format flags -- %s" %
                               "".join( self.flagset ))

  def apply(self, fargs):
    N = 1
    if "@" in self.flagset: N = 0
    try:
      N = max(0, CLFormat.nparam(self.params[0], fargs, N))
    except IndexError: pass

    if "@" in self.flagset: 
      fargs.setpos(N)
    else :
      if ":" in self.flagset: fargs.setipos(-N)
      else: fargs.setipos(N)

    return u""


