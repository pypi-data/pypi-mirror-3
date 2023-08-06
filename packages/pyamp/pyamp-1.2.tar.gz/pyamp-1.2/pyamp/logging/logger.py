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
'''The logger module contains the LogLevel, Logger, FileLogger, and LogData
classes.

These classes are focused on logging system output to various types of
output streams (e.g., console, or a file), as well as logging messages at
various different log levels.

'''
import logging

from pyamp.patterns import Borg
from pyamp.logging.colors import Colors
from pyamp.logging.prefix import Prefix


__all__ = ["LogLevel", "Logger", "FileLogger", "SingleLogger", "LogData"]


class LogLevel:
    '''The LogLevel class contains definitions of all of the various log
    levels that can be used for logging messages. These levels are designed
    to make it easier to parse the output of a system to find different types
    of issues that were encountered at runtime.

    * **DEBUG** -- The debugging log level. Has a value of 10.
    * **INFO** -- The information log level. Has a value of 20.
    * **WARN** -- The warning log level. Has a value of 30.
    * **WARNING** -- The warning log level. Has a value of 30.
    * **ERROR** -- The error log level. Has a value of 40.
    * **CRITICAL** -- The critical log level. Has a value of 50.
    * **FATAL** -- The fatal log level. Has a value of 50.

    '''
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = logging.WARN
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL


class Logger(logging.Logger):
    '''The Logger class provides the ability to log various types
    of messages to a specific stream, and formats the messages using given
    :class:`Prefix` objects.

    The Logger class will log each :class:`LogLevel` with a colored
    prefix indicating the name of the log level. Logged messages are only
    displayed in the event that the :class:`LogLevel` at which they are
    logged is greater than or equal to the current :class:`LogLevel` of the
    Logger which is logging the message. Each :class:`LogLevel.DEBUG`
    message can also have an optional debug level specified, which will allow
    that message to be displayed so long as the specified debug level is less
    than or equal to the configured debug level of the Logger object.

    Each Logger object can be named, and colored, which means that
    any message logged using that object will be displayed with a prefix
    indicating the name (and displayed in the specified color) of the object
    which logged the message.

    Logger objects can be given a chain of :class:`Prefix` objects.
    Any message logged using that Logger object will then have a
    series of prefixes added to the front of the message.

    Logger objects can also have a handler specified, which specifies
    the type of stream which will be handled by this Logger. For
    example, to output to the console a value of :class:`logging.StreamHandler`
    could be specified, whereas a value of :class:`logging.FileHandler` could
    be specified to log to a specific file.

    Example::

        # Create a Logger with the name 'Example1'
        logger = Logger("Example1")
        logger.info("Information message")

        # Create a Logger with the name 'Example2', a foreground
        # color of Blue, and logs DEBUG messages that have a debug
        # level less than or equal to 10.
        logger = Logger("Example2", color=Colors.Foreground.Blue,
                        logLevel=LogLevel.DEBUG, debugLevel=10)
        logger.debug("This message is displayed", 2)
        logger.debug("This message is not displayed", 11)

        # Create a Logger with the name 'Example3' that only displays
        # ERROR messages
        logger = Logger("Example3", logLevel=LogLevel.ERROR)
        logger.warn("This would not be displayed")

    '''
    # Map log levels to their corresponding string values, and colors
    levelMap = {
        LogLevel.DEBUG: ("DEBUG", Colors.Foreground.Green),
        LogLevel.INFO: ("INFO", Colors.Foreground.White),
        LogLevel.WARN: ("WARN", Colors.Foreground.Orange),
        LogLevel.WARNING: ("WARN", Colors.Foreground.Orange),
        LogLevel.ERROR: ("ERROR", Colors.Foreground.Red),
        LogLevel.CRITICAL: ("CRITICAL", Colors.Foreground.Red),
        LogLevel.FATAL: ("FATAL", Colors.Foreground.Red),
        }

    def __init__(self, name=None, color=Colors.Foreground.White,
                 prefix=Prefix(), logLevel=LogLevel.WARN,
                 debugLevel=0, handler=logging.StreamHandler()):
        '''
        * name -- The name of the Logger
        * color -- The color to use for this Logger
        * prefix -- The :class:`Prefix` chain to use for this Logger
        * logLevel -- The log level to use for this Logger
        * debugLevel -- The debug level
        * handler -- The handler to use for this Logger

        '''
        logging.Logger.__init__(self, name)
        self.__color = color
        self.__debugLevel = debugLevel
        self.setLevel(logLevel)
        self.addHandler(handler)
        self.setPrefix(prefix)

    def setName(self, name):
        '''Set the name for this logger.

        * name -- The name

        '''
        self.name = name

    def setPrefix(self, prefix):
        '''Set the prefix for this logger.

        * prefix -- The prefix

        '''
        # Create a default prefix if one was not given
        prefix = Prefix() if prefix is None else prefix

        # Add the logger's name prefix onto the end of any prefix given
        self.__prefix = Prefix(text=self.name, color=self.__color,
                               prefix=prefix)

    def debug(self, message, level=0, *args, **kwargs):
        '''Log a debug message.

        * message -- The message to log
        * level -- The debug level
        * args -- The arguments
        * kwargs -- The keyword arguments

        '''
        # Only issue the debug message if the debug level for this
        # message is lower than or equal to the current debug level
        if self.__debugLevel >= level:
            self.log(LogLevel.DEBUG, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        '''Log an info message.

        * message -- The message to log
        * args -- The arguments
        * kwargs -- The keyword arguments

        '''
        self.log(LogLevel.INFO, message, *args, **kwargs)

    def warn(self, message, *args, **kwargs):
        '''Log a warning message.

        * message -- The message to log
        * args -- The arguments
        * kwargs -- The keyword arguments

        '''
        self.log(LogLevel.WARN, message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        '''Log a warning message.

        * message -- The message to log
        * args -- The arguments
        * kwargs -- The keyword arguments

        '''
        self.log(LogLevel.WARN, message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        '''Log an error message.

        * message -- The message to log
        * args -- The arguments
        * kwargs -- The keyword arguments

        '''
        self.log(LogLevel.ERROR, message, *args, **kwargs)

    def fatal(self, message, *args, **kwargs):
        '''Log a fatal message.

        * message -- The message to log
        * args -- The arguments
        * kwargs -- The keyword arguments

        '''
        self.log(LogLevel.FATAL, message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        '''Log a critical message.

        * message -- The message to log
        * args -- The arguments
        * kwargs -- The keyword arguments

        '''
        self.log(LogLevel.FATAL, message, *args, **kwargs)

    def log(self, logLevel, message, *args, **kwargs):
        '''Log a message at the given log level.

        * logLevel -- The level at which to log
        * message -- The message to log
        * args -- The arguments
        * kwargs -- The keyword arguments

        '''
        # Add a prefix for the given log level onto the logger's prefix
        prefix = Prefix(self.__getLogLevelStr(logLevel),
                        color=self.__getLogLevelColor(logLevel),
                        prefix=self.__prefix)

        newMessage = self.__getMessage(message, **kwargs)

        # Apply the prefix to the message, disabling colors as expected
        useColors = (self.__color is not None)
        message = prefix.apply(newMessage, useColors)

        logging.Logger.log(self, logLevel, message, *args)

    @classmethod
    def __getMessage(cls, message, **kwargs):
        '''Return the message including all of the keyword arguments
        and their corresponding values.

        * message -- The message to log
        * kwargs -- The keyword arguments to include in the message

        '''
        # The spacing applied before the first keyword in the list
        firstSpacing = "\n%s" % (' ' * 9)

        # The spacing between each keyword in the list
        spacing = ", "

        # Create strings for each keyword along with its value
        keywords = map(lambda (k, v): "%s=%s" % (k, str(v)), kwargs.items())

        # Create the string with all of the keywords and values
        keywordStr = ''
        if len(keywords) > 0:
            keywordStr = "%s%s" % (firstSpacing, spacing.join(keywords))

        return "%s%s" % (message, keywordStr)

    def __getLogLevelStr(self, logLevel):
        '''Return the string representation of the given log level.

        * logLevel -- The log level

        '''
        # Find the maximum length of strings
        maxLen = max(map(lambda i: len(i[0]), self.levelMap.values()))
        logStr = self.levelMap.get(logLevel, str(logLevel))[0]

        # Find the spacing to add to the end of the log string
        # to make all of the strings the same length
        spacing = ' ' * max(maxLen - len(logStr), 0)
        return "%s%s" % (logStr, spacing)

    def __getLogLevelColor(self, logLevel):
        '''Return the color for the given log level.

        * logLevel -- The log level

        '''
        color = self.levelMap.get(logLevel, str(logLevel))[1]
        return color


class FileLogger(Logger):
    '''The FileLogger class provides a wrapper class for a
    :class:`Logger` object which outputs its messages to a specified
    file. When creating the FileLogger, it can be specified whether existing
    files should be overwritten, or appended to, when messages are initially
    logged to the file.

    '''

    def __init__(self, filename, append=True, name=None, prefix=Prefix(),
                 logLevel=LogLevel.WARN):
        '''
        * filename -- The file which will be logged to
        * overwrite -- True to append to the log file, False to overwrite
        * name -- The name of the Logger
        * prefix -- The :class:`Prefix` chain to use for this FileLogger
        * logLevel -- The log level to use for this FileLogger

        '''
        # Determine the writing mode for the file
        mode = 'a' if append else 'w'

        # Create the file handler with the given filename, and mode
        handler = logging.FileHandler(filename, mode=mode)
        Logger.__init__(self, name=name, color=None, prefix=prefix,
                        logLevel=logLevel, handler=handler)


class SingleLogger(Borg):
    '''The SingleLogger class implements the :class:`pyamp.patterns.Borg`
    design pattern for creating a single system wide :class:`Logger` object.

    This allows an entire system to access the same :class:`Logger` object so
    that each component can log messages with the same data (e.g., log level,
    color, prefix, etc).

    '''
    _LoggerName = "_logger"

    def __init__(self):
        '''Create the SingleLogger object.'''
        Borg.__init__(self)
        if not hasattr(self, SingleLogger._LoggerName):
            setattr(self, SingleLogger._LoggerName, None)

    @classmethod
    def getInstance(cls):
        '''Get the instance of the :class:`Logger` object.'''
        return getattr(SingleLogger(), SingleLogger._LoggerName, None)

    @classmethod
    def createFileLogger(cls, logFile, append=False, logLevel=LogLevel.WARN):
        '''Create a system-wide :class:`FileLogger` object.

        * logFile -- The log file to use
        * append -- True to append to the file, False to overwrite
        * logLevel -- The log level for the logger

        '''
        fileLogger = FileLogger(logFile, append=append,
                                logLevel=logLevel)

        logger = SingleLogger()
        setattr(logger, SingleLogger._LoggerName, fileLogger)

    @classmethod
    def createLogger(cls, name, logLevel=LogLevel.WARN):
        '''Create a system-wide :class:`Logger` object.

        * name -- The name of Logger
        * logLevel -- The log level for the logger

        '''
        theLogger = Logger(name, logLevel=logLevel)

        logger = SingleLogger()
        setattr(logger, SingleLogger._LoggerName, theLogger)

    @classmethod
    def debug(cls, message):
        '''Log the given debug message.

        * message -- The message to log

        '''
        SingleLogger.log(LogLevel.DEBUG, message)

    @classmethod
    def info(cls, message):
        '''Log the given information message.

        * message -- The message to log

        '''
        SingleLogger.log(LogLevel.INFO, message)

    @classmethod
    def write(cls, message):
        '''Write an information message to the logger.

        * message -- The message to write

        '''
        cls.log(LogLevel.INFO, message)

    @classmethod
    def warn(cls, message):
        '''Log the given warning message.

        * message -- The message to log

        '''
        SingleLogger.log(LogLevel.WARN, message)

    @classmethod
    def warning(cls, message):
        '''Log the given warning message.

        * message -- The message to log

        '''
        SingleLogger.log(LogLevel.WARN, message)

    @classmethod
    def error(cls, message):
        '''Log the given error message.

        * message -- The message to log

        '''
        SingleLogger.log(LogLevel.ERROR, message)

    @classmethod
    def fatal(cls, message):
        '''Log the given fatal message.

        * message -- The message to log

        '''
        SingleLogger.log(LogLevel.FATAL, message)

    @classmethod
    def critical(cls, message):
        '''Log the given critical message.

        * message -- The message to log

        '''
        SingleLogger.log(LogLevel.CRITICAL, message)

    @classmethod
    def log(cls, logLevel, message):
        '''Log the given message at the given log level.

        * logLevel -- The log level
        * message -- The message to log

        '''
        logger = getattr(SingleLogger(), SingleLogger._LoggerName, None)
        if logger is not None:
            logger.log(logLevel, message)


class LogData:
    '''The LogData class provides the ability to store logging data for an
    entire system in an object that can be easily handled.

    The LogData class stores a :class:`LogLevel` and an integer debug level
    for a system, and provides the ability to create a named :class:`Logger`
    from the stored values.

    For example::

        # Any Logger objects created from this LogData object will have a
        # LogLevel of DEBUG, and a debug level of 10.
        logData = LogData(LogLevel.DEBUG, 10)

        # Create a logger named 'ExampleLogger' which will log messages
        # with a red foreground color.
        logger = logData.get("ExampleLogger", Colors.Foreground.Red)

        # This message will be displayed
        logger.debug("Example message", 2)

        # This message will not be displayed
        logger.debug("Example message", 11)


    LogData objects can be easily passed around which allows the
    :class::`LogLevel` and debug level values to be easily propagated
    throughout the system, rather than having individual values for each
    system component.

    '''

    def __init__(self, logLevel=LogLevel.INFO, debugLevel=0,
                 prefix=Prefix()):
        '''
        * logLevel -- The log level
        * debugLevel -- The debug level
        * prefix -- The prefix chain to use for all loggers

        '''
        self.__logLevel = logLevel
        self.__debugLevel = debugLevel
        self.__prefix = prefix

    def get(self, name=None, color=Colors.Foreground.White):
        '''Get a new Logger with the given name.

        * name -- The name to assign the Logger
        * color -- The color to use for the Logger

        '''
        return Logger(name, logLevel=self.__logLevel,
                      debugLevel=self.__debugLevel, color=color,
                      prefix=self.__prefix)
