# Copyright 2012 Brett Ponsler
# This file is part of pyamp.
#
# pyamp is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyamp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyamp.  If not, see <http://www.gnu.org/licenses/>.
'''The exceptions module contains definitions of common Exception
classes which are used throughout the pyamp project to indicate
errors to the programmer.

'''
from pyamp.util.objects import getName


class UndefinedPropertyError(Exception):
    '''A class or object is missing a required property.'''

    def __init__(self, obj, propertyName):
        '''
        * obj -- The class or object
        * propertyName -- The name of the property that is required

        '''
        message = "Class [%s] is missing a required property: [%s]" % \
            (getName(obj), propertyName)

        Exception.__init__(self, message)


class UndefinedFunctionError(Exception):
    '''A class or object is missing a required function.'''

    def __init__(self, obj, functionName):
        '''
        * obj -- The class or object
        * functionName -- The name of the required function

        '''
        message = "Class [%s] is missing a required function: [%s]" % \
            (getName(obj), functionName)

        Exception.__init__(self, message)


class FinalFunctionError(Exception):
    '''The FinalFunctionError class provides an Exception which is raised
    in the event that a class attempts to override a final function.

    '''

    def __init__(self, classObj, functionName):
        '''
        * classObj -- The classObj (class, instance, or a string)
        * functionName -- The name of final function

        '''
        message = "The '%s' function is final and cannot be overridden by " \
            "subclasses of '%s'!" % (functionName, getName(classObj))
        Exception.__init__(self, message)


class InvalidPropertyValueError(Exception):
    '''The InvalidPropertyValueError is raised in the event that a class
    property has an unexpected, or invalid, value.

    '''

    def __init__(self, classObj, propName, value, expected):
        '''
        * classObj -- The class obj (class, instance, or string name)
        * propName -- The name of the invalid property
        * value -- The invalid property value
        * expected -- The expected value for the property

        '''
        message = "Property '%s' for '%s' has an invalid value: %s, " \
            "expected: %s" % (propName, getName(classObj),
                              str(value), expected)
        Exception.__init__(self, message)
