import numpy

class Person(object):
	"""docstring for Person"""
	def __init__(self):
		self.names = [
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
		self.id = int(numpy.random.rand(1)[0]*len(self.names))
	def name(self):
		return self.names[self.id][0]
	def gender(self):
		return self.names[self.id][1]
	def age(self):
		return int(numpy.random.rand(1)[0] * 52 +18)
	def college(self):
		return int(numpy.random.rand(1)[0] * 6 + 1)
	def friends(self):
		return int(numpy.random.rand(1)[0] * 500)

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

