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
'''The argument module contains the Argument class which provides
the ability to create and manage arguments that can be passed
through HTTP requests.

'''


class Argument:
    '''The Argument class encapsulates the concept of an HTTP argument
    passed through a URL request.

    Arguments can have a specific type, can be required or optional,
    and can have a default value if they are optional and not passed in
    the request.

    '''

    def __init__(self, argumentType, required=False, default=None):
        '''
        * argumentType -- The type of the argument
        * required -- True if the argument is required, False otherwise
        * default -- The default value for optional Arguments

        '''
        self.__type = argumentType
        self.__required = required

        # Ensure that the default value is the correct type
        if default is not None and type(default) != self.__getType():
            raise Exception("Default value must be type %s" % \
                                self.__getType().__name__)

        self.__defaultValue = self.convertValue(default)

    def getDefaultValue(self):
        '''Return the default value for this Argument.'''
        return self.__defaultValue

    def isRequired(self):
        '''Determine if this is a required Argument or an optional Argument.'''
        return self.__required

    def convertValue(self, value):
        '''Convert the given value to the expected type of the Argument.

        * value -- The value of the argument passed in the request

        '''
        if value is None:
            return value

        try:
            evaluated = eval(str(value))
        except NameError:
            evaluated = value

        if type(evaluated) != self.__getType():
            raise Exception("Argument expected type '%s' but found " \
                                "type '%s'" % (self.__getType().__name__,
                                               type(evaluated).__name__))

        # The types match, return the converted value
        return evaluated

    ##### Private Functions #####

    def __getType(self):
        '''Get the type of this Argument.'''
        return type(self.__type())


class IntArgument(Argument):
    '''The IntArgument class provides a class to easily create
    an integer argument.

    '''

    def __init__(self, required=False, default=None):
        '''
        * required -- True if the argument is required, False otherwise
        * default -- The default value for optional Arguments

        '''
        Argument.__init__(self, int, required, default)


class FloatArgument(Argument):
    '''The FloatArgument class provides a class to easily create
    an float argument.

    '''

    def __init__(self, required=False, default=None):
        '''
        * required -- True if the argument is required, False otherwise
        * default -- The default value for optional Arguments

        '''
        Argument.__init__(self, float, required, default)


class BoolArgument(Argument):
    '''The BoolArgument class provides a class to easily create
    an boolean argument.

    '''

    def __init__(self, required=False, default=None):
        '''
        * required -- True if the argument is required, False otherwise
        * default -- The default value for optional Arguments

        '''
        Argument.__init__(self, bool, required, default)


class StrArgument(Argument):
    '''The StrArgument class provides a class to easily create
    a string argument.

    '''

    def __init__(self, required=False, default=None):
        '''
        * required -- True if the argument is required, False otherwise
        * default -- The default value for optional Arguments

        '''
        Argument.__init__(self, str, required, default)
