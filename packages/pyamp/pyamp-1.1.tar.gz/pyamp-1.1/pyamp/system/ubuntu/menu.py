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
'''The menu module contains the Menu class which provides the ability to locate
the configuration file for the Ubuntu application menu, as well as locating the
system directory containing the applications.

'''
from os import environ
from os.path import exists, join


__all__ = ["Menu"]


class Menu:
    '''The Menu class provides the ability to find the file containing
    the configuration data pertaining to the Ubuntu applications menu, as
    well as the ability to locate the directory which stores the specific
    application configuration files.

    '''

    # A tuple containing the directories and final filename for
    # the applications menu file to locate
    MenuFilename = ("menus", "applications.menu")

    # Get the home directory location
    Home = environ.get("HOME")

    # Get the XDG_CONFIG_HOME environment variable, defaulting to the
    # ~/.config directory if it is not set
    ConfigHome = environ.get("XDG_CONFIG_HOME", join(Home, ".config"))

    # Get the XDG_CONFIG_DIRS environment variable, defaulting to the
    # /etc/xdg directory if it is not set
    ConfigDirs = environ.get("XDG_CONFIG_DIRS", join("/etc", "xdg"))

    # Get the XDG_DATA_DIRS environment variable, defaulting to the
    # /usr/share directory if it is not set
    DataDirs = environ.get("XDG_DATA_DIRS", join("/usr", "share"))

    @classmethod
    def findMenuFile(cls):
        '''Return the system file associated with the applications menu, or
        None if it was unable to be located.

        '''
        # How to locate the applications menu file:
        # 1. Search each directory in $XDG_CONFIG_HOME in order to find
        #    menus/applications.menu. If $XDG_CONFIG_HOME is not set, it
        #    defaults to the ~/.config/ directory.
        # 2. Search each directory in $XDG_CONFIG_DIRS in order to find
        #    menus/applications.menu. If $XDG_CONFIG_DIRS is not set, it
        #    defaults to the /etc/xdg/ directory.
        # 3. Use the first applications.menu file found.

        order = cls.ConfigHome.split(":") + cls.ConfigDirs.split(":")

        for directory in order:
            applicationFile = join(directory, *cls.MenuFilename)
            if exists(applicationFile):
                return applicationFile

        return None

    @classmethod
    def findApplicationsDirectory(cls):
        '''Return the directory which contains the application desktop files,
        or None if it was unable to be located.

        '''
        # Get the base directory for applications from XDG_DATA_DIRS
        # if that is not set, then default to /usr/share
        for directory in Menu.DataDirs.split(":"):
            applicationsDir = join(directory, "applications")
            if exists(applicationsDir):
                return applicationsDir

        return None
