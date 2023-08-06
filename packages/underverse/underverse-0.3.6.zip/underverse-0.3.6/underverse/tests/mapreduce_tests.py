from underverse import Underverse, SubVerse
from underverse.model import Document as D
from test_data_gen import Person
import unittest, os

class MapReduceTestCase(unittest.TestCase):
	def setUp(self):
		self.uv = Underverse()
		self.uv.load('speed_test_smaller.sql')
		self.uv.load('speed_test_smaller_obj.sql')
		Underverse.create_mappers(Person)
		# print Underverse.class_names

	def tearDown(self):
		self.uv.close()

	def test_reduce(self):
		self.test = self.uv.test
		count = self.test.reduce(len)
		self.assertTrue(count == 250)

	def test_simple_reduce(self):
		self.test = self.uv.test
		count = SubVerse(self.test).simple_reduce(len)
		self.assertTrue(count == 250)

	def test_simple_reduce2(self):
		self.test = self.uv.test
		count = self.test.all().simple_reduce(len)
		self.assertTrue(count == 250)

	def test_groupby(self):
		self.test = self.uv.test
		unique_names = self.test.unique('name')
		groups = self.test.groupby('name')
		self.assertTrue(len(list(unique_names)) == len(list(groups)))

	def test_groupby2(self):
		self.test = self.uv.test
		worked = True
		# print self.test.groupby('name')
		for name, ppl in self.test.groupby('name'):
			if len(ppl) != len(list(self.test.find(D.name == name))):
				worked = False
		self.assertTrue(worked)

	def test_groupby3(self):
		self.test = self.uv.test
		unique_names = self.test.unique('name', 'age')
		groups = self.test.groupby('name', 'age')
		self.assertTrue(len(list(unique_names)) == len(list(groups)))

	def test_groupby4(self):
		self.test = self.uv.test
		worked = True
		for name, ppl in self.test.groupby('name'):
			if type(ppl) != SubVerse:
				worked = False
		self.assertTrue(worked)

	def test_map(self):
		self.test = self.uv.test
		worked = True

		def name_mapper(array):
			for doc in array:
				yield doc.name, doc

		for name, ppl in self.test.map(name_mapper):
			if type(ppl) != SubVerse:
				worked = False
		self.assertTrue(worked)

	def test_map2(self):
		self.test = self.uv.test
		unique_names = self.test.unique('name')

		worked = True
		def name_mapper(array):
			for doc in array:
				yield doc.name, doc
		groups = self.test.map(name_mapper)
		self.assertTrue(len(list(unique_names)) == len(list(groups)))

# ==================

	# def test_groupby_obj(self):
	# 	self.test = self.uv.test_obj
	# 	unique_names = self.test.unique('__Person__.name')
	# 	groups = self.test.groupby('__Person__.name')
	# 	self.assertTrue(len(list(unique_names)) == len(list(groups)))

	# def test_groupby_obj2(self):
	# 	self.test = self.uv.test
	# 	worked = True
	# 	# print self.test.groupby('name')
	# 	for name, ppl in self.test.groupby('name'):
	# 		if len(ppl) != len(list(self.test.find(D.name == name))):
	# 			worked = False
	# 	self.assertTrue(worked)

	# def test_groupby_obj3(self):
	# 	self.test = self.uv.test
	# 	unique_names = self.test.unique('name', 'age')
	# 	groups = self.test.groupby('name', 'age')
	# 	self.assertTrue(len(list(unique_names)) == len(list(groups)))

	# def test_groupby_obj4(self):
	# 	self.test = self.uv.test
	# 	worked = True
	# 	for name, ppl in self.test.groupby('name'):
	# 		if type(ppl) != SubVerse:
	# 			worked = False
	# 	self.assertTrue(worked)

	def test_map_obj(self):
		self.test = self.uv.test_obj
		worked = True

		def name_mapper(array):
			for doc in array:
				# print type(doc), doc.name
				# print doc.__Person__, type(doc.__Person__)
				yield doc.name, doc

		# name_mapper = lambda x: [(y.name, y) for y in x]

		for name, ppl in self.test.map(name_mapper):
			# print name, len(ppl)
			if type(ppl) != SubVerse:
				worked = False
		self.assertTrue(worked)

	def test_map_obj2(self):
		self.test = self.uv.test_obj
		unique_names = self.test.unique('name')

		worked = True
		def name_mapper(array):
			for doc in array:
				yield doc.name, doc
		groups = self.test.map(name_mapper)
		g = len(list(groups))
		us = len(list(unique_names))
		self.assertTrue(g == us)

if __name__ == '__main__':

	# uv = Underverse()
	# # uv.load('speed_test_smaller.sql')
	# uv.load('speed_test_smaller_obj.sql')
	# # Underverse.create_mappers(Person)
	# # print Underverse.class_names
	# test = uv.test_obj
	# print test.limit(1)

	suite = unittest.TestLoader().loadTestsFromTestCase(MapReduceTestCase)
	unittest.TextTestRunner(verbosity=2).run(suite)
