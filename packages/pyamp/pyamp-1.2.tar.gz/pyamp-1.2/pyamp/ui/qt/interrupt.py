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
'''The interrupt module contains the InterruptThread class which provides
a Thread which will periodically notify a QWidget.

'''
from time import sleep
from PyQt4 import Qt, QtCore

from pyamp.exceptions import UndefinedFunctionError


class InterruptThread(Qt.QThread):
    '''The InterruptThread class implements a :class:`PyQt4.Qt.QThread` to call
    the **interrupt** function of a given object at a specifiable rate.

    The InterruptThread class can define the :attr:`period` property to
    determine the number of seconds the :class:`PyQt4.Qt.QThread` will sleep
    during each iteration. The default :attr:`period` is 0.1 seconds.

    This class throws an :class:`amp.exceptions.UndefinedFunctionError` in the
    event that the **interrupt** function is not defined by the :attr:`parent`
    object.

    .. note:: The **interrupt** function takes one parameter which is the
              current interation number that the interrupt thread is on. The
              iteration number increases once per cycle.

    Example::

        class Example():
            def __init__(self):
                self.__interrupt = InterruptThread(self, period=0.5)
                self.__interrupt.start()

            def interrupt(self, i):
                print i

    '''

    period = 0.1
    '''Definine the number of seconds the :class:`PyQt4.Qt.QThread` will sleep
    between each cycle, prior to interrupting the :attr:`parent` object.

    '''

    def __init__(self, parent, period=None):
        '''
        * parent -- The parent of this thread.
        * period -- The number of seconds to sleep between each interrupt

        .. note:: The :attr:`parent` object must have a function named
                  **interrupt** defined.

        '''
        Qt.QThread.__init__(self)

        # Ensure that the parent has an interrupt attribute and that
        # the attribute is a function. Throw an error if the function
        # does not exist
        interruptFn = getattr(parent, "interrupt", None)
        if interruptFn is None or not hasattr(interruptFn, "__call__"):
            raise UndefinedFunctionError(parent, "interrupt")

        self.__parent = parent
        self.__interruptSignal = QtCore.SIGNAL("interrupt")

        # Use the given period if one is given. This value overrides the
        # class defined property if it is specified
        if period is not None:
            self.period = period

        # Connect the interrupt signal to the parent's interrupt function
        self.connect(self, self.__interruptSignal, parent.interrupt)

    def run(self):
        '''Run the interrupt thread.'''
        # Keep track of the number of iterations
        iterations = 0
        while True:
            sleep(self.period)

            # Emit the interrupt signal to notify the parent object
            self.emit(self.__interruptSignal, iterations)
            iterations += 1


class Interruptable:
    '''The Interruptable class provides an interface for interrupting
    a class at a specific interval.

    This class created an :class:`InterruptThread` object which notifies
    the :func:`interrupt` function at the specified :attr:`period`.

    Example::

        class Example(Interruptable):
            def __init__(self):
                Interruptable.__init__(self, period=1)

            # This function is called once per second, and i is the current
            # iteration number.
            def interrupt(self, i):
                print i

    '''

    def __init__(self, period=0.1):
        '''
        * period -- The number of seconds to sleep during each cycle

        '''
        self.__interruptThread = InterruptThread(self, period)
        self.__interruptThread.start()

    def interrupt(self, _i):
        '''Override the interrupt function. This function is called once
        per cycle of the :class:`InterruptThread`.

        .. note:: This function should be overridden by subclasses.

        '''
        pass
