from predicates import Predicate as P
import stream

__all__ = ['DocumentModel', 'Document']

class DocumentModel(type):
	"""Base class for Model"""

	def __getattr__(self, attr):
		return Document(attr)

class Document(object):
	"""
This class is the main class for handling document queries. 

Here are some query examples::

	print Document.age < 5
	print Document.age <= 5
	print Document.age > 5
	print Document.age >= 5
	print Document.age == 5
	print Document.age != 5
	print Document.name.len(5)
	print Document.age.btw(20, 50)
	print Document.age
	print Document.name.type(str)
	print Document.name.in_(['Max'])
	print Document.name.nin(['Max'])
	print Document.name.match('Max')
	print Document.name.search('ax')
	print Document.name.nmatch('Max')
	print Document.name.nsearch('Max')

	# cheezy example
	def email_search(value, domain=None):
		if domain in value:
			return True
		else:
			return False

	#defining you own predicate functions...
	# if the function returns 'True', then the object will be included in the results, otherwise, it will be left out.
	#also, any arguments passed to the 'udp' function, they will be passed to the given predicate as input. 
	for d in verse.find(Document.email.udp(email_search, domain='gmail')):
		print d

	# for the above example, you could have done it like this.
	for d in verse.find(Document.email.search('gmail')):
		print d

To query for the first object, use the ``find_one`` function instead of ``find``.::

	# to find the first document, call find_one instead of find
	for d in verse.find_one(Document.email.udp(email_search, domain='gmail')):
		print d

	"""
	__metaclass__ = DocumentModel

	def __init__(self, name):
		super(Document, self).__init__()
		self._name = name
		self._predicate = P.exists(name)
		self._desc = "has key: "+name

	def __lt__(self, value):
		self._desc = "%s < %s" % (self._name, value)
		self._predicate = P.lt(self._name, value)
		return self

	def __le__(self, value):
		self._desc = "%s <= %s" % (self._name, value)
		self._predicate = P.lte(self._name, value)
		return self

	def __gt__(self, value):
		self._desc = "%s > %s" % (self._name, value)
		self._predicate = P.gt(self._name, value)
		return self

	def __ge__(self, value):
		self._desc = "%s >= %s" % (self._name, value)
		self._predicate = P.gte(self._name, value)
		return self

	def __eq__(self, value):
		self._desc = "%s == %s" % (self._name, value)
		self._predicate = P.eq(self._name, value)
		return self

	def __ne__(self, value):
		self._desc = "%s != %s" % (self._name, value)
		self._predicate = P.ne(self._name, value)
		return self

	def len(self, value):
		self._desc = "len(%s) == %s" % (self._name, value)
		self._predicate = P.len(self._name, value)
		return self

	def btw(self, left, right):
		self._desc = "%s < %s < %s" % (left, self._name, right)
		self._predicate = P.btw(self._name, left, right)
		return self

	def udp(self, function, *args, **kwargs):
		self._desc = "%s(%s" % (function.__name__, self._name)
		if len(args) > 0:
			self._desc += ", " + ', '.join(args)
		if len(kwargs) > 0:
			self._desc += ", " + ', '.join(['%s=%s' % (k, v) for k, v in kwargs.items()])
		self._desc += ")"
		self._predicate = P.udp(self._name, function, *args, **kwargs)
		return self

	def type(self, value):
		self._desc = "type(%s) == %s" % (self._name, value.__name__)
		self._predicate = P.type_(self._name, value)
		return self

	def in_(self, value):
		self._desc = "%s in %s" % (self._name, value)
		self._predicate = P.in_(self._name, value)
		return self

	def nin(self, value):
		self._desc = "%s not in %s" % (self._name, value)
		self._predicate = P.nin(self._name, value)
		return self

	def match(self, value):
		self._desc = "re.compile('%s').match(%s)" % (value, self._name)
		self._predicate = P.match(self._name, value)
		return self

	def search(self, value):
		self._desc = "re.compile('%s').search(%s)" % (value, self._name)
		self._predicate = P.search(self._name, value)
		return self

	def nmatch(self, value):
		self._desc = "not re.compile('%s').match(%s)" % (value, self._name)
		self._predicate = P.nmatch(self._name, value)
		return self

	def nsearch(self, value):
		self._desc = "not re.compile('%s').search(%s)" % (value, self._name)
		self._predicate = P.nsearch(self._name, value)
		return self

	@classmethod
	def	__orderby__(self, array, key=None):
		return sorted(array, key=key)

	@staticmethod
	def orderby(*args):
		print args
		if len(args) > 0:
			return P.udf(Document.__orderby__, key=P.orderby(*args))
		else:
			raise TypeError, "Order by must have string arguments"

	@classmethod
	def __lim__(self, array, count=2**32):
		c = 0
		docs = []
		for doc in array:
			if c < count:
				docs.append(doc)
			c += 1
		return docs

	@staticmethod
	def limit(value):
		if not type(value) is int:
			raise ValueError, "Limit predicates must be integers: limit(5)"

		return P.udf(Document.__lim__, count=value)

	@classmethod
	def __limskip__(self, array, _skip=0, _limit=2**32):
		c = 0
		l = 0
		docs = []
		for doc in array:
			if c >= _skip and l < _limit:
				docs.append(doc)
				l += 1
			c += 1
		return docs

	@staticmethod
	def limskip(_skip, _limit):
		if not type(_skip) is int:
			raise ValueError, "Skip argument must be an integer: K.limskip(2, 5)"
		if not type(_limit) is int:
			raise ValueError, "Limit argument must be an integer: K.limskip(2, 5)"

		return P.udf(Document.__limskip__, _skip, _limit)

	@classmethod
	def __skip__(self, array, _skip=0):
		c = 0
		docs = []
		for doc in array:
			if c >= _skip:
				docs.append(doc)
			c += 1
		return docs

	@staticmethod
	def skip(value):
		if not type(value) is int:
			raise ValueError, "Skip predicates must be integers: K.skip(5)"

		return P.udf(Document.__skip__, value)

	def __exists__(self):
		return P.exists(self._name)

	def __predicate__(self):
		return self._predicate

	@property
	def exists(self):
		return self.__exists__()

	@property
	def predicate(self):
		return self.__predicate__()

	def __str__(self):
		return "<Document: \"%s\">" % self._desc


if __name__ == '__main__':
	from underverse import *
	# import Model as F

	uv = Underverse()
	verse = uv.test

	emails = ['gmail.com', 'hotmail.com', 'yahoo.com', 'gmail.com', 'gmail.com']
	a = range(5)
	b = range(5)

	verse.from_array(zip(a, b, emails), names=['x', 'y', 'email'])

	for doc in verse:
		print doc

	# print Model.__dict__

	# print Model.__getattr__('name')

	# print Model('name') < 5
	print Document.age < 5, Document.age <= 5
	print Document.age < 5
	print Document.age <= 5
	print Document.age > 5
	print Document.age >= 5
	print Document.age == 5
	print Document.age != 5
	print Document.name.len(5)
	print Document.age.btw(20, 50)
	print Document.age

	print Document.name.type(float)
	print Document.name.in_(['Max'])
	print Document.name.nin(['Max'])
	print Document.name.match('Max')
	print Document.name.search('ax')
	print Document.name.nmatch('Max')
	print Document.name.nsearch('Max')

	def email_search(value, domain=None):
		if domain in value:
			return True
		else:
			return False

	for d in verse.find(Document.email.udp(email_search, domain='gmail')):
		print d

	print
	# for d in verse.find_one(Document.email.udp(email_search, domain='gmail')):
	# 	print d

	print 
	for d in verse.find(Document.email.search('gmail'), Document.x == 0):
		print d

	# for d in verse.find_new(Model.email.udp(email_search, domain='gmail')):
		# print d
