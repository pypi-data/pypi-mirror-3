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
'''The baseWidget module contains the BaseWidget class which provides an
implementation of the BaseView specific to creating an extending a
QWidget object.

'''
from PyQt4 import QtGui

from pyamp.ui.qt import BaseView
from pyamp.logging import Colors


class LayoutType:
    '''The LayoutType class contains definitions of the different
    types of layouts.

    '''
    Vertical = "vertical"
    Horizontal = "horizontal"

    @classmethod
    def get(cls, layoutType):
        '''Get the Qt layout object for the given layout type.

        * layoutType -- The type of layout

        '''
        layoutMap = {
            LayoutType.Vertical: QtGui.QVBoxLayout,
            LayoutType.Horizontal: QtGui.QHBoxLayout
            }

        layout = layoutMap.get(layoutType, lambda: None)

        # Create the layout
        return layout()


class BaseWidget(QtGui.QWidget, BaseView):
    '''The BaseWidget class provides an implementation of the
    :class:`amp.ui.qt.BaseView` class designed to set up and create a
    :class:`PyQt4.QtGui.QWidget` object.

    This class provides serveral functions which can be overridden by
    subclasses to easily add features to the BaseWidget. These functions
    are called in the following order during the set up process:

      1. configure()
      2. configureLayout()
      3. createElements()
      4. setupConnections()

    '''
    __spacing = 0
    __leftMargin = 0
    __topMargin = 0
    __rightMargin = 0
    __bottomMargin = 0

    layoutType = LayoutType.Vertical
    '''The layoutType property contains the type of layout to use for this
    Widget. It should be a value from the :class:`LayoutType` class.

    '''

    tabOrder = None
    '''The tabOrder property allows concrete widgets to set their tab order.
    Each element in the list will be tab connected to the next element in
    the list. The list will cycle around to the front so the final element
    is tab connected to the first element.

    '''

    def __init__(self, name=None, controller=None, mainWindow=None,
                 logData=None, logColor=Colors.Foreground.White):
        '''
        * name -- The name of the BaseWidget
        * controller -- The controller for the BaseWidget
        * mainWindow -- The main window
        * logData -- The :class:`pyamp.logging.LogData` object
        * logColor -- The color to use for logging

        '''
        # No widgets, or items to begin with
        self.__widgets = []
        self.__items = []

        QtGui.QWidget.__init__(self)
        BaseView.__init__(self, name, controller, mainWindow,
                          logData, logColor)

        # Set the name of the widget to be the given name
        self.setObjectName(self.name)

    ##### Functions for setting up and tearing down the view #####

    def setStyleSheet(self, styleSheet):
        '''Set the style sheet for this widget.

        * styleSheet -- The StyleSheet

        '''
        QtGui.QWidget.setStyleSheet(self, str(styleSheet))

    def getWidgets(self):
        '''Return the list of child widgets for this BaseWidget.'''
        return self.__widgets

    def getItems(self):
        '''Return the list of child items for this BaseWidget.'''
        return self.__items

    def setupView(self):
        '''Create and set up this view.'''
        # Create all the sub widgets for this view
        elements = self.createElements()

        # Add all of the widgets, in the specified order, to the layout
        self.addElements(elements)

        if self.tabOrder is not None and len(self.tabOrder) > 0:
            # Create a list of elements with the first element at
            # the end of the list
            shiftedElements = self.tabOrder[1:] + self.tabOrder[0]

            # Tab connect all the elements to their shifted pair
            for first, second in zip(self.tabOrder, shiftedElements):
                self.setTabOrder(first, second)

    def clear(self):
        '''Remove all of the child widgets and items currently for this
        BaseWidget.

        '''
        self.clearWidgets()
        self.clearItems()

        self.__widgets = []
        self.__items = []

    def clearWidgets(self):
        '''Clear all the widgets from this BaseWidget.'''
        for widget in self.__widgets:
            self.mainLayout.removeWidget(widget)
            widget.hide()

    def clearItems(self):
        '''Clear all the items from this BaseWidget.'''
        for item in self.__items:
            self.mainLayout.removeItem(item)

    ##### Functions for manipulating the view #####

    def addElements(self, elements):
        '''Add a list of elements to the main layout.

        * elements -- The list of elements

        '''
        for element in elements:
            self.addElement(element)

    def addElement(self, element):
        '''Add an element to the main layout.

        * element -- The element to add

        '''
        # Add the element depending on what type of element it is
        if isinstance(element, QtGui.QLayoutItem):
            self.mainLayout.addItem(element)
            self.__items.append(element)
        elif isinstance(element, QtGui.QWidget):
            self.mainLayout.addWidget(element)
            self.__widgets.append(element)
        else:
            raise Exception("Unknown element type: [%s]" % type(element))

    def addWidget(self, widget):
        '''Add a widget to the main layout.

        * widget -- The widget to add

        '''
        self.mainLayout.addWidget(widget)
        self.__widgets.append(widget)

    def addItem(self, item):
        '''Add an item to the main layout.

        * item -- The item to add

        '''
        self.mainLayout.addItem(item)
        self.__items.append(item)

    def createLayout(self):
        '''Create the main layout.'''
        # Create the main layout for the widget
        self.mainLayout = LayoutType.get(self.layoutType)

        # Get rid of the spacing between components placed in the layout
        # as well as the margins
        self.mainLayout.setSpacing(self.__spacing)
        self.mainLayout.setContentsMargins(self.__leftMargin,
                                           self.__topMargin,
                                           self.__rightMargin,
                                           self.__bottomMargin)

        # Set the layout for this widget
        self.setLayout(self.mainLayout)

    ##### Functions to be overridden by the subclass #####

    def configure(self):
        '''Configure the view.'''
        pass

    def configureLayout(self):
        '''Configure the layout for this view.'''
        pass

    def createElements(self):
        '''Create the elements for this view. Return the list of widgets,
        or items in the order that they should be added to the layout.

        '''
        return []

    def setupConnections(self):
        '''Set up any connections this view requires.'''
        pass

    #### Getter and setter functions #####

    def setSpacing(self, spacing):
        '''Set the spacing between components in the layout.

        * spacing -- The spacing

        '''
        self.__spacing = spacing

    def setMargins(self, left=None, top=None, right=None, bottom=None):
        '''Set the content margins for this widget's layout.

        * left -- The left margin
        * top -- The top margin
        * right -- The right margin
        * bottom -- The bottom margin

        '''
        self.__leftMargin = self.__leftMargin if left is None else left
        self.__topMargin = self.__topMargin if top is None else top
        self.__rightMargin = self.__rightMargin if right is None else right
        self.__bottomMargin = self.__bottomMargin if bottom is None else bottom

    ##### Override QWidget functions #####

    def paintEvent(self, _event):
        '''Override the paintEvent function to allow StylSheets to work for
        this QWidget.

        Note this function was taken from the documentation of style sheets
             for custom QWidget classes.

        * _event -- The QPaintEvent

        '''
        opt = QtGui.QStyleOption()
        opt.init(self)

        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)
