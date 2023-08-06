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
'''The colors module contains the Colors class which provides definitions
for various foreground and background colors that can be used to log messages
in various colors.

'''


__all__ = ["Colors"]


class Colors:
    '''The Colors class contains two classes which define possible Foreground
    and Background colors. These colors can be used to colorize console output
    in a specific way.

    '''
    Tag = "\033["
    Symbol = "m"

    class Foreground:
        '''The Foreground class contains definitions of the following
        foreground colors.

        * *White*
        * *White_Bold*
        * *White_Underline*
        * *Black*
        * *Blue*, and *Light_Blue*
        * *Purple*, and *Light_Purple*
        * *Green*, and *Light_Green*
        * *Red*, and *Light_Red*
        * *Gray*, and *Light_Gray*
        * *Cyan*, and *Light_Cyan*
        * *Orange*, and *Light_Yellow*

        '''
        White = 0
        White_Bold = 1
        White_Underline = 4

        Black = 30
        Red = 31
        Green = 32
        Orange = 33
        Blue = 34
        Purple = 35
        Cyan = 36
        Gray = 37

        Light_Gray = 90
        Light_Red = 91
        Light_Green = 92
        Light_Yellow = 93
        Light_Blue = 94
        Light_Purple = 95
        Light_Cyan = 96

    class Background:
        '''The Background class contains definitions of the following
        background colors.

        * *White_Bold_Underline*
        * *Blue*, and *Light_Blue*
        * *Purple*, and *Light_Purple*
        * *Green*, and *Light_Green*
        * *Red*, and *Light_Red*
        * *Gray*, and *Light_Gray*
        * *Cyan*, and *Light_Cyan*
        * *Orange*, and *Light_Yellow*

        '''
        White_Bold_Underline = 7
        Red = 41
        Green = 42
        Orange = 43
        Blue = 44
        Purple = 45
        Cyan = 46
        Gray = 47

        Light_Gray = 100
        Light_Red = 101
        Light_Green = 102
        Light_Yellow = 103
        Light_Blue = 104
        Light_Purple = 105
        Light_Cyan = 106
