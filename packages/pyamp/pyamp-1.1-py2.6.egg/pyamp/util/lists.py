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
'''The lists module contains utility functions for managing and manipulating
lists objects.

'''


def splitList(items, conditionFn):
    '''Split a list into two halves using a condition function where the first
    list returned contains all the elements for which the condition function
    evaluated to True, and the second list returned contains all the elements
    for which the condition function evaluated to False.

    * items -- The list of items
    * conditionFn -- The condition function to apply to all the items

    '''
    trueList = []
    falseList = []

    for item in items:
        if conditionFn(item):
            trueList.append(item)
        else:
            falseList.append(item)

    return trueList, falseList


def filterNone(items):
    '''Return the given list with any item which is None removed from
    the list.

    * items -- The list of items

    '''
    return [item for item in items if item is not None]
