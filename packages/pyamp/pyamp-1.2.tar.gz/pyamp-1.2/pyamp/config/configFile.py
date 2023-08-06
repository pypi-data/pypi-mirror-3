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
'''The configFile module contains the ConfigFile class which provides
the ability to parse a configuration file for configured :class:`Option`
objects.

'''
from os.path import exists
from ConfigParser import ConfigParser

from pyamp.logging import Loggable


__all__ = ["ConfigFile"]


class ConfigFile(Loggable):
    '''The ConfigFile class is responsible for parsing a configuration file
    with the given dictionary of sections and options, and variables.

    The ConfigFile class takes a dictionary of options which map the
    configuration section names to the list of configuration :class:`Option`
    objects associated with that section. It also takes a dictionary of
    variables mapping the name of the variable to the value for the variable.
    The variable names can then be used in a configuration file by adding
    a $ before the variable name. This value will then be replaced with the
    value assigned in the variables dictionary.

    This class implements the :class:`Loggable` interface. This class uses the
    :mod:`ConfigParser` module to parse the configuration file, and thus parses
    configuration files of the same format.

    '''

    def __init__(self, configurationFile=None, options=None, variables=None,
                 logger=None):
        '''
        * configurationFile -- The configuration file to load
        * options -- The dictionary of supported options
        * variables -- The dictionary of supported variables
        * logger -- The logger

        '''
        Loggable.__init__(self, self.__class__.__name__, logger)

        # Define the set of variables that can be used in the config file
        # Note: Each variable must be used with a $ before it to indicate that
        #       it is a config variable that should be replaced. Variable names
        #       should also be all caps, and do not include spaces.
        self.__variables = {} if variables is None else variables

        # A dictionary mapping section names to the Option objects that each
        # section contains
        self.__options = {} if options is None else options
        self.__settings = {}

        # Initialize all of the variables which will store options
        # prior to parsing the configuration file
        for section, sectionOptions in self.__options.iteritems():
            # Ensure that a list of options is given
            objType = type(self.__options[section])
            if objType != type(list()):
                raise Exception("Section [%s] must have a list of options " \
                                    "not a '%s'!" % (section, objType))

            for option in sectionOptions:
                setattr(self, option.getName(), option.getDefaultValue())

        # Print all of the variables for debugging
        for name, value in self.__variables.iteritems():
            self.debug("Variable: [%s] = %s" % (name, str(value)), level=5)

        if configurationFile is not None:
            self.parse(configurationFile)

    def getSettings(self):
        '''Get the settings dictionary.'''
        return self.__settings

    def get(self, section, option, defaultValue=None):
        '''Get the value of the given configuration option from the given
        section.

        * section -- The section name
        * option -- The option
        * defaultValue -- The default value if the option does not exist

        '''
        sectionOptions = self.__settings.get(section, {})
        return sectionOptions.get(option, defaultValue)

    def parse(self, filename):
        '''Parse a configuration file.

        * filename -- The configuration file to parse

        '''
        if exists(filename):
            self.__configParser = ConfigParser()
            self.__configParser.read(filename)

            # Traverse all of the configuration sections found
            for section in self.__configParser.sections():
                configSection = self.__getSectionOptions(section)

                # Determine if the section exists before proceeding
                if configSection is not None:
                    # Create the section entry in our settings dictionary
                    if section not in self.__settings:
                        self.__settings[section] = {}

                    # Traverse all of the configuration options
                    for optionName in self.__configParser.options(section):
                        # Continue only if we found the current option
                        if optionName in configSection:
                            optionObj = configSection.get(optionName)
                            value = self.__configParser.get(section,
                                                            optionName)
                            finalValue = self.__getValue(optionObj, value)

                            self.__settings[section][optionName] = finalValue
                        else:
                            self.warn("Unknown configuration option " \
                                          "[%s/%s]" % (section, optionName))
                else:
                    self.warn("Unknown configuration section [%s]" % section)

    def __getValue(self, optionObj, value):
        '''Get the complete value for the given option.

        * option -- The option
        * value -- The value

        '''
        # Replace all variables, and convert the value to the expected type
        optionValue = self.__replaceVariables(value)
        return optionObj.convert(optionValue)

    def __replaceVariables(self, optionValue):
        '''Replace all variables found within the option value.

        * optionValue -- The value of the option

        '''
        # Replace all of the variables with their corresponding replacements
        for variable, replacement in self.__variables.iteritems():
            variable = "$%s" % variable.upper()
            optionValue = optionValue.replace(variable, replacement)

        return optionValue

    def __getSectionOptions(self, section):
        '''Return a dictionary mapping Option names to the actual Option
        objects for the given section.

        * section -- The section

        '''
        optionsDict = {}
        for option in self.__options.get(section, []):
            if option is not None:
                optionsDict[option.getName()] = option

        return optionsDict
