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
'''The keys module contains definitions for various keys that
can be pressed on a keyboard.

'''


__all__ = ["Keys"]


class Keys:
    '''The Keys class contains definitions of various keys.'''
    Backspace = '\x7f'
    Enter = '\n'
    Escape = '\x1b'

    class Control:
        '''The Control class contains definitions of various control keys.'''
        N = '\x0e'
        P = '\x10'
