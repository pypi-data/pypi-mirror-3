# coding=utf-8

import unittest, logging
from pyprint_r import print_r

logging.basicConfig(level = logging.DEBUG)

class Class:
	def __init__(self):
		self.foo = 10

instance = Class()

class test_case(unittest.TestCase):
	def test_instance(self):
		print('class instance:')
		print_r(instance)

	def test_list(self):
		print('list:')
		print_r([1,2,3, {'foo': 1, 'bar': 2}, instance])

	def test_dict(self):
		print('dict:')
		print_r({
			'number': 1,
			'object': {
				'string': "text",
				'list' : [1, 2, instance]
			},
			'instance' : instance
		})

if __name__ == '__main__':
	unittest.main()