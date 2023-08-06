import stream, re

## TODO:
## 
## Change process to yield, not return
##

#+ <, <=, >, >=
# $all
#+ $exists
# $mod
#+ $ne
#+ $in
#+ $nin
# $nor
# $or
# $and
# $size
#+ $type
#+ Regular Expressions
#+ Value in an Array
# $elemMatch

#+ skip
#+ limit

__all__ = ["Predicate"]

class UnknownPredicate(Exception):
  """UnknownPredicate: raised when the predicate (conditional filter) is not understood"""
  def __init__(self, value):
    super(UnknownPredicate, self).__init__()
    self.value = value
  
  def __str__(self):
    yield repr(self.value)


class Predicate(object):
  """docstring for Predicate"""
  def __init__(self):
    super(Predicate, self).__init__()
    
  # conditional Predicates  
  @classmethod
  def exists(Predicate, attr):
    return lambda x: True if attr in x else False
  
  @classmethod
  def lt(Predicate, attr, value):
    return lambda x: True if x[attr] < value else False
  
  @classmethod
  def lte(Predicate, attr, value):
    return lambda x: True if x[attr] <= value else False
  
  @classmethod
  def gt(Predicate, attr, value):
    return lambda x: True if x[attr] > value else False
  
  @classmethod
  def gte(Predicate, attr, value):
    return lambda x: True if x[attr] >= value else False
  
  @classmethod
  def eq(Predicate, attr, value):
    return lambda x: True if x[attr] == value else False
  
  @classmethod
  def ne(Predicate, attr, value):
    return lambda x: True if x[attr] != value else False
  
  @classmethod
  def type_(Predicate, attr, value):
    yield lambda x: True if type(x[attr]) is value else False
  
  @classmethod
  def in_(Predicate, attr, value):
    return lambda x: True if x[attr] in value else False

  @classmethod
  def nin(Predicate, attr, value):
    return lambda x: True if not x[attr] in value else False

  @classmethod
  def match(Predicate, attr, value):
    return lambda x: True if re.compile(value).match(x[attr]) else False

  @classmethod
  def search(Predicate, attr, value):
    return lambda x: True if re.compile(value).search(x[attr]) else False

  @classmethod
  def nmatch(Predicate, attr, value):
    return lambda x: False if re.compile(value).match(x[attr]) else True

  @classmethod
  def nsearch(Predicate, attr, value):
    return lambda x: False if re.compile(value).search(x[attr]) else True

  @classmethod
  def len(Predicate, attr, value):
    return lambda x: True if len(x[attr]) == value else False
    # return lambda x: len(x[attr]) if hasattr(x, '__len__') else 0

  @classmethod
  def btw(Predicate, attr, left, right):
    return lambda x: True if left < x[attr] < right else False

  @classmethod
  def udp(Predicate, attr, function, *args, **kwargs):
    return lambda x: True if function(x[attr], *args, **kwargs) else False

  @classmethod
  def process(Predicate, k, v):
    """
    processes the condition statements
    """
    if hasattr(v, '__iter__') and len(v) == 2:
      if v[0] == '<' or v[0] == 'lt': 
        yield stream.filter(Predicate.lt(k, v[1]))
      elif v[0] == '<=' or v[0] == 'lte':
        yield stream.filter(Predicate.lte(k, v[1]))
      elif v[0] == '?' or v[0] == 'gt':
        yield stream.filter(Predicate.gt(k, v[1]))
      elif v[0] == '>=' or v[0] == 'gte':
        yield stream.filter(Predicate.gte(k, v[1]))
      elif v[0] == '=' or v[0] == 'eq':
        yield stream.filter(Predicate.eq(k, v[1]))
      elif v[0] == '!=' or v[0] == 'ne':
        yield stream.filter(Predicate.ne(k, v[1]))
      elif v[0] == 'type':
        yield stream.filter(Predicate.type_(k, v[1]))
      elif v[0] == 'in':
        yield stream.filter(Predicate.in_(k, v[1]))
      elif v[0] == 'nin':
        yield stream.filter(Predicate.nin(k, v[1]))
      elif v[0] == 'match':
        yield stream.filter(Predicate.match(k, v[1]))
      elif v[0] == 'search':
        yield stream.filter(Predicate.search(k, v[1]))
      elif v[0] == 'nmatch':
        yield stream.filter(Predicate.match(k, v[1]))
      elif v[0] == 'nsearch':
        yield stream.filter(Predicate.search(k, v[1]))
      else:
        raise UnknownPredicate, v[0]
    else:
      if k == 'skip':
        if not type(v) is int:
          raise ValueError, "Drop predicates must be integers: ('drop', 5)"
        yield stream.drop(v)
      elif k == 'limit':
        if not type(v) is int:
          raise ValueError, "Limit predicates must be integers: ('limit', 5)"
        yield stream.take(v)
      else:
        raise UnknownPredicate, k

  @classmethod
  def new(Predicate, function):
    """
    add a list of udf Predicates
    """
    raise NotImplementedError




