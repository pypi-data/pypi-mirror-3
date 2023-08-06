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
'''The option module contains the Option class for creating a specific
configuration option, as well as the ClOption class for creating a
command line option.

'''
from pyamp.util.dictionary import addNotNone


__all__ = ["Option", "ClOption", "ClBoolOption"]


class Option:
    '''The Option class encapsulates a single configuration option. It contains
    the name of the option, a default value for the option, as well as a
    function to convert the option into a specific type.

    '''

    def __init__(self, name, defaultValue=None, typeFn=None,
                 commandLine=False):
        '''
        * name -- The name of the option
        * defaultValue -- The default value for this option
        * typeFn -- The function to convert the value to a specific type
        * commandLine -- True to be a command line option

        '''
        self.__name = name
        self.__defaultValue = defaultValue
        self.__typeFn = typeFn
        self.__commandLine = commandLine

    def isCommandLine(self):
        '''Determine if this Option is configurable through the command
        line.

        '''
        return self.__commandLine

    def getName(self):
        '''Get the name of this Option.'''
        return self.__name

    def getDefaultValue(self):
        '''Get the default value for this Option.'''
        return self.__defaultValue

    def convert(self, value):
        '''Convert the given value into the expected type for this Option.

        * value -- The value to convert

        '''
        convertedValue = value
        if self.__typeFn is not None:
            convertedValue = self.__typeFn(value)

        return convertedValue


class ClOption(Option):
    '''The ClOption class encapsulates an :class:`Option` that is configurable
    through the command line as well as through a configuration file.

    '''

    def __init__(self, name, abbr=None, defaultValue=None,
                 action=None, optionType=None, helpText=None):
        '''
        * name -- The name of the option
        * abbr -- The abbreviated name
        * defaultValue -- The default value for this option
        * action -- The action used for this option
        * optionType -- The type of the option
        * helpText -- The help text to display

        '''
        self.__abbreviatedName = abbr
        self.__action = action
        self.__help = helpText
        self.__type = optionType

        Option.__init__(self, name, defaultValue=defaultValue,
                        commandLine=True)

    def addOption(self, parser):
        '''Add the command line option to the command line parser.

        * parser -- The command line parser

        '''
        name = self.getName()

        keywords = {}
        addNotNone(keywords, "default", self.getDefaultValue())
        addNotNone(keywords, "action", self.__action)
        addNotNone(keywords, "type", self.__type)
        addNotNone(keywords, "help", self.__help)

        # Add the option to the option parser according to the
        # configured options
        if self.__abbreviatedName is not None:
            parser.add_option("-%s" % self.__abbreviatedName, "--%s" % name,
                              **keywords)
        else:
            parser.add_option("--%s" % name, **keywords)


class ClBoolOption(ClOption):
    '''The ClBoolOption encapsulates a boolean configuration option.

    If the boolean does not exist, the option will be set to the default value
    otherwise it will be set to the inverse of the default value.

    '''

    def __init__(self, name, abbr=None, defaultValue=False, helpText=None):
        '''
        * name -- The name of the option
        * abbr -- The abbreviated name for the option
        * defaultValue -- The default value (True or False)
        * helpText -- The help text for this option

        '''
        action = "store_%s" % str(not defaultValue).lower()

        ClOption.__init__(self, name, abbr=abbr, defaultValue=defaultValue,
                          action=action, helpText=helpText)
