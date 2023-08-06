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
'''The resizePolicy module contains the ResizePolicy class which encapsulates
a specific policy for resizing widgets.

'''


class ResizePolicy:
    '''The ResizePolicy encapsulates a specific policy for resizing widgets.

    The possible resize policies are:

        * **Fixed** -- The size never changes
        * **Expanding** -- The size expands

    For a specific policy, the ResizePolicy class can return the correct size
    for a widget, given the widget's current size as well as the size of all
    of the widget's child widgets.

    For the *Fixed* resize policy: the size will always remain the same.

    For the *Expanding* resize policy: the size will always expand to fit all
    of the widget's children.

    Example::

        from PyQt4 import QtCore
        from pyamp.ui.qt import ResizePolicy

        # Create the size of the widget, and the list of sizes for all of
        # the widget's children
        size = QtCore.QSize(100, 200)
        childSizes = [QtCore.QSize(200, 500), QtCore.QSize(300, 400)]

        # Get the list of widths and heights for the child widgets
        childWidths = map(QtCore.QSize.width, childSizes)
        childHeights = map(QtCore.QSize.width, childSizes)

        # Both of these return: 100
        # Which is the given value of width
        ResizePolicy.getSize(ResizePolicy.Fixed, size.width(), childWidths)
        ResizePolicy.getWidth(ResizePolicy.Fixed, size, childSizes)

        # Both of these return: 900
        # Which is the sum of the childHeights list
        ResizePolicy.getSize(ResizePolicy.Expanding, size.height(),
                             childHeights)
        ResizePolicy.getHeight(ResizePolicy.Fixed, size, childSizes)

    '''
    Fixed = 0
    Expanding = 1

    @classmethod
    def getWidth(cls, policy, size, sizeList):
        '''For the given resize policy, get the correct width for the size of
        the widget as well as the size of all of the widget's children.

        * resizePolicy -- The resize policy
        * size -- The main :class:`PyQt4.QtCore.QSize` of the widget
        * sizeList -- The list of :class:`PyQt4.QtCore.QSize` for sub widgets

        '''
        widthList = map(QtCore.QSize.width, sizeList)
        return cls.getSize(policy, size.width(), widthList)

    @classmethod
    def getHeight(cls, policy, size, sizeList):
        '''For the given resize policy, get the correct height for the size of
        the widget as well as the size of all of the widget's children.

        * resizePolicy -- The resize policy
        * size -- The main :class:`PyQt4.QtCore.QSize` of the widget
        * sizeList -- The list of :class:`PyQt4.QtCore.QSize` for sub widgets

        '''
        heightList = map(QtCore.QSize.height, sizeList)
        return cls.getSize(policy, size.height(), heightList)

    @classmethod
    def getSize(cls, policy, size, sizeList):
        '''Get the correct size based on the given resize policy.

        * resizePolicy -- The resize policy
        * size -- The main single size (width or height) of the widget
        * sizeList -- The list of the single dimension size (widths or heights)
                      of widgets's children

        '''
        policyMap = {
            cls.Fixed: cls.__getFixedSize,
            cls.Expanding: cls.__getExpandingSize
            }

        policyFn = policyMap.get(policy)
        if policyFn is not None:
            return policyFn(size, sizeList)
        else:
            raise Exception("Unknown Policy [%s]" % policy)

    @classmethod
    def __getFixedSize(cls, size, _sizeList):
        '''Return the fixed size.

        * resizePolicy -- The resize policy
        * size -- The main size (width or height) of the widget
        * _sizeList -- The list of the size (widths or heights) of sub widgets

        '''
        return size

    @classmethod
    def __getExpandingSize(cls, _size, sizeList):
        '''Return the expanding size.

        * resizePolicy -- The resize policy
        * _size -- The main size (width or height) of the widget
        * sizeList -- The list of the size (widths or heights) of sub widgets

        '''
        # Return the sum of all the subwidget sizes
        return sum(sizeList)
