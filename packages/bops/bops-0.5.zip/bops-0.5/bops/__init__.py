# Copyright (C) 2011 by Max Franks

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import numpy
from bop import *
from bops.exceptions import *

__all__ = ['bop', 'btw', 'eq', 'false', 'gt', 'gtoe', 'l2a', 'logand', 'logor', 'lt', 'ltoe', 'oband', 'obor', 'true']

#functions

def l2a(_list):
	'''
This function converts a python list to a numpy array. This is an internal function used in the boolean functions that allows for passing them regular lists.

	'''
	return numpy.array(_list)

def eq(a, eq):
	""" 
**Equals** (i == eq)

This function returns a boolean array, with indexes representing matches and non-matches (True or False). **True** values represent indexes that are equal to the number given.

**Usage**::

	>>> import bops
	>>> r = range(10)
	>>> b = bops.eq(r, 2)
	array([False, False,  True, False, False, False, False, False, False, False], dtype=bool)

	"""
	if type(a) == list:
		a = l2a(a)
	elif type(a) != numpy.ndarray:
		raise TypeException('1st', type(a), 'numpy.ndarray')
	return (a == eq)

def true(a):
	""" 
**True** (i == 1 or i)

Returns a list of indexes that are **True** for the boolean array argument.

**Usage**::

	>>> import bops
	>>> r = range(10)
	>>> b = bops.btw(r, 2, 8)
	>>> b
	array([False, False, False,  True,  True,  True,  True,  True, False, False], dtype=bool)
	>>>
	>>> bops.true(b)
	array([3, 4, 5, 6, 7], dtype=int64)

	
	"""
	if type(a) == list:
		a = l2a(a)
	elif type(a) == bool:
		return []
	elif type(a) != numpy.ndarray:
		raise TypeException('1st', type(a), 'numpy.ndarray')
	return numpy.nonzero(a)[0]

def false(a):
	""" 
**False** (i == 0 or not i)

Returns a list of indexes that are **False** for the boolean array argument.

**Usage**::

	>>> import bops
	>>> r = range(10)
	>>> b = bops.btw(r, 2, 8)
	>>> b
	array([False, False, False,  True,  True,  True,  True,  True, False, False], dtype=bool)
	>>>
	>>> bops.false(b)
	array([0, 1, 2, 8, 9], dtype=int64)

	
	"""
	if type(a) == list:
		a = l2a(a)
	elif type(a) != numpy.ndarray:
		raise TypeException('1st', type(a), 'numpy.ndarray')
	# return true(eq(a, 0))
	return numpy.nonzero(a == 0)[0]

def btw(a, _min, _max):
	""" 
**Between** (i > min and i < max)

This function returns a boolean array, with indexes representing matches and non-matches (True or False). **True** values represent indexes that are between the min and max numbers given.
The comarisons are *exclusive* of the min and max values given.

**Usage**::

	>>> import bops
	>>> r = range(10)
	>>> bops.btw(r, 2, 8)
	array([False, False, False,  True,  True,  True,  True,  True, False, False], dtype=bool)
	
	"""
	if type(a) == list:
		a = l2a(a)
	elif type(a) != numpy.ndarray:
		raise TypeException('1st', type(a), 'numpy.ndarray')
	return (a > _min)*(a < _max)

def gt(a, gt):
	""" 
**Greater-than** (>)

This function returns a boolean array, with indexes representing matches and non-matches (True or False). **True** values represent indexes that are greater than the number given.

**Usage**::

	>>> import bops
	>>> r = range(10)
	>>> bops.gt(r, 5)
	array([False, False, False, False, False, False,  True,  True,  True,  True], dtype=bool)
	
	"""
	if type(a) == list:
		a = l2a(a)
	elif type(a) != numpy.ndarray:
		raise TypeException('1st', type(a), 'numpy.ndarray')
	return (a > gt)

def lt(a, lt):
	""" 
**Less-than** (<)

This function returns a boolean array, with indexes representing matches and non-matches (True or False). **True** values represent indexes that are less than the number given.

**Usage**::

	>>> import bops
	>>> r = range(10)
	>>> bops.lt(r, 5)
	array([ True,  True,  True,  True,  True,  False, False, False, False, False], dtype=bool)
	
	"""
	if type(a) == list:
		a = l2a(a)
	elif type(a) != numpy.ndarray:
		raise TypeException('1st', type(a), 'numpy.ndarray')
	return (a < lt)

def gtoe(a, gt):
	""" 
**Greater-than OR Equal to** (>=)

This function returns a boolean array, with indexes representing matches and non-matches (True or False). **True** values represent indexes that are greater than or equal to the number given.

**Usage**::

	>>> import bops
	>>> r = range(10)
	>>> bops.gtoe(r, 5)
	array([False, False, False, False, False,  True,  True,  True,  True,  True], dtype=bool)
	"""
	if type(a) == list:
		a = l2a(a)
	elif type(a) != numpy.ndarray:
		raise TypeException('1st', type(a), 'numpy.ndarray')
	return (a >= gt)

def ltoe(a, lt):
	""" 
**Less-than OR Equal to** (<=)

This function returns a boolean array, with indexes representing matches and non-matches (True or False). **True** values represent indexes that are less than or equal to the number given.

**Usage**::

	>>> import bops
	>>> r = range(10)
	>>> bops.ltoe(r, 5)
	array([ True,  True,  True,  True,  True,  True, False, False, False, False], dtype=bool)
	
	"""
	if type(a) == list:
		a = l2a(a)
	elif type(a) != numpy.ndarray:
		raise TypeException('1st', type(a), 'numpy.ndarray')
	return (a <= lt)

def logor(*args):
	"""
This function provides the logical OR for all boolean arrays passed in.

**Example Script**::

	#import numpy for random number generation
	import numpy

	#import bops for boolean operation
	import bops

	#use numpy to generate an array of random numbers with 10 values
	rand1 = numpy.random.rand(10)

	#'gt' returns a boolean array with values for each index, where false means the value is NOT > 0.8 and a true value where it is > 0.8
	gt1 = bops.gt(rand1, 0.8)

	#'lt' returns a boolean array with values for each index, where false means the value is NOT < 0.2 and a true value where it is < 0.2
	lt2 = bops.lt(rand1, 0.2)

	#'logand' also returns a boolean array with the logical OR of both gt1 and lt2 arrays
	#This is used to find values that are greater than 0.8 OR less than 0.2
	logor(gt1, lt2)

	"""
	if len(args) < 1:
		raise Exception, "Argument list is empty"
	arr = args[0]
	for a in args:
		if type(a) == list:
			a = l2a(a)
		elif type(a) != numpy.ndarray:
			raise Exception, 'All arguments must be of type numpy.ndarray, not ', type(a)
		arr = a | arr
	return arr

def logand(*args):
	"""
This function provides the logical AND for all boolean arrays passed in.

**Example Script**::

	#import numpy for random number generation
	import numpy

	#import bops for boolean operation
	import bops

	#use numpy to generate an array of random numbers with 10 values
	rand1 = numpy.random.rand(10)

	#'gt' returns a boolean array with values for each index, where false means the value is NOT > 0.3 and a true value where it is > 0.3
	gt1 = bops.gt(rand1, 0.3)

	#'lt' returns a boolean array with values for each index, where false means the value is NOT < 0.6 and a true value where it is < 0.6
	lt2 = bops.lt(rand1, 0.6)

	#'logand' also returns a boolean array with the logical AND of both gt1 and lt2 arrays
	#This is used to find values that are greater than 0.3 AND less than 0.6
	logand(gt1, lt2)

	"""	
	if len(args) < 1:
		raise Exception, "Argument list is empty"
	arr = args[0]
	for a in args:
		if type(a) == list:
			a = l2a(a)
		elif type(a) != numpy.ndarray:
			raise Exception, 'All arguments must be of type numpy.ndarray, not ', type(a)
		arr = a * arr
	return arr


def oband(a, **kwargs):
	"""
This function uses the kwargs hash to find the AND of multiple attributes

**Example Usage**::

	import numpy

	#test class
	class test(object):
	  def __init__(self, x):
	    self.x = x
	    self.y = x*2
	    self.r = numpy.random.rand(1)[0]
	  def __str__(self):
	    return "<Test: X: %(x)i Y: %(y)i >" % self.__dict__
	
	#generate 25 test objects
	tests = [test(i) for i in range(25)]
	
	#TRUE indexes with object AND
	indexes = true(oband(tests, x=3, y=6))


In the above example, 'tests' is a list of objects, that have attributes of x and y.
This function finds all the objects in the list that have an x value of 3 AND a y value of 6
	"""
	_bool = None
	for k in kwargs:
		if _bool is None:
			_bool = (l2a([getattr(b, str(k)) for b in a]) == kwargs[k])
		else:
			_bool = _bool * (l2a([getattr(b, str(k)) for b in a]) == kwargs[k])
	return _bool

def obor(a, **kwargs):
	"""
This function uses the kwargs hash to find the OR of multiple object attributes. 

**Example Usage**::
   
	import numpy

	#test class
	class test(object):
	  def __init__(self, x):
	    self.x = x
	    self.y = x*2
	    self.r = numpy.random.rand(1)[0]
	  def __str__(self):
	    return "<Test: X: %(x)i Y: %(y)i >" % self.__dict__
	
	#generate 25 test objects
	tests = [test(i) for i in range(25)]
	
	#TRUE indexes with object OR
	indexes = true(obor(tests, x=3, y=8))


In the above example, 'tests' is a list of objects that have attributes of x and y. This function finds all the objects in the list that have an x value of 3 OR a y value of 8
	"""
	_bool = None
	for k in kwargs:
		if _bool is None:
			_bool = (l2a([getattr(b, str(k)) for b in a]) == kwargs[k])#getattr(b, str(k)) l2a([b.__dict__[str(k)]
		else:
			_bool = _bool | (l2a([getattr(b, str(k)) for b in a]) == kwargs[k])
	return _bool


if __name__ == "__main__":

	import numpy
	from time import clock

	#test class
	class test(object):
		"""docstring for test"""
		def __init__(self, x):
			self.x = x
			self.y = x*2
			self.r = numpy.random.rand(1)[0]
		def __str__(self):
			return "<Test: X: %(x)i Y: %(y)i >" % self.__dict__
	
	tests = [test(i) for i in range(25000)]
	print repr(test(5))
	
	#TRUE indexes with object AND with logical AND
	start1 = clock()
	print len(true(logand(oband(tests, x=3, y=6), gt([b.r for b in tests], 0.5))))
	end1 = clock()
	print "obor: ", ("%2.6f" % (end1 - start1))

	#TRUE indexes with EQ and GT with logical AND
	start2 = clock()
	xs = eq([b.x for b in tests], 3)
	ys = eq([b.y for b in tests], 6)
	rs = gt([b.r for b in tests], 0.5)
	print len(true(logand(xs, ys, rs)))
	end2 = clock()
	print "list and eq: ", ("%2.6f" % (end2 - start2))

	#straight loops
	start3 = clock()
	indexes =[]
	for i, t in enumerate(tests):
		if t.x == 3 and t.y == 6 and t.r > 0.5:
			indexes.append(i)
	end3 = clock()
	print len(indexes)
	print "loops: ", ("%2.6f" % (end3 - start3))

	#data creation outside timer, for an optimized test 
	#	(in optimized code these arrays would be creates outside the loop)
	xs = l2a([b.x for b in tests])
	ys = l2a([b.y for b in tests])
	rs = l2a([b.r for b in tests])
	start4 = clock()
	print len(true((eq(xs, 3) * eq(ys, 6) * gt(rs, 0.5))))
	end4 = clock()
	print "fast list and eq: ", ("%2.6f" % (end4 - start4))

	#data creation outside timer, for an optimized test 
	#	(in optimized code these arrays would be creates outside the loop)
	#using raw numpy code and not bops
	xs = l2a([b.x for b in tests])
	ys = l2a([b.y for b in tests])
	rs = l2a([b.r for b in tests])
	start5 = clock()
	print len(numpy.nonzero((xs == 3) * (ys == 6) * (rs > 0.5))[0])
	end5 = clock()
	print "alt fast list and eq: ", ("%2.6f" % (end5 - start5))

	#BETWEEN tests
	#using bops
	start6 = clock()
	print len(true(logand(btw(rs, 0.3, 0.6))))
	end6 = clock()
	print "btw: ", ("%2.6f" % (end6 - start6))

	#using loops
	indexes =[]
	etests = enumerate(tests)
	start7 = clock()
	for i, t in etests:
		if t.r > 0.3 and t.r < 0.6:
			indexes.append(i)
	end7 = clock()
	print len(indexes)
	print "loops btw: ", ("%2.6f" % (end7 - start7))

	a = zip(range(10), range(10))
	cols = ['a','b']

	data = bop(a, cols)
	print data