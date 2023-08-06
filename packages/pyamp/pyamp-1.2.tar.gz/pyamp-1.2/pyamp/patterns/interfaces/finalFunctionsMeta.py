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
'''The finalFunctionsMeta module contians classes which provide the
ability to declare specific functions of a class to be 'final', which
means that an Exception will be raised in the event that a subclass
tries to override the functionality of those functions.

Here is an example of using the classes in this module::

    # First define the metaclass that defines the list of final functions
    class FinalMeta(FinalFunctionsMeta):
        finalFunctions = ["__del__"]

    # Now define the base class which forces all child classes to use the
    # correct metaclass
    class Parent(FinalFunctionsParentBase):
        requiredMetaclass = FinalMeta

        def __init__(self):
            FinalFunctionsParentBase.__init__(self)

    # Finally, define the child class and override a few of the
    # parents functions
    class Child(Parent):
        __metaclass__ = FinalMeta

        # This function can be overridden
        def __init__(self):
            Parent.__init__(self)

        # This function CANNOT be overridden
        def __del__(self):
            Parent.__del__(self)

    # This will throw an Exception indicating that __del__ cannot be
    # overridden by the Child class!
    c = Child()

'''
from pyamp.util import isFunction
from pyamp.patterns.interfaces import RequiredProperties
from pyamp.exceptions import FinalFunctionError, InvalidPropertyValueError


class FinalFunctionsMeta(type):
    '''The FinalFunctionMeta class is a metaclass which provides the ability
    to define a list of functions that should not be allowed to be overridden
    by classes which use this metaclass.

    '''
    finalFunctions = []

    def __new__(mcs, className, parents, attributes):
        ''' '''
        for name, attribute in attributes.iteritems():
            if name in mcs.finalFunctions and isFunction(attribute):
                raise FinalFunctionError(className, name)

        return type.__new__(mcs, className, parents, attributes)


class FinalFunctionsParentBase(object, RequiredProperties):
    '''The FinalFunctionsParentBase provides a base class which provides the
    ability to define final functions in the base class. This will prevent any
    subclasses from overloading these specific, i.e., final, functions.

    This class provides the ability to specify the specific metaclass that
    **must** be defined for all subclasses of this base class. The metaclass
    chosen should be a subclass of the :class:`.FinalFunctionsMeta` metaclass
    which defines the list of final functions and keeps them from being
    overridden.

    '''
    requiredMetaclass = None

    def __init__(self):
        '''Create the FinalFunctionsParentBase class.'''
        # Set the required metaclass, only if one is provided
        if self.requiredMetaclass is not None:
            self._RequiredProperties = [("__metaclass__",
                                         self.requiredMetaclass)]
        RequiredProperties.__init__(self)
