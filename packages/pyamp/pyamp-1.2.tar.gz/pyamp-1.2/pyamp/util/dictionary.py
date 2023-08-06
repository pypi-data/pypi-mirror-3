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
'''The dictionary module Contains utility methods for manipulating and dealing
with dictionary objects.

'''


def getItems(dictionary, items, default=None):
    '''Return the given items in the dictionary, each item is taken
    from the dictionary contained within the previous item, and if
    one of the items in the chain does not exist this function
    returns the default value.

    Example::

        from pyamp.util.dictionary import getItems

        d = {"first": {"second": {"third": 500}}}

        # Prints: 500
        print getItems(d, ["first", "second", "third"])

        # Prints: 200
        print getItems(d, ["first", "non-existent"], 200)

    * dictionary -- The dictionary
    * items -- The list of items
    * default -- The default value

    '''
    for item in items:
        if dictionary is not None and item in dictionary:
            dictionary = dictionary[item]
        else:
            return default

    return dictionary


def addNotNone(dictionary, key, value):
    '''Add the given value for the given key to the dictionary, only if the
    value is not None.

    * dictionary -- The dictionary to add the key to
    * key -- The key
    * value -- The value for the key

    '''
    if value is not None:
        dictionary[key] = value

    return dictionary
