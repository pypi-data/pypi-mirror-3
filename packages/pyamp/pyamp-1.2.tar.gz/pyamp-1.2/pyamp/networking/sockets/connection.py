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
'''Contains the Connection class. '''
from sys import stderr
from socket import error as socket_error

from pyamp.util import getStackTrace
from pyamp.processes.threading import Thread


__all__ = ['Connection']


class Connection(Thread):
    '''The Connection class handles receiving data from a single
    socket connected to a server.

    This class implements the :class:`pyamp.processes.Thread` and the
    :class:`pyamp.logging.Loggable` interfaces.

    '''

    def __init__(self, server, conn, addr, logger=None):
        '''
        * server -- The server object
        * conn -- The socket connection
        * addr -- The address for this connection
        * logger -- The LogData or Logger object for this class

        '''
        Thread.__init__(self, logger=logger)
        self.__server = server
        self.__connection = conn
        self.__addr = addr

    def onCycle(self, _i):
        '''Called for each cycle of the :class:`pyamp.processes.Thread`.

        * i -- The current cycle number

        '''
        try:
            data = self.__connection.recv(1)

            if len(data) == 0:
                self.shutdown()
            else:
                self.__server.onReceive(self.__addr, data)
        except socket_error, e:
            self.onException(e, getStackTrace())

            # Shutdown if an exception is encountered
            self.shutdown()

    def onShutdown(self):
        '''Called in the event that the :class:`pyamp.processes.Thread` is
        shutdown.

        '''
        self.__server.closeConnection(self.__addr)

    def onException(self, _e, traceback):
        '''Called in the event of an exception.

        * e -- The exception
        * traceback -- The traceback

        '''
        print >> stderr, traceback
