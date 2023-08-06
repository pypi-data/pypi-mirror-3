#-*- coding: utf-8 -*-
# Copyright (c) 2012 Tetsu Takaishi.  All rights reserved.

import sys, re, StringIO
import select
import scheme
from scheme import LispEOFError, LispSyntaxError, LispCustomError

# memo:      codec:  p = InPort( codecs.getreader("utf-8")(sys.stdin) )
pass
class InPort(object):
  def __init__(self, stream, embedded=False):
    self.stream = stream; 
    self.embedded = embedded

    self.unread = [u"",0];
    if self.embedded:
      self.unread = [u"%>",0]

    self.iseof = False
    #self.rxget = cached_regex()

    self.shebang = False
    if hasattr(self.stream, "isatty") :
      self.shebang = not self.stream.isatty()

    self._rx_atomtoken = re.compile(r'''(?:[\\].|[^\s()"';#`,])*''')
    self._rx_psymtoken =  re.compile(r'((?:[\\].|[^\\|])*)\|')
    self._rx_strtoken =  re.compile(r'((?:[\\].|[^\\"])*)"')
    self._rx_comtoken = re.compile(r'(\n|[^\s])$')
    self._rx_shptoken = re.compile("[tf(]|<\w+>", re.IGNORECASE)
    self._rx_regextoken = re.compile(r'((?:[\\].|[^\\/])*)/([imsuLx]*)')
    self._rx_token = re.compile(r"""\s*(,@|[()"';#`,]?)""")
    if self.embedded:  # `%>....<%` is embedded-string token
      self._rx_token = re.compile(r"""\s*(%>|,@|[()"';#`,]?)""")
    self._rx_em_endtoken = re.compile(r'<%[^%]|<%$')
    self._rx_em_begintoken = re.compile(r'%>')

  def getname(self):
    "Return the stream name"
    try: return self.stream.name
    #except AttributeError:
    except Exception:
      if isinstance(self.stream, StringIO.StringIO): return "<string-port>"
      return str(self.stream)

  def close(self): self.stream.close()

  def byte_available(self, timeout=0):
    fd = self.stream.fileno()
    ret = select.select([fd],[],[], timeout)
    return fd in ret[0]

  def isready(self, timeout=0):
    if self.iseof: return True
    (line, pos) = self.unread
    L = len(line)
    if pos < L : return True
    #elif pos == L and L > 0:
      #eof check
    #return line[pos - 1] != u"\n"  # CR ???
    return self.byte_available(timeout)
    
  def get_char(self, peep=False):
    (line, pos) = self.unread
    if pos >= len(line) and not self.iseof:
      self.unread = [self.nextline(), 0]
      (line, pos) = self.unread

    if pos >= len(line): return u"" # eof
    ch = line[pos]
    if not peep: self.unread[1] = pos + 1
    return ch

  def get_line(self):
    (line, pos) = self.unread
    if pos >= len(line) and not self.iseof:
      (line, pos) = [self.nextline(), 0]
    self.unread = [u"",0]
    #if pos >= len(line): return u"" # eof
    return line[pos:]

  def get_unread(self): return (self.unread[0])[self.unread[1]:]

  def next_unread(self):
    "Read next linke if unread-buffer is empty, otherwise return self.unread."
    if self.unread[1] >= len( self.unread[0] ):
      self.unread = [self.nextline(), 0]
    return self.unread

  def get_atmtoken(self):
    (line, pos) = self.next_unread()
    if line == u"": raise LispEOFError("reading atom token")
    if line[pos] == u"|":   # when vertical-bar
      self.unread[1] = pos + 1
      return self.get_psymtoken()
    elif line.startswith(u":|", pos): # when keyword + vertical-bar
      self.unread[1] = pos + 2
      return u":" + self.get_psymtoken()
    else:
      # rx = re.compile(r'''(?:[\\].|[^\s()"';#`,])*''')
      # print "atom match %s" % line[pos:]
      mobj = self._rx_atomtoken.match(line, pos)
      if mobj:
        newpos = mobj.end()
        if self.embedded:
          # _rx_em_begintoken = re.compile(r'%>')
          m = self._rx_em_begintoken.search(line, pos, newpos)
          if m: newpos = m.start(0)
        self.unread[1] = newpos
        if pos == newpos: LispCustomError("Program error", "get_atmtoken")
        return line[pos:newpos]
      else:
        raise LispCustomError("Program Error", "get_atmtoken")

  def get_psymtoken(self):
    slist = []
    while True:
      (line, pos) = self.next_unread()
      if line == u"": raise LispEOFError("reading symbol literal")
      mobj = self._rx_psymtoken.match(line, pos)
      if mobj:
        self.unread[1] = mobj.end()
        slist.append(mobj.group(1))
        return u'|' +  u"".join(slist) + u'|'
      else:
        slist.append(line[pos:])
        self.unread = [u"",0]

  def get_strtoken(self):
    slist = []
    while True:
      (line, pos) = self.next_unread()
      if line == u"": raise LispEOFError("reading string literal")
      #rx = re.compile(r'((?:[\\].|[^\\"])*)"')
      # print "string match %s" % line[pos:]
      mobj = self._rx_strtoken.match(line, pos)
      if mobj:
        self.unread[1] = mobj.end()
        slist.append(mobj.group(1))
        return u'"' +  u"".join(slist) + u'"'
      else:
        slist.append(line[pos:])
        self.unread = [u"",0]

  def get_comtoken_fast(self): # not used
    self.unread = [u"",0]
    return u";"

  def get_comtoken_slow(self):
    while True:
      (line, pos) = self.next_unread()
      if line == u"": raise LispEOFError("reading comment")
      #rx = re.compile(r'(\n|[^\s])$')
      # print "comment match %s" % line[pos:]
      mobj = self._rx_comtoken.search(line, pos)
      self.unread = [u"",0]
      if mobj: return u";"

  def get_shptoken(self):
    (line, pos) = self.next_unread()
    if line == u"": raise LispEOFError("reading sharp prefix")
    #rx = re.compile("[tf(]|<\w+>", re.IGNORECASE)
    mobj = self._rx_shptoken.match(line, pos)
    if mobj:
      self.unread[1] = mobj.end()
      return u"#" + mobj.group(0)

    if(line[pos] == "/"):  # regex token
      self.unread[1] = pos + 1
      return self.get_rxtoken()
    elif(line[pos] == "\\"): # character token
      m = re.compile(r".(\W|\w+)").match(line, pos)
      if m:
        self.unread[1] = m.end()
        return u"#\\" + m.group(1)
    else:
      self.unread[1] = pos + 1
      raise LispSyntaxError("reading # prefix token", u"#" + line[pos])

  def get_rxtoken(self):
    rxlist = []
    while True:
      (line, pos) = self.next_unread()
      if line == u"": raise LispEOFError("reading regex literal")
      #rx = re.compile(r'((?:[\\].|[^\\/])*)/([imsuLx]*)')
      # print "regex match %s" % line[pos:]
      mobj = self._rx_regextoken.match(line, pos)
      if mobj:
        self.unread[1] = mobj.end()
        rxlist.append(mobj.group(1))
        return u'#/' + u"".join(rxlist) + u'/' + mobj.group(2)
      else:
        rxlist.append(line[pos:])
        self.unread = [u"",0]

  def get_em_strtoken(self):
    "Embedded string tokenizer"
    slist = []
    def mkresult():
      s = re.sub(r'<%%', u"<%", u"".join(slist))
      return u'#"""' +  s + u'"""'

    while True:
      (line, pos) = self.next_unread()
      if line == u"": 
        return mkresult()
        
      # _rx_em_endtoken = re.compile(r'<%[^%]|<%$')
      mobj = self._rx_em_endtoken.search(line, pos)
      if mobj:
        self.unread[1] = mobj.start() + 2
        slist.append( line[pos:mobj.start()] )
        return mkresult()
      else:
        slist.append(line[pos:])
        self.unread = [u"",0]

  #(map list (list 'dwq#t)) ;-> petite,kawa: -> ((dwq) (#t))
  #                             gosh guile: ->  ((#{dwq\#t}#))
  # But, 'ab\#t -> ab\x23;t in petite and kawa
  # debug
  # from lizpop.inport import InPort
  # import sys,re
  # i = InPort(sys.stdin)
  # i.get_token()
  pass
  def get_token(self):
    while True:
      (line, pos) = self.next_unread()
      if line == u"": raise EOFError

      if self.shebang:
        self.shebang = False
        if line.startswith("#!", pos) and pos == 0:
          # convert shebang line to scheme-comment
          self.unread[0] = u";" + line
          continue

      # rx(r'''\s*(,@|#[\\tf/(]|[;)("'`,]|[^\s)('"`,;]+)''',"i").match(line, pos)
      #_tkpat_top = r''',@|#[\\tf/(]|[;)("'`,]'''
      #rx = re.compile(r"""\s*(,@|[()"';#`,]?)""")
      mobj = self._rx_token.match(line, pos)
      if mobj:
        self.unread[1] = mobj.end(1)
        c = mobj.group(1)
        if c == u'': 
          if self.unread[1] >= len(line): continue
          return self.get_atmtoken() # symbol or numeric
        if c == u'"': return self.get_strtoken()
        elif c == u";": 
          # comment token was not returned
          #return self.get_comtoken_slow() 
          self.get_comtoken_slow()
          continue
        elif c == u"#": return self.get_shptoken()
        elif self.embedded and c == u"%>": 
          return self.get_em_strtoken() 
        else: return c
      else:
        raise LispCustomError("Program Error", "get_token")

  def nextline(self):
    if self.iseof: return u""
    s = self.stream.readline().decode("utf-8", "replace")

    if s == u"" : 
      self.iseof = True
      return u""
    return s
