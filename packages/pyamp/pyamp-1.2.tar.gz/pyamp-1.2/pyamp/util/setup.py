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
'''The setup module contains utility functions pertaining to aiding
the process of setting up a Python module using the distutil setup.py
script.

'''
from sys import stderr
from os.path import join, basename

from pyamp.util import getContents


def getDataFiles(directory, outputBaseDir):
    '''Return a list of the the data file tuples to use when setting
    up this system. Each item in the list should be a tuple where the
    first element in the tuple is the destination directory, and the
    second item in the tuple is the list of files which should be
    copied to the destination directory (without being renamed).

    The output of this function should be used as the value for the
    data_files attribute for the setup.py script.

    '''
    # Grab the contents of the current directory
    files, directories = getContents(directory, ignoreSvn=True, absPath=True)

    # Create the tuple for the current directory
    outputTuple = [(outputBaseDir, files)]

    # Now recurse to include tuples for all sub-directories
    for dirName in directories:
        newOutputDir = join(outputBaseDir, basename(dirName))
        outputTuple.extend(getDataFiles(dirName, newOutputDir))

    return outputTuple


def isModuleInstalled(moduleName):
    '''Check that the given Python module name is installed and accessible.
    Return True if the module is installed, False otherwise.

    * moduleName -- The module name that must be installed

    '''
    try:
        __import__(moduleName, globals(), locals(), [], -1)
        return True
    except ImportError, e:
        return False


def requireModules(programName, requiredModules):
    '''The given modules are required to be installed. If any of the modules
    are not installed, raise an Exception.

    * requiredModules -- The list of required module names

    '''
    # Check for all the required modules
    for moduleName in requiredModules:
        # Check that the given module is installed
        if not isModuleInstalled(moduleName):
            raise Exception("Missing required module '%s'" % moduleName)
