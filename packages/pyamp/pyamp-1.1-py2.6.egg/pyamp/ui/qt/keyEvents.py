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
'''The keyEvents module contains the KeyEvents class which provides the
ability to parse a QKeyEvent into a string representation of the keys
that were pressed.

'''
from PyQt4.QtCore import Qt


__all__ = ['KeyEvents']


class KeyEvents:
    '''This class provided functions for dealing with
    :class:`PyQt4.QtGui.QKeyEvent` objects.

    The main function of this class is to provide a method to convert a
    :class:`PyQt4.QtGui.QKeyEvent` object into a string representation of the
    keys that were pressed in the given event.

    '''
    # @todo: ADD ALL THE Qt.KEYS TO THIS LIST, including 0-255 keys
    # @todo: after that, get rid of the two separate key handling parts in
    #        parse
    # found: http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qt.html#KeyboardModifier-enum
    KeyMap = {
        Qt.Key_Escape: 'ESC',
        Qt.Key_Tab: 'TAB',
        Qt.Key_Backspace: 'BKSPC',
        Qt.Key_Return: 'RET',
        Qt.Key_Enter: 'ENT',
        }

    @classmethod
    def parse(cls, event):
        '''Parse the given QKeyEvent into the string representation of
        the keys pressed.

        * event -- The QKeyEvent

        '''
        keyList = KeyEvents.__getModifiers(event)

        # Convert the key into a character, assuming it's within the
        # proper range
        if event.key() in range(256):
            keyList.append(chr(event.key()))
        else:
            specialKey = KeyEvents.__getSpecialKey(event.key())
            if specialKey is not None:
                keyList.append(specialKey)

        return '-'.join(keyList)

    @classmethod
    def __getModifiers(cls, event):
        '''Get the list of pressed modifiers from the current key event.

        * event -- The QKeyEvent

        '''
        keyList = []

        modMap = {Qt.ControlModifier: 'C',
                  Qt.AltModifier: 'A',
                  Qt.MetaModifier: 'M'}

        # Check each of the modifiers in the dictionary against
        # the currently pressed modifiers
        modifiers = event.modifiers()
        for modifier in modMap:
            # If the modifier is pressed, keep track of it
            if modifier & modifiers:
                keyList.append(modMap[modifier])

        return keyList

    @classmethod
    def __getSpecialKey(cls, key):
        '''Get the string representation for a special key.

        * key -- The key pressed

        '''
        # Traverse all of the keys to determine which key this is
        for keyValue in KeyEvents.KeyMap:
            if keyValue == key:
                return KeyEvents.KeyMap[keyValue]

        return None
