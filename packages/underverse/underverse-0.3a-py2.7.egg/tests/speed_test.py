from underverse import Underverse
from underverse.model import Document
from test_data_gen import Person
from time import clock

def load(collection, num):
	collection.purge()
	start = clock()
	for p in range(num):
		person = Person()
		d = {'name': person.name, 'age': person.age, 'gender': person.gender, 'friends': person.friends, 'college': person.college}
		collection.add(d)
	return "%s - %0.5f elapsed" % (num, clock() - start)

def load_bulk(collection, num, buffer=150000):
	collection.purge()
	data = []
	start = clock()
	for p in range(num):
		person = Person()
		d = {'name': person.name, 'age': person.age, 'gender': person.gender, 'friends': person.friends, 'college': person.college}
		data.append(d)
		if p > 1 and p % buffer == 0:
			collection.add(data)
			print "%s - %0.5f elapsed" % (p, clock() - start)
			data = []
	collection.add(data)
	return "%s - %0.5f elapsed" % (num, clock() - start)

def timing(col, num, fast_only=False, buffer=150000):
	if not fast_only:
		print "load:      ", load(col, num)
	print "load_bulk: ", load_bulk(col, num, buffer)
	print

def main():
	uv = Underverse()
	test = uv.test	

	# timing(test, 25)
	timing(test, 250)
	# timing(test, 2500)
	# timing(test, 25000)
	# timing(test, 250000, fast_only=True)
	# timing(test, 2500000, fast_only=True)

	uv.dump('speed_test_smaller.sql')

	# print load_bulk(col, 2500000, 15000)
