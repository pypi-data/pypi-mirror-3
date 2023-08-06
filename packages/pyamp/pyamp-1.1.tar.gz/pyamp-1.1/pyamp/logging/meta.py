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
'''The meta module contains the LoggerMeta, and FunctionLoggerMeta classes.

These classes provide the ability for create a class which will have the
ability to be logged, or to wrap certain class functions with logging messages
to indicate when the function was entered and exited.

'''
from pyamp.logging.prefix import Prefix
from pyamp.logging.logger import Logger, LogLevel


__all__ = ["LoggerMeta", "FunctionLoggerMeta", "doNotLog"]


class LoggerMeta(type):
    '''The LoggerMeta is a metaclass that provides the ability to create a
    :class:`Logger` for a given class. The class has the ability to set the
    following static class properties.

    * *logLevel* -- Set log level for the logger
    * *logPrefix* -- Set the log prefix for the logger

    Any classes that use LoggerMeta as their metaclass will have a 'logger'
    property created, which will be a :class:`Logger` object with the preset
    logLevel, and logPrefix.

    Example::

        class Example:
            __metaclass__ = LoggerMeta
            logLevel = LogLevel.INFO
            logPrefix = Prefix(text="TestPrefix")

        if __name__ == '__main__':
            example = Example()

            # Prints: [Example]: [TestPrefix]: This is an information message
            example.logger.info("This is an information message")

    '''
    # Define the static properties name as used by the main class
    LogLevel = "logLevel"
    LogPrefix = "logPrefix"

    # The name of the attribute which will store the created logger
    _Logger = "logger"

    def __new__(mcs, className, parents, attributes):
        '''
        * className -- The name of the class
        * parents -- The class parents
        * attributes -- The class attributes

        '''
        # Create the logger for this class, and store it in
        # the attributes for the class
        logLevel = attributes.get(LoggerMeta.LogLevel, LogLevel.INFO)
        logPrefix = attributes.get(LoggerMeta.LogPrefix, Prefix())

        logger = Logger(name=className, prefix=logPrefix, logLevel=logLevel)
        attributes.setdefault(LoggerMeta._Logger, logger)

        return type.__new__(mcs, className, parents, attributes)


class FunctionLoggerMeta(LoggerMeta):
    '''The FunctionLoggerMeta class is a metaclass that provides the ability
    to log specific functions of a class. This metaclass uses the
    :class:`Logger` object (as created by the :class:`LoggerMeta` class) to
    print debug statements as functions of a class are entered and exited.

    The following types of functions will NOT be logged:
        * Builtin functions (i.e., the function name ends with '__')
        * Functions that are decorated with the :func:`doNotLog` function

    All other functions will log a DEBUG message when the function is entered
    and when the function is exited. This provides an easy way to toggle the
    ability to view the scope of functions during the runtime of a system.

    Example::

        class Example:
            __metaclass__ = FunctionLoggerMeta

            def test(self):
                print "This is a test"


        if __name__ == '__main__':
            example = Example()

            # Prints:
            #    [DEBUG]: Entering test
            #    This is a test
            #    [DEBUG]: Exiting test
            example.test()

    '''
    # The attribute used to identify functions that should not be logged
    DoNotLog = "doNotLog"

    def __new__(mcs, className, parents, attributes):
        '''
        * className -- The name of the class
        * parents -- The class parents
        * attributes -- The class attributes

        '''
        LoggerMeta.__new__(mcs, className, parents, attributes)

        # Get the logger object created by the LoggerMeta class
        logger = attributes.get(LoggerMeta._Logger)

        # Traverse through all of the attributes
        for name, func in attributes.iteritems():
            # If we should log this function, then wrap it with
            # debug statements which will be printed when the
            # function is entered and exited
            if mcs.__shouldLog(name, func):
                def loggingWrapper(funcName, function, funcLogger):
                    '''Function to wrap the decorating function so
                    that we can pass it other arguments.

                    * funcName -- The name of the function
                    * function -- The actual function to call
                    * funcLogger -- The logger to use for this function

                    '''
                    def tempFunction(*attrs, **kwargs):
                        '''Function to decorate the desired function
                        with debug statements before and after the
                        function is called.

                        * attrs -- The incoming attributes
                        * kwargs -- The incoming keyword arguments

                        '''
                        funcLogger.debug("Entering %s" % funcName)
                        function(*attrs, **kwargs)
                        funcLogger.debug("Exiting %s" % funcName)
                    return tempFunction

                # Overwrite the function with the logging wrapper
                attributes[name] = loggingWrapper(name, func, logger)

        return type.__new__(mcs, className, parents, attributes)

    @classmethod
    def __shouldLog(mcs, funcName, func):
        '''Determine if the given function should be logged.

        * funcName -- The name of the function
        * func -- A pointer to the actual function

        '''
        return all([mcs.__isFunction(func),
                    mcs.__isNotBuiltin(funcName),
                    mcs.__canLog(func)])

    @classmethod
    def __isFunction(mcs, obj):
        '''Determine if the given object is a function.

        * obj -- The object

        '''
        return hasattr(obj, '__call__')

    @classmethod
    def __isNotBuiltin(mcs, objName):
        '''Determine if the given object is a builtin attribute or not.

        * objName -- The name of the object

        '''
        return not objName.endswith("__")

    @classmethod
    def __canLog(mcs, obj):
        '''Determine if the given object can be logged by checking if
        it has the FunctionLoggerMeta.DoNotLog attribute set.

        * obj -- The object'''
        return not getattr(obj, FunctionLoggerMeta.DoNotLog, False)


def doNotLog(function):
    '''The doNotLog function is a decorator function which flags a function
    so that it does not get logged by the :class:`FunctionLoggerMeta` class.

    Any functions decorated with 'doNotLog' will be ignored by the
    :class:`FunctionLoggerMeta` class.

    Example::

        class Example:
            __metaclass__ = FunctionLoggerMeta

            # This function will be logged
            def logged(self):
                pass

            # This function will not be logged
            @doNotLog
            def notLogged(self):
                pass

    '''
    setattr(function, FunctionLoggerMeta.DoNotLog, True)
    return function
