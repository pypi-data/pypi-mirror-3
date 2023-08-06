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
'''The thread module contains the Thread class which provides the ability to
create a threaded class. The Thread class manages starting the thread, and
shutting it down appropriately. The subclasses Thread will can be notified when
the thread starts, is shut down, or at each cycle so it can perform some
process.

'''
import threading
from sys import stderr
from time import sleep

from pyamp.logging import Loggable
from pyamp.util import getStackTrace


__all__ = ["Cycle", "Thread"]


class Thread(threading.Thread, Loggable):
    '''The Thread class provides a base class for creating threaded classes. It
    is essentially a wrapper for the :class:`threading.Thread` class to make
    threaded classes easier to manage.

    It provides the following functions that can be overridden by subclasses:

    * onStart(self) -- This function is called when the Thread is started.

    * onException(self, e, trace) -- This function is called in the event that
                                   an exception is encountered while the
                                   Thread is cycling.

    * onCycle(self, increment) -- This function is called once each time the
                                Thread cycles.

    * onShutdown(self) -- This function is called in the event that the Thread
                          is shutdown.

    Once the Thread has started it continues to run until the :func:`shutdown`
    function is called, or until the condition function returns False.

    Subclasses can set the Period property which sets the number of seconds
    that the Thread will sleep at the end of each cycle. The default value is
    one millisecond.

    This class implements the :class:`pyamp.logging.Loggable` interface.

    '''
    # This property sets the number of seconds to sleep at the end of
    # each cycle
    Period = 0.01

    def __init__(self, conditionFn=lambda: True, logger=None):
        '''
        * conditionFn -- A function that determines when the Thread should exit
        * logger -- The logger for this class

        '''
        threading.Thread.__init__(self)
        Loggable.__init__(self, self.__class__.__name__, logger)

        self.__conditionFn = conditionFn
        self.__shouldRun = False

    def run(self):
        '''Run the Thread until it is shut down or its condition function
        returns False.

        '''
        self.__shouldRun = True

        self.onStart()

        i = 1
        # Continue until the thread is shut down, or the condition
        # function returns False
        while self.__shouldRun and self.__conditionFn():
            try:
                self.onCycle(i)
            except Exception, e:
                self.onException(e, getStackTrace())

            i += 1
            sleep(self.Period)

        self.onStop()

    def shutdown(self):
        '''Shutdown the Thread.'''
        self.onShutdown()
        self.__shouldRun = False

    def isRunning(self):
        '''Determine if the Thread is still running.'''
        return self.__shouldRun

    ##### Functions to be overridden by concrete Threads #####

    def onException(self, e, trace):
        '''The Thread encountered an exception.

        .. note:: This function should be overridden by concrete Threads.

        * e -- The exception
        * trace -- The traceback for the exception

        '''
        print >> stderr, self, e, trace

    def onStart(self):
        '''This method is called when the Thread is started and should
        be overridden by subclasses.

        .. note:: This function should be overridden by concrete Threads.

        '''
        pass

    def onCycle(self, increment):
        '''This method is called when at each cycle of the Thread and should
        be overridden by subclasses.

        .. note:: This function should be overridden by concrete Threads.

        * increment -- The current increment number

        '''
        pass

    def onShutdown(self):
        '''This method is called when the Thread is shut down and should
        be overridden by subclasses.

        .. note:: This function should be overridden by concrete Threads.

        '''
        pass

    def onStop(self):
        '''This method is called when the Thread is stopped.

        .. note:: This function should be overridden by concrete Threads.

        '''
        pass


class Cycle(Loggable):
    '''The Cycle class provides a class which will continue cycling until
    a condition is no longer True.

    '''

    def __init__(self, conditionFn, logger=None):
        '''
        * conditionFn -- The condition function
        * logger -- The logger object

        '''
        Loggable.__init__(self, self.__class__.__name__, logger)

        self.__conditionFn = conditionFn
        self.__shouldRun = False

    def start(self):
        '''Start cycling until the condition function returns False.'''
        self.__shouldRun = True
        while self.__conditionFn() and self.__shouldRun:
            try:
                sleep(0.1)
            except (KeyboardInterrupt, SystemExit):
                return False

        return True

    def shutdown(self):
        '''Stop cycling.'''
        self.__shouldRun = False
