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
'''The scrollableList module contains the ScrollableList class which provides
and implementation of the BaseWidget class to display a WidgetList within
a QScrollArea.

'''
from PyQt4 import QtCore, QtGui

from pyamp.ui.qt import BaseWidget
from pyamp.ui.qt import WidgetList


class ScrollBarPolicy:
    '''The ScrollBarPolicy class contains the policies which control
    the visibility of a scrollbar.

    '''

    AsNeeded = QtCore.Qt.ScrollBarAsNeeded
    '''The scrollbar will be visible only when the all of the scroll area
    cannot be viewed at once.

    '''

    AlwaysOff = QtCore.Qt.ScrollBarAlwaysOff
    '''The scrollbar will never be displayed.'''

    AlwaysOn = QtCore.Qt.ScrollBarAlwaysOn
    '''The scrollbar will always be displayed.'''


class ScrollableList(BaseWidget):
    '''The ScrollableList class creates a BaseWidget that contains a
    QScrollArea which displays a WidgetList inside of the scroll area. This
    allows a the user to scroll through the WidgetList to see previously added
    widgets.

    In order to fix the size of the scroll area, subclasses of ScrollableList
    should set the *size* class property which is a QSize object.

    '''
    size = QtCore.QSize(-1, -1)
    '''The size property contains the size of the scrollable list.'''

    margin = 0
    '''The margin property contains the margin between all items in the list.

    '''

    horizontalPolicy = ScrollBarPolicy.AlwaysOff
    '''The horizontalPolicy property contains the :class:`.ScrollBarPolicy`
    for the horizontal scrollbar.

    '''

    verticalPolicy = ScrollBarPolicy.AsNeeded
    '''The verticalPolicy property contains the :class:`.ScrollBarPolicy`
    for the vertical scrollbar.

    '''

    def sizeHint(self):
        '''Override the QWidget sizeHint function to return the size of this
        ScrollableList.

        '''
        return self.size

    def createElements(self):
        '''Override the BaseWidget createElements class.'''
        self.__listView = WidgetList("%sWidgetList" % self.name)
        self.__listView.size = self.size
        self.__listView.setMargin(self.margin)

        self.__scrollArea = QtGui.QScrollArea()
        self.__scrollArea.setWidget(self.__listView)

        # Set the horizontal and vertical scrollbar policies
        self.__scrollArea.setHorizontalScrollBarPolicy(self.horizontalPolicy)
        self.__scrollArea.setVerticalScrollBarPolicy(self.verticalPolicy)

        return [self.__scrollArea]

    def addWidget(self, widget):
        '''Add a widget to the ScrollableList widget.'''
        self.__listView.addWidget(widget)

    def addItem(self, item):
        '''Add an item to the ScrollabelList widget.'''
        self.__listView.addItem(item)

    def clearWidgets(self):
        '''Clear all of the widgets from the ScrollableList.'''
        self.__listView.clear()

    def getWidgetList(self):
        '''Get the WidgetList for this ScrollabeList.'''
        return self.__listView

    def getScrollArea(self):
        '''Get the QScrollArea for this widget.'''
        return self.__scrollArea

    def scroll(self, amount):
        '''Scroll the vertical scrollbar by the given amount.

        * amount -- The amount to scroll (negative being scrolling up, and
                    is positive scrolling down)

        '''
        verticalScrollBar = self.__scrollArea.verticalScrollBar()
        verticalScrollBar.setValue(verticalScrollBar.value() + amount)

    def scrollTo(self, y=0):
        '''Scroll to the given position.

        * y -- The y position to scroll to

        '''
        verticalScrollBar = self.__scrollArea.verticalScrollBar()
        verticalScrollBar.setSliderPosition(y)

    def scrollToBottom(self):
        '''Scroll to the bottom of the list.'''
        verticalScrollBar = self.__scrollArea.verticalScrollBar()
        verticalScrollBar.setSliderPosition(verticalScrollBar.maximum())

    def scrollToTop(self):
        '''Scroll to the top of the list.'''
        verticalScrollBar = self.__scrollArea.verticalScrollBar()
        verticalScrollBar.setSliderPosition(verticalScrollBar.minimum())


if __name__ == '__main__':
    import sys
    from PyQt4.Qt import QApplication, QMainWindow

    class MainWindow(QMainWindow):
        '''A MainWindow for testing the ScrollableList and WidgetList.'''

        def __init__(self):
            '''Create the MainWindow.'''
            QMainWindow.__init__(self)

            # self.__view = WidgetList(mainWindow=self)
            self.__view = ScrollableList(mainWindow=self)
            ScrollableList.size = QtCore.QSize(100, 300)
            self.setCentralWidget(self.__view)

            for i in range(10):
                label = QtGui.QLabel("Test %d" % (i + 1))
                self.__view.addWidget(label)

            for i in range(3):
                label = QtGui.QPushButton("Test %d" % (i + 1))
                self.__view.addWidget(label)

            for i in range(4):
                label = QtGui.QLineEdit()
                self.__view.addWidget(label)

            self.__view.clear()

            for i in range(4):
                label = QtGui.QLineEdit()
                self.__view.addWidget(label)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
