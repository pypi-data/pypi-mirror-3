import numpy

__all__ = ['Person']

names = [
			('Mary', 'F'), 			('Marsha', 'F'),	('Max', 'M'),
			('Joe', 'M'), 			('John', 'M'),		('Jacob', 'M'),
			('Bob', 'M'), 			('Billy', 'M'),		('Bobby', 'M'),
			('Zaphod', 'M'), 		('Zack', 'M'),		('Zackary', 'M'),
			('Trillian', 'F'), 	('Tristan', 'F'),	('Trinity', 'F'),
			('Ford', 'M'), 		  ('Jim', 'M'),			('Jimmy', 'M'),
			('Arthor', 'M'), 	  ('Andy', 'M'),		('Anna', 'F'),
			('Jax', 'M'), 		  ('Jason', 'M'),		('Johnathan', 'M'),
			('Marvin', 'M'), 	  ('Michael', 'M'),	('Mike', 'M'),
			('Lucy', 'F'), 		  ('Linda', 'F'),		('Lisa', 'F')
			]

class Person(object):
	"""docstring for Person"""
	def __init__(self):
		self.id = int(numpy.random.rand(1)[0]*len(names))
		self.name = names[self.id][0]
		self.gender = names[self.id][1]
		self.age = int(numpy.random.rand(1)[0] * 52 + 18)
		self.college = int(numpy.random.rand(1)[0] * 5)
		self.friends = int(numpy.random.rand(1)[0] * 500)

	def name(self):
		return self.name
		
	def gender(self):
		return self.gender
		
	def age(self):
		return self.age
		
	def college(self):
		return self.college
		
	def friends(self):
		return self.friends
		

	# def __dict__(self):
		# return dict({'name':self.name(),'age':self.age(),'gender':self.gender(),'friends':self.friends(),'college':self.college()})


if __name__ == '__main__':

	people = [Person() for a in range(250000)]
	
	#output file
	out = open('people.csv', 'w')
	out.write('name,gender,age,years in college,number of friends\n')
	
	previous = Person()
	for p in people:
		if p.name() == previous.name():
			p = Person()
		s = ','.join(str(a) for a in [p.name(), p.gender(), p.age(), p.college(), p.friends()])+'\n'
		out.write(s)
		previous = p
	
	out.close()
	print "Done."
