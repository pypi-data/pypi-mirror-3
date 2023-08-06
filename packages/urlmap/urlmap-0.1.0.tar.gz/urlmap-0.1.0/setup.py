#!/usr/bin/env python

"""
urlmap
======
Yet another library to map URLs to Python objects and get parameters.
This is designed to be as lightweight as possible. Please fork, but merge requests that add new "features" are likely to be rejected.

License
-------
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

import distutils.core

try:
	import setuptools
except ImportError:
	pass

from urlmap import __version__

distutils.core.setup(
	name="urlmap",
	version=__version__,
	description="Map urls to Python objects",
	long_description=__doc__,
	author="Benjamin Sherratt",
	author_email="ben.sherratt@gmail.com",
	url="https://github.com/0wls/urlmap",
	packages=["urlmap"],
	setup_requires = [],
	license="MIT"
)
