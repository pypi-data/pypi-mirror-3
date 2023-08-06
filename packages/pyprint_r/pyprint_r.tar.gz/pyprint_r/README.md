# print_r()

This module provides a function that prints human-readable information about the object

##Prototype:
	string print_r (mixed object [, bool view = False])

##Installation

*1. Install using [Setuptools] (http://pypi.python.org/pypi/setuptools):*

Download the module from: http://pypi.python.org/pypi/pyprint_r/

	# python setup.py install

Or run using [easy_install] (http://packages.python.org/distribute/easy_install.html):

	# easy_install pyprint_r

*Include:*

	from pyprint_r import print_r

NOTE: If you have not installed [setuptools] (http://pypi.python.org/pypi/setuptools) you should read about [Distribute] (http://packages.python.org/distribute/).

*Distribute installation:*

	curl -O http://python-distribute.org/distribute_setup.py
	python distribute_setup.py
	easy_install pip

*2. Install using the compilation:*
Create a *.py* file and include:

	from print_r import *

Then you will get a file named *print_r.pyc* and place the one in your installation/working directory

## Use
*For example you could use the following code:*

	from print_r import *

	class Class:
		def __init__(self):
			self.foo = 10

	instance = Class()

	obj = {
		'number': 1,
		'object': {
			'string': "text",
			'list' : [1, 2, 3]
		},
		'class' : Class,
		'instance' : instance
	};

	print_r(Class);
	print_r(obj);
	print_r(list);

*Result:*

	class
	------------------------------
	<class '__main__.Class'>

	dict
	------------------------------
	{
		class: <class '__main__.Class'>,
		instance: {
			foo: 10
		},
		number: 1,
		object: {
			list: [1, 2, 3],
			string: "text"
		}
	}

	list
	------------------------------
	[0] => 1
	[1] => 2
	[2] => 3

If you set the second parameter <view> in boolean value True, you will get an alternate view.<br />

*Result:*

	class
	------------------------------
	<class '__main__.Class'>

	dict
	------------------------------
	{
		[class] => <class '__main__.Class'>,
		[instance] => {
			[foo] => 10
		},
		[number] => 1,
		[object] => {
			[list] => [1, 2, 3],
			[string] => "text"
		}
	}

	list
	------------------------------
	[0] => 1
	[1] => 2
	[2] => 3


* License
    The toCSS module is licensed under the MIT (MIT_LICENSE.txt) license.

* Copyright (c) 2011 [Alexander Guinness] (https://github.com/monolithed)
