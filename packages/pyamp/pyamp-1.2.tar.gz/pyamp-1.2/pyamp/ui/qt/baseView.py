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
'''The baseView module contains the BaseView class which provides a base
framework for more easily creating and using Qt objects.

'''
from pyamp.logging import Loggable, Colors
from pyamp.patterns import RequiredProperties


class BaseView(Loggable, RequiredProperties):
    '''The BaseView class provides a base framework for creating Qt
    objects.

    It provides several functions that are called in a specific order,
    and are to be overridden by subclasses in order to provide a
    specific implementation for the BaseView. These functions pertain
    to certain aspects of setting up a view and are called in the
    following order:

    1. configure()
    2. createLayout()
    3. configureLayout()
    4. setupView()
    5. setupConnections()

    This class implements the :class:`pyamp.logging.Loggable` interface
    and provides the ability to specify the :attr:`logData` object
    as well as the :attr:`color` to use for logging (the default
    color is to use a white foreground color).

    '''

    def __init__(self, name=None, controller=None, mainWindow=None,
                 logData=None, logColor=Colors.Foreground.White):
        '''
        * name -- The name of the BaseView
        * controller -- The controller for the BaseView
        * mainWindow -- The main window
        * logData -- The LogData object
        * logColor -- The color to use for the logger

        '''
        # Use the class name if there was no name provided
        if name is None:
            name = self.__class__.__name__

        # Create the loggable interface
        Loggable.__init__(self, name, logData, logColor)
        RequiredProperties.__init__(self)

        # Store the given parameters
        self.name = name
        self.controller = controller
        self.mainWindow = mainWindow

        # Configure the size for this view
        self.configure()

        # Create and configure the main layout for this class
        self.createLayout()
        self.configureLayout()

        # Create and set up the view
        self.setupView()

        # Now set up any connections for this view
        self.setupConnections()

        # Complete any commands to complete the setup
        self.completeSetup()

    ##### Functions to be overridden by the subclass #####

    def setupView(self):
        '''Create and set up this view.

        .. note:: This function should be overridden by subclasses.

        '''
        pass

    def configure(self):
        '''Configure the view.

        .. note:: This function should be overridden by subclasses.

        '''
        pass

    def createLayout(self):
        '''Create the main layout.

        .. note:: This function should be overridden by subclasses.

        '''
        pass

    def configureLayout(self):
        '''Configure the layout for this view.

        .. note:: This function should be overridden by subclasses.

        '''
        pass

    def setupConnections(self):
        '''Set up any connections this view requires.

        .. note:: This function should be overridden by subclasses.

        '''
        pass

    def completeSetup(self):
        '''Finish setting up the view.

        .. note:: This function should be overridden by subclasses.

        '''
        pass

    def setController(self, controller):
        '''Set the controller object for this view.

        * controller -- The controller

        '''
        self.controller = controller
