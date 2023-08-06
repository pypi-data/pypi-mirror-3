"""
Underverse is named after the destination and afterlife of the Necromonger's from the 
Chronicles of Riddick. This module is so named because the author likes the movie.

The Underverse is an Object Document Mapper, or ODM. An ODM performs roughly the same 
functions for unstructured data as an ORM (Object Relational Mapper) does for relational 
data minus the 'relationships...

In Python, SQLAlchemy is the ORM of choice. The Underverse follows the same 
design principles seen in SQLAlchemy. So if you've used it before, this module 
should feel right at home.

.. note::

  Underverse is now **beta** due to the arrival of v0.3. However, there may still be uncovered bugs or unexpected errors waiting to be found. I'm continually working to increase the test coverage and to update the docs.

  If bugs are found, please join the `Google Group <http://groups.google.com/group/python-underverse>`_ and post the issue. Suggestions are also welcome. The project will be on github soon.


.. warning::
  
  Underverse underwent a tremendous maturation process between versions 0.2.3 and 0.3. Therefore, if you downloaded an earlier version, it would greatly benefit you to upgrade to the latest version.

What is Underverse?
===================

At it's core, the Underverse is a JSON-based document store built on top of SQlite. JSON was chosen over pickle because of it's size, simplicity, readability and speed. These features, combined with SQlite, make for a simple and elegant solution. Everything in the Underverse is written to use Python's generators to provide for a streamlined process for data access and manipulation. The module provides ways to quickly load, update, group, map and filter data.

To avoid some mis-conceptions, here's what it is and what it's not:

**Underverse is**:

  * Fast, easy, simple and clean
  * A zero-configuration solution
  * Extremely light-weight
  * Specialized

    * Think of a Knife, not a Low Orbit Ion Cannon
    * Agile, not encumbered by over-bearing features

  * Lean, very lean
  * **A wicked-sick, data-analysis module**
  * **NOT** a do-everything module
  * **NOT** into *keeping up with the Joneses*
  * **NOT** a NoSQL client-server solution

    * if you want one, you'd have to wrap it yourself (or use one that already works and save yourself a headache)

  * **NOT** a full NoSQL solution

    * it has no indexes
    * it has no built-in replication
    * it has no sharding-capability

  * **NOT** a solution for anyone with high-availability needs (again, not a client-server solution)


The Underverse was designed to be **an analysis module**. It was engineered to be a defense for low-strafing questions on Friday @ 440 PM. It was built to answer questions *FAST*. With this in mind and by using NoSQL / Post-modern document storage principles, the Underverse can evolve over time allowing for increasingly deeper questions to be asked of the data it houses.

**Author's Advice**:

  You'll do yourself a favor by remembering what this module was designed for. Every weapon has a specific purpose, use them for what they were built for in order to construct your own arsenal for dispatching problems and questions from customers.

Do that and your boss won't know whether to hug you or kiss you. Hopefully neither if your boss is like most (that's also assuming you are not his (or her - for the PC crowd) secretary).. On second thought, just keep any dreams of hugs or kisses to yourself...

*"You keep what you kill."* - Lord Marshal

Questions are your prey.

Introduction
============

These next few sections outline possible points of familiarity for those who have worked with relational databases or other NoSQL data stores. I've also included a section comparing Underverse and SQL-Alchemy. As I've said before, if you've used SQL-Alchemy before then you should see some similarities.

Organization / Lingo
--------------------

Here are the relationships between the objects found in Underverse and a traditional RDBMS, as well as their counter-parts using NoSQL-speek:

.. raw:: html

  <br \>
  <div style="width:90%" id="main">
    <table class="ctable" id="if_class_comparison">
        <thead>
          <tr>
              <td>RDBMS</td>
              <td>NoSQL-speek</td>
              <td>Underverse</td>
          </tr>
        </thead>
      <tbody>
          <tr>
            <td>Database</td>
            <td>Database</td>
            <td>Underverse</td>
          </tr>
          <tr>
            <td>Table</td>
            <td>Collection</td>
            <td>Verse</td>
          </tr>
          <tr>
            <td>ResultSet</td>
            <td>-</td>
            <td>SubVerse</td>
          </tr>
          <tr>
            <td>ResultRow</td>
            <td>Document</td>
            <td>NecRow</td>
          </tr>
      </tbody>
    </table>
  </div>
  <br \>

SQL-Alchemy Comparison
----------------------

Underverse's query syntax is similar to SQLAlchemy's. However, Underverse removes some of the complexity of getting started. 

But before I go any further, understand that Underverse is NOT meant to battle SQL-Alchemy in hand-to-hand combat. 
There are many, many things that SQL-Alchemy does that are top-notch in the ORM world, most of which will never be covered in Underverse. 
I have really enjoyed using SQL-Alchemy in the past. However, some, perhaps even most, projects can get away with using a much 
lighter-weight approach to managing data. Underverse is meant to fill that niche.

Here's a comparison for those of you who are familiar to SQL-Alchemy:

**SQLAlchemy**::

  from sqlalchemy import create_engine, Column, Integer, String
  from sqlalchemy.ext.declarative import declarative_base
  from sqlalchemy.orm import scoped_session, sessionmaker

  Base = declarative_base()

  class User(Base):
      __tablename__ = 'users'

      id = Column(Integer, primary_key=True)
      name = Column(String)
      fullname = Column(String)
      password = Column(String)

      def __init__(self, name, fullname, password):
          self.name = name
          self.fullname = fullname
          self.password = password

      def __repr__(self):
         return "<User('%s','%s', '%s')>" % (self.name, self.fullname, self.password)

  session = scoped_session(sessionmaker(bind=create_engine('sqlite:///:memory:', echo=False)))

  ed_user = User('ed', 'Ed Jones', '3d5_p455w0r6')
  session.add(ed_user)

Let's take a look at everything that's happening. Before you can do anything you 
have to define a data model. In the example case, the ``User`` class is defined 
with first name, full name and password fields. 

Next, a session is created to operate on. Then a ``User`` object is instantiated 
and finally added to the session.

**Underverse**::


  from underverse import Underverse

  uv = Underverse()
  users = uv.users

  ed_user = { 'name': 'ed', 'fullname':'Ed Jones', 'password':'3d5_p455w0r6'}
  users.add(ed_user)

Ok, at first glance you can see a large difference in the lines of code required. 
Let's talk about what Underverse is doing. 

When ``uv = Underverse()`` is called, a connection to an in-memory SQLite database 
is made behind the scenes. Then a table is created by using 
``users = uv.user``. No class structure or data model is needed to insert data. 
Then to insert data, you simply call ``users.add(ed_user)``.

.. note::
  
  Yes, I understand that SQL-Alchemy is an ORM and Underverse is not. The above was simply 
  to show the differences of loading data.

  Please, don't send me hate mail.


Querying
--------

Using the same SQL-Alchemy code above, here's how querying is handled in both frameworks. Again, this is NOT a replacement for SQL-Alchemy, but rather a lighter-weight approach data storage and retrieval.

**SQL-Alchemy**::

  session.query(User).filter(User.fullname=='Ed Jones')

This statement finds all rows in the ``users`` table where ``fullname == 'Ed Jones'``.

Similarly **Underverse** does this::

  from underverse.model import Document
  users.find(Document.name == 'ed')

When using Underverse, the ``Document`` class is the main query object. It handles all document queries for every document collection. There's no need to create a class for every table or collection.


Module Documentation
====================

"""
import sqlite3, uuid, time
from predicates import Predicate as P#, Sorter
from model import Document, DocumentModel, QuasiDead
from ordereddict import OrderedDict

try:
  import simplejson as json
  # print "Using simplejson..."
except ImportError:
  import json
  # print "Using json..."

try:
  import numpy as np
  HAS_NUMPY = True
except ImportError:
  HAS_NUMPY = False

encoder = json
decoder = json


__all__ = ['NecRow', 'Underverse', 'Verse', 'SubVerse', 'and_', 'or_']

## TODO
#
# add column mapping capability using a list of predicates, 
#   if a predicate is false, it goes to the next one until there are no more. The default column mapping is Column1 - ColumnN
#   the predicates evaluate each line and return a list of strings if it meets certain criterion, otherwise it returns false
#
#+ add connection option for non-memory sqlite files
#+ add groupby functionality
#- add verse slicing capability using sqlite rowid or stream
#+ add a purge all function
# add logging capability
#   no glob results, # of
#    found #
#+ add update all functionality, like add_all
#+ add where select functionality
# and/or functionality?
#+ add map functionality
#+  add reduce functionality
#+ merge add / add_all functions

#+ implement paging

#- subclass stream?
#-   no, overload operators
# 
#bulk insert: verse << list of rows
#insert: verse < row
#update: row < dict, row + dict
#remove: verse - row,
#purge: verse >> NULL (new class)

#+add sqlalchemy-ish functionality
#+   operators on column names
#+   Predicates with overloaded operators? No
#
#+ Document class with operator overloading which returns a predicate for filtering
#   Much more readable
#
#   Document.name == 'Max'
#   ('name', ['eq', 'Max'])
#

# add to numpy functionality using np.fromiter(data, dtype, count=len(data))
#+ add functionality to add/update an entire column
#+  def verse.add_column(data, name, commit=True):
#   if len(data) != len(self.data):
#      raise Exception, "column data must be the same length as existing data"
#
#+  def verse.add_columns(data, names, commit=True):
#   if len(data) != len(self.data):
#      raise Exception, "column data must be the same length as existing data"
#
#-base class

#Performance
#??? both the unique and mapper verse functions have callback capability
#limskip is fast, slicing is faster after data filter has been persisted

# possibility of removing stream from dependencies
#needed? use versioning to persist changes to data
#needed?   add a purge (clean) functionality to remove older versions

#Data Validation
#Sub-class unittest
#RuleSets and Rules
#RuleSet - parent class
# - has rules
# - rules can be applied to datasets to filter / flag conditional criterion
# - data attributes are used to store rule results
# - - rules -> RuleSet -> Rule
#Rule decorator

# Operand Enumeration
and_ = ' and '
or_ = ' or '

class NecroEncoder(json.JSONEncoder):
  def default(self, obj):
    if not type(obj).__name__ in Underverse.class_names:
      Underverse.class_names.append(type(obj).__name__)
      Underverse.create_encoder_decoder(type(obj))
    
    for encode in Underverse.user_def_encoders:
      if encode[0](obj):
        return encode[1](obj)
    return json.JSONEncoder.default(self, obj)

def as_obj(obj):
  # print obj
  for decode in Underverse.user_def_decoders:
    # print decode[0](obj), obj
    if decode[0](obj):
      return decode[1](obj)
  return obj


class NecRow(dict):
  """

Each document is based on a Python dict object. When interacting with SQlite, this class is the storage object. Python classes can be persisted using Underverse as long as they have a *__dict__* function. If *object* is the super class you should be fine.

When documents are persisted, they are given a *UUID* as well as *created_at* and *updated_at* properties. This is why the data persisted is slightly larger than the raw data. 

The persisted object can both get and set variables easily using the *dot* syntax.


.. code-block:: python

  #connect to existing document store
  uv = Underverse("existing.db")

  #each Verse (or SQlite table) has iterator functionality
  for person in uv.people:
    
    #Get first name and last name
    first = person.first_name
    last = person.last_name
    
    #set full name
    person.full_name = "%s %s" % (first, last)

  """
  def __init__(self, *args, **kwargs):
    super(NecRow, self).__init__(*args, **kwargs) #*args, **kwargs
    # self.update(*args, **kwargs) # use the free update to set keys
    
    if not "uuid" in self:
      self["uuid"] = str(uuid.uuid4())
    if not "created_at" in self:
      self["created_at"] = time.time()
    if not "updated_at" in self:
      self["updated_at"] = self["created_at"]

  def __getattr__(self, attr):
    try:
      if attr in self:
        return self[attr]
      elif '__data__' in self:
        return getattr(self['__data__'], attr)
    except:
      raise #AttributeError, "Attribute not found: '%s'" % str(attr)

  def __setattr__(self, attr, value):
    self[attr] = value

  def __str__(self):
    return str(encoder.dumps(self, cls=NecroEncoder))
    # return str(encoder.dumps(self))

  def __repr__(self):
    return repr(encoder.dumps(self, cls=NecroEncoder))

  def __dict__(self):
    return self
  
def adapter(data):
  return encoder.dumps(data, cls=NecroEncoder)

def converter(s):
  return NecRow(**decoder.loads(s, object_hook=as_obj))

# Register the adapter/converter
sqlite3.register_adapter(NecRow, adapter)
sqlite3.register_converter("necro", converter)

class SubVerse(object):
  """

If you are familiar to database programming, you can think of SubVerse 
as something similar to a ResultSet object. Anytime a query is made 
of a Verse (or collection) object, this is what is returned. Therefore, 
this object contains most of the logic in terms of filtering, grouping and mapping data.

However, you can also use it without having to load data into an 
Underverse instance. It will also operate on a list of dicts out of the box.

.. ::

  >>> dicts = [{'name':'ed', 'fullname':'Ed Jones', 'password':'3d5_p455w0r6'},
  ...     {'name':'wendy', 'fullname':'Wendy Williams', 'password':'foobar'},
  ...     {'name':'mary', 'fullname':'Mary Contrary', 'password':'xxg527'},
  ...     {'name':'fred', 'fullname':'Fred Flinstone', 'password':'blah'}]

  >>> for user in SubVerse(dicts).find(Document.name == 'ed'):
  ... print user
  {'fullname': 'Ed Jones', 'password': '3d5_p455w0r6', 'name': 'ed'}
  
Notice that the found document doesn't have a *UUID*, *created_at* or *updated_at* keys. This is because it was never loaded into SQlite.

  """
  def __init__(self, division):
    super(SubVerse, self).__init__()
    self.division = division

  def find(self, *filters):
    """
    Filters a list of NecRows based on input conditions searches verse for true predicates

    You can look at the find function for *Verse* to get an example on how to query.
    """
    
    if len(filters) == 0:
      return SubVerse(self)
    
    def filter_(array, attr, predicate):
      true = []
      for row in array:
        if attr in row:
          if predicate(row):
            true.append(row)
      return true

    result = list(self)
    for _filter in filters:
      if hasattr(_filter, '__predicate__'):
        result = filter_(result, _filter._name, _filter._predicate)
      elif callable(_filter):
        result = _filter(result)
      else:
        raise TypeError, "Filter given isn't recognized"

    return SubVerse([r for r in result])

  def find_one(self, *filters):
    """
    Executes the same way as the ``find`` function, but only returns the first document.

    Returns None if no document is found matching conditions

    """
    fs = list(filters)
    fs.append(Document.limit(1))
    one = self.find(*fs)
    if len(one) == 1:
      return one[0]
    return None

  def paginate(self, count):
    """
    Pages the collection.

    If a collection has 5000 documents, calling ``verse.paginate(500)`` will return 10 pages of 500 documents each.

    """
    page = []
    for doc in self:
      
      if len(page) % count == 0:
        yield page
        page = []
      page.append(doc)
    if len(page) > 0:
      yield page

  # def __getattr__(self, attr):
    # for a in self.division:
      # print a
      # if attr in a or hasattr(a, attr):
        # yield a[attr]
      # yield getattr(a, attr)
      # elif 

#   def to_numpy(self, attr, _type):
#     """
# If NumPy is installed, this function will return a numpy.ndarray of the given attribute and of the given type.

# .. code-block:: python

#   for person, ppl in users.groupby('name'):

#     np_age = ppl.to_numpy('age', int)

#     print "AGE: %0.2f  %0.2f  %0.2f  %0.2f" % (np.min(np_age), np.max(np_age), np.mean(np_age), np.std(np_age))

#     """
#     if HAS_NUMPY:
#       return np.fromiter(getattr(self, attr), _type)
#     else:
#       raise Exception, "NumPy must be installed to use this function."

  def purify(self, *cols):
    """
Converts the given attributes to a NumPy recarray. This can provide a speed boost for data filtering, grouping and manipulation.

.. seealso::
  
  Please look at the Verse 'purify' documentation on how to use this functionality.

    """
    if HAS_NUMPY:
      return QuasiDead.from_dicts(self.division, *cols)
    else:
      raise Exception, "NumPy must be installed to use this function."

  def __len__(self):
    return len(self.division)

  def __iter__(self):
    return iter(self.division)

  def __getitem__(self, _slice):
    return self.division[_slice]

  def __expandmap(self, mapped_results):
    '''
    This class expands a dictionary, where the keys are iterables, 
      into a list with the mapped values as the last index.
    '''
    expanded_results = []
    for k, v in mapped_results.items():
      tmp = []
      if hasattr(k, '__iter__') and type(k) != str:
        tmp.extend(k)
      else:
        if len(k) > 0 and type(k) != str and type(k) != unicode:
          for l in k: tmp.append(l)
        else:
          tmp.append(k)
      tmp.append(SubVerse(v))
      expanded_results.append(tmp)
    return expanded_results

  def groupby(self, *attrs):
    """
Grouping data can be extremely powerful in data analysis. Therefore, data grouping and aggregation 
in Underverse does not hold back nor does it disappoint.

.. seealso::
  
  Please look at the groupby functionality for a Verse for a more comprehensive usage explanation.

    """
    groups = []
    for attr in attrs:
      if not attr in groups:
        if type(attr) == Document:
          groups.append(attr._name)
        elif type(attr) == str:
          groups.append(attr)
        else:
          raise TypeError, "Group by arguments must be either str or Document types"
    data = {}
    for a in self:
      key = []
      for attr in groups:
        if attr in a:
          key.append(a[attr])
      if not tuple(key) in data:
        data[tuple(key)] = []
      data[tuple(key)].append(a)
    
    return self.__expandmap(data)
    # for k, v in data.items():
      # yield k, SubVerse(v)

  def unique(self, *attrs):
    """
    Finds all the unique values for one or more columns
    """
    names = {}

    if len(attrs) == 0:
      raise TypeError, "Unique function requires data attributes to group on"
    elif len(attrs) == 1 and callable(attrs[0]):
      for k in attrs[0](iter(self)):
        if not tuple(k) in names:
          names[tuple(k)] = 0
          yield k
    else:
      
      def func(array, attrs):
        for a in array:
          ks = []
          for attr in attrs:
            if type(attr) is str:
              ks.append(a[attr])
            if type(attr) is Document:
              ks.append(a[attr._name])
          yield tuple(ks)
      
      for k in func(iter(self), attrs):
        if not tuple(k,) in names:
          names[tuple(k,)] = None
          yield k

  def map(self, function):
    """
    Calls a map function on the subverse.
    
    Mapper functions must or yield a two-value tuple. 
    This tuple represents a key-value pair. The key will be used to 
    aggregate similar data. The value can be anything, but remember 
    you will have a list of these values for every key.
    
    """
    names = OrderedDict()
    
    for k, v in function(iter(self)):
      if not k in names:
        names[k] = [v]
      else:
        names[k].append(v)
    for k, v in names.items():
      yield k, v

  def reduce(self, mapper_results, reducer):
    '''
This function 'reduces' the data returned from each map group. 
Reducers are meant to return a single value per group. However, due to python's
typing you can return a list, dictionary or tuple because they are objects themselves.
    '''
    new = OrderedDict()
    if reducer is not None:
      for key, group in mapper_results:
        new[key] = reducer(group)
    else:
      raise TypeError, "'reduce' argument cannot be 'None'. It must be callable."
    return new

  def mapreduce(self, mapper, reducer, expand=True, sort=True):
    '''
This function calls the map and reduce functions and returns 
the results as a dictionary.

However, if the **expand** option is ``True``, the results will be 
expanded into a list. This means that each row in the results 
will be a tuple, with the last value being the mapped data 
(returned as the value from the mapper function).
    '''
    d = self.reduce(self.map(mapper), reducer)

    if type(sort) is bool:
      if sort == True:
        d = OrderedDict(sorted(d.items()))
    elif type(sort) is str and len(sort) > 0:
      if sort.strip().lower() == 'map':
        d = OrderedDict(sorted(d.items(), key=lambda x: x[0]))
      elif sort.strip().lower() == 'reduce':
        d = OrderedDict(sorted(d.items(), key=lambda x: x[1]))
      else:
        raise ValueError, "The 'sort' argument can either be a boolean value or a string \n containing 'map' or 'reduce'. \n'"+str(type(sort))+"' arguments are not accepted."       

    if not expand:
      return d.items()
    else:
      return self.__expandmap(d)

  def orderby(self, *attrs):
    """
Orders a SubVerse by the attributes given
    """
    groups = []
    for attr in attrs:
      if not attr in groups:
        if type(attr) == Document:
          groups.append(attr._name)
        elif type(attr) == str:
          groups.append(attr)
        else:
          raise TypeError, "Order by arguments must be either str or Document types"
    if len(groups) == 0:
      return sorted(self)
    return P.orderby(*groups)(self)
    # return sorted(self, key=lambda x: tuple([getattr(x, arg) for arg in groups]))

  def limit(self, count):
    """
    Returns a user-defined limited number of documents.
    """
    return self.find(Document.limit(count))

  def skip(self, count):
    """
    Returns all documents after the user-defined number have been skipped.
    """
    return self.find(Document.skip(count))    

class Verse(object):
  """
A Verse is a class which represents a collection of similar data. 
If you're familiar to traditional relational databases, it's like a table. 
It can also be described as a document collection. In the background, it's 
actually a SQlite table. This class allows for standard CRUD 
(create, read, update and delete) operations.

.. code-block:: python

  uv = Underverse()
  
  #there are two ways to create a new document collection
  members = uv.members
  
  #or...
  accounts = uv.new("accounts")
  
The code above creates a new collection if it doen't currently exist 
or connects to an existing collection.  
  
  """
  def __init__(self, connection, name):
    super(Verse, self).__init__()
    self.connection = connection
    self.name = name
    self.len = -1
    self.dirty = True
    
    # self.connection.create_function("has", 2, has)
    # self.connection.create_function("get", 2, get)
    # self.connection.create_function("eq", 3, eq)
    self.cursor = self.connection.cursor()
    self.cursor.execute("create table if not exists %s (uuid unique, data necro);" % name)

  def add_column(self, array, name, commit=True):
    """
Adds an array with column names to the dataset.

.. note::
  
  The given array must be the same size as the entire 
  collection. If this doesn't fit with what you are 
  trying to do, just use the included update functionality.

    """
    if not hasattr(array, '__iter__'):
      raise TypeError, "Array must be iterable. The new column data is the 1st argument"
    if  len(array) != len(self):
      raise ValueError, "Input column must be the same size as the existing data. array: %s, existing: %s" % (len(array), len(self))
    if not type(name) is str:
      raise TypeError, "Column name must be a string"

    count = 0
    updates = []
    for a in self:
      a[name] = array[count]
      count += 1
      updates.append(a)

      if commit and count % 2500 == 0:
        self.update(updates)
        updates = []
    
    if commit:
      self.update(updates)

    return SubVerse(self)

  def from_array(self, array, names, commit=True):
    """

Adds an array with column names to the dataset.

.. code-block:: python

  uv = Underverse()
  table = uv.collection
  
  array = [[1,2,3],[4,5,6],[7,8,9]]

  table.from_array(array, names=['x', 'y', 'z'])

.. todo::
  
  Add predicate naming functionality. Every row will be passed 
  through each conditional function and return column names 
  if it's criterion is met. If no predicate matches the data, 
  either the row is skipped or is given default column names 
  (col1 - colN).

    """
    if not hasattr(array, '__iter__'):
      raise TypeError, "Array must be iterable"
    if len(names) != len(array[0]):
      raise ValueError, "Names and array arguments must have the same number of columns"
    
    data = []
    for a in array:
      row = {}
      for i, j in enumerate(a):
        row[names[i]] = j
      data.append(row)

    if commit:
      self.add(data)
    return SubVerse(data)

  def add(self, necro):
    """
Adds a NecRow or a list of NecRows to the database.

.. code-block:: python

  uv = Underverse()
  table = uv.helion
  
  #you can either add one row at a time
  table.add({'a':1, 'b': 2})

  # or do bulk inserts
  array = [
    {'a':1,'b':2,'c':3},
    {'a':4,'b':5,'c':6},
    {'a':7,'b':8,'c':9}]

  table.add(array)

.. note::
  
  Bulk inserts are noticibly faster

    """
    self.dirty = True
    if hasattr(necro, '__iter__') and type(necro) != NecRow and type(necro) != dict:

      def generator(new_converts):
        for n in new_converts:
          # print type(n)
          if type(n) is not NecRow:
            if not hasattr(n, '__dict__') and not type(n) is dict:
              necro = NecRow({'data':n})
            elif type(n) is dict:
              necro = NecRow(n)
            elif hasattr(n, '__dict__'):
                Underverse.create_mappers(type(n))
                necro = NecRow()
                necro.update({'__data__':n})
            else:
              necro = NecRow(dict(n))
            yield (str(necro.uuid), adapter(necro),)
          else:
            yield (str(n.uuid), adapter(n),)

      self.cursor.executemany("insert into %s (uuid, data) values (?, ?)" % self.name, generator(necro))
    elif type(necro) is NecRow:
      self.cursor.execute("insert into %s (uuid, data) values (?, ?)" % self.name, (necro.uuid, adapter(necro)))
    elif type(necro) is dict:
      necro = NecRow(dict(necro))
      self.cursor.execute("insert into %s (uuid, data) values (?, ?)" % self.name, (necro.uuid, adapter(necro)))
    elif hasattr(necro, '__dict__'):
      necro = NecRow(necro.__dict__)
      self.cursor.execute("insert into %s (uuid, data) values (?, ?)" % self.name, (necro.uuid, adapter(necro)))
    else:
      raise TypeError, "Add argument must be of type NecRow or a list of NecRows"

    self.connection.commit()
    return self.cursor.execute("select changes();").fetchone()[0]

  def all(self):
    """
Returns a SubVerse object containing all objects in the verse / collection

    """
    return SubVerse(iter(self))

  def __getattr__(self, attr):
    """

You can also get a list for a particular data attribute for the entire collection.

.. code-block:: python
  
  uv = Underverse("existing.db")
  
  #connect to the table
  members = uv.members
  
  for last_name in members.last_name:
    print last_name
    
The code above will loop over the entire collection of members and 
print the 'last_name' variable for each document. If a document does 
not have the 'last_name' attribute it is currently skipped. 

.. todo::
  
  Future versions may include a default value for documents not 
  containing a given attribute.

    """
    for a in self:
      if attr in a:
        yield a[attr]

  def __iter__(self):
    # return self.cursor.execute('select data as "data [necro]" from %s' % self.name)
    for n in self.cursor.execute('select data as "data [necro]" from %s' % self.name):
      yield n[0]

  def groupby(self, *attrs):
    """
The grouping of similar data is essential to most 
data analysis operations. This function is similar in 
nature to the *map* function with perhaps more readable syntax.
    
The *groupby* function doesn't have as much power as the *map* function,
however, this function aggregates data based on one or more attributes.
    
The map capability allows for more freedom with the possibility of 
calculated key-value pairs.

.. code-block:: python

  uv = Underverse()
  
  members = uv.members
  
  #insert data
  #...
  members.add(list_of_ppl)
  
  for state, inhabitants in members.groupby('state'):
    print "State: %s" % state
    print " - Population: %s" % len(inhabitants)
  
The code above will print all the states that have any 
members as it's citizens. The 'inhabitants' variable is a 
SubVerse instance containing all the citizens for the given 
state.

You can group by more than one column as well, such as ``members.groupy('state', 'county')``.
    
    """
    return SubVerse(iter(self)).groupby(*attrs)
    # for k, v in SubVerse(iter(self)).groupby(*attrs):
      # yield k, v

  def orderby(self, *attrs):
    """
Orders the collection by one or more columns

.. code-block:: python

  uv.docs.orderby('name', '-age')

The ``orderby`` functionality now has *ASC* and *DESC* 
capability. Descending order is achieved by pre-pending 
a '**-**' (negative sign or hyphen) to the column name.

However, you can also do this:

.. code-block:: python

  uv.docs.find(D.orderby('name', '-age'))

    """
    return P.orderby(*attrs)(self)
    # return P.orderby(*attrs)(SubVerse(self))
    # return SubVerse(self).orderby(*attrs)


  def unique(self, *attrs):
    """
Finds all the unique values for one or more columns

.. code-block:: python

  uv.verse.unique('name', 'age')

    """
    return SubVerse(iter(self)).unique(*attrs)
    # for u in SubVerse(iter(self)).unique(*attrs):
      # yield u

  def __len__(self):
    """

Returns the number of documents for the entire collection

    """
    if self.dirty or self.len == -1:
      self.dirty = False
      self.len = self.cursor.execute('select count(*) from %s' % self.name).fetchone()[0]
    return self.len

  def find(self, *filters):
    """
Searches verse for documents that meet all the predicates given. 
A SubVerse instance is returned containing all the found documents.
This is how querying is handled in the Underverse.

**Usage**::
  
  #create in-memory database
  uv = Underverse()

  # this loads a previous dump of an Underverse instance (`uv.dump("backup.sql")`)
  uv.load("backup.sql")

  #Document instances are the 'query' objects in the Underverse. 
  #Unlike SQLAlchemy, each table doesn't need to have a model. 
  #The Underverse uses one model object for all tables...
  #The 'country_code' is the attribute (or 'column' in traditional RDBMS) you are searching for.
  #In this case, the coder is searching for all members in the US.
  for person in uv.members.find(Document.country_code == "US"):
    print person

    #calculate stats
    #...
  
  #closes the connection
  uv.close()


Look at the `Document` documentation for all supported query operators.

    """
    return SubVerse(self.all()).find(*filters)

  def find_one(self, *filters):
    """

Searches verse for the first document that is true for all predicates given

    """
    return SubVerse(self.all()).find_one(*filters)

  def glob(self, globs, case_sensitive=True, operand=and_):
    """
Searches verse using SQlite GLOB statements. This is used to limit the number of documents being queried for.

**Example usage:**

For example, say you have an unstructured CSV (comma separated values) file with 
network traffic. The file has several different types of logging messages with 
both received and transmitted messages. You need to search for a specific 
logging message, but there's a lot of data and converting all the extra messages 
would be pointless and time consuming. Here's how you would filter out the extra 
messages and then group by IP address.

.. code-block:: python

  uv = Underverse()
  uv.load("logs.sql")
  logs = uv.logs
  
  #finds all WARNING messages that were received
  warnings_received = logs.glob('rxnet', 'WARNING')
  
  # groups the warnings by IP
  for ip, warnings in warnings_received.groupby("ip"):
    print '\\nIP Address: ' + str(ip)
    
    for warning in warnings:
      print ' - Description: ' + str(warning.desc)
  
.. note::
  
  **Performance Hint**

    Use this whenever you can to gain a performance boost. Because this 
    function uses SQlite's GLOB functionality, the documents can be searched before 
    they are converted to python dictionary. 

    """
    attrs = []
    
    def helper(attr):
      attr = attr.strip()
      if not attr.startswith("*"):
        attr = "*"+attr
      if not attr.endswith("*"):
        attr = attr+"*"
      if not case_sensitive:
        attr = attr.lower()
        if not attr in attrs:
          return " lower(data) glob '"+attr+"'"
      else:
        if not attr in attrs:
          return " data glob '"+attr+"'"
    
    if hasattr(globs, '__iter__'):
      for glob in globs:
        attrs.append(helper(glob))
    elif type(globs) is str:
        attrs.append(helper(globs))
    else:
      raise TypeError, "GLOBs must be strings or a list of strings"
    
    # print 'select data as "data [necro]" from %s where%s' % (self.name, operand.join(attrs))
    result = self.cursor.execute('select data as "data [necro]" from %s where%s' % (self.name, operand.join(attrs)))
    return SubVerse([r[0] for r in result])

  def update(self, necro):
    """
Updates a document or a list of documents.


**One possible usage..**
  
Say you have a website where members can comment on blog posts. You 
want to run some stats on how many posts each user has commented on. 
But when you were building your site you didn't think about that...

Let's say that you have already loaded your members into an Underverse 
instance. Being the brilliant coder you are, you have also given each 
member a list of their comments as well. You just want to add a comment 
count. Here's one way to do it.

.. code-block:: python

  # connect to SQlite database
  uv = Underverse("web.db")
  
  #select members table
  members = uv.members
  
  #update every member in collection
  for member in members:
    
    #assuming each member has a list of comments under member.comments
    #the same syntax is used for adding a new attribute of updating an existing attribute
    member.comment_count = len(member.comments)
    
    #update document: collection.update(document)
    members.update(member)

Bulk operations are normally faster. This is how you could do the same thing using bulk updates.

.. code-block:: python

  uv = Underverse("web.db")
  members = uv.members

  #create a list of documents to be updated
  updated = []
  
  #update every member in the collection
  for member in members:
    
    #assuming each member has a list of comments under member.comments
    #the same syntax is used for adding a new attribute of updating an existing attribute
    member.comment_count = len(member.comments)

    # add member to the list to be updated
    updated.append(member)
    
    # incremental updates can be achieved like so
    # updating every 2500 documents
    if len(updated) % 2500 == 0:
      members.update(updated)
      
      #don't forget to clear the queue
      updated = []

  # commit any remaining documents in queue
  members.update(updated)

.. note::
  
  **Performance Hint**

    Bulk updates are faster because SQlite is handling more of 
    the work. Any time you can limit function calls, do it. 

    """
    self.dirty = True
    if hasattr(necro, '__iter__') and type(necro) != NecRow:
      
      def generator(necros):
        for n in necros:
          if type(n) is not NecRow:
            if not hasattr(n, '__dict__'):
              necro = NecRow({'data':n})
            else:
              necro = NecRow(n.__dict__)
            yield (adapter(necro), necro.uuid,)
          else:
            n.updated_at = time.time()
            yield (adapter(n), n.uuid,)
      self.cursor.executemany("update %s set data=? where uuid=?;" % self.name, (generator(necro)))
    elif type(necro) is NecRow:
      necro.updated_at = time.time()
      self.cursor.execute("update %s set data='%s' where uuid='%s';" % (self.name, adapter(necro), necro.uuid))
    else:
      raise TypeError, "Update argument must be of type NecRow or a list of NecRows"

    self.connection.commit()
    return self.cursor.execute("select changes();").fetchone()[0]
  
  def remove(self, necro):
    """
Removes a documents or a list of documents.

This function operates just like the 'add' and 'update' 
operations. It accepts either a single document or a 
list of documents.

.. todo::
  
  Add exceptions to function (ie, raise TypeError for unrecognized arguments).

    """
    self.dirty = True
    if hasattr(necro, '__iter__') and type(necro) != NecRow:
      concat = []
      for n in necro:
        concat.append("'"+n.uuid+"'")
      self.cursor.execute("delete from %s where uuid in (%s);" % (self.name, ','.join(concat)))
    else:
      self.cursor.execute("delete from %s where uuid = ?;" % (self.name), necro.uuid)
    self.connection.commit()
    return self.cursor.execute("select changes();").fetchone()[0]

  def purge(self):
    """Removes all data in collection"""
    self.dirty = True
    self.cursor.execute("delete from %s;" % (self.name))
    self.connection.commit()
    return self.cursor.execute("select changes();").fetchone()[0]

  def map(self, function):
    """
    Calls a map function on the entire collection.
    
    Mapper functions must or yield a two-value tuple. 
    This tuple represents a key-value pair. The key will be used to 
    aggregate similar data. The value can be anything, but remember 
    you will have a list of these values for every key.
    
    """
    return SubVerse(self).map(function)
    # for k, v in SubVerse(self.all()).map(function):
      # yield k, v

  def reduce(self, function):
    """
    Calls a reduce function on the entire collection.
    
    """
    return SubVerse(self).reduce(function)
    # for k, v in SubVerse(self.all()).reduce(function):
      # yield k, v

  def mapreduce(self, mapper, reducer, expand=True, sort=False):
    """
    Calls map and reduce functions on the entire collection.
    """
    return SubVerse(self).mapreduce(mapper, reducer, expand, sort)
    # for k, v in SubVerse(self).mapreduce(mapper, reducer, expand, sort):
      # yield k, v

  def paginate(self, count):
    """
    Pages the collection.

    If a collection has 5000 documents, calling ``verse.paginate(500)`` will 
    return 10 pages of 500 documents each.
    """
    return self.all().paginate(count)
    # for page in self.all().paginate(count):
      # yield page

  def purify(self, *cols):
    """
Converts the given attributes to a NumPy recarray. This can provide for an easy transition to NumPy.

.. warning::
  
  The 'purify' function requires that NumPy is installed.

.. note::
  
  **Design History**:
  
    Just as an FYI, before Underverse was started, I worked on another analysis module 
    called bops. *bops* has similar functionality as Underverse, however, it is 
    limited to rectangular datasets. Bops used NumPy as it's foundation and was blazing fast
    because of it. However, it was also a memory hog. Many of the design features seen in 
    Underverse were originally 'fleshed out' in *bops*.
    
    I have rewritten the core of *bops* and added it as an extension to Underverse. 
    It is called the ``QuasiDead``.
    
    This extension allows for a subset of a Verse to be shoved temporarily into NumPy to give the 
    coder access to the added functionality NumPy provides. In order for this to work, the chosen 
    attributes are sliced from the document collection and molded into a structured data set 
    which NumPy can handle.
    
    Each ``QuasiDead`` instance can also be grouped, ordered and filtered.

.. note::
  
  **Performance Note**
  
    'Purifying' data does not result in any noticeable speed increase in the grouping, filtering 
    and sorting of data. To the contrary, it's been my experience that Python's built-in generators outperform NumPy. This is 
    mainly due to the cost of creating a recarray from the document store. Therefore, the only reason to 'purify' your data
    would be to make use of some of NumPy's functionality.

.. code-block:: python

  uv = Underverse()
  uv.load('data.sql')
  
  data = uv.data
  
  # creates a numpy recarray with 4 columns captured from the documents in the 'data' collection
  qd = data.purify('name', 'age', 'gender', 'country')
  
  # the new QuasiDead instance has limited functionality outside of it's code ``numpy.recarray``.
  # However, grouping and ordering can be achieved the same way as a document collection in Underverse.
  for country, citizens in qd.groupby('country'):
    print country, len(citizens)
    
  # numpy string array
  names = qd.name
  
.. seealso::
  
  Please look at the QuasiDead documentation for more information on what this unique class can be used for.

    """
    if HAS_NUMPY:
      return self.all().purify(*cols)#QuasiDead.from_dicts(self.division, *cols)
    else:
      raise Exception, "NumPy must be installed to use the 'purify' function."

  def __call__(self, *args):
    return self.find(*args)

  def limit(self, count):
    """
Returns a user-defined limited number of documents.

.. code-block:: python

  docs = uv.data.limit(50)

Or..

.. code-block:: python

  docs = uv.data.find(Document.age > 25).limit(50)

.. note::
  
  You can also chain the ``limit`` and ``skip`` functions together.

    """
    return self.all().limit(count)

  def skip(self, count):
    """
Returns all documents after the user-defined number have been skipped.

.. code-block:: python

  docs = uv.data.skip(50)

Or..

.. code-block:: python

  docs = uv.data.find(Document.age > 25).skip(50)

.. note::
  
  You can also chain the ``limit`` and ``skip`` functions together.

    """
    return self.all().skip(count)

class Underverse(object):
  """

This class is the core of the module. It provides the interface for either an in-memory or on-disk SQlite database. In-memory databases are noticably faster than files because of disk IO. However, this module provides functionality to both dump an in-memory database and load data into one.

Getting started is as easy as:

.. code-block:: python

  # importing the module
  from underverse import *
  
  # creates a connection to the ether
  uv = Underverse()

An on-disk data store can be created like so:
  
.. code-block:: python
  
  uv = Underverse('helion.db')
  
.. note::
  
  The extension doesn't matter, but traditionally SQlite databases are saved as either *.db* or *.sqlite*.

  """
  user_def_encoders = []
  user_def_decoders = []
  class_names = []
  
  def __init__(self, filename=None):
    super(Underverse, self).__init__()
    
    if filename is None:
      self.connection = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_COLNAMES)
    else:
      self.connection = sqlite3.connect(filename, detect_types=sqlite3.PARSE_COLNAMES)
    
    if HAS_NUMPY:
      numpy_encoder = (lambda obj: True if isinstance(obj, np.ndarray) else False, 
                lambda obj: {'__numpy__' : obj.tolist()})
      numpy_decoder = (lambda obj: True if '__numpy__' in obj else False, 
                lambda obj: np.array(obj['__numpy__']))
      Underverse.add_json_ext(numpy_encoder, numpy_decoder)

  def __iter__(self):
    """
The Underverse can be iterated over to produce a list of 'Verses' or tables in the underlying SQlite data store.
    
.. code-block:: python

  from underverse import Underverse
  uv = Underverse('/path/to/on-disk/database.db')

  #Here's how to print a list of the tables
  for verse in uv:
    print verse
    
    """
    for name in self.connection.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name;'):
      yield name[0]
  
  def __getattr__(self, attr):
    """
New 'Verses' or tables can be created easily

.. code-block:: python

  verse = uv.helion
  
The above statement creates a two-column table in the SQlite data store.

    """
    if not attr in self.__dict__:
      return self.new(attr)
  
  def new(self, name):
    """
You can also create a table like this:

.. code-block:: python

  #this creates a new collection called 'data'
  verse = uv.new('data')

  #perhaps an easier and more elegant method is the following
  table2 = uv.table2

The above statements create a two-column table in the SQlite data store.
    
    """
    return Verse(self.connection, name)

  def close(self):
    """
Closes the database connection

.. code-block:: python

  uv.close()

    """
    self.connection.close()

  def dump(self, filename):
    """
Dumps the underverse to a .sql file which can be loaded in the future.
    
.. code-block:: python

  uv.dump("backup.sql")
  
    """
    with open(filename, 'w') as f:
      for line in self.connection.iterdump():
        f.write('%s\n' % line)

  def load(self, filename):
    """
Loads a persited underverse. Using this method to populate a collection is substantially faster than loading all the data using the *add* method.

.. code-block:: python

  uv.load("backup.sql")

    """
    with open(filename, 'r') as f:
     self.connection.cursor().executescript(f.read())

  @staticmethod
  def add_json_ext(encoder=None, decoder=None):
    """
Allows user to define custom JSON encoding and decoding.

.. note::

  This is an advanced feature. This is only useful if you want certain objects to be encoded in a custom way. Most users will never need to use this functionality.

.. code-block:: python

  # Here's a possible use case:
  # The following code transforms a NumPy array into a JSON list and back again 
  # during the encoding and decoding process

  # if the object is a numpy.ndarray, then it's converted to a Python list 
  # and saved in a Python dict with '__numpy__' as it's key
  numpy_encoder = (lambda obj: True if isinstance(obj, np.ndarray) else False, 
            lambda obj: {'__numpy__' : obj.tolist()})

  # when decoding, if the dict has a key '__numpy__', 
  # then the list is converted to a numpy.ndarray object
  numpy_decoder = (lambda obj: True if '__numpy__' in obj else False, 
            lambda obj: np.array(obj['__numpy__']))

  Underverse.add_json_ext(numpy_encoder, numpy_decoder)

**User Defined Encoders**:

  Encoders must be a two-element tuple. The first element determines when to use the custom encoding logic. The second element determines how to save the object.

**User Defined Decoders**:

  Decoders, like encoders must be a two-element tuple. The first element, once again, determines when to use the custom decoding logic. The second element determines how to read / decode the object into the desired object.

    """
    if encoder is not None and hasattr(encoder, '__iter__') and len(encoder) == 2:
        # user_def_encoders.append([lambda obj: True if isinstance(obj, np.ndarray) else False, lambda obj: {'__numpy__' : obj.tolist()}])
        Underverse.user_def_encoders.append(encoder)
    if decoder is not None and hasattr(decoder, '__iter__') and len(decoder) == 2:
        # user_def_decoders.append([lambda obj: True if '__numpy__' in obj else False, lambda obj: np.array(obj['__numpy__'])])
        Underverse.user_def_decoders.append(decoder)

  @staticmethod
  def create_encoder_decoder(_cls):
    def ret_type(**kwargs):
      c = _cls.__new__(_cls)
      c.__dict__.update(**kwargs)
      return c
  
    encode = (lambda obj: True if isinstance(obj, _cls) else False, lambda obj: {'__%s__' % _cls.__name__ : obj.__dict__})
    decode = (lambda obj: True if '__%s__' % _cls.__name__ in obj else False, lambda obj: ret_type(**obj['__%s__' % _cls.__name__]))
    Underverse.add_json_ext(encode, decode)
    return True

  @staticmethod
  def create_mappers(*_cls):
    """
This code will allow for the decoding of previously JSON-encoded Python objects.

.. note::
  
  This method is only required for the decoding of Python objects. Encoding 
  is handled automatically for all but the most demanding of circumstances.

**Loading of Python objects** (script1.py)::

  class Comment(object):
    def __init__(self, text):
      super(Comment, self).__init__()
      self.text = text
    
    def len(self):
      return len(self.text)
  
  class Message(object):
    def __init__(self, x, y, z):
      super(Message, self).__init__()
      self.x = x
      self.y = y
      self.z = z
      self.n = np.arange(5) # numpy array
      self.m = Comment('Starting to come together')

  class AnotherTestClass(object):
    def __init__(self, text):
      super(AnotherTestClass, self).__init__()
      self.a = Comment(text)
      self.msg = Message(2,3,4)
      self.array = range(3)
  
  uv = Underverse()
  
  test = uv.test
  test.add(AnotherTestClass('test #1'))
  
  uv.dump('obj_testing.sql')


.. note::

  If you notice, none of the above classes require a 'base class' in order 
  to interact with Underverse. This allows the coder to use existing 
  classes without ANY changes as all...
  
  This is one of many design elements which separates Underverse from all previous ORMs and ODMs.


**Decoding of JSON into Python objects** (script2.py)::

  from underverse import Underverse
  from some_module import AnotherTestClass, Comment, Message

  # creates the object mappers used to decode these three class
  # notice that numpy.ndarray is not in the list, Underverse provides 
  # this capability as long as NumPy is installed
  Underverse.create_mappers(AnotherTestClass, Comment, Message)

  uv = Underverse()
  uv.load('obj_testing.sql')
  
  for r in self.uv.test:
    print r.msg.m.text


The code above was slightly modified from several test cases. Therefore, 
it should be guaranteed to work.. The example given obviously isn't 
a representation of an actual application, but rather an example of 
the existing support for nested class structures. The JSON is
decoded flawlessly to reveal nearly exact duplicates of the objects
that were encoded originally. The only difference are the memory 
spaces they reside in. 

.. note::
  
  This method is **ONLY** required if the loading and reading of the 
  persisted documents happen in different scripts. Otherwise, Underverse 
  will remember the object classes from when they were loaded originally.

    """
    for c in _cls:
      Underverse.create_encoder_decoder(c)
    return True


if __name__ == '__main__':
  import time
  from test_data_gen import Person
  from model import Document
  
  uv = Underverse()
  # uv = Underverse(filename='testing.db')
  # uv.load('out.sql')

  verse = uv.mars
  verse.purge()
  # print verse.count()

  v = []
  start = time.clock()
  for i in range(5000):
    v.append(Person())
    if len(v) % 2500 == 0:
      verse.add(v)
      v = []
  verse.add(v)
  print "adding all: ", time.clock() - start


  # start = time.clock()
  # for i in range(50):
  #   verse.add(Person())
  # print "adding: ", time.clock() - start

  # print verse.cursor.execute("select data as 'data [necro]' from first where has('name', data)").fetchall()
  # start = time.clock()
  # c = 0
  # for v in verse:
  #   if 'F' in v.gender and v.age < 25:
  #     c += 1

  # print "hard-coded: ", time.clock() - start, c  
  
  # start = time.clock()
  # c = 0
  # for i in verse.find(('gender', ['eq', 'F']), ('age', ['lt', 25])):
    # c+= 1
  # print "predicate: ", time.clock() - start, c

  # results = verse.find(Document.name == "Max")

  # print len(verse)
  # print

  # print
  # start = time.clock()
  # c = 0
  # for i in verse.find_one(Document.name == "Max"):
    # print i
    # c+= 1
  # print "filter - eq: ", time.clock() - start, c

  # print
  # start = time.clock()
  # c = 0
  # for i in verse.glob('Max'):#.where(('name', ['search', 'Max'])):
  # for i in verse.glob(('Max',)):#.where(('name', ['search', 'Max'])):
    # print i
    # c+= 1
  # print "glob: ", time.clock() - start, c

  # start = time.clock()
  # c = 0
  # for i in results.find(Document.skip(2)):
  #   # print i
  #   c+= 1
  # print "filter skip: ", time.clock() - start, c

  # start = time.clock()
  # c = 0
  # for i in results[2:]:
  #   # print i
  #   c+= 1
  # print "filter skip slice: ", time.clock() - start, c

  # start = time.clock()
  # c = 0
  # for i in results.find(Document.limit(5)):
  #   # print i
  #   c+= 1
  # print "filter limit: ", time.clock() - start, c

  # start = time.clock()
  # c = 0
  # for i in results[:5]:
  #   # print i
  #   c+= 1
  # print "filter limit slice: ", time.clock() - start, c

  # start = time.clock()
  # c = 0
  # # for i in verse.find(Document.name == "Max", Document.limskip(2, 5)):
  # for i in results >> stream.item[:5]:
  #   # print i
  #   c+= 1
  # # print "filter skip / limit: ", time.clock() - start, c
  # print "filter slice: ", time.clock() - start, c

  # start = time.clock()
  # c = 0
  # # for i in verse.find(Document.name == "Max", Document.limskip(2, 5)):
  # for i in results[:5]:
  #   # print i
  #   c+= 1
  # # print "filter skip / limit: ", time.clock() - start, c
  # print "filter slice 2: ", time.clock() - start, c
  # # print verse.find(Document.name == "Max")[]

  # start = time.clock()
  # c = 0
  # for i in results >> stream.drop(5) >> stream.take(5):
  #   # print i
  #   c+= 1
  # print "filter limit skip: ", time.clock() - start, c

  # print
  # start = time.clock()
  # c = 0
  # for i in verse.find(Document.name == "Max", Document.limskip(0, 5)):
  #   # print i
  #   c+= 1
  # print "filter limskip: ", time.clock() - start, c

  #Paging
  # p = 0
  # for page in verse >> stream.chop(500):
  #   print "Page %s" % p, len(page)
  #   p += 1

  #Paging
  p = 0
  for page in verse.paginate(500):
    print "Page %s" % p, len(page)
    p += 1

  exit()

  # print
  # start = time.clock()
  # c = verse.remove(verse.find(('name', ['search', 'John'])))
  # print "bulk remove: ", time.clock() - start, c

  start = time.clock()
  c = 0
  for i in verse.unique('name'):
    c+= 1
  print "uniq names: ", time.clock() - start, c

  def names(array):
    for a in array:
      yield a['name']

  start = time.clock()
  c = 0
  for i in verse.unique(names):
    c+= 1
  print "uniq names function: ", time.clock() - start, c

  start = time.clock()
  c = 0
  for i in verse.unique(Document.name):
    c+= 1
  print "uniq names filter: ", time.clock() - start, c

  start = time.clock()
  c = 0
  for i, j in verse.groupby('name'):
    c+= 1
    # print i, len(j)
  print "groupby names: ", time.clock() - start, c

  def names(array):
    for a in array:
      yield (a['name'], a['age'] // 10 * 10,), a

  start = time.clock()
  c = 0
  for i, j in verse.map(names):
    c+= 1
    # print i, len(j)
  print "map names: ", time.clock() - start, c

  # uv.dump('out.sql')
  # verse.purge()
  uv.close()
  print "Done."



