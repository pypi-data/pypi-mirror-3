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
'''The enum module contains the Enum class which provides the ability to
make a class act as an enumeration.

'''


class Enum:
    '''The Enum class provides the ability to create a class which acts as an
    enumeration. Class properties can be set as the enumeration values, and a
    dictionary of the entire enumeration keys and values can be retrieved.

    Example::

        class Test(Enum):
            Prop1 = "This is a string property"
            Prop2 = 123
            Another = True
            AnyIdName = {"test": 0}
            ListId = [1, 2, 3, 4]

    Calling Test.get(), returns::

        { "Prop1": "This is a string property",
          "Prop2": 123,
          "Another": True,
          "AnyIdName": {"test": 0},
          "ListId": [1, 2, 3, 4]
        }

    '''

    def __init__(self):
        '''Create an Enum.'''
        pass

    @classmethod
    def get(cls):
        '''Get the list of configured enumeration values.'''
        properties = {}
        for name in cls.__getAttributes():
            properties[name] = getattr(cls, name, None)

        return properties

    @classmethod
    def __getAttributes(cls):
        '''Get the list of the class attributes.'''
        return [item for item in dir(cls) if cls.__notBuiltinOrFunction(item)]

    @classmethod
    def __notBuiltinOrFunction(cls, name):
        '''Return True if the class attribute with the given name is not a
        builtin attribute (starts with an underscore) and it is also not
        a function.

        * name -- The name of the attribute to evaluate

        '''
        attr = getattr(cls, name, None)
        return not name.startswith("_") and not hasattr(attr, "__call__")
