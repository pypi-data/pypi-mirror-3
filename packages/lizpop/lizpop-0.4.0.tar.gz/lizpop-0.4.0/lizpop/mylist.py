# -*- coding: utf-8 -*-
_undefobj = object()

def isPair(obj):
  "Listable and not Nil ?"
  if isinstance(obj, Listable):
    #if obj.isNil(): return False
    if obj is Nil: return False 
    return True
  return False

def isProperList(obj):
  "(list? obj)"
  if isinstance(obj,Listable):
    lst = obj
    while isPair(lst): lst = lst.cdr()
    return lst is Nil
  return False

class Listable(object):
  # Derived class is required following method.
  #   def __init__(self, car-data, cdr-link)
  #   def cdr(self):
  #   def car(self): 
  #   def isNil(self):
  #   def setcar(self,data):
  #   def setcdr(self,link):

  # Iterate cdr while pair?(cdr)
  def each(self):
    lst = self
    # while isinstance(lst, Listable) and (not lst.isNil()): 
    while isinstance(lst, Listable) and (lst is not Nil):
      #print "begin yield with %s" % str(lst.car()) # debug
      yield lst.car()
      lst = lst.cdr()

  def __iter__(self):
    #print "__iter__ comes" #debug
    return self.each()

  # last:  True  -- Iterate tha last non proper cell.
  # e.g. l = List.from_iter([1,2,3],10)
  #     [str(lst) for lst in l.eachlist(True)]
  #  => ['List.make(1, 2, 3)', 'List.make(2, 3)', 'List.make(3)', '10']
  #     [str(lst) for lst in l.eachlist()]
  #  => ['List.make(1, 2, 3)', 'List.make(2, 3)', 'List.make(3)']
  #     [str(lst) for lst in List.make(1,2,3).eachlist(True)]
  #  => ['List.make(1, 2, 3)', 'List.make(2, 3)', 'List.make(3)', 'nil']
  def eachlist(self,last=False):
    lst = self
    while isPair(lst):
      yield lst
      lst = lst.cdr()
    if last: yield(lst)

  # Split proper-list and non-proper-cell with tuple.
  # e.g.
  # [str(x) for x in List.from_iter([1,2,3]).split_tail()] 
  #  => ['List.make(1, 2, 3)', 'nil']
  # [str(x) for x in List.from_iter([1,2,3],"z").split_tail()] 
  #  => ['List.make(1, 2, 3)', 'z']
  # [str(x) for x in Nil.split_tail()] #=> ['nil', 'nil']
  def split_tail(self):
    (left, right) = (Nil, Nil)
    for x in self.eachlist(True):
      if isPair(x): left = type(self)(x.car(),left)
      else: right = x
    return (left.nreverse(),right)

  # NYI: The circular list is not supported. 
  def __str__(self):
    #return self.__class__.__name__ + ".make(" + ", ".join((str(x) for x in self)) + ")"
    return type(self).__name__ + ".make(" + ", ".join((str(x) for x in self)) + ")"

  def lispstr(self):
    (left, right) = self.split_tail()
    return("(" +
           " ".join( (x.lispstr() if isinstance(x,Listable) else str(x)) for x in left) +
           (")" if right is Nil else " . %s)" % right) )

  #(list-ref list k)
  # Ignore last cell of non-proper-list.
  # e.g. l.ref(5,fallback=0)
  def ref(self,n,**fallback):
    lst = self; count = 0
    while isPair(lst):
      if( count == n):return lst.car()
      count += 1 ; lst = lst.cdr()
    if( "fallback" in fallback ): return fallback["fallback"]
    raise IndexError, "n=%s is out of range" % n
  nth = ref #alias of ref

  #(list-tail list n)
  def nthcdr(self,n,**fallback):
    lst = self; count = 0
    while True:
      if( count == n):return lst
      #if( lst.isNil() ): break
      if not isPair(lst): break
      count += 1 ; lst = lst.cdr()
    if( "fallback" in fallback ): return fallback["fallback"]
    raise IndexError, "n=%s is out of range" % n

  def __getitem__(self,n):
    #print "__getitem__ comes" # debug
    return self.ref(n)

  def __setitem__(self,n,data):
    target = self.nthcdr(n)
    if isPair(target): target.setcar(data)
    else: raise IndexError, "n=%s is out of range" % n

  def delete_if(self, func, only_first=False):
    if self is Nil: return self
    top = self.__class__(None, self)
    lst = top
    while isPair(lst.cdr()):
      if func(lst.cdr().car()):
        lst.setcdr(lst.cdr().cdr())
        if only_first: return top.cdr()
      else : lst = lst.cdr()
    return top.cdr()

  def delete(self, target, only_first=False):
    return self.delete_if(lambda data: target == data, only_first)

  def delete_is(self, target, only_first=False):
    return self.delete_if(lambda data: target is data, only_first)

  # The last dot-pair is not put into calculation. 
  def length(self,maximum=-1):
    if maximum < 0 : return self.__len__()
    lst = self ; lng = 0
    while isPair(lst):
      if lng >= maximum: return lng
      lng += 1 ; lst = lst.cdr()
    return lng

  # The last dot-pair is not put into calculation. 
  # e.g. len( List.from_iter((1,2,3),"z") ) #=> 3
  def __len__(self):
    #print "__len__ comes" # debug
    lst = self ; lng = 0
    # while isinstance(lst, Listable) and (not lst.isNil()): 
    while isinstance(lst, Listable) and (lst is not Nil):
      lng += 1 ; lst = lst.cdr()
    return lng
    
  def map(self, proc):
    klass = type(self)
    top = klass(None)
    (ret, lst) = (top, self)
    while (lst is not Nil) and isinstance(lst, Listable) :
      ret.setcdr( klass( proc(lst.car()) ) )
      (ret, lst)  = (ret.cdr(), lst.cdr())
    return top.cdr()

  def map_p(self, proc):
    klass = type(self)
    top = klass(None)
    ret = top; lst = self
    while not lst.isNil():
      ret.setcdr( klass(proc(lst.car())) )
      ret = ret.cdr() ; lst = lst.cdr()
    return top.cdr()

  @classmethod
  def from_iter(cls,iterable,last=_undefobj):
    """Make Listable from iterable.
    last is last data (defalut is Nil)"""
    lst = Nil
    for data in iterable: lst = cls(data,lst)
    return lst.nreverse(last)

  @classmethod
  def make(cls, *args):
    return cls.from_iter(args)

  def copy(self):
    (lst, ret) = (self, Nil)
    klass = type(self)
    while isPair(lst):
      ret = klass(lst.car(),ret)
      lst = lst.cdr()
    return ret.nreverse(lst)

  # /ohome/tez/java/epl/util/SList.java
  # If last == None then lsave = lst ; lst.nreverse(); lsave.cdr() is Nil.
  # If last != None then lsave = lst ; lst.nreverse(last); lsave.cdr() is last.
  pass
  def nreverse(self, last=_undefobj):
    if last is _undefobj: ret = Nil
    else: ret = last
    lst = self
    #while isinstance(lst, Listable) and (not lst.isNil()):
    while isinstance(lst, Listable) and (lst is not Nil):
      nxt = lst.cdr()
      lst.setcdr(ret)
      ret = lst
      lst = nxt
      #(ret,lst) = (lst,nxt)
    return ret

  # [R5RS]
  # The resulting list is always newly allocated, except that it shares
  # structure with the last list argument. The last argument may actually
  # be any object; an improper list results if the last argument is not a
  # proper list.
  @classmethod
  def append(klass, *args):
    lst = Nil
    for arg in args[0:-1]:
      while isPair(arg):
        lst = klass(arg.car(), lst)
        arg = arg.cdr()
      if arg is not Nil:
        raise TypeError("in append: proper-list required")
    if(lst is Nil):return args[-1]
    last = lst
    ret = lst.nreverse()
    last.setcdr(args[-1])
    return ret

  # more generalized form of `append'
  # ARGS can be iterable, except the last.
  # e.g.
  # (define (append* . args) 
  #   (apply (attr *scheme* 'ScmList 'append_any) args))
  # (append* '(1 2 3) "abc" '()) ;-> (1 2 3 "a" "b" "c")
  # (append* '(1 2 3) '(4 5 . 6) '(7 8)) ;-> (1 2 3 4 5 7 8)
  # (append '(1 2 3) '(4 5 . 6) '(7 8)) ;-> error
  # List.append_any([1,2,3],Nil) is equivalent to List.from_iter([1,2,3])
  @classmethod
  def append_any(klass, *args):
    lst = Nil
    for arg in args[0:-1]:
      for data in arg: lst = klass(data,lst)
    if(lst is Nil):return args[-1]
    last = lst
    ret = lst.nreverse()
    last.setcdr(args[-1])
    return ret

  # (append! '(a . b) '(a b c)) ;->(a a b c)
  def nconc(self, *args):
    lst = self
    for other in args:
      while isPair(lst.cdr()): lst = lst.cdr()
      lst.setcdr(other)
    return self

  # same as (equal? lst other)
  # Deep compare, so very expensive.
  # NYI: The circular list is not supported. 
  # e.g.
  # l = List.from_iter( (0,1, List.from_iter(("a","b")), 3,4) )
  # l2 = l.copy()
  # print l,l2 #=> List(0, 1, List(a, b), 3, 4) List(0, 1, List(a, b), 3, 4)
  # l == l2 #=> True
  # l[2] = List.make("a","b","c")
  # print l,l2 #=> List(0, 1, List(a, b, c), 3, 4) List(0, 1, List(a, b), 3, 4)
  # l == l2 #=> False
  def __eq__(self, other):
    #print "%s's __eq__ called" % self.__class__.__name__ #debug
    if not isinstance(self, type(other)): return False
    alist = self ; blist = other
    while isPair(alist) and isPair(blist):
      if alist is blist : return True   # for circular list
      if not alist.car() == blist.car(): return False
      alist = alist.cdr()
      blist = blist.cdr()
    # if isPair(alist) or isPair(blist): return False
    return alist == blist

  def __ne__(self,other): return not self.__eq__(other)
      

class NilCell(Listable):
  def car(self): return self
  def cdr(self): return self
  def isNil(self): return True
  def setcar(self,data):pass
  def setcdr(self,link):pass
  def __str__(self): return "nil"
  def __eq__(self,other): return isinstance(self,type(other))
  def nconc(self,*args):
    if args:
      if isinstance(args[0],Listable): return args[0].nconc(*args[1:])
      return args[0] # Nil.nconc("a") #-> "a"
    return self
  def map(self, proc): return self
  def map_p(self, proc): return self
  def copy(self): return self

Nil = NilCell()

class List(Listable):
  #e.g. l = List("a", List("b", List("c")))
  # for x in l: print x, #=> a b c
  def __init__(self, data, link=Nil):
    self._car = data
    self._cdr = link

  def car(self): return self._car
  def cdr(self): return self._cdr
  def isNil(self): return False
  def setcar(self,data): self._car = data
  def setcdr(self,link): self._cdr = link

