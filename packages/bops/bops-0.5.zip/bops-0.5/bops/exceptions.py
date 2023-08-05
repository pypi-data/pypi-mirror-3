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

__all__ = ['MapperException','TypeException']

#this exception is raised if the argument given is not correct
class TypeException(Exception):
	"""docstring for TypeException"""
	def __init__(self, _placement='', _type='', text=''):
		self.value = str(_placement)+" argument must be of type '"+text+"' not '"+str(_type)+"'"
	def __str__(self):
		return repr(self.value)

class MapperException(Exception):
	"""docstring for MapperException"""
	def __init__(self, mapper):
		self.value = "Mapper function '"+mapper.__name__+"' must return exactly 2 values. (a key/value pair - simple put, a two-element tuple)"
	def __str__(self):
		return repr(self.value)

