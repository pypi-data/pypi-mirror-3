from predicates import Predicate as P
import stream

__all__ = ['Model']

class DataModel(type):
	"""docstring for Model"""

	def __getattr__(self, attr):
		return Model(attr)

class Model(object):
	"""docstring for Model"""
	__metaclass__ = DataModel

	def __init__(self, name):
		super(Model, self).__init__()
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
	def limit(self, value):
		if not type(value) is int:
			raise ValueError, "Limit predicates must be integers: limit(5)"
			# yield stream.take(v)

		self._name = "limit_"
		self._desc = "limit('%s')" % (value)
		self._predicate = stream.take(value)
		return self

	@classmethod
	def limskip(self, _skip, _limit):
		if not type(_skip) is int:
			raise ValueError, "Skip argument must be an integer: K.limskip(2, 5)"
		if not type(_limit) is int:
			raise ValueError, "Limit argument must be an integer: K.limskip(2, 5)"

		self._name = "limskip_"
		self._desc = "skip('%s'), limit(%s)" % (_skip, _limit)
		# self._predicate = _skip
		# self._predicate = stream.filter(_skip)
		self._predicate = stream.drop(_skip) >> stream.take(_limit)
		return self

	@classmethod
	def skip(self, value):
		if not type(value) is int:
			raise ValueError, "Skip predicates must be integers: K.skip(5)"

		self._name = "skip_"
		self._desc = "skip('%s')" % (value)
		# self._predicate = _skip
		# self._predicate = stream.filter(_skip)
		self._predicate = stream.drop(value)
		return self

	# def __call__(self, *args, **kwargs):
		# return self._predicate(*args, **kwargs)

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
		return "<Model: \"%s\">" % self._desc


if __name__ == '__main__':
	from underverse import *
	# import Model as F

	uv = Underverse()
	verse = uv.test

	emails = ['gmail.com', 'hotmail.com', 'yahoo.com', 'gmail.com', 'gmail.com']
	a = range(5)
	b = range(5)

	verse.from_array(zip(a, b, emails), names=['x', 'y', 'email'])

	# print Model.__dict__

	# print Model.__getattr__('name')

	# print Model('name') < 5
	print Model.name < 5
	print Model.name <= 5
	print Model.name > 5
	print Model.name >= 5
	print Model.name == 5
	print Model.name != 5
	print Model.name.len(5)
	print Model.name.btw(2, 5)
	print Model.name

	print Model.name.type(float)
	print Model.name.in_(['Max'])
	print Model.name.nin(['Max'])
	print Model.name.match('Max')
	print Model.name.search('ax')
	print Model.name.nmatch('Max')
	print Model.name.nsearch('Max')

	def email_search(value, domain=None):
		if domain in value:
			return True
		else:
			return False

	for d in verse.find_new(Model.email.udp(email_search, domain='gmail')):
		print d

	# for d in verse.find_new(Model.email.udp(email_search, domain='gmail')):
		# print d
