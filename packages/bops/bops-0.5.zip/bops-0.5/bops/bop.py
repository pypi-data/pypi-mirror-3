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

import numpy as np
import re, decimal, warnings
from bops import *
from bops.exceptions import *
# from collections import OrderedDict
from bops.ordereddict import OrderedDict

__all__ = ['bop']

class bop(object):
	"""
This class is meant for **very** quick data filtering and analysis.

:param data: The data is a 2d list. Meaning either a list of lists or a list of tuples.
:type data: list of lists
:param names: This can either be a comma delimited list of strings or a list of strings.
:type names: comma delimited string
:raises: ``TypeError`` - if *names* is not a string or list of strings


**Usage**::

	from bops import bop
	
	# Name the columns
	cols = 'radar,range,az,el'

	# Perform data grouping on database results
	data = bop(results, cols)

	"""
	aliases = {"avg":np.mean,"len":np.size, "bool":np.bool_, "unicode":np.unicode_, "str":np.str_, "complex":np.complex_, "int":np.int_, "float":np.float_}
	def __init__(self, data=[], names=''):
		super(bop, self).__init__()

		if type(names) is str:
			self.names = ','.join([s.lower().strip() for s in names.split(',')])
		elif type(names) in [list, tuple]:
			if type(names[0]) is not str:
				raise TypeError, "'names' arg should be either a list or tuple of string, or a comma delimited string "
			self.names = ','.join([s.lower().strip() for s in names])
		else:
			raise TypeError, "'names' arg should be either a list or tuple of string, or a comma delimited string "
		
		#save the column names
		self.attrs = [s.lower() for s in self.names.split(',')]

		#determine data type and act accordingly
		#mainly this is here because of some of the data types that sqlalchemy 
		#	returns were not compatible to numpy arrays
		# print type(data)
		if type(data) == np.core.records.recarray or type(data) == np.core.records.record:
			self.records = data
		elif type(data) == list or type(data) == np.ndarray:
			if len(data) > 0:

				nu = []
				for col, col_name in enumerate(self.attrs):
					if type(data[0][col]) is decimal.Decimal:
						tmp = []
						for f in data:
							try:
								tmp.append(float(str(f[col]).strip()))
							except:
								warnings.warn(col_name+" did not have a float value ("+str(f[col])+"); Set to '0.0'.", UserWarning, stacklevel=1)
								tmp.append(0.0)
						nu.append(tmp)
					elif re.search(r'^-?[0-9]+$', str(data[0][col]).strip()) != None:
						tmp = []
						for f in data:
							try:
								tmp.append(int(float(str(f[col]).strip())))
							except:
								warnings.warn("'"+col_name+"' column did not have an int value ("+str(f[col])+"); Set to '0'.", UserWarning, stacklevel=1)
								tmp.append(0)
						nu.append(tmp)
					elif re.search(r'^-?[0-9]+(\.[0-9]+)?$', str(data[0][col]).strip()) != None:
						tmp = []
						for f in data:
							try:
								tmp.append(float(str(f[col]).strip()))
							except:
								warnings.warn(col_name+" did not have a float value ("+str(f[col])+"); Set to '0.0'.", UserWarning, stacklevel=1)
								tmp.append(0.0)
						nu.append(tmp)
					else:
						nu.append([str(f[col]) for f in data])
				self.records = np.core.records.fromarrays(nu, names=self.names)
			else:
				raise Exception, "No data given"
		elif type(data) == bop:
			self.records = data.records
		else:
			self.records = np.core.records.fromrecords(data, names=self.names)
		
		for i, col_name in enumerate(self.attrs):
			setattr(self, col_name.lower(), getattr(self.records, col_name))


	def __getattr__(self, attr):

		if attr.startswith('groupby_'):
			at = attr.replace('groupby_', '', 1)
			if '__' in at:
				return self.groupby(*(at.split('__')))
			else:
				return self.groupby(at)
		if attr.startswith('orderby_'):
			at = attr.replace('orderby_', '', 1)
			if '__' in at:
				return self.orderby(*(at.split('__')))
			else:
				return self.orderby(at)
		
		#if the attr is in the cols, then return the data
		if attr in self.attrs or attr.lower() in self.attrs:
			return getattr(self.records,attr.lower())
		else:
			#does the attribute actually exist?
			array = None
			try:
				array = getattr(self.records, '_'.join(attr.lower().split('_')[:-1]))
			except:
				# raise
				pass

			#parse the functon call
			#the function call is delimited by the last '_'
			func = attr.split('_')[-1]

			# Is there an alias function, with this name?
			# If so, call the function and return the results.
			if func in bop.aliases:
				return bop.aliases[func](array)

			#method_missing tests whether it is a numpy function or a custom one
			ret = self._method_missing(func, array)
			if ret is not None and ret is not False:
				return ret
			else:
				s = []
				s.append("-"*80)
				s.append("This '"+str(self.__class__.__name__)+"' object has no attribute '"+attr+"'")
				s.append("Either you have a typo, '"+attr+"', or '"+attr.split('_')[-1]+"' is not a valid numpy function.")
				s.append("Recognized attributes are: "+str(self.names)+"")
				s.append("-"*80)
				
				raise AttributeError, '\n'+'\n'.join(s)

	def alias(self, *args, **kwargs):
		'''
.. versionadded:: 0.3.1

This function allows you to alias functions and callables for use with the method missing functionality.
For more information look in the section.

:param args: Dictionaries are the only object used, everything else is skipped. Keys are the aliases and the values are the callables. Key word arguments, kwargs, are also permitted.
:type args: dict
:returns: bop.aliases - all existing aliases
:raises: 


**Usage**::

	from bops import bop
	
	# Name the columns
	cols = 'name,gender,age'

	# Perform data grouping on database results
	data = bop(results, cols)

	# Simply takes a numpy array of 'F'\'s and 'M'\'s and turns it into a list of 'Female'/'Male' strings
	def full_gender(array):
		gender = []
		for g in array:
			if g in 'F':
				gender.append('Female')
			else:
				gender.append('Male')
		return np.asarray(gender)

	# This aliases the function name so it can be used with the underscore shortcut functionality
	# NOTE: The keyword CANNOT have underscores in the name, however, the function name can.
	data.alias(fullgender=full_gender)

	# An example of this functionality
	full_gender = data.gender_fullgender

	# NOTE: data.gender_fullgender is the same as full_gender(data.gender)

.. warning::

	Aliased function names cannot have underscores in the name. ie. ``data.alias(full_gender=full_gender)`` does **NOT** work. Aliased names must be single words, like *fullgender*.

		'''
		for arg in args:
			if type(arg) == dict:
				for k, v in arg.items():
					if re.search(r'^[a-zA-Z0-9]+$', str(k).strip()):
						if callable(v):
							bop.aliases[k] = v
					else:
						raise ValueError, "All keys, must be alpha-numeric. No special characters are permitted. You may want to try '" +re.sub(r'[_]+', '', k)+ "' instead of '"+k+"'"
		for k, v in kwargs.items():
			if re.search(r'^[a-zA-Z0-9]+$', str(k).strip()):
				if callable(v):
					bop.aliases[k] = v
			else:
				raise ValueError, "All keyword names, must be alpha-numeric. No special characters are permitted. You may want to try '" +re.sub(r'[_]+', '', k)+ "' instead of '"+k+"'"
		return bop.aliases


	def _method_missing(self, func, array):
		'''
This method adds functions to the recognized attributes (i.e. column names).
This functionality can be used for automatically calling numpy functions on data.

**Example Usage**::

	from bops import bop
	
	# Name the columns
	cols = 'radar,range,az,el'

	# Perform data grouping on database results
	data = bop(results, cols)

	# An example of this functionality (finds the average range value by using the np.mean function)
	max_range = data.range_mean

	# Another example would be calling the numpy histogram function
	range_histogram = data.range_histogram

	# This works by splitting on `` _ ``, and getting the last index then calling the function with numpy.function

		'''
		try:
			#does numpy have the function being called?
			return getattr(np, func)(array)
		except:
			return False

	def __str__(self):
		return str(self.records)
	
	def __len__(self):
		return len(self.records)

	def __getitem__(self, index):
		return self.__class__(self.records[(index)], self.attrs)

	def __iter__(self):
		return iter(self.records)

	def __list__(self):
		return [list(l) for l in list(self.records)]

	def data(self):
		return np.array([list(l) for l in list(self.records)])

	def select(self, index):
		"""

.. versionadded:: 0.1

This method allow you select data slices from the original data.
This returns a new bop instance with only the new data selected

:param filters: The filter is a simple numpy array of booleans. The boolean array is then applied to the entire dataset, returning only the ``True`` indexes.
:type filters: ``numpy.ndarray of booleans``
:returns:  A new ``bop`` instance of only the filtered data.

**Usage**::

	from bops import bop
	
	# Name the columns
	cols = 'radar,range,az,el'

	# Perform data grouping on database results
	data = bop(results, cols)

	# Select data where range > 1500
	# The 'filter', data.range > 1500, 
	# returns a boolean array which is 
	# then applied to the entire dataset, 
	# returning indices where the filter is True.
	far = data.select(data.range > 1500)

	# Filters can be multiplied to have the logical AND of both filters.
	far_high = data.select((data.range > 1500) * (data.el > 60))

	# Or you can save the filters as variables:
	range_filter = data.range > 1500
	el_filter = data.el > 60
	far_high = data.select(range_filter * el_filter)

		"""
		return self.__class__(self.records[index], self.attrs)

	def groupby(self, *args, **kwargs):
		"""
.. versionadded:: 0.1
.. versionchanged:: 0.2, 0.5

This method groups data together based on the string attributes provided.
Unlike SQL, this method returns the data behind the grouping.
Returns all the grouping attributes and the data behind it in a list of tuples

:param attrs: The columns to group by (a list of column names)
:type attrs: list
:param expand: This flag *expands* the output, instead of returning a dictionary.
:type expand: bool
:returns:  Either a list (if expanded) which is the default, or a dictionary.

**Usage**::

	from bops import bop

	# Name the columns
	cols = 'state,town,zip,population'

	# Perform data grouping on database results
	data = bop(results, cols)

	# Group by state
	states = data.groupby('state')

	# Loop through states
	# Using the default ``expand`` option, ``groupby`` returns a list of tuples, with the last index as the data in the group.
	for state, state_data in states:
		print state, len(state_data)
	
	# If we grouped by multiple columns, it would be used like so:
	state_zip = data.groupby('state', 'zip')
	
	# Iterating through the results like so:
	for state, zip, state_zip_data in state_zip:
		print state, zip, len(state_zip_data)
	
	# Now if the 'expand' option is set to False, this is how it would be used.
	state_zip_dict = data.groupby('state', 'zip', expand=False)

	for key, value in state_zip_dict.items():
		# The key contains the grouped column values
		state, zip = key

		# The value contains the data found for that group.
		state_zip_data = value

		print state, zip, len(state_zip_data)

	# Using the expand=False simply allows dictionary access instead of a list.

		"""
		#temperarily holds only the attr of the data for grouping
		groupby = []

		#gathers only the information that being grouped on
		for attr in args:
			groupby.append(getattr(self.records, attr.lower()))

		expand = True
		if 'expand' in kwargs:
			expand = kwargs['expand']
		
		#finds all the data behind the unique values previously found using a mapreduce operation
		return self.mapreducebatch(groupby, expand=expand)

	def orderby(self, *args):
		"""
.. versionadded:: 0.1
.. versionchanged:: 0.2

This method orders the data **in place** on the columns given. Multiple column ordering is possible.

:param attrs: The columns to order by (a list of column names)
:type attrs: list

**Usage**::

	from bops import bop

	# Name the columns
	cols = 'range,az,el'

	# Perform data grouping on database results
	data = bop(results, cols)

	# Order on range
	data.orderby('range')

		"""
		self.records.sort(order=args)
		return self
	
	def map(self, mapper):
		'''

.. versionadded:: 0.3

This method maps all the appropriate groups in accordance with the mapper function passed in.
The mapper function is called on every element of the data.
The mapper function should return a key, value pair.

:param mapper: A callable object (normally a function). Will be called for each data point.
:type mapper: callable
:returns: A dictionary of mapped keys and grouped lists.
:raises: MapperException

**Usage**::

	from bops import bop

	# Name the columns
	cols = 'name,gender,age'

	# Perform data grouping on database results
	data = bop(results, cols)
	
	# This mapper function classifies the row as it's gender and age group (decade).
	# All mappers MUST return a 2-element tuple. This represents a key/value pair for a dictionary.
	def gender_age_group_mapper(row):
		return (row.gender, row.age // 10 * 10), row
	
	# The mapper is the argument to the bop.map function.
	gender_ages = data.map(gender_age_group_mapper)

	# The key returned is the tuple of gender and age_group
	# The value contains all rows that share the same gender and age group.
	for key, value in gender_ages.items():
		gender, age_group = key
		similar_people = value

.. warning::
	When using the **row** object passed to the mapper function, ALL attributes are lowercase.

		'''
		d = OrderedDict()
		for elem in self:
			r = mapper(elem)
			if r is not None:
				try:
					key, value = r
				except ValueError:
					raise MapperException(mapper)
				except:
					print "Unknown Exception: bops doesn't know how to handle this error, therefore there's probably something wrong with your code."
					raise
				if key in d:
					d[key].append(value)
				else:
					d[key] = [value]
		return d

	def reduce(self, mapper_results, reducer):
		'''
.. versionadded:: 0.3

This function 'reduces' the data returned from each map group. 
Reducers are meant to return a single value per group. However, due to python's
typing you can return a list, dictionary or tuple because they are objects themselves.

:param mapper_results: A dictionary object. This is the results returned from a bop.map call.
:type mapper_results: dict
:param reducer: A callable object (normally a function). This function is meant to act on all the results for a mapped group.
:type reducer: callable
:returns: A dictionary of mapped keys and grouped lists.
:raises: TypeError - if *reducer* is *None*

**Usage**::

	from bops import bop

	# Name the columns
	cols = 'name,gender,age'

	# Perform data grouping on database results
	data = bop(results, cols)
	
	# This mapper function classifies the row as it's gender and age group (decade).
	# All mappers MUST return a 2-element tuple. This represents a key / value pair for a dictionary.
	def gender_age_group_mapper(row):
		return (row.gender, row.age // 10 * 10), row
	
	# The mapper is the argument to the bop.map function.
	gender_ages = data.map(gender_age_group_mapper)

	# The key returned is the tuple of gender and age_group
	# The value contains all rows that share the same gender and age group.
	for key, value in gender_ages.items():
		gender, age_group = key
		similar_people = value
	
	# This reduce function returns a dictionary. The keys are the same as the map results. 
	# However, the values are returned from the reducer function.
	# This simply uses the built-in 'len' function to count the people in each group.
	counts = data.reduce(gender_ages, len)

	# This is used like so:
	for key, value in counts.items():
		gender, age_group = key
		similar_people_count = value

		'''
		new = OrderedDict()
		if reducer is not None:
			for key, group in mapper_results.items():
				new[key] = reducer(group)
		else:
			raise TypeError, "'reduce' argument cannot be 'None'. It must be callable."
		return new

	def complexreduce(self, mapper_results, reducer):
		'''
.. versionadded:: 0.3

This function 'reduces' the data returned from each map group.
Reducers are meant to return a single value per group. However, due to python's
typing you can return a list, dictionary or tuple because they are objects themselves.

This function is very similar to reduce, the only difference is that
both the key and value returned from the mapper are passed to the reducer, instead of just the value.

The only reason for using this instead of the regular reduce function, is if 
there is data in the mapped key that a normal reducer would not have access to.

:param mapper_results: A dictionary object. This is the results returned from a bop.map call.
:type mapper_results: dict
:param reducer: A callable object (normally a function). This function is meant to act on all the results for a mapped group.
:type reducer: callable
:returns: A dictionary of mapped keys and grouped lists.
:raises: TypeError - if *reducer* is **None**

		'''
		if reducer is not None:
			for key, group in mapper_results.items():
				mapper[key] = reducer(key, group)#,  self.__class__(group, self.names))
		else:
			raise TypeError, "'reduce' argument cannot be 'None'. It must be callable."
		return mapper

	def __expandmap(clazz, mapped_results):
		'''

		.. versionadded:: 0.2

		This class expands a dictionary, where the keys are iterables, 
			into a list with the mapped values as the last index.
		'''
		expanded_results = []
		for k, v in mapped_results.items():
			tmp = []
			if hasattr(k, '__iter__'):
				tmp.extend(k)
			else:
				if len(k) > 0 and type(k) != str and type(k) != np.string_:
					for l in k: tmp.append(l)
				else:
					tmp.append(k)
			tmp.append(v)
			expanded_results.append(tmp)
		return expanded_results

	def mapreduce(self, mapper, reducer, expand=True, sort=False, complex=False):
		'''
.. versionadded:: 0.3
.. versionchanged:: 0.5

This function calls the map and reduce functions and the results will be 
expanded into a list. This means that each row in the results will be a tuple, 
with the last value being the mapped data (returned as the value from the mapper function).

However, if the **expand** option is ``False``, the results as a dictionary. 
The key will be a tuple, and the value will be a list of all rows matching 
the mapper output.

The key(s) returned from the mapper function will be indexes [:-1] 
for each row of results. 

The sort flag can also be used to sort results. 
The results will be sorted on keys returned from the mapper function.

:param mapper: A callable object (normally a function). Will be called for each data point.
:type mapper: callable
:param reducer: A callable object (normally a function). This function is meant to act on all the results for a mapped group.
:type reducer: callable
:param expand: If **False**, The results are a dictionary, otherwise the results are *expanded* into a list of tuples.
:type expand: bool
:param sort: Sorts the results based on the key returned from the mapper function.
:type sort: bool
:param complex: Uses a complexreduce function instead of normal reducers. This means that both the key and value form the mapper function is passed to the reducer function.
:type complex: bool
:returns: A list of tuples. If *expand* is **False**, a dictionary of mapped keys and grouped lists.
:raises: TypeError - if *reducer* is **None**

**Usage**::

	from bops import bop

	results = sqlalchemy magic ....

	# Name the columns
	cols = 'name,gender,age,college'

	# Perform data grouping on database results
	data = bop(results, cols)
	
	# This mapper function classifies the row as it's gender and age group (decade).
	# All mappers MUST return a 2-element tuple. This represents a key / value pair for a dictionary.
	# However, the key can also be a tuple
	def gender_age_group_mapper(row):
		return (row.gender, row.age // 10 * 10), row
	
	# The mapper, gender_age_group_mapper, is the argument to the bop.map function.
	# The reducer, len, is the same as if you would pass it to a bop.reduce function.
	# This mapreduce function returns a dictionary when expand=False. The keys are the first argument of the map results.
	# However, the values are returned from the reducer function.
	# This simply uses the built-in 'len' function to count the people in each group.
	# Remember, expand=False means a dictionary is returned.
	counts = data.mapreduce(gender_age_group_mapper, len, expand=False)

	# This is used like so:
	for key, value in counts.items():
		gender, age_group = key
		similar_people_count = value

	# If True, the 'expand' option can make results easier to use:
	# expand=True is the new default in v0.5+
	counts = data.mapreduce(gender_age_group_mapper, len, expand=True)

	for gender, age_group, similar_people_count in counts:
		print gender, age_group, similar_people_count
		
		# 'gender' and 'age_group' are the 'mapper' key tuple, where 'similar_people_count' is the result from the reduce function, 'len'.

	# This counts the number of people in the gender/age group that have more than 4 yrs in college.
	def grads(group):
		return sum([1 for p in group if p.college > 4])
	
	# This mapreduce function returns a list of tuples instead of a dictionary, simply because the expand option is True (which is the new default in v0.5+).
	gender_age_grad = data.mapreduce(gender_age_group_mapper, reducer=grads, expand=True)

	# With the expand option as True, the mapper key and reducer value is readily available for iteration.
	for gender, age_group, grads in gender_age_grad:
		print gender, age_group, grads

		'''
		if not complex:
			d = self.reduce(self.map(mapper), reducer)
		else:
			d = self.complexreduce(self.map(mapper), reducer)

		if type(sort) is bool:
			if sort == True:
				d = OrderedDict(sorted(d.items()))
		elif type(sort) is str and len(sort) > 0:
			if sort.strip().lower() == 'map':
				d = OrderedDict(sorted(d.items(), key=lambda x: x[0]))
			elif sort.strip().lower() == 'reduce':
				d = OrderedDict(sorted(d.items(), key=lambda x: x[1]))
			else:
				raise ValueError, "The 'sort' argument can either be a bolean value or a string \n containing 'map' or 'reduce'. \n'"+str(type(sort))+"' arguments are not accepted."				

		if not expand:
			return d
		else:
			return self.__expandmap(d)

	def mapreducebatch(self, maps=[], reducer=None, names='', expand=True):
		'''
.. versionadded:: 0.3
.. versionchanged:: 0.5

This function performs the same work as the 'mapreduce' function but 
uses numpy for a speed boost.

Here are the differences:

1.	The 'maps' argument should be a list of numpy arrays or lists.
	This list corresponds to the key of a normal mapper function. 
	In other words, this list represents the columns you are grouping by.
2.	This function uses numpy array and numpy.core.records module to speed up execution.
3.	The names argument can be used to specify the column names for the results returned.

:param maps: A list of numpy arrays.
:type maps: list
:param reducer: A callable object (normally a function). This function is meant to act on all the results for a mapped group.
:type reducer: callable
:param names: A comma delimited string of column names.
:type names: str
:param expand: If **False**, The results are a dictionary, otherwise the results are *expanded* into a list of tuples.
:type expand: bool
:returns: A list of tuples. If *expand* is **False**, a dictionary of mapped keys and grouped lists. However, if the *names* arg is given and not an empty string, then the results will be another **bop** instance with the columns set to the *names* argument.

**Usage**::

	from bops import bop

	# sqlalchemy magic...
	results = session.execute('SELECT name,gender,age,college FROM students;').fetchall()

	# Name the columns
	cols = 'name,gender,age,college'

	# Initialize bop instance
	data = bop(results, cols)

	# Define graduated
	# This is a reducer do be used on the data for each group after it has passed 
	#   through a map operation.
	# NOTE: All reducers are given the entire mapped data group.
	# This reducer returns the number of people who have more than 4 years in college.
	def graduated(group):
		return len(np.nonzero(data.college > 4)[0])

	# This is one attribute of the data describing the age groups that ppl belong to.
	# This basically determines the decade of your age. 
	# Simply put, if you are 35, it returns 30, for 58 it returns 50
	# This allows the data to be aggregated by ppl of similar age
	agegroup = data.age // 10 * 10

	# This is the map reduce operation call
	# It finds all the unique combinations of gender and age group and passes 
	#   each unique group to the reducer separately.
	# If a reducer is left out, then the data returned is the raw data that belong to that group.
	# The 'expand' option makes the output easier to deal with, however, if you 
	#   only want a key / value pair to be returned, leave out this option.
	#The 'names' option are the column names to be returned
	gender_age_grad = data.mapreducebatch([data.gender, agegroup], reducer=graduated, expand=True, names='gender,agegroup,graduates')

	# This orders the data by gender and age group for ordered output.  
	gender_age_grad.orderby('gender','agegroup')
  
	# Output the results in a pretty fashion
	print
	print repr("Gender").rjust(7),repr("Age Group").rjust(4),repr(">4yrs in college").rjust(17)
	for gender, age, grad in gender_age_grad:
		print repr(gender).ljust(9),repr(age).ljust(11),repr(grad).ljust(17)
	print

		'''

		base = np.core.records.fromarrays(maps)
		# if names != '':
			# base.names = names
		us = np.unique(base)

		results = {}
		for u in us:
			# finds indexes that match the unique map key
			indexes = np.nonzero(base == u)
			if reducer is not None:
				red = reducer(self[indexes])
				if red is not None:
					results[u] = red
			else:
				results[u] = self[indexes]
		if expand:
			results = self.__expandmap(results)

		if names != '':
			if not expand:
				results = self.__expandmap(results)
			return self.__class__(results, names)
		# if type(results) == dict:
		# 	return results.items()
		# else:
		return results

