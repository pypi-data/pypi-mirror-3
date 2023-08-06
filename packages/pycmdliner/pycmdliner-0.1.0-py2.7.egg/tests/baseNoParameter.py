#!/usr/bin/env python
#
# Copyright 2012 Filippo Pacifici
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

'''
Test cases for base scenario of Command Liner

Tries jsut to run a command without parameters
'''

from pycmdliner.pycmdliner import Pycmdliner
from pycmdliner.pycmdliner import InvalidInputError


def testValidConfig():
	'''
	Tests some cases with valid input configuration
	'''
	config = {'commandMapping':
		{'command1': 'method1', 'command2': 'method2'}}
	business = Business()
	cmdliner = Pycmdliner(config, business)
	cmdliner.process(['command1'])
	assert(business.m1 == True)
	assert(business.m2 == False)
	assert(business.m3 == False)


def testNoCommand():
	'''
	Tests a case where the command does not exist.
	'''
	config = {'commandMapping':
		{'command1': 'method1', 'command2': 'method2'},
		'appHeader': 'My useless program version 0.1',
		'usageString': "Don't use"}
	business = Business()
	cmdliner = Pycmdliner(config, business)

	cmdliner.process(['argfargf', 'argf'])
	assert(business.m1 == False)
	assert(business.m2 == False)
	assert(business.m3 == False)

	'try with a default method'
	del config['usageString']
	config['usageMethod'] = 'default'
	cmdliner = Pycmdliner(config, business)

	cmdliner.process(['argfargf', 'argf'])
	assert(business.m1 == False)
	assert(business.m2 == False)
	assert(business.m3 == False)

	'try with a defautl method that does not exist'
	del config['usageMethod']
	config['usageMethod'] = 'Strupniveralms'
	cmdliner = Pycmdliner(config, business)

	try:
		cmdliner.process(['argfargf', 'argf'])
		assert (False)
	except Exception:
		pass

	'''Try with a usage file'''
	del config['usageMethod']
	config['usageFile'] = './testUsage.txt'

	cmdliner = Pycmdliner(config, business)

	cmdliner.process(['argfargf', 'argf'])
	assert(business.m1 == False)
	assert(business.m2 == False)
	assert(business.m3 == False)


def testPassingParameters():
	'''
	Tests a case where the user provides parameters.
	'''
	config = {'commandMapping':
		{'command1': 'method1', 'command4': 'method4'},
		'appHeader': 'My useless program version 0.1',
		'usageString': "Don't use"}
	business = Business()
	cmdliner = Pycmdliner(config, business)

	cmdliner.process(['command4', 1, 2])
	assert(business.m1 == False)
	assert(business.m2 == False)
	assert(business.m3 == False)
	assert(business.m4 == 3)


def testSingleCommand():
	'''
	Tests the case where the configuration contains only a default command
	not to be provided in input. (commands like ls which take only parameters
		or options)
	'''
	config = {'defaultCommand': 'method4',
		'usageString': 'Use at your high risk',
		'appHeader': 'Myapp version 1234.12'}
	business = Business()
	cmdliner = Pycmdliner(config, business)

	cmdliner.process([1, 2])
	assert(business.m1 == False)
	assert(business.m2 == False)
	assert(business.m3 == False)
	assert(business.m4 == 3)


class Business(object):
	"""Business object for the tests"""
	def __init__(self):
		super(Business, self).__init__()
		self.m1 = False
		self.m2 = False
		self.m3 = False
		self.m4 = False

	def method1(self):
		self.m1 = True

	def method2(self):
		self.m2 = True

	def method3(self):
		self.m3 = True

	def method4(self, a, b, c='x'):
		self.m4 = a + b

	def default(self):
		return 'Use at your risk'

if __name__ == '__main__':
	testValidConfig()
	print 'Valid basic config'
	testNoCommand()
	print 'Valid error in case of invalid command'
	testPassingParameters()
	print 'Valid passing of parameters'
	testSingleCommand()
	print 'Tested with a single command'
