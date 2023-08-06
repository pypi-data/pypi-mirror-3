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
'''The directories module contains utility functions which pertain to
manipulating directories and files and getting information pertaining to
both directories and files on a system.

'''
from os import listdir
from os.path import abspath, join, isfile, isdir


def isSvnDirectory(filename):
    '''Determine if the given filename pertains to an SVN directory. '''
    return filename == ".svn"


def getContents(directory, ignoreSvn=False, absPath=False, filterFn=None):
    '''Get the contents of a directory. Return a list of all the files in
    the directory, as well as a list of all the directories. Provide the
    ability to ignore any SVN directories.
    
    * directory -- The directory to get the contents for
    * ignoreSvn -- True to ignore SVN directories, False otherwise
    * absPath -- True to return the absolute path for files and directories
    * filterFn -- The filter function to apply to the filenames

    '''
    files = []
    directories = []

    # Use a default filter function if one is not given
    filterFn = lambda name: True if filterFn is None else filterFn

    for filename in listdir(directory):
        # Only keep track of the file if we are not ignoring SVN directories,
        # or this is not an SVN directory
        if not ignoreSvn or not isSvnDirectory(filename):
            fullFilename = abspath(join(directory, filename))

            # Add the item to the correct list depending on its type
            if isfile(fullFilename) and filterFn(fullFilename):
                files.append(fullFilename if absPath else filename)
            elif isdir(fullFilename):
                directories.append(fullFilename if absPath else filename)

    # Convert the files and directories into sets to get rid of any
    # duplicate entries that might exist
    return set(files), set(directories)


def getPythonContents(directory, absPath=False):
    '''Get the Python modules files contained within the given
    directory.

    * directory -- The directory to get the contents for
    * absPath -- True to return absolute paths to files

    '''
    # Create a filter function to grab only Python module files
    filterFn = lambda filename: filename.endswith(".py")
    return getContents(directory, ignoreSvn=True, absPath=absPath,
                       filterFn=filterFn)
