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
'''The server module contains the Server class which provides the
ability to create a thread which acts as a server and allows data to
be sent and received from various connections.

'''
import socket

from pyamp.util.sockets import setReusable
from pyamp.processes.threading import Thread
from pyamp.util.debugging import getStackTrace


__all__ = ['Server']


class Server(Thread):
    '''The Server class handles creating a server on a specific host and
    port. It also handles multiple connections to the server while being able
    to receive data from any of those connections.

    This class implements the :class:`pyamp.processes.Thread` and
    :class:`pyamp.logging.Loggable` interfaces.

    '''

    def __init__(self, connectionClass, port, host='', logger=None):
        '''
        * connectionClass -- The class used to handle each connection
        * port -- The server port number
        * host -- The server host
        * logger -- The LogData or Logger for this class

        '''
        Thread.__init__(self, logger=logger)

        self.__connections = {}
        self.__addr = (host, port)
        self.__connectionClass = connectionClass

    def onStart(self):
        '''Called when the :class:`pyamp.processes.Thread` is started.'''
        self.__sockFd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sockFd.setblocking(0)
        setReusable(self.__sockFd)

        self.__sockFd.bind(self.__addr)
        self.__sockFd.listen(1)
        self.debug("Server started on %d" % self.__addr[1])

    def onCycle(self, _i):
        '''Called for every cycle of the :class:`pyamp.processes.Thread`.

        * i -- The current cycle number

        '''
        try:
            # Accept an incoming connect
            conn, addr = self.__sockFd.accept()
            self.openConnection(conn, addr)
        except Exception, e:
            self.onException(e, getStackTrace())

    def onReceive(self, addr, data):
        '''Called in the event that data is received.

        * addr -- The address of the connection where the data originated
        * data -- The data that was received

        '''
        self.debug("    [%s]: %s" % (addr, data.strip()), level=2)

    def onShutdown(self):
        '''Called in the event that the :class:`pyamp.processes.Thread` is
        shutdown.

        '''
        # Close all the connections
        for connection in self.__connections.values():
            connection.close()
        self.__connections = {}

        self.__sockFd.close()

    def openConnection(self, conn, addr):
        '''Handle the newly opened connection.

        * conn -- The socket object for the connection
        * addr -- The address for the connection

        '''
        connection = self.__connectionClass(self, conn, addr)
        connection.start()
        self.__connections[addr] = conn
        self.debug("Accepted connection: %s [%d]" % \
                       (self.__formatAddress(addr), len(self)))

    def closeConnection(self, addr):
        '''Close an open connection.

        * addr -- The address for the connection to close

        '''
        connection = self.__connections.get(addr)
        if connection is not None:
            self.debug("Closing connection: %s" % self.__formatAddress(addr))
            connection.close()
            del self.__connections[addr]
            return True
        else:
            return False

    def __len__(self):
        '''Get the number of connections.'''
        return len(self.__connections)

    @classmethod
    def __formatAddress(cls, addr):
        '''Format an address tuple into a string. Where the first element
        in the tuple is the IP address, and the second element in the tuple
        is the port number.

        * addr -- The address to format

        '''
        if addr is not None and len(addr) == 2:
            return "%s:%d" % (addr[0], addr[1])
        else:
            return None


if __name__ == '__main__':
    from time import sleep
    testPort = 12345

    server = Server(testPort)
    server.start()

    # Continue while the server is still running
    while server.isRunning():
        try:
            sleep(0.1)
        except (KeyboardInterrupt, SystemExit):
            print "Shutting down"
            server.shutdown()
            break

    exit(1)
