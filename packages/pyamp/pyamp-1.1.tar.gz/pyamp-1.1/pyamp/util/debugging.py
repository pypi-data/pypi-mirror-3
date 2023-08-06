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
'''The debugging module contains utility methods which are useful when
debugging systems.

'''
from sys import exc_info
from traceback import format_exception


__all__ = ["getStackTrace", "getClassName"]


def getStackTrace():
    '''Get the current stack trace as a string.'''
    return ''.join(format_exception(*exc_info()))


def getClassName(obj):
    '''Get the class name for the given object.

    * obj -- The object

    '''
    return obj.__class__.__name__
