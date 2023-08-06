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
'''The loggable module contains the Loggable class which provides the ability
to create a class which is loggable. Any class that is Loggable will have the
following logging functions exposed:

    * debug(message, debugLevel, args, kwargs)
    * info(message, debugLevel, args, kwargs)
    * warn(message, debugLevel, args, kwargs)
    * warning(message, debugLevel, args, kwargs)
    * error(message, debugLevel, args, kwargs)
    * fatal(message, debugLevel, args, kwargs)
    * critical(message, debugLevel, args, kwargs)
    * log(logLevel, message, debugLevel, args, kwargs)

'''
from pyamp.logging import Colors, Logger, LogData


__all__ = ["Loggable"]


class Loggable:
    '''The Loggable class provides the ability to expose the logging methods
    (i.e., debug, info, warn, warning, error, fatal, critical, and error) on
    a specific class. This provides the ability to easily log messages
    throughout a class without needed to specifically create a :class:`Logger`
    object.

    The Loggable class can be created from either a :class:`Logger` object, or
    a :class:`LogData` object.

    '''

    def __init__(self, name=None, logger=None, color=Colors.Foreground.White):
        '''
        * name -- The name of the Logger
        * logger -- The LogData, or Logger object to use
        * color -- The color of the Logger

        '''
        # If a LogData or Logger object is not given, then use a default
        # LogData object
        if logger is None:
            logger = LogData()

        # Determine if a LogData object or Logger object was given
        # and store the logger appropriately
        if isinstance(logger, LogData):
            self._logger = logger.get(name, color)
        elif isinstance(logger, Logger):
            self._logger = logger
        else:
            message = "Loggable logger must be LogData or Logger, not [%s]" \
                % logger
            raise Exception(message)

    def debug(self, message, level=0, *args, **kwargs):
        '''Log a debug message.

        * message -- The message to log
        * level -- The debug level
        * args -- The arguments
        * kwargs -- The keyword arguments

        '''
        if self.__hasLogger():
            self._logger.debug(message, level, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        '''Log an info message.

        * message -- The message to log
        * args -- The arguments
        * kwargs -- The keyword arguments

        '''
        if self.__hasLogger():
            self._logger.info(message, *args, **kwargs)

    def warn(self, message, *args, **kwargs):
        '''Log a warning message.

        * message -- The message to log
        * args -- The arguments
        * kwargs -- The keyword arguments

        '''
        if self.__hasLogger():
            self._logger.warn(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        '''Log a warning message.

        * message -- The message to log
        * args -- The arguments
        * kwargs -- The keyword arguments

        '''
        if self.__hasLogger():
            self._logger.warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        '''Log an error message.

        * message -- The message to log
        * args -- The arguments
        * kwargs -- The keyword arguments

        '''
        if self.__hasLogger():
            self._logger.error(message, *args, **kwargs)

    def fatal(self, message, *args, **kwargs):
        '''Log a fatal message.

        * message -- The message to log
        * args -- The arguments
        * kwargs -- The keyword arguments

        '''
        if self.__hasLogger():
            self._logger.fatal(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        '''Log a critical message.

        * message -- The message to log
        * args -- The arguments
        * kwargs -- The keyword arguments

        '''
        if self.__hasLogger():
            self._logger.debug(message, *args, **kwargs)

    def log(self, logLevel, message, *args, **kwargs):
        '''Log a message at the given log level.

        * logLevel -- The level at which to log
        * message -- The message to log
        * args -- The arguments
        * kwargs -- The keyword arguments

        '''
        if self.__hasLogger():
            self._logger.log(logLevel, message, *args, **kwargs)

    def __hasLogger(self):
        '''Determine if the Logger is valid.'''
        return hasattr(self, "_logger") and self._logger is not None
