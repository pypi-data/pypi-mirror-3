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
'''The requiredProperties module contains a class which provides
an interface which allows a class to define a set of properties
which the subclasses are required to define. This class handles
checking that each of those required properties are defined and
throwing an error in the event that one of them is not defined.

'''
from pyamp.exceptions import UndefinedPropertyError, InvalidPropertyValueError


class RequiredProperties:
    '''The RequiredProperties class provides an interface which allows
    subclasses to define a set of properties that must be defined for
    that class.

    This class checks that all of those properties are defined, and if
    one of them is not defined this class throws an exception.

    '''
    _RequiredProperties = []
    '''The list of properties that are required to be defined. Each item in
    the list can be either a single property name which must be defined, or
    a tuple where the first element in the tuple is the name of the property
    that must be defined and the second element in the tuple is the value
    the property must have.

    .. note:: Subclasses should set this property to the list of
       properties that are required for the particular class.

    '''

    def  __init__(self):
        '''Check that all the required properties are defined.'''
        self.__checkRequiredProperties(self)

    @classmethod
    def checkRequiredProperties(cls, obj):
        ''' '''
        cls.__checkRequiredProperties(obj)

    ##### Private functions #####

    @classmethod
    def __checkRequiredProperties(cls, obj):
        '''Check that all of the required properties are defined and
        throw an error in the event if any are not defined.

        * obj -- The object to ensure has all its required properties

        '''
        for prop in obj._RequiredProperties:
            # Determine if the property is only a property name, or if it
            # also includes a required value as well
            if type(prop) == type(str()):
                cls.__requireProperty(obj, prop)
            elif type(prop) == type(tuple()) and len(prop) == 2:
                # Grab the name (first element) and value (second element)
                name, value = prop
                
                cls.__requirePropertyValue(obj, name, value)
            else:
                raise InvalidPropertyValueError(obj, "_RequiredProperties",
                                        prop, "string, or tuple of length two")

    @classmethod
    def __requireProperty(cls, obj, name):
        '''Check that the property with the given name is defined.

        * obj -- The object being checked for the required property
        * name -- The name of the required property

        '''
        if not hasattr(obj, name):
            raise UndefinedPropertyError(obj, name)

    @classmethod
    def __requirePropertyValue(cls, obj, name, expected):
        '''Check that the property with the given name is defined and has
        the expected value.

        * obj -- The object being checked for the required property
        * name -- The name of the required property
        * expected -- The expected value for the property

        '''
        cls.__requireProperty(obj, name)

        # Ensure that the property has the expected value
        actual = getattr(obj, name) 
        if actual != expected:
            raise InvalidPropertyValueError(obj, name, actual, expected)
