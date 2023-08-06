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
'''Contains various type conversion functions for converting configuration
options into specific types.

'''
from pyamp.logging import LogLevel


__all__ = ["logLevel", "string", "boolean"]


def logLevel(value):
    '''Get the log level type from the string representation of
    the log level (DEBUG, INFO, WARN, or ERROR).

    * value -- The string value for the desired log level

    '''
    return getattr(LogLevel, value.upper(), LogLevel.INFO)


def string(value):
    '''Convert the given value into a string type -- being sure to remove
    any quotations that may be around the string.

    * value -- The value to convert into a string

    '''
    value = str(value)

    # If the string contains quotes around the string, then remove them
    if len(value) > 0 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]

    return value


def boolean(value):
    '''Convert the given value into a boolean type.

    * value -- The value to convert into a string

    '''
    return str(value).lower() == "true"
