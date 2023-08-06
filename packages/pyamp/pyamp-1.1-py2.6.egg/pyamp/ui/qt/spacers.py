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
'''The spacers module contains classes which provide the ability to easily
create horizontal or vertical QSpacerItems.

'''
from PyQt4.Qt import QSizePolicy
from PyQt4.QtGui import QSpacerItem


class HorizontalSpacer(QSpacerItem):
    '''Create a horizontallay expanding spacer.'''

    def __init__(self, width=10, height=10):
        '''
        * width -- The minimum width
        * height -- The fixed height

        '''
        QSpacerItem.__init__(self, width, height,
                             hPolicy=QSizePolicy.Expanding)


class VerticalSpacer(QSpacerItem):
    '''Create a vertically expanding spacer.'''

    def __init__(self, width=10, height=10):
        '''
        * width -- The fixed width
        * height -- The minimum height

        '''
        QSpacerItem.__init__(self, width, height,
                             vPolicy=QSizePolicy.Expanding)


class FixedHorizontalSpacer(QSpacerItem):
    '''Create a horizontally fixed spacer item.'''

    def __init__(self, width=10, height=10):
        '''
        * width -- The fixed width
        * height -- The height for the spacer

        '''
        QSpacerItem.__init__(self, width, height, hPolicy=QSizePolicy.Fixed)


class FixedVerticalSpacer(QSpacerItem):
    '''Create a vertically fixed spacer item.'''

    def __init__(self, width=10, height=10):
        '''
        * width -- The width for the spacer
        * height -- The fixed height

        '''
        QSpacerItem.__init__(self, width, height, vPolicy=QSizePolicy.Fixed)
