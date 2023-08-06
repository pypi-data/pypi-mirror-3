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
'''The console module provides the ability to retrieve input from the user
through the console.

'''
from fcntl import ioctl
from select import select
from struct import unpack
from tty import setcbreak
from sys import stdin, stdout, stderr
from termios import tcgetattr, tcsetattr, TCSADRAIN, TIOCGWINSZ

from pyamp.util import getStackTrace
from pyamp.processes.threading import Thread


__all__ = ["ConsoleInput"]


class ConsoleInput(Thread):
    '''The ConsoleInput class provides the ability to receive input from
    a user through the console. This class runs as a separate thread which
    monitors the console for input and notifies a callback method in the event
    that keyboard input is received.

    The callback method must take one argument which is the character that was
    read as input. This class also provides the ability to register a callback
    function to be called in the event that an exception occurs during the
    processing of the thread.

    This class implements the :class:`pyamp.processes.Thread`, and the
    :class:`amp.logging.Loggable` interfaces.

    '''

    def __init__(self, callback, conditionFn=lambda: True,
                 exceptionFn=None, logger=None):
        '''
        * callback -- The function called when input is received
        * conditionFn -- The function used to determine whether we should
                         continue waiting for input
        * exceptionFn -- The functionc called when an exception is encountered
        * logger -- The logger object

        '''
        Thread.__init__(self, conditionFn, logger)

        self.__callback = callback
        self.__exceptionFn = exceptionFn
        self.__shouldRun = False

    def onStart(self):
        '''Called when the ConsoleInput thread is started.'''
        self.__oldSettings = tcgetattr(stdin)
        setcbreak(stdin.fileno())

    def onCycle(self, _increment):
        '''Called during each cycle of the Thread.

        * increment -- The current increment number

        '''
        try:
            if ConsoleInput.__isData():
                c = stdin.read(1)
                try:
                    self.__callback(c)
                except Exception, e:
                    self.onException(e, getStackTrace())
        finally:
            self.shutdown()

    def onShutdown(self):
        '''Called when the ConsoleInput Thread is shutdown.'''
        tcsetattr(stdin, TCSADRAIN, self.__oldSettings)

    def onException(self, e, traceback):
        '''This function is called in the event that an exception
        occurs during the processing of the thread.

        * e -- The exception
        * traceback -- The traceback

        '''
        if self.__exceptionFn is not None:
            self.__exceptionFn(e, traceback)
        else:
            print >> stderr, traceback

    @classmethod
    def clearScreen(cls):
        '''Clear the console screen.'''
        stdout.write('\033[2J')
        stdout.write('\033[H')
        stdout.flush()

    @classmethod
    def getSize(cls):
        '''Get the size of the current console screen.'''
        rows, cols = unpack('hh', ioctl(stdout, TIOCGWINSZ, '1234'))
        return rows, cols

    @classmethod
    def getRows(cls):
        '''Get the number of rows for this console screen.'''
        rows, _ = ConsoleInput.getSize()
        return rows

    @classmethod
    def getCols(cls):
        '''Get the number of columns for this console screen.'''
        _, cols = ConsoleInput.getSize()
        return cols

    @classmethod
    def __isData(cls):
        '''Determine if there is input available to process.'''
        return select([stdin], [], [], 0) == ([stdin], [], [])


if __name__ == '__main__':
    def printIn(message):
        '''Test function for printing a line.

        * message -- The message to print

        '''
        print message

    console = ConsoleInput(printIn)
    console.start()
