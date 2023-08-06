from underverse import Underverse
from underverse.model import Document
from test_data_gen import Person
import unittest, os

class AnotherTestClass(object):
	"""docstring for AnotherTestClass"""
	def __init__(self, text):
		super(AnotherTestClass, self).__init__()
		self.a = Comment(text)
		self.msg = Message(2,3,4)
		self.array = range(3)

class Comment(object):
	"""docstring for Comment"""
	def __init__(self, text):
		super(Comment, self).__init__()
		self.text = text

	def len(self):
		return len(self.text)

class Message(object):
	"""docstring for Message"""
	def __init__(self, x, y, z, **kwargs):
		super(Message, self).__init__()
		self.x = x
		self.y = y
		self.z = z
		try:
			import numpy as np
			self.n = np.arange(5)
		except ImportError, e:
			self.n = range(5)
		
		self.m = Comment('Starting to come together')

class LoadTestCase(unittest.TestCase):
	def setUp(self):
		self.uv = Underverse()

	def tearDown(self):
		self.uv.close()

	def test_create_verse(self):
		# """creates a verse"""
		self.users = self.uv.users
		self.assertIn(self.users.name, self.uv)

	def test_load_dict(self):
		# """loads a single python dict"""
		self.users = self.uv.users

		user = { 'name': 'ed', 'fullname':'Ed Jones', 'password':'3d5_p455w0r6'}
		self.users.add(user)

		u = self.users.find_one(Document.name == 'ed', Document.password == '3d5_p455w0r6', Document.fullname == 'Ed Jones')
		self.assertTrue(u['name'] == user['name'] and u['fullname'] == user['fullname'] and u['password'] == user['password'])

	def test_load_dict_len(self):
		# """loads a single python dict"""
		self.users = self.uv.users

		user = { 'name': 'ed', 'fullname':'Ed Jones', 'password':'3d5_p455w0r6'}
		self.users.add(user)
		self.assertTrue(len(self.users) == 1)

	def test_load_multiple_objs(self):
		# """loads several python class objects"""
		self.users = self.uv.users

		for person in range(50):
			self.users.add(Person())

		self.assertTrue(len(self.users) == 50)

	def test_bulk_load(self):
		# """bulk loads several python class objects"""
		self.users = self.uv.users
		self.users.add([Person() for i in range(50)])
		self.assertTrue(len(self.users) == 50)

	def test_dump(self):
		self.users = self.uv.users
		self.users.add([Person() for i in range(50)])
		self.uv.dump('test.sql')
		self.assertTrue(os.path.exists('test.sql'))

	def test_load(self):
		self.uv.load('test.sql')
		self.assertTrue(len(self.uv.users) == 50)

	# @unittest.skip("takes a while")
	def test_load_large(self):
		self.uv.load('speed_test_smaller.sql')
		self.assertTrue(len(self.uv.test) == 250)

	def test_update(self):
		self.users = self.uv.users
		user = { 'name': 'ed', 'fullname':'Ed Jones', 'password':'3d5_p455w0r6'}
		self.users.add(user)

		u = self.users.find_one(Document.name == 'ed', Document.password == '3d5_p455w0r6', Document.fullname == 'Ed Jones')
		u.age = 25
		self.users.update(u)

		u = self.users.find_one(Document.name == 'ed', Document.password == '3d5_p455w0r6', Document.fullname == 'Ed Jones')
		self.assertTrue(hasattr(u, 'age') and u.age == 25)

	def test_update_list(self):
		self.users = self.uv.users
		user = { 'name': 'ed', 'fullname':'Ed Jones', 'password':'3d5_p455w0r6'}
		self.users.add(user)

		u = self.users.find_one(Document.name == 'ed', Document.password == '3d5_p455w0r6', Document.fullname == 'Ed Jones')
		u.friends = ['Michael', 'Luke', 'Amy']
		self.users.update(u)

		u = self.users.find_one(Document.name == 'ed', Document.password == '3d5_p455w0r6', Document.fullname == 'Ed Jones')
		self.assertTrue(hasattr(u, 'friends') and type(u.friends) == list)

	def test_update_np_array(self):
		try:
			import numpy as np
		except ImportError:
			self.skipTest("NumPy not installed")

		# if the object is a numpy.ndarray, then it's converted to a Python list and saved in a dict with '__numpy__' as it's key
		numpy_encoder = (lambda obj: True if isinstance(obj, np.ndarray) else False, 
				lambda obj: {'__numpy__' : obj.tolist()})

		# when decoding, if the dict has a key '__numpy__', then the list is converted to a numpy.ndarray object
		numpy_decoder = (lambda obj: True if '__numpy__' in obj else False, 
				lambda obj: np.array(obj['__numpy__']))

		Underverse.add_json_ext(numpy_encoder, numpy_decoder)

		self.users = self.uv.users
		user = { 'name': 'ed', 'fullname':'Ed Jones', 'password':'3d5_p455w0r6'}
		self.users.add(user)

		u = self.users.find_one(Document.name == 'ed', Document.password == '3d5_p455w0r6', Document.fullname == 'Ed Jones')
		u.list = np.arange(5)
		self.users.update(u)

		u = self.users.find_one(Document.name == 'ed', Document.password == '3d5_p455w0r6', Document.fullname == 'Ed Jones')
		self.assertTrue(hasattr(u, 'list') and type(u.list) == np.ndarray)

	# def test_numpy_iter(self):
	# 	try:
	# 		import numpy as np
	# 	except ImportError:
	# 		self.skipTest("NumPy not installed")

	# 	self.users = self.uv.users
	# 	self.users.add([Person() for i in range(5)])
		
	# 	print list(self.users.age)
	# 	# print len(list(self.users.age))
	# 	self.assertTrue(self.users.all().to_numpy('age', int).size == 50)

	def test_load_and_read_objects(self):
		try:
			import numpy as np
		except ImportError:
			self.skipTest("NumPy not installed")

		test = self.uv.test
		test.add(AnotherTestClass('test #1'))
		
		good = True

		from underverse import NecRow
		for r in test:			
			if not (type(r) == AnotherTestClass or type(r) == NecRow):
				good = False
			if not (type(r.a) == Comment):
				good = False
			if not (type(r.msg.n) == np.ndarray):
				good = False
			if not (type(r.msg.m) == Comment):
				good = False
			if not (type(r.msg) == Message):
				good = False
		self.assertTrue(good)

	def test_dump_objects(self):
		try:
			import numpy as np
		except ImportError:
			self.skipTest("NumPy not installed")

		test = self.uv.test
		test.add(AnotherTestClass('test #1'))
		self.uv.dump('obj_testing.sql')
		self.assertTrue(True)

	def test_load_objects(self):
		try:
			import numpy as np
		except ImportError:
			self.skipTest("NumPy not installed")

		Underverse.create_mappers(AnotherTestClass, Comment, Message)

		self.uv.load('obj_testing.sql')
		good = True

		from underverse import NecRow
		for r in self.uv.test:
			if not (type(r) == AnotherTestClass or type(r) == NecRow):
				good = False
			if not (type(r.a) == Comment):
				good = False
			if not (type(r.msg.n) == np.ndarray):
				good = False
			if not (type(r.msg.m) == Comment):
				good = False
			if not callable(r.msg.m.len):
				good = False
			if not (type(r.msg) == Message):
				good = False
		self.assertTrue(good)


if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(LoadTestCase)
	unittest.TextTestRunner(verbosity=2).run(suite)

	# suite = unittest.TestSuite()
	# suite.addTest(LoadTestCase('test_update_list'))
	# unittest.TextTestRunner(verbosity=2).run(suite)
