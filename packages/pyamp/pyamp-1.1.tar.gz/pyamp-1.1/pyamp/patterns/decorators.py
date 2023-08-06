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
'''Contains decorator functions for performing various common tasks.'''


__all__ = ["listProperty"]


def listProperty(propName, values):
    '''The listProperty function returns a decorator that appends a list of
    values (to the property with the given name) to a function's attributes.

    Example::

        @listProperty("test", [1, "two", 3])
        def example(self):
            pass

        @listProperty("prop", [1])
        @listProperty("prop", ["another property"])
        @listProperty("prop", [True])
        def example2(self):
            pass

        # Prints: [1, "two", 3]
        print example.test

        # Prints: [1, "another property", True]
        print example2.prop

    * propName -- The name of the property to set on the decorated function
    * values -- The value, or list of values, to append

    '''
    # Ensure that we were given a list of values
    if type(values) != type(list()):
        values = [values]

    def wrapper(function):
        '''A decorator function for adding a list of values to a function.

        * function -- The function

        '''
        current = getattr(function, propName, [])
        setattr(function, propName, current + values)
        return function

    return wrapper
