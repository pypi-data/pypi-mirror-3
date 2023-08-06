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
'''The interface module provides a base class which provides a function to
decorate functions in order to label specific functions as *interface*
functions.

The :class:`PassThrough' class is an implementation of the :class:`Interface`
class which provides the ability to connect a child :class:`PassThrough` object
to a parent :class:`PassThrough` object so that any time the child's interface
functions are called, the call is instead redirected to the parent's function
of the same name.

'''


__all__ = ["Interface", "PassThrough"]


class Interface:
    '''The Interface class provides to ability to identify specific class
    functions to be 'interface' functions.

    This class contains a class property called InterfaceProperty which defines
    the name of the property used to identify interface functions.

    This class provides a :func:`interface` function which uses the
    InterfaceProperty property to create an implementation specific decorator
    which can be used to decorate functions that should identified as interface
    functions.

    Example::

       class Example(Interface):
           InterfaceProperty = "ExampleInterfaceProperty"

           @Example.interface
           def testPrint(self, message):
               print "Message:", message

    This the above example the :func:`testPrint` function has been decorated
    and is thus an interface function.

    '''

    @classmethod
    def interface(cls, function):
        '''A decorator for functions to make them interface functions for
        this Interface instance.

        * function -- The function to decorate

        '''
        setattr(function, cls.InterfaceProperty, True)
        return function

    def getInterfaceFunctions(self):
        '''Get a dictionary of the interface function names mapped
        to the actual functions.

        '''
        functions = {}

        # Traverse all of the class attributes
        for attrName in dir(self):
            attr = getattr(self, attrName, None)

            # Only deal with existing functions
            if attr is not None and hasattr(attr, "__call__"):
                # Determine if the function is allowed to pass through
                if hasattr(attr, self.InterfaceProperty):
                    functions[attrName] = attr

        return functions

    def connect(self, parent):
        '''Connect to a parent's interface methods.

        Note: This should be overriden by concrete Interfaces

        * parent -- The parent interface object

        '''
        pass

    @classmethod
    def isInterface(cls, obj):
        '''Determine if the given object is an instance of the interface.

        * obj -- The object

        '''
        return isinstance(obj, cls)


class PassThrough(Interface):
    '''The PassThrough :class:`Interface` provides the ability for a child
    PassThrough object to connect functions of the same name to the parent's
    :class:`Interface` functions.

    When a child class connects to the parent's interface functions, all calls
    to the child's interface functions are instead redirected to the parent's
    functions of the same name.

    Example::

        class Parent(PassThrough):
            @PassThrough.interface
            def testPrint(self, message):
                print "Parent message:", message

        class Child(PassThrough):
            pass

        parent = Parent()
        child = Child()
        child.connect(parent)

        # Prints:
        #    "Parent message:", this is a message
        child.testPrint("this is a message")

    '''
    InterfaceProperty = "PassThroughFunction"

    def connect(self, parent):
        '''Connect the child to the parent's interface functions.

        * parent -- The parent Interface

        '''
        # Make sure the parent implements the interface
        if not PassThrough.isInterface(parent):
            raise Exception("Parent [%s] must implement the " \
                                "PassThrough interface!" % parent)

        # Duplicate each of our parent's interface functions for our
        # own use, to pass the calls straight through
        for name, function in parent.getInterfaceFunctions().iteritems():
            setattr(self, name, function)


if __name__ == '__main__':
    class Parent(PassThrough):
        '''Class for testing the pass through interface.'''
        @PassThrough.interface
        def testPrint(self, message):
            '''Function for testing the pass through interface.'''
            print "Parent message:", message

    class Child(PassThrough):
        '''Class for testing the pass through interface.'''
        pass

    testParent = Parent()
    testChild = Child()
    testChild.connect(testParent)

    testChild.testPrint("this is a message")
