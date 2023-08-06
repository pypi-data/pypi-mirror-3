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
'''The prefix module contains the Prefix, FnPrefix, and TimePrefix classes.

These classes provide the ability to create specific logging prefixes which
will be printed at the start of a logged message. These prefixes can be things
such as: the output of a specific function, the current time, or custom
prefixes.

'''
from datetime import datetime

from pyamp.logging.colors import Colors


__all__ = ["Prefix", "FnPrefix", "TimePrefix"]


class Prefix:
    '''The Prefix class provides the ability to add chain of prefixes to a
    message. A Prefix contains text which is printed in square brackets
    before the given message. The following shows an example of the a
    Prefix for the string "DEBUG".

    Example::

        prefix = Prefix(text="DEBUG")

        # Prints: [DEBUG]: This is the message
        prefix.apply("This is the message")

    A Prefix can be colored, and it can contain other prefixes which are
    appended to the message before adding the current Prefix.

    An example of multiple prefixes::

        debugPrefix = Prefix(text="DEBUG")
        examplePrefix = Prefix(text="example", prefix=debugPrefix)
        datePrefix = Prefix(text="03/11/2012", prefix=examplePrefix)

        # Prints: [DEBUG]: [example]: [03/11/2012]: This is the message
        datePrefix.apply("This is the message")

    '''
    # Define the default color for prefixes
    DefaultColor = Colors.Foreground.White

    def __init__(self, text=None, color=DefaultColor, prefix=None):
        '''
        * text -- The text to display in the Prefix
        * color -- The color in which the Prefix will be displayed
        * prefix -- The next Prefix in the chain

        '''
        self.__text = text
        self.__color = color
        self.__prefix = prefix

    def apply(self, message, useColors=False):
        '''Apply the chain of Prefixes to the given message.

        * message -- The message to apply the Prefix chain to
        * useColors -- True to use colors, False otherwise

        '''
        # First apply the sub prefix, is there is one
        if self.__prefix is not None:
            message = self.__prefix.apply(message, useColors)

        return self._addPrefix(self.__text, message, useColors)

    def _addPrefix(self, text, message, useColors=False):
        '''Add the given prefix text to the message.

        * text -- The prefix text to add
        * message -- The message to which the prefix will be added
        * useColors -- True to use colors, false otherwise

        '''
        if text is None:
            text = ''
        else:
            text = "[%s]: " % (self.__colorize(text) if useColors else text)

        return "%s%s" % (text, message)

    def __colorize(self, message):
        '''Colorize the given message using our current color.

        * message -- The message to colorize

        '''
        return "%s%s%s" % (self.__getColor(self.__color),
                           message, self.__getColor(Prefix.DefaultColor))

    @classmethod
    def __getColor(cls, color):
        '''Get the color string for the given color.

        * color -- The color

        '''
        return "%s%d%s" % (Colors.Tag, color, Colors.Symbol)


class FnPrefix(Prefix):
    '''The FnPrefix class provides to ability to create a :class:`Prefix` whose
    text results from calling a specified function when the :class:`Prefix` is
    applied to a message.

    Example::

        prefix = FnPrefix(function=lambda: "Hey!")

        # Prints: [Hey!]: This is the message
        prefix.apply("This is the message")

    This class can be used to dynamically create the text used for a prefix by
    calling a function which returns the desired value for the prefix.

    '''
    def __init__(self, function, color=Prefix.DefaultColor, prefix=None):
        '''
        * function -- The function which returns the Prefix text
        * color -- The color in which the Prefix will be displayed
        * prefix -- The next Prefix in the chain

        '''
        Prefix.__init__(self, None, color=color, prefix=prefix)
        self.__function = function

    def _addPrefix(self, text, message, useColors=False):
        '''Override the _addPrefix base class method.

        * text -- The prefix text to add
        * message -- The message to which the prefix will be added
        * useColors -- True to use colors, false otherwise

        '''
        return Prefix._addPrefix(self, self.__function(), message,
                                 useColors)


class TimePrefix(FnPrefix):
    '''The TimePrefix provides the ability to add a :class:`Prefix` which
    displays the date and or time when the :class:`Prefix` is applied to the
    message in a specified format.

    Example::

        prefix = TimePrefix(format="%Y-%m-%d")

        # Prints: [2012-03-22]: This is the message
        prefix.apply("This is the message")

    This class is useful for dynamically timestamping logged messages so they
    can easily be tracked in the system output.

    '''
    def __init__(self, format=None, color=Prefix.DefaultColor, prefix=None):
        '''
        * format -- The format in which the time will be displayed. See the
                    man page for 'date'
        * color -- The color in which the Prefix will be displayed
        * prefix -- The next prefix in the chain

        '''
        self.__format = format
        FnPrefix.__init__(self, self.__getTime, color=color, prefix=prefix)

    def __getTime(self):
        '''Return the current time in the specified time format.'''
        now = datetime.now()

        if self.__format is not None:
            return now.strftime(self.__format)
        else:
            return str(now)
