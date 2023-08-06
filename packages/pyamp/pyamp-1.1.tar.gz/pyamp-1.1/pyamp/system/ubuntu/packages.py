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
'''The packages module contains utility functions which pertain to
manipulating packages on an Ubunut system, e.g., determining if a package
is installed on the system or not.

'''
from commands import getoutput


def getInstalledPackages():
    '''Get the list of packages that are installed on the system.'''
    cmd = "dpkg --get-selections | grep -v 'deinstall' | awk '{print $1}'"
    return getoutput(cmd).split('\n')


def isInstalled(packageName):
    '''Determine if a package is installed on the system or not.

    * packageName -- The name of the package
    '''
    return packageName in getInstalledPackages()
