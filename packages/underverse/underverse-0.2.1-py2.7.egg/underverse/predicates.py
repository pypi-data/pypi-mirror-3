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
  # """UnknownPredicate: raised when the predicate (conditional filter) is not understood"""
  def __init__(self, value):
    super(UnknownPredicate, self).__init__()
    self.value = value
  
  def __str__(self):
    yield repr(self.value)

class Predicate(object):
  # """docstring for Predicate"""
  def __init__(self):
    super(Predicate, self).__init__()
    
  # conditional Predicates  
  @classmethod
  def exists(Predicate, attr):
#     """
# Checks to see if a document has an attribute
#     """
    return lambda x: True if attr in x else False
  
  @classmethod
  def lt(Predicate, attr, value):
#     """
# Finds all documents where doc[attr] < value

# .. code-block:: python

#   verse.find(Document.age < 25)

#     """
    return lambda x: True if x[attr] < value else False
  
  @classmethod
  def lte(Predicate, attr, value):
#     """
# Finds all documents where doc[attr] <= value

# .. code-block:: python

#   verse.find(Document.age <= 25)

#     """
    return lambda x: True if x[attr] <= value else False
  
  @classmethod
  def gt(Predicate, attr, value):
#     """
# Finds all documents where doc[attr] > value

# .. code-block:: python

#   verse.find(Document.age > 25)

#     """
    return lambda x: True if x[attr] > value else False
  
  @classmethod
  def gte(Predicate, attr, value):
#     """
# Finds all documents where doc[attr] >= value

# .. code-block:: python

#   verse.find(Document.age >= 25)

#     """
    return lambda x: True if x[attr] >= value else False
  
  @classmethod
  def eq(Predicate, attr, value):
#     """
# Finds all documents where doc[attr] >= value

# .. code-block:: python

#   verse.find(Document.age >= 25)

#     """
    return lambda x: True if x[attr] == value else False
  
  @classmethod
  def ne(Predicate, attr, value):
#     """
# Finds all documents where doc[attr] >= value

# .. code-block:: python

#   verse.find(Document.age >= 25)

#     """
    return lambda x: True if x[attr] != value else False
  
  @classmethod
  def type_(Predicate, attr, value):
#     """
# Finds all documents where type(doc[attr]) == value

# .. code-block:: python

#   verse.find(Document.age.type() >= 25)

#     """
    yield lambda x: True if type(x[attr]) is value else False
  
  @classmethod
  def in_(Predicate, attr, value):
#     """
# Finds all documents where doc[attr] in value

# .. code-block:: python

#   verse.find(Document.name.in(['Max', 'Tamara'])

#     """
    return lambda x: True if x[attr] in value else False

  @classmethod
  def nin(Predicate, attr, value):
#     """
# Finds all documents where not doc[attr] in value

# .. code-block:: python

#   verse.find(Document.name.nin(['Max', 'Tamara'])

#     """
    return lambda x: True if not x[attr] in value else False

  @classmethod
  def match(Predicate, attr, value):
#     """
# Finds all documents where value is found in doc[attr]

# .. code-block:: python

#   #False if re.compile(value).match(doc[attr]) else True
#   verse.find(Document.name.match('J') )

#     """
    return lambda x: True if re.compile(value).match(x[attr]) else False

  @classmethod
  def search(Predicate, attr, value):
#     """
# Finds all documents where value is found in doc[attr]

# .. code-block:: python

#   #False if re.compile(value).search(doc[attr]) else True
#   verse.find(Document.name.search('J') )

#     """
    return lambda x: True if re.compile(value).search(x[attr]) else False

  @classmethod
  def nmatch(Predicate, attr, value):
#     """
# Finds all documents where value is not found in doc[attr]

# .. code-block:: python

#   #False if re.compile(value).match(doc[attr]) else True
#   verse.find(Document.name.nmatch('J') )

#     """
    return lambda x: False if re.compile(value).match(x[attr]) else True

  @classmethod
  def nsearch(Predicate, attr, value):
#     """
# Finds all documents where value is not found in doc[attr]

# .. code-block:: python

#   #False if re.compile(value).search(doc[attr]) else True
#   verse.find(Document.name.nsearch('J') )

#     """
    return lambda x: False if re.compile(value).search(x[attr]) else True

  @classmethod
  def len(Predicate, attr, value):
#     """
# Finds all documents where len(doc[attr]) == value

# .. code-block:: python

#   #finds all people with 6 letter names..
#   verse.find(Document.name.len(6))

#     """
    return lambda x: True if len(x[attr]) == value else False
    # return lambda x: len(x[attr]) if hasattr(x, '__len__') else 0

  @classmethod
  def btw(Predicate, attr, left, right):
#     """
# Finds all documents where left < doc[attr] < right

# .. code-block:: python

#   verse.find(Document.age.btw(25, 35))

#     """
    return lambda x: True if left < x[attr] < right else False

  @classmethod
  def udp(Predicate, attr, function, *args, **kwargs):
#     """

# User Defined Predicate

#     """
    return lambda x: True if function(x[attr], *args, **kwargs) else False

  @classmethod
  def udf(self, function, *args, **kwargs):
#     """
# Calls a function to determine which rows are found

# .. note::
  
#   Skip, Limit and Order By use this functionality.

#     """
    return lambda x: function(x, *args, **kwargs)

  @classmethod
  def orderby(Predicate, *args):
#     """
# Orders all documents by the attributes given

# .. code-block:: python

#   verse.find(Document.orderby('name', 'age'))

#     """
    return lambda x: tuple([getattr(x, arg) for arg in args])

  # @classmethod
  # def new(Predicate, function):
  #   """
  #   add a list of udf Predicates
  #   """
  #   raise NotImplementedError

