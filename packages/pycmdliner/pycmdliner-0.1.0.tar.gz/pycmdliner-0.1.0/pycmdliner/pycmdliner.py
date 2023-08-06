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


import sys
import inspect


class Pycmdliner(object):
    '''
    Python Command liner script.

    Provides the boiler plate code for developing command line non
    interactive tools.

    The main idea is that the user provides a small configurationa and
    an object that implements business logic, then this script interprets
    input parameters and invokes the correct  method on the business logic
    object setting correctly input parameters and attributes.

    Created on Aug 27, 2012

    @author: fpacifici
    '''

    def __init__(self, configuration, businessObject):
        '''
        Initializes the Command liner providing the business object,
        if needed it gets the list of input parameters and the configuration
        '''
        super(Pycmdliner, self).__init__()
        if configuration == None or businessObject == None:
            raise Exception('Configuration and Business Object cannot be' +
                ' null to instantiate a PyCmdLiner')

        if type(configuration) != dict:
            raise Exception('COnfiguration must be a dictionary')

        self.configuration = configuration
        self.businessObject = businessObject


    def process(self, inputParams = sys.argv[1:], businessObject = None):
        '''
        Performs the actual processing of the command line tool.

        1) parse input commands elements to check if the size is correct
        2) find the command to be executed
        3) gets the method name for the command to be executed
        4) runs the command.
        '''
        self.printCaption()

        if businessObject == None and self.businessObject == None:
            raise Exception('Business object not provided')
        bObject = self.businessObject
        if businessObject != None:
            bObject = businessObject

        methodToExecute = None
        try:
            methodToExecute = self.__extractMethod__(inputParams, bObject)
        except InvalidInputError:
            self.printDefaultUsage()
            return

        '''applies an offset to parameters list only if the first parameter is the name
        of the command, otherwise passes the full parameters list'''
        offset = 0 if 'defaultCommand' in self.configuration else 1

        return self.__runMethod__(bObject, methodToExecute, inputParams[offset:])


    def printCaption(self):
        '''
        Prints the application header as provided in the configuration.
        '''
        if 'appHeader' in self.configuration:
            print self.configuration['appHeader']


    def printDefaultUsage(self):
        '''
        Prints the usage of the application, either taking it from the configuration
        or taking it from a business method, or taking it from a file.
        '''
        if 'usageString' in self.configuration:
            print self.configuration['usageString']
        elif 'usageMethod' in self.configuration:
            print self.__runMethod__(self.businessObject, self.configuration['usageMethod'])
        elif 'usageFile' in self.configuration:
            f = open(self.configuration['usageFile'], 'r')
            for line in f:
                print line


    def __basicInputValidation__(self, inputParameters):
        '''
        Validate input parameters according to the configuration
        '''
        if len(inputParameters) < 1:
            raise InvalidInputError('Not Enough input parameters')


    def __extractMethod__(self, inputParameters, businessObject):
        if 'commandMapping' not in self.configuration and 'defaultCommand' not in self.configuration:
            raise Exception('Invalid configuration: commandMapping section not present')

        else:
            mapping = None
            offset = 0
            if 'commandMapping' in self.configuration:
                self.__basicInputValidation__(inputParameters)
                command = inputParameters[0]
                if command in self.configuration['commandMapping']:
                    mapping = self.configuration['commandMapping'][command]
                    offset = 1
                else:
                    raise InvalidInputError('Command %s does not exist' % command)
            elif 'defaultCommand' in self.configuration:
                mapping = self.configuration['defaultCommand']

            self.__checkParameters__(inputParameters[offset:],
                mapping, businessObject)

            return mapping


    def __checkParameters__(self, inputParameters, objectMethodName, businessObject):
        '''
        Checks if the provided input parameters are valid in number for
        the provided method.

        First the minimum number of input parameter is checked. Then
        the maximum number is checked as well.
        '''
        methodObject = getattr(businessObject, objectMethodName)
        totalParamsNumber = len(inspect.getargspec(methodObject).args)
        '''remove self'''
        totalParamsNumber = totalParamsNumber - 1
        nonMandatoryPs = inspect.getargspec(methodObject).defaults
        nonMandatoryparamsNumber = 0 if nonMandatoryPs == None else len(nonMandatoryPs)

        passedParamsNumber = len(inputParameters)

        if passedParamsNumber < (totalParamsNumber - nonMandatoryparamsNumber) or passedParamsNumber > totalParamsNumber:
            raise InvalidInputError('Invalid number of passed params: %d' % passedParamsNumber)


    def __runMethod__(self, businessObject, methodName, params = []):
        method = getattr(businessObject, methodName)
        return method(*params)


class InvalidInputError(Exception):
    """Manages invalid input exceptions"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
