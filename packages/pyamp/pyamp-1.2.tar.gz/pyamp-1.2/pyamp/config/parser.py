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
'''The parser module contains the OptionsParser class which provides the
ability to parse a configuration file and command line given a set of
available options.

.'''
from os.path import exists
from optparse import OptionParser

from pyamp.patterns import Borg
from pyamp.config.configFile import ConfigFile
from pyamp.logging import Colors, Loggable
from pyamp.exceptions import InvalidConfigurationPropertyValueError


__all__ = ["OptionsParser"]


class OptionsParser(Borg, Loggable):
    '''The OptionsParser class is responsible for parsing command line and
    configuration file options and providing the ability to get the value of a
    given option.

    This class implements the :class:`pyamp.patterns.Borg` design pattern and
    also implements the :class:`pyamp.logging.Loggable` interface.

    '''

    Variables = {}
    '''This property contains a dictionary mapping variable names
    to their respective values. These variables can be used
    within the configuration file and will be replaced by the
    assigned values.

    Variables can be used in the configuration file by appending a dollar sign
    before the name of the variable. The variable will then replaced with its
    value prior to parsing the file.

    Example::

        # $HOME will be replaced with the user's home directory before parsing
        [Section]
        Var = $HOME

    '''

    Options = {}
    '''This property contains a dictionary mapping section names to the list of
    options contained within that section. Options must be a subclass of
    the :class:`Option` class. These are the sections and options that will
    be loaded from the configuration file and the command line arguments.

    .. note:: Any :class:`.ClOption` objects that are given will be
       configurable via the configuration file and from the command line.

    '''

    ClOptions = []
    '''This property contains the list of options that are only configurable
    via the command line.

    '''

    def init(self, logger=None):
        '''Override the :class:`pyamp.patterns.Borg` init function.

        * logger -- The :class:`pyamp.logging.Logger` or
                    :class:`pyamp.logging.LogData` object

        '''
        self.options = {}
        self.clOptions = {}
        self.setLogger(logger)

        # Create the command line and configuration file parsers
        self.__createCommandLineParser()
        self.__createConfigParser()

    def setLogger(self, logger, color=Colors.Foreground.White):
        '''Set the logger for the OptionsParser.

        * logger -- The :class:`pyamp.logging.Logger` or
                    :class:`pyamp.logging.LogData` object

        '''
        Loggable.__init__(self, self.__class__.__name__, logger, color)

    def parse(self, argv, filename):
        '''Parse the command line options, and the configuration file.

        * argv -- The command line options
        * filename -- The path to the configuration file

        '''
        # First parse the configuration file
        self.__parseFile(filename)

        # Now parse the command line options, which override any
        # overlapping configuration properties
        self.__parseCommandLine(argv)

        # Print out all of the settings that are configured for
        # debugging purposes
        for _, options in self.options.iteritems():
            for optionName, value in options.iteritems():
                self.debug("[%s] = %s" % (optionName, str(value)), level=5)

        # Verify that all of the configuration properties have valid values
        for section, options in self.options.iteritems():
            for optionName, value in options.iteritems():
                self.__verifyValue(section, optionName, value)

        # Verify that all of the comman line arguments have valid values
        for optionName, value in self.clOptions.iteritems():
            self.__verifyClValue(optionName, value)

    @classmethod
    def get(cls, section, optionName, defaultValue=None):
        '''Get the value of an option from the given section.

        * section -- The name of the section
        * optionName -- The name of the option
        * defaultValue -- The default value if the option does not exist

        '''
        sectionOptions = cls().options.get(section, {})
        return sectionOptions.get(optionName, defaultValue)

    @classmethod
    def set(cls, section, optionName, value):
        '''Set the value of an option from the given section.

        * section -- The name of the section
        * optionName -- The name of the option
        * value -- The value

        '''
        sectionOptions = cls().options.get(section, {})
        sectionOptions[optionName] = value

    @classmethod
    def getCl(cls, optionName, defaultValue=None):
        '''Get the value of a command line option.

        * optionName -- The name of the command line option
        * defaultValue -- The default value if the option does not exist

        '''
        return cls().clOptions.get(optionName, defaultValue)

    @classmethod
    def setCl(cls, optionName, value):
        '''Set the value of a command line option.

        * optionName -- The name of the command line option
        * value -- The value

        '''
        cls().clOptions[optionName] = defaultValue

    def __parseCommandLine(self, argv):
        '''Parse the command line options.

        * argv -- The command line options

        '''
        # Parse the given command line options
        (options, _) = self._commandLineParser.parse_args(argv)

        # Join the command line options with our current options and
        # allow the command line options to override any currently
        # set option values
        for section, optionDict in self._commandLineOptions.iteritems():
            for optionName, _ in optionDict.iteritems():
                value = getattr(options, optionName)

                if value is not None:
                    if section not in self.options:
                        self.options[section] = {}
                    self.options[section][optionName] = value

        # Store all of the command line option values
        for clOption in self.ClOptions:
            optionName = clOption.getName()
            if hasattr(options, optionName):
                value = getattr(options, optionName, None)
                self.clOptions[optionName] = value

    def __parseFile(self, filename):
        '''Parse the configuration file.

        * filename -- The configuration file

        '''
        if exists(filename):
            self._configParser.parse(filename)
            settings = self._configParser.getSettings()
            self.options = dict(self.options.items() + settings.items())

    def __createCommandLineParser(self):
        '''Create the command line parser object.'''
        # Keep a list of all of the command line option variable names
        self._commandLineOptions = {}

        # Parser for the command line options
        parser = OptionParser()

        # Traverse all of the configured sections
        for section, options in self.Options.iteritems():
            # Travese only the options in this section that are configurable
            # via the command line
            for option in [opt for opt in options if opt.isCommandLine()]:
                optionName = option.getName()
                defaultValue = option.getDefaultValue()

                # @todo: create other Option objects that can use more values
                #        from this class...help, have no value, etc
                parser.add_option("--%s" % optionName, dest=optionName,
                                  default=defaultValue)

                if section not in self._commandLineOptions:
                    self._commandLineOptions[section] = {}
                self._commandLineOptions[section][optionName] = defaultValue

        # Add all of the command line only options
        for clOption in self.ClOptions:
            clOption.addOption(parser)

        # Store the command line parser locally
        self._commandLineParser = parser

    def __createConfigParser(self):
        '''Create the configuration file parser object.'''
        # Create the dictionary mapping sections to their respective Options
        self._configOptions = self.Options

        # Define all of the configuration variables that can be used
        self._configVariables = self.Variables

        # Create the configuration parser using the configured variables and
        # configuration options
        self._configParser = ConfigFile(logger=self._logger,
                                        options=self._configOptions,
                                        variables=self._configVariables)

    def __getOption(self, section, optionName):
        '''Find the option object with the given section and name.

        * section -- The section the option is in
        * optionName -- The name of the option

        '''
        sectionOptions = self.Options.get(section, [])

        foundOption = None
        for option in sectionOptions:
            if option.getName() == optionName:
                foundOption = option
                break

        return foundOption

    def __getClOption(self, optionName):
        '''Find the command line option object with the given name.

        * optionName -- The name of the option

        '''
        foundOption = None
        for option in self.ClOptions:
            if option.getName() == optionName:
                foundOption = option
                break

        return foundOption

    def __verifyValue(self, section, optionName, value):
        '''Ensure that the given value for the given section option is a
        valid value for this option. Throw an exception otherwise.

        * section -- The section name
        * optionName -- The option name
        * value -- The value to verify

        '''
        optionObj = self.__getOption(section, optionName)

        if optionObj is not None:
            # Determine if this value is an accepted value for this option
            if not optionObj.isAcceptedValue(value):
                values = optionObj.getAcceptedValues()
                raise InvalidConfigurationPropertyValueError(optionName,
                                                             values,
                                                             section=section)

    def __verifyClValue(self, optionName, value):
        '''Ensure that the given value for the given command line argument is a
        valid value for this option.

        * optionName -- The option name
        * value -- The value to verify

        '''
        optionObj = self.__getClOption(optionName)

        if optionObj is not None:
            # Determine if this value is an accepted value for this option
            if not optionObj.isAcceptedValue(value):
                values = optionObj.getAcceptedValues()
                raise InvalidConfigurationPropertyValueError(optionName,
                                                             values)
