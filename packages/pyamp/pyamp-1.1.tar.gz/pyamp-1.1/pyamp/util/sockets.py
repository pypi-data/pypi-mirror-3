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
'''Contains utility methods for modifying socket attributes.'''
from socket import SOL_SOCKET, SO_REUSEADDR


__all__ = ["setReusable"]


def setReusable(sockFd):
    '''Set the given socket to be reusable.

    * sockFd -- The socket file descriptor

    '''
    # Set SO_REUSEADDR (if available on this platform)
    if hasattr(sockFd, 'SOL_SOCKET') and hasattr(sockFd, 'SO_REUSEADDR'):
        sockFd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
