"""
Underverse is named after the destination of the Necromonger's from the 
Chronicles of Riddick. This module is so named because the author likes the movie.

The Underverse is an Object Document Mapper, or ODM. An ODM performs the same 
functions as an ORM (Object Relational Mapper) does for relational data. 

In Python, SQLAlchemy is the ORM of choice. The Underverse follows the same 
design principles seen in SQLAlchemy. So if you've used it before, this module 
should feel right at home.

Background
==========

At it's core, the Underverse is a JSON-based document store built on top of SQlite. JSON was chosen over pickle because of it's size, simplicity, readbility and speed. These features, combined with SQlite, make for a simple and elegant solution.

Everything in the Underverse is written to use Python's generators to provide for a streamlined process for data access and manipulation. The module provides ways to quickly load, update, group, map and filter data.


"""
import sqlite3, collections, stream, uuid, time
from predicates import Predicate as P
from model import Model

try:
  import simplejson as json
  print "Using simplejson..."
except ImportError:
  import json
  print "Using json..."

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
# add verse slicing capability using sqlite rowid or stream
#+ add a purge all function
# add logging capability
#   no glob results, # of
#    found #
#+ add update all functionality, like add_all
#+ add where select functionality
# and/or functionality?
#+ add map functionality
#  add reduce functionality
#+ merge add / add_all functions

#implement paging by using stream.chop

# subclass stream?
#   no, overload operators
# 
#bulk insert: verse << list of rows
#insert: verse < row
#update: row < dict, row + dict
#remove: verse - row,
#purge: verse >> NULL (new class)

#+add sqlalchemy-ish functionality
#+   operators on column names
#-   Predicates with overloaded operators? No
#
#+ Model class with operator overloading which returns a predicate for filtering
#   Much more readable
#
#   Model.name == 'Max'
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
#base class

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

class NecRow(dict):
  """
  Base follower
  """
  def __init__(self, *args, **kwargs):
    super(NecRow, self).__init__(*args, **kwargs)
    # self.update(dict(*args, **kwargs)) # use the free update to set keys
    
    if not "uuid" in self:
      self["uuid"] = str(uuid.uuid4())
    if not "created_at" in self:
      self["created_at"] = time.time()
    if not "updated_at" in self:
      self["updated_at"] = self["created_at"]

  def __getattr__(self, attr):
    return self[attr]

  def __setattr__(self, attr, value):
    self[attr] = value

  def __str__(self):
    return str(encoder.dumps(self))

  def __repr__(self):
    return repr(encoder.dumps(self))

  def __dict__(self):
    return self

def adapter(data):
  return encoder.dumps(data)

def converter(s):
  return NecRow(**decoder.loads(s))

# Register the adapter/converter
sqlite3.register_adapter(NecRow, adapter)
sqlite3.register_converter("necro", converter)

class SubVerse(object):
  """docstring for SubVerse"""
  def __init__(self, division):
    super(SubVerse, self).__init__()
    self.division = division

  def find(self, *filters):
    """
    Filters a list of NecRows based on input conditions
    searches verse for true predicates
    """
    
    result = iter(self)
    attrs = []
    reserved = ["limit_", "skip_", "limskip_"]
    for _filter in filters:
      if not _filter in attrs and not _filter._name in reserved:
        attrs.append(_filter)
        result = result >> stream.filter(_filter.exists)
      if not _filter._name in reserved:
        result = result >> stream.filter(_filter.predicate)
      else:
        result = result >> _filter._predicate
    # if count is None:
    return SubVerse([r for r in result])
    # elif count is not None:
      # return SubVerse([r for i, r in enumerate(result) if i >= skip and i < (skip + count)])

  def find_one(self, *filters):
    """
    searches verse for the first true predicates
    """
    fs = list(filters)
    fs.append(K.limit(1))
    return self.find(*fs)

  def paginate(self, count):
    """
    Pages the SubVerse
    """
    for page in self >> stream.chop(count):
      yield page

  def __getattr__(self, attr):
    for a in self:
      if attr in a:
        yield a[attr]

  def __len__(self):
    return len(self.division)

  def __iter__(self):
    return iter(self.division)

  def __getitem__(self, _slice):
    return self.division[_slice]

  def groupby(self, *attrs):
    """
    The grouping of similar data is essential to most 
    data analysis operations. This function is similar in 
    nature to the *map* function with perhaps more readable syntax.
    
    The *groupby* function doesn't have as much power as the *map* function,
    however, this function aggregates data based on one or more attributes.
    
    The map capability allows for more freedom with the possibility of calculated key-value pairs.
    """
    groups = []
    for attr in attrs:
      if not attr in groups:
        groups.append(attr)
    data = {}
    for a in self:
      key = []
      for attr in groups:
        if attr in a:
          key.append(a[attr])
      if not tuple(key) in data:
        data[tuple(key)] = []
      data[tuple(key)].append(a)
    
    for k, v in data.items():
      yield k, SubVerse(v)

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
            if type(attr) is Model:
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
    names = {}
    
    for k, v in function(iter(self)):
      if not k in names:
        names[k] = [v]
      else:
        names[k].append(v)
    for k, v in names.items():
      yield k, v

class Verse(object):
  """

A Verse is a class which represents similar data. In the background, it's actually a SQlite table. This class allows for standard CRUD (create, read, update and delete) operations. 
  
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
  table = uv.table
  
  array = [[1,2,3],[4,5,6],[7,8,9]]

  table.from_array(array, names=['x', 'y', 'z'])

.. todo::
  
  Add predicate naming functionality. Every row will be passed through each conditional function and return column names if it's criterion is met. If no predicate matches the data, either the row is skipped or is given default column names (col1 - colN).

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
  table = uv.table
  
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
    if hasattr(necro, '__iter__') and type(necro) != NecRow:

      def generator(new_converts):
        for n in new_converts:
          # print type(n)
          if type(n) is not NecRow:
            if not hasattr(n, '__dict__') and not type(n) is dict:
              necro = NecRow({'data':n})
            elif type(n) is dict:
              necro = NecRow(n)
            else:
              necro = NecRow(n.__dict__)
            yield (str(necro.uuid), adapter(necro),)
          else:
            yield (str(n.uuid), adapter(n),)

      self.cursor.executemany("insert into %s (uuid, data) values (?, ?)" % self.name, generator(necro))
    elif type(necro) is NecRow:
      self.cursor.execute("insert into %s (uuid, data) values (?, ?)" % self.name, (necro.uuid, adapter(necro)))
    elif hasattr(necro, '__dict__') or type(necro) is dict:
      necro = NecRow(necro.__dict__)
      self.cursor.execute("insert into %s (uuid, data) values (?, ?)" % self.name, (necro.uuid, adapter(necro)))
    else:
      raise TypeError, "Add argument must be of type NecRow or a list of NecRows"

    self.connection.commit()
    return self.cursor.execute("select changes();").fetchone()[0]

  def all(self):
    """
Returns an iterator over all NecRows in the verse / database
    


    """
    return SubVerse(iter(self))

  def __getattr__(self, attr):
    for a in self:
      if attr in a:
        yield a[attr]

  def __iter__(self):
    for n in self.cursor.execute('select data as "data [necro]" from %s' % self.name):
      yield n[0]

  def groupby(self, *attrs):
    """
    The grouping of similar data is essential to most 
    data analysis operations. This function is similar in 
    nature to the *map* function with perhaps more readable syntax.
    
    The *groupby* function doesn't have as much power as the *map* function,
    however, this function aggregates data based on one or more attributes.
    
    The map capability allows for more freedom with the possibility of calculated key-value pairs.
    """
    for k, v in SubVerse(iter(self)).groupby(*attrs):
      yield k, v

  def unique(self, *attrs):
    """
    Finds all the unique values for one or more columns
    """
    for u in SubVerse(iter(self)).unique(*attrs):
      yield u

  def __len__(self):
    """
    returns the number os necromongers
    """
    if self.dirty or self.len == -1:
      self.dirty = False
      self.len = self.cursor.execute('select count(*) from %s' % self.name).fetchone()[0]
    return self.len

  def find(self, *filters):
    """
    searches verse for true predicates
    """
    return SubVerse(self.all()).find(*filters)

  def find_one(self, *filters):
    """
    searches verse for the first true predicates
    """
    fs = list(filters)
    fs.append(K.limit(1))
    return SubVerse(self.all()).find(*fs)

  def glob(self, globs, case_sensitive=True, operand=and_):
    """
    searches verse using GLOBs
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
    updates a NecRow or a list of NecRows
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
    removes a NecRow or a list of NecRows
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
    """
    removes all data in verse
    """
    self.dirty = True
    self.cursor.execute("delete from %s;" % (self.name))
    self.connection.commit()
    return self.cursor.execute("select changes();").fetchone()[0]

  def map(self, function):
    """
    Calls a map function on the entire verse.
    
    Mapper functions must or yield a two-value tuple. 
    This tuple represents a key-value pair. The key will be used to 
    aggregate similar data. The value can be anything, but remember 
    you will have a list of these values for every key.
    
    """
    for k, v in SubVerse(iter(self)).map(function):
      yield k, v


class Underverse(object):
  """
  
The Underverse
==============

This class is the core of the module. It provides the interface for either an in-memory or on-disk SQlite database. In-memory databases are noticably faster than files because of disk IO. However, this module provides functionality to both dump an in-memory database and load data into one.

Getting started is as easy as:

.. code-block:: python

  # importing the module
  from underverse import *
  
  # creates a connection to the ether
  uv = Underverse()

An on-disk data store can be created like so:
  

.. code-block:: python
  
  uv = Underverse('helio.uv')
  
.. note::
  
  The extension doesn't matter, but traditionally SQlite databases are saved as either *.db* or *.sqlite*.

  """
  def __init__(self, filename=None):
    super(Underverse, self).__init__()
    
    if filename is None:
      self.connection = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_COLNAMES)
    else:
      self.connection = sqlite3.connect(filename, detect_types=sqlite3.PARSE_COLNAMES)

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

  verse = uv.new('table')
    
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
Dumps the underverse
    
.. code-block:: python

  uv.dump("backup.db")
  
    """
    with open(filename, 'w') as f:
      for line in self.connection.iterdump():
        f.write('%s\n' % line)

  def load(self, filename):
    """
Loads a persited underverse

.. code-block:: python

  uv.load("backup.db")

    """
    with open(filename, 'r') as f:
     self.connection.cursor().executescript(f.read())


if __name__ == '__main__':
  import time
  from test_data_gen import Person
  from model import Model
  
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

  # results = verse.find(Model.name == "Max")

  print len(verse)
  print

  # print
  start = time.clock()
  c = 0
  for i in verse.find(Model.name == "Max"):
    # print i
    c+= 1
  print "filter - eq: ", time.clock() - start, c

  # print
  start = time.clock()
  c = 0
  # for i in verse.glob('Max'):#.where(('name', ['search', 'Max'])):
  for i in verse.glob(('Max',)):#.where(('name', ['search', 'Max'])):
    # print i
    c+= 1
  print "glob: ", time.clock() - start, c

  # start = time.clock()
  # c = 0
  # for i in results.find(Model.skip(2)):
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
  # for i in results.find(Model.limit(5)):
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
  # # for i in verse.find(Model.name == "Max", Model.limskip(2, 5)):
  # for i in results >> stream.item[:5]:
  #   # print i
  #   c+= 1
  # # print "filter skip / limit: ", time.clock() - start, c
  # print "filter slice: ", time.clock() - start, c

  # start = time.clock()
  # c = 0
  # # for i in verse.find(Model.name == "Max", Model.limskip(2, 5)):
  # for i in results[:5]:
  #   # print i
  #   c+= 1
  # # print "filter skip / limit: ", time.clock() - start, c
  # print "filter slice 2: ", time.clock() - start, c
  # # print verse.find(Model.name == "Max")[]

  # start = time.clock()
  # c = 0
  # for i in results >> stream.drop(5) >> stream.take(5):
  #   # print i
  #   c+= 1
  # print "filter limit skip: ", time.clock() - start, c

  # print
  # start = time.clock()
  # c = 0
  # for i in verse.find(Model.name == "Max", Model.limskip(0, 5)):
  #   # print i
  #   c+= 1
  # print "filter limskip: ", time.clock() - start, c

  #Paging
  # p = 0
  # for page in verse >> stream.chop(500):
  #   print "Page %s" % p
  #   p += 1

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
  for i in verse.unique(Model.name):
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



