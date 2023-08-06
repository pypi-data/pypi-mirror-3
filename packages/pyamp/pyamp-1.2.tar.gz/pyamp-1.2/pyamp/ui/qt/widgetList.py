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
'''Contains the WidgetList and ScrollableList classes which provide the
ability to create a list of widgets, and contain that list within a
QScrollArea.

'''
from PyQt4 import QtCore

from pyamp.ui.qt import BaseWidget
from pyamp.ui.qt import StyleSheet
from pyamp.ui.qt import ResizePolicy


class WidgetList(BaseWidget):
    '''The WidgetList class defines a BaseWidget object that has the ability
    to display a list of widgets vertically one after the other. This class
    handles resizing the widget appropriately based on the widgets that
    are in the list.

    '''
    size = QtCore.QSize(-1, -1)
    horizontalResizePolicy = ResizePolicy.Fixed
    verticalResizePolicy = ResizePolicy.Expanding

    def setVerticalResizePolicy(self, policy):
        '''Set the vertical resize policy.

        * policy -- The new resize policy

        '''
        self.verticalResizePolicy = policy

    def setHorizontalRezizePolicy(self, policy):
        '''Set the horizontal resize policy.

        * policy -- The new resize policy

        '''
        self.horizontalResizePolicy = policy

    def addWidget(self, widget):
        '''Add a widget to this widget list.

        * widget -- The widget to add

        '''
        BaseWidget.addWidget(self, widget)
        self.__resize()

    def addItem(self, item):
        '''Add an item to the widget list.

        * item -- The item to add

        '''
        BaseWidget.addItem(self, item)
        self.__resize()

    def clear(self):
        '''Clear all the widgets from the list.'''
        BaseWidget.clear(self)
        self.__resize()

    def setMargin(self, margin):
        '''Set the margin for this widget list.

        * margin -- The margin to use

        '''
        styleSheet = StyleSheet(margin=margin)
        self.setStyleSheet(styleSheet)

    ##### Private functions #####

    def __resize(self):
        '''Resize the WidgetList based on the current widgets in the list.'''
        sizes = map(lambda widget: widget.sizeHint(), self.getWidgets())
        sizes += map(lambda item: item.sizeHint(), self.getItems())

        widths = map(lambda size: size.width(), sizes)
        heights = map(lambda size: size.height(), sizes)

        # Get the width and height according to the resize policy
        width = ResizePolicy.getSize(self.horizontalResizePolicy,
                                     self.size.width(), widths)
        height = ResizePolicy.getSize(self.verticalResizePolicy,
                                     self.size.height(), heights)

        self.setGeometry(0, 0, width, height)
