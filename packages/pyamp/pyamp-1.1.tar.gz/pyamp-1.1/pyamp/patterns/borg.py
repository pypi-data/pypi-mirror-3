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
'''The borg module contains the Borg class which provides an implementation
of the Borg design pattern, which is a Singleton like pattern for Python.

'''


__all__ = ["Borg"]


class Borg(object):
    '''The Borg class implements the Borg design pattern which provides
    a singleton like pattern for Python.

    A Borg object can be accessed by calling the :func:`getInstance` function.
    This functions returns an instance of the Borg class which stores its state
    between successive calls to get the Borg object.

    Instances of the Borg class can implement the :func:`init` function which
    is called when the Borg class is first created and initialized. This allows
    the concrete Borg classes to set up the initial state for their object.

    Example::

        class Example(Borg):
            def init(self, *args, **kwargs):
                self.x = kwargs['x']

        class First:
            def __init__(self):
                # An example of passing a value to the Borg instance
                b = Example(x=200)
                print "First, b.x:", b.x

        class Second:
            def __init__(self):
                # Optionally could use Borg.getInstance()
                b = Example.getInstance()
                print "Second, b.x:", b.x
                b.x = 500

        if __name__ == '__main__':
            First()
            Second()

            b = Example.getInstance()
            print "Third, b.x:", b.x

            # Prints:
            #    First, b.x: 200
            #    Second, b.x: 200
            #    Third, b.x: 500

    '''
    __sharedState = {}

    def __init__(self, *args, **kwargs):
        '''
        * args -- The arguments
        * kwargs -- The keyword arguments

        '''
        self.__dict__ = self.__sharedState

        # This needs to be moved one class up...

        # Keep track of the initialization status of this class
        if not self.getPrivateAttr("__init", False):
            self.setPrivateAttr("__init", True)
            self.init(*args, **kwargs)

    def init(self, *args, **kwargs):
        '''This function is called the first time the class is initialized,
        and should be overridden by concrete subclasses.

        * args -- The arguments
        * kwargs -- The keyword arguments

        '''
        pass

    def setPrivateAttr(self, name, value):
        '''Set the value of a private class attribute.

        * name -- The name of the private attribute
        * value -- The value to set the attribute to

        '''
        setattr(self, self.__mangleName(name), value)

    def getPrivateAttr(self, name, default=None):
        '''Return the value of a private class attribute.

        * name -- The name of the private attribute
        * default -- The value returned if the attribute does not exist

        '''
        return getattr(self, self.__mangleName(name), default)

    def __mangleName(self, name):
        '''Mangle the private attribute name.

        * name -- The private attribute name

        '''
        return "_%s%s" % (self.__class__.__name__, name)

    @classmethod
    def getInstance(cls):
        '''Get an instance of the Borg object.'''
        return cls()
