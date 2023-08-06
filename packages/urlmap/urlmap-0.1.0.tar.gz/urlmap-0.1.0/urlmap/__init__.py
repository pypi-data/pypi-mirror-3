"""
urlmap

Copyright (c) 2012 Benjamin Sherratt

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

__version__ = "0.1.0"

import re

class RouteException(Exception):
	"""
	Generic route exception
	"""

	def __init__(self, route):
		self._route = route

class BadRouteException(RouteException):
	"""
	Badly formed route exception
	"""

	pass

class RouteNotFoundException(RouteException):
	"""
	Route not found exception
	"""

	pass

class RouteExistsException(RouteException):
	"""
	Route exists exception
	"""

	pass

class _Component(object):
	def __init__(self):
		self._obj = None
		self._literals = {}
		self._regexes = {}

	def __call__(self, key):
		try:
			return (self._literals[key], None)
		except KeyError:
			for (regex, component) in self._regexes.values():
				if regex.match(key):
					return (component, key)

			raise LookupError()

	def __getitem__(self, key):
		try:
			return self._literals[key]
		except KeyError:
			(regex, component) = self._regexes[key]
			return component

	def __setitem__(self, key, value):
		if key[0] == "^" and key[-1] == "$":
			self._regexes[key] = (re.compile(key), value)
		else:
			self._literals[key] = value

	@property
	def obj(self):
		return self._obj

	@obj.setter
	def obj(self, obj):
		self._obj = obj

route_component_tree = _Component()

def _split_route(route):
	split_route = str(route).split("/")

	if split_route[0] == "":
		split_route = split_route[1:]

		if split_route[-1] == "":
			split_route = split_route[:-1]

		return split_route
	else:
		raise BadRouteException(route)

def map(route):
	"""
	This maps an object to a route that you specify.
	Use this function to decorate the object.
	"""

	def mapper(obj):
		split_route = _split_route(route)

		current_component = route_component_tree

		for part in split_route:
			try:
				current_component = current_component[part]
			except KeyError:
				next_component = _Component()
				current_component[part] = next_component
				current_component = next_component

		if not current_component.obj:
			current_component.obj = obj

			return obj
		else:
			raise RouteExistsException(route)

	return mapper

def retrieve(route):
	"""
	This returns a tuple of the object associated with a route and all the parameters extracted from the URL.
	"""

	parameters = []
	split_route = _split_route(route)

	current_component = route_component_tree

	for part in split_route:
		try:
			(current_component, parameter) = current_component(part)

			if parameter:
				parameters.append(parameter)
		except LookupError:
			raise RouteNotFoundException(route)

	if current_component.obj:
		return (current_component.obj, parameters)
	else:
		raise RouteNotFoundException(route)
