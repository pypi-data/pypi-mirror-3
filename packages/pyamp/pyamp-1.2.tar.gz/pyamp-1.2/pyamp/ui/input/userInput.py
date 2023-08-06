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
'''The userInput module contains the UserInput class which provides
the ability to process keyboard presses from a user and call a specific
function when certain keys are received.

'''
from copy import copy

from pyamp.ui.input.evdev import Device


__all__ = ["UserInput"]


# Function for determining if a list item is not the given value
_NOT_FUNCTION = lambda value: lambda item: item != value


class UserInput:
    '''The UserInput class uses the :mod:`amp.ui.input.evdev` module to
    receive the user's keyboard presses given the specific Linux
    keyboard device.

    This class provides to ability to add a series of callbacks for
    specific keyboard presses. These functions will be called in the
    event that the key presses occur.

    '''

    def __init__(self, keyboard, debug=False):
        '''
        * keyboard -- The Linux keyboard device
        * debug -- True for debugging mode, False otherwise

        '''
        self.__dev = Device(keyboard)
        self.__debug = debug

        # Key for alphanumeric keys, punctuation, and any key
        self.KEY_ALPHA_NUMERIC = "KEY_ALPHANUMERIC"
        self.KEY_PUNCTUATION = "KEY_PUNCTUATION"
        self.KEY_ANY = "KEY_ANY"

        # Define control modifiers
        self.MOD_CTRL = "MOD_CTRL"
        self.MOD_LEFTCTRL = "KEY_LEFTCTRL"
        self.MOD_RIGHTCTRL = "KEY_RIGHTCTRL"
        self.MOD_LEFTRIGHTCTRL = "MOD_LEFTRIGHTCTRL"

        self.MOD_ALT = "MOD_ALT"
        self.MOD_LEFTALT = "KEY_LEFTALT"
        self.MOD_RIGHTALT = "KEY_RIGHTALT"
        self.MOD_LEFTRIGHTALT = "MOD_LEFTRIGHTALT"

        self.MOD_SHIFT = "MOD_SHIFT"
        self.MOD_LEFTSHIFT = "KEY_LEFTSHIFT"
        self.MOD_RIGHTSHIFT = "KEY_RIGHTSHIFT"
        self.MOD_LEFTRIGHTSHIFT = "MOD_LEFTRIGHTSHIFT"

        self.MOD_META = "MOD_META"
        self.MOD_LEFTMETA = "KEY_LEFTMETA"
        self.MOD_RIGHTMETA = "KEY_RIGHTMETA"
        self.MOD_LEFTRIGHTMETA = "MOD_LEFTRIGHTMETA"

        self.KEY_ESC = "KEY_ESC"
        self.KEY_1 = "KEY_1"
        self.KEY_2 = "KEY_2"
        self.KEY_3 = "KEY_3"
        self.KEY_4 = "KEY_4"
        self.KEY_5 = "KEY_5"
        self.KEY_6 = "KEY_6"
        self.KEY_7 = "KEY_7"
        self.KEY_8 = "KEY_8"
        self.KEY_9 = "KEY_9"
        self.KEY_0 = "KEY_0"
        self.KEY_MINUS = "KEY_MINUS"
        self.KEY_EQUAL = "KEY_EQUAL"
        self.KEY_BACKSPACE = "KEY_BACKSPACE"
        self.KEY_TAB = "KEY_TAB"
        self.KEY_Q = "KEY_Q"
        self.KEY_W = "KEY_W"
        self.KEY_E = "KEY_E"
        self.KEY_R = "KEY_R"
        self.KEY_T = "KEY_T"
        self.KEY_Y = "KEY_Y"
        self.KEY_U = "KEY_U"
        self.KEY_I = "KEY_I"
        self.KEY_O = "KEY_O"
        self.KEY_P = "KEY_P"
        self.KEY_LEFTBRACE = "KEY_LEFTBRACE"
        self.KEY_RIGHTBRACE = "KEY_RIGHTBRACE"
        self.KEY_ENTER = "KEY_ENTER"
        self.KEY_LEFTCTRL = "KEY_LEFTCTRL"
        self.KEY_A = "KEY_A"
        self.KEY_S = "KEY_S"
        self.KEY_D = "KEY_D"
        self.KEY_F = "KEY_F"
        self.KEY_G = "KEY_G"
        self.KEY_H = "KEY_H"
        self.KEY_J = "KEY_J"
        self.KEY_K = "KEY_K"
        self.KEY_L = "KEY_L"
        self.KEY_SEMICOLON = "KEY_SEMICOLON"
        self.KEY_APOSTROPHE = "KEY_APOSTROPHE"
        self.KEY_GRAVE = "KEY_GRAVE"
        self.KEY_LEFTSHIFT = "KEY_LEFTSHIFT"
        self.KEY_BACKSLASH = "KEY_BACKSLASH"
        self.KEY_Z = "KEY_Z"
        self.KEY_X = "KEY_X"
        self.KEY_C = "KEY_C"
        self.KEY_V = "KEY_V"
        self.KEY_B = "KEY_B"
        self.KEY_N = "KEY_N"
        self.KEY_M = "KEY_M"
        self.KEY_COMMA = "KEY_COMMA"
        self.KEY_DOT = "KEY_DOT"
        self.KEY_SLASH = "KEY_SLASH"
        self.KEY_RIGHTSHIFT = "KEY_RIGHTSHIFT"
        self.KEY_KPASTERISK = "KEY_KPASTERISK"
        self.KEY_LEFTALT = "KEY_LEFTALT"
        self.KEY_SPACE = "KEY_SPACE"
        self.KEY_CAPSLOCK = "KEY_CAPSLOCK"
        self.KEY_F1 = "KEY_F1"
        self.KEY_F2 = "KEY_F2"
        self.KEY_F3 = "KEY_F3"
        self.KEY_F4 = "KEY_F4"
        self.KEY_F5 = "KEY_F5"
        self.KEY_F6 = "KEY_F6"
        self.KEY_F7 = "KEY_F7"
        self.KEY_F8 = "KEY_F8"
        self.KEY_F9 = "KEY_F9"
        self.KEY_F10 = "KEY_F10"
        self.KEY_NUMLOCK = "KEY_NUMLOCK"
        self.KEY_SCROLLLOCK = "KEY_SCROLLLOCK"
        self.KEY_KP7 = "KEY_KP7"
        self.KEY_KP8 = "KEY_KP8"
        self.KEY_KP9 = "KEY_KP9"
        self.KEY_KPMINUS = "KEY_KPMINUS"
        self.KEY_KP4 = "KEY_KP4"
        self.KEY_KP5 = "KEY_KP5"
        self.KEY_KP6 = "KEY_KP6"
        self.KEY_KPPLUS = "KEY_KPPLUS"
        self.KEY_KP1 = "KEY_KP1"
        self.KEY_KP2 = "KEY_KP2"
        self.KEY_KP3 = "KEY_KP3"
        self.KEY_KP0 = "KEY_KP0"
        self.KEY_KPDOT = "KEY_KPDOT"
        self.KEY_103RD = "KEY_103RD"
        self.KEY_F13 = "KEY_F13"
        self.KEY_102ND = "KEY_102ND"
        self.KEY_F11 = "KEY_F11"
        self.KEY_F12 = "KEY_F12"
        self.KEY_F14 = "KEY_F14"
        self.KEY_F15 = "KEY_F15"
        self.KEY_F16 = "KEY_F16"
        self.KEY_F17 = "KEY_F17"
        self.KEY_F18 = "KEY_F18"
        self.KEY_F19 = "KEY_F19"
        self.KEY_F20 = "KEY_F20"
        self.KEY_KPENTER = "KEY_KPENTER"
        self.KEY_RIGHTCTRL = "KEY_RIGHTCTRL"
        self.KEY_KPSLASH = "KEY_KPSLASH"
        self.KEY_SYSRQ = "KEY_SYSRQ"
        self.KEY_RIGHTALT = "KEY_RIGHTALT"
        self.KEY_LINEFEED = "KEY_LINEFEED"
        self.KEY_HOME = "KEY_HOME"
        self.KEY_UP = "KEY_UP"
        self.KEY_PAGEUP = "KEY_PAGEUP"
        self.KEY_LEFT = "KEY_LEFT"
        self.KEY_RIGHT = "KEY_RIGHT"
        self.KEY_END = "KEY_END"
        self.KEY_DOWN = "KEY_DOWN"
        self.KEY_PAGEDOWN = "KEY_PAGEDOWN"
        self.KEY_INSERT = "KEY_INSERT"
        self.KEY_DELETE = "KEY_DELETE"
        self.KEY_MACRO = "KEY_MACRO"
        self.KEY_MUTE = "KEY_MUTE"
        self.KEY_VOLUMEDOWN = "KEY_VOLUMEDOWN"
        self.KEY_VOLUMEUP = "KEY_VOLUMEUP"
        self.KEY_POWER = "KEY_POWER"
        self.KEY_KPEQUAL = "KEY_KPEQUAL"
        self.KEY_KPPLUSMINUS = "KEY_KPPLUSMINUS"
        self.KEY_PAUSE = "KEY_PAUSE"
        self.KEY_F21 = "KEY_F21"
        self.KEY_F22 = "KEY_F22"
        self.KEY_F23 = "KEY_F23"
        self.KEY_F24 = "KEY_F24"
        self.KEY_KPCOMMA = "KEY_KPCOMMA"
        self.KEY_LEFTMETA = "KEY_LEFTMETA"
        self.KEY_RIGHTMETA = "KEY_RIGHTMETA"
        self.KEY_COMPOSE = "KEY_COMPOSE"
        self.KEY_STOP = "KEY_STOP"
        self.KEY_AGAIN = "KEY_AGAIN"
        self.KEY_PROPS = "KEY_PROPS"
        self.KEY_UNDO = "KEY_UNDO"
        self.KEY_FRONT = "KEY_FRONT"
        self.KEY_COPY = "KEY_COPY"
        self.KEY_OPEN = "KEY_OPEN"
        self.KEY_PASTE = "KEY_PASTE"
        self.KEY_FIND = "KEY_FIND"
        self.KEY_CUT = "KEY_CUT"
        self.KEY_HELP = "KEY_HELP"
        self.KEY_MENU = "KEY_MENU"
        self.KEY_CALC = "KEY_CALC"
        self.KEY_SETUP = "KEY_SETUP"
        self.KEY_SLEEP = "KEY_SLEEP"
        self.KEY_WAKEUP = "KEY_WAKEUP"
        self.KEY_FILE = "KEY_FILE"
        self.KEY_SENDFILE = "KEY_SENDFILE"
        self.KEY_DELETEFILE = "KEY_DELETEFILE"
        self.KEY_XFER = "KEY_XFER"
        self.KEY_PROG1 = "KEY_PROG1"
        self.KEY_PROG2 = "KEY_PROG2"
        self.KEY_WWW = "KEY_WWW"
        self.KEY_MSDOS = "KEY_MSDOS"
        self.KEY_COFFEE = "KEY_COFFEE"
        self.KEY_DIRECTION = "KEY_DIRECTION"
        self.KEY_CYCLEWINDOWS = "KEY_CYCLEWINDOWS"
        self.KEY_MAIL = "KEY_MAIL"
        self.KEY_BOOKMARKS = "KEY_BOOKMARKS"
        self.KEY_COMPUTER = "KEY_COMPUTER"
        self.KEY_BACK = "KEY_BACK"
        self.KEY_FORWARD = "KEY_FORWARD"
        self.KEY_CLOSECD = "KEY_CLOSECD"
        self.KEY_EJECTCD = "KEY_EJECTCD"
        self.KEY_EJECTCLOSECD = "KEY_EJECTCLOSECD"
        self.KEY_NEXTSONG = "KEY_NEXTSONG"
        self.KEY_PLAYPAUSE = "KEY_PLAYPAUSE"
        self.KEY_PREVIOUSSONG = "KEY_PREVIOUSSONG"
        self.KEY_STOPCD = "KEY_STOPCD"
        self.KEY_RECORD = "KEY_RECORD"
        self.KEY_REWIND = "KEY_REWIND"
        self.KEY_PHONE = "KEY_PHONE"
        self.KEY_ISO = "KEY_ISO"
        self.KEY_CONFIG = "KEY_CONFIG"
        self.KEY_HOMEPAGE = "KEY_HOMEPAGE"
        self.KEY_REFRESH = "KEY_REFRESH"
        self.KEY_EXIT = "KEY_EXIT"
        self.KEY_MOVE = "KEY_MOVE"
        self.KEY_EDIT = "KEY_EDIT"
        self.KEY_SCROLLUP = "KEY_SCROLLUP"
        self.KEY_SCROLLDOWN = "KEY_SCROLLDOWN"
        self.KEY_KPLEFTPAREN = "KEY_KPLEFTPAREN"
        self.KEY_KPRIGHTPAREN = "KEY_KPRIGHTPAREN"
        self.KEY_INTL1 = "KEY_INTL1"
        self.KEY_INTL2 = "KEY_INTL2"
        self.KEY_INTL3 = "KEY_INTL3"
        self.KEY_INTL4 = "KEY_INTL4"
        self.KEY_INTL5 = "KEY_INTL5"
        self.KEY_INTL6 = "KEY_INTL6"
        self.KEY_INTL7 = "KEY_INTL7"
        self.KEY_INTL8 = "KEY_INTL8"
        self.KEY_INTL9 = "KEY_INTL9"
        self.KEY_LANG1 = "KEY_LANG1"
        self.KEY_LANG2 = "KEY_LANG2"
        self.KEY_LANG3 = "KEY_LANG3"
        self.KEY_LANG4 = "KEY_LANG4"
        self.KEY_LANG5 = "KEY_LANG5"
        self.KEY_LANG6 = "KEY_LANG6"
        self.KEY_LANG7 = "KEY_LANG7"
        self.KEY_LANG8 = "KEY_LANG8"
        self.KEY_LANG9 = "KEY_LANG9"
        self.KEY_PLAYCD = "KEY_PLAYCD"
        self.KEY_PAUSECD = "KEY_PAUSECD"
        self.KEY_PROG3 = "KEY_PROG3"
        self.KEY_PROG4 = "KEY_PROG4"
        self.KEY_SUSPEND = "KEY_SUSPEND"
        self.KEY_CLOSE = "KEY_CLOSE"
        self.KEY_UNKNOWN = "KEY_UNKNOWN"
        self.KEY_BRIGHTNESSDOWN = "KEY_BRIGHTNESSDOWN"
        self.KEY_BRIGHTNESSUP = "KEY_BRIGHTNESSUP"

        # Add codes for standard buttons
        self.__codes = {}

        self.addCodes({self.KEY_SPACE: ' ',
                       self.KEY_MINUS: '-',
                       self.KEY_APOSTROPHE: "'",
                       self.KEY_DOT: '.',
                       self.KEY_TAB: '\t'})

        # Add all the numbers to the codes
        for num in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            self.addCode(getattr(self, "KEY_%s" % num.upper()), num)

        # Add all lowercase and uppercase letters to codes
        for key in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
                    'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
                    'w', 'x', 'y', 'z']:
            keyName = getattr(self, "KEY_%s" % key.upper())
            self.addCodes({keyName: key, (keyName, self.MOD_SHIFT): key})

        # Create a list of the modifiers
        self.modifiers = []
        for mod in ['CTRL', 'ALT', 'SHIFT', 'META']:
            left, right, _, _ = self.__get_modifiers_from_name(mod)
            self.modifiers.append(left)
            self.modifiers.append(right)

        self.__pressed_modifiers = []

        #define dictionary look up for key press cases
        self.__keyPressCases = {}

    def addKey(self, key, callback):
        '''Add a single key to the key press cases. The key can be a tuple
        where the first argument is the list of keys, or a single key, and the
        second argument is a list of modifiers. Optionally, is can just be
        a list of keys, or it can be a single key.

        '''
        # Get the combinations and code for this key
        combinations = self.__get_combinations_from_tuple(key)

        # Assign the code to all the combinations
        for selection in combinations:
            if self.__debug:
                print "Adding key:", selection
            self.__keyPressCases[selection] = callback

    def addKeys(self, keys):
        '''Add a key to the key press cases. The keys is a dictionary of
        keys. Each key in the dictionary is a normal tuple form of a key,
        and the value of the dictionary key is the callback method.

        '''
        for key in keys:
            self.addKey(key, keys[key])

    def addKeyList(self, keys, callback):
        '''Add a list of keys mapped to a single function. Keys can be a tuple
        where the first index the a list of keys, or a single key, and the
        second index is the list of modifiers. Or it can be a list of keys, and
        finally it can be just a single key.

        '''
        for key in keys:
            self.addKey(key, callback)

    def addCode(self, key, code):
        '''Add codes for given key press events. The key can be a tuple
        where the first index is a list of keys and the second index is a
        list of modifiers. Or it can be simply a list of keys, or it can
        be a single key.

        '''
        # Get the combinations and code for this key
        combinations = self.__get_combinations_from_tuple(key)

        # Assign the code to all the combinations
        for selection in combinations:
            if self.__debug:
                print "Assigning code: %s to %s" % (selection, code.__str__())
            self.__codes[selection] = code

    def addCodes(self, keys):
        '''Add codes for given key press events. Each key in the keys
        dictionary can be a tuple where the first index is a list of keys
        and the second index is a list of modifiers. Or it can be simply a
        list of keys, or it can be a single key.

        '''
        # Add codes for all the keys given
        for key in keys:
            self.addCode(key, keys[key])

    def handleKeyPress(self):
        '''Handle keys that are pressed.'''
        self.__dev.poll()

        processed = False
        buttons = self.__dev.buttons

        # Clear all the buttons that are zero from the dictionary
        for key in buttons.copy():
            if buttons[key] == 0:
                if key in self.modifiers:
                    self.__pressed_modifiers.remove(key)
                del buttons[key]

        # Traverse all the keys in the dictionary
        for key in buttons:
            if buttons[key] != 0 and key in self.modifiers:
                if key not in self.__pressed_modifiers:
                    self.__pressed_modifiers.append(key)

            modStr = self.__get_key_presses(buttons.copy(),
                                            copy(self.__pressed_modifiers))

            # Determine if there is a case for this key
            if not self.__applyAnyKey(modStr):
                if modStr in self.__keyPressCases:
                    self.__keyPressCases[modStr](self.__get_code(modStr))
                    processed = True

        # Clear all the buttons from the dictionary
        for key in buttons.copy():
            if key not in self.modifiers:
                del buttons[key]

        buttons.clear()
        return processed

    ##### Private Methods #####

    def __applyAnyKey(self, modStr):
        '''Determine if there is a mapping for KEY_ANY and if there
        is then use the callback.

        '''
        anyKey = "<%s>" % self.KEY_ANY
        if anyKey in self.__keyPressCases:
            self.__keyPressCases[anyKey](self.__get_code(modStr))
            return True
        else:
            return False

    def __replace_modifiers(self, name, modifiers):
        '''Replace any modifiers with their correct modifier keys.
        e.g. MOD_SHIFT_LEFT and MOD_SHIFT_RIGHT are replaced with
        MOD_SHIFT.

        '''
        left, right, both, any = self.__get_modifiers_from_name(name)

        # If any or both exists then remove left and right
        if any in modifiers or both in modifiers:
            # Remove left if it exists in the list
            # @todo: make remove all instances of left
            modifiers = filter(_NOT_FUNCTION(left), modifiers)

            # Remove right if it exists in the list
            modifiers = filter(_NOT_FUNCTION(right), modifiers)
        elif left in modifiers and right in modifiers:
            modifiers.remove(left)
            modifiers.remove(right)
            modifiers.append(both)

    def __replace_all_modifiers(self, modifiers):
        self.__replace_modifiers("CTRL", modifiers)
        self.__replace_modifiers("ALT", modifiers)
        self.__replace_modifiers("SHIFT", modifiers)
        self.__replace_modifiers("META", modifiers)

    def __check_modifier(self, mod, modifiers):
        if mod in modifiers:
            return "<%s>" % mod

    def __determine_keys(self, key):
        '''Get the list of keys based on a specific key.'''
        keys = []

        # Handle the alpha numeric case, and all other cases
        if key == self.KEY_ANY:
            keys.extend([self.KEY_ANY])
        elif key == self.KEY_ALPHA_NUMERIC:
            # Add all the numeric digits
            keys.extend([self.KEY_0, self.KEY_1, self.KEY_2, self.KEY_3,
                         self.KEY_4, self.KEY_4, self.KEY_6, self.KEY_7,
                         self.KEY_8, self.KEY_9])

            # Add all the lowercase, and uppercase alphabetic keys
            for key in [self.KEY_A, self.KEY_B, self.KEY_C, self.KEY_D,
                        self.KEY_E, self.KEY_F, self.KEY_G, self.KEY_H,
                        self.KEY_I, self.KEY_J, self.KEY_K, self.KEY_L,
                        self.KEY_M, self.KEY_N, self.KEY_O, self.KEY_P,
                        self.KEY_Q, self.KEY_R, self.KEY_S, self.KEY_T,
                        self.KEY_U, self.KEY_V, self.KEY_W, self.KEY_X,
                        self.KEY_Y, self.KEY_Z]:
                # Add the lower case key, then add capital letters
                # with both left and right shift
                keys.append(key)
                keys.append(self.__combine_keys([self.MOD_LEFTSHIFT, key]))
                keys.append(self.__combine_keys([self.MOD_RIGHTSHIFT, key]))
        elif key == self.KEY_PUNCTUATION:
            # Add unshifted keys, and shifted keys
            marks = ['DOT', 'APOSTROPHE', 'COMMA', 'SEMICOLON', 'MINUS']

            # Add all the keys that do not require shift
            for key in marks:
                name = getattr(self, "KEY_%s" % key)
                keys.append(name)

            # Add all the keys that require shift to be pressed
            for key in marks:
                name = getattr(self, "KEY_%s" % key)
                keys.append(self.__combine_keys([self.MOD_LEFTSHIFT, name]))
                keys.append(self.__combine_keys([self.MOD_RIGHTSHIFT, name]))
        else:
            keys.append(key)

        return keys

    def __get_modifiers_from_name(self, name):
        left = getattr(self, "MOD_LEFT%s" % name)
        right = getattr(self, "MOD_RIGHT%s" % name)
        both = getattr(self, "MOD_LEFTRIGHT%s" % name)
        any = getattr(self, "MOD_%s" % name)

        return left, right, both, any

    def __get_modifiers(self, modifiers):
        '''Convert the list of modifier constants into a single string
        representing the modifier key combination.

        '''
        if type(modifiers) is type(str()):
            modifiers = [modifiers]

        if type(modifiers) is not type(list()):
            raise Exception("modifiers must be a list!")

        self.__replace_all_modifiers(modifiers)

        mods = ""
        for name in ["CTRL", "ALT", "SHIFT", "META"]:
            left, right, both, any = self.__get_modifiers_from_name(name)

            # Add the modifiers to the list correctly
            if any in modifiers:
                mods += self.__check_modifier(any, modifiers)
            elif both in modifiers:
                mods += self.__check_modifier(both, modifiers)
            else:
                # Add left and right to the list
                if left in modifiers:
                    mods += self.__check_modifier(left, modifiers)
                elif right in modifiers:
                    mods += self.__check_modifier(right, modifiers)

        return mods

    def __get_code(self, key):
        '''Get the code for the given key.'''
        if key in self.__codes:
            return self.__codes[key]
        else:
            return ''

    def __get_options(self, name, modifiers):
        '''Get the list of options that are present in the modifier
        list for the given modifier name.

        '''
        left, right, both, any = self.__get_modifiers_from_name(name)

        if any in modifiers:
            return [left, right]
        elif left in modifiers and right not in modifiers:
            return [left]
        elif right in modifiers and left not in modifiers:
            return [right]
        elif left in modifiers and right in modifiers or \
                both in modifiers:
            return [both]
        else:
            return [None]

    def __get_modifier_permutations(self, modifierList, modList, inMods=[]):
        '''Get all the permutations of modifiers present in the
        modifierList and return them as items in the modList.

        '''
        if len(modifierList) == 0:
            return

        modifiers = modifierList.pop()
        for mod in modifiers:
            mods = copy(inMods)

            if mod is not None:
                mods.append(mod)

            rest = self.__get_modifier_permutations(copy(modifierList),
                                                    modList, mods)
            if rest is None:
                modList.append(mods)

        return 1

    def __get_key_combinations(self, buttons, modifiers):
        '''Return the list of key combinations that are present in
        the buttons and list of modifiers.

        '''
        key = ""
        modList = []

        self.__replace_all_modifiers(modifiers)

        control = self.__get_options('CTRL', modifiers)
        alt = self.__get_options('ALT', modifiers)
        shift = self.__get_options('SHIFT', modifiers)
        meta = self.__get_options('META', modifiers)

        modList = []
        self.__get_modifier_permutations([control, alt, shift, meta], modList)

        modStrings = []
        for mods in modList:
            modStr = self.__get_modifiers(mods)

            # Add any other keys
            for key in buttons:
                realKeys = self.__determine_keys(key)
                strMod = copy(modStr)

                for rk in realKeys:
                    modStr = "%s<%s>" % (strMod, rk)
                    modStrings.append(modStr)

        return modStrings

    def __get_key_presses(self, buttons, modifiers):
        '''Get the string formatted for a key press.'''
        mods = self.__get_modifiers(modifiers)

        for key in buttons:
            mods += "<%s>" % key

        return mods

    def __get_keys_modifiers_from_tuple(self, key):
        '''Get the keys and modifiers for the given tuple.'''
        # Handle the different types of input
        if type(key) is type(tuple()):
            # Get the key codes and modifiers from the tuple
            keys = key[0]
            modifiers = key[1]

            # Force the key codes and modifiers to be lists
            keys = self.__force_list(keys)
            modifiers = self.__force_list(modifiers)
        elif type(key) is type(list()):
            # A list of keys, no modifiers
            keys = key
            modifiers = []
        elif type(key) is type(str()):
            # A single key, no modifiers
            keys = [key]
            modifiers = []
        else:
            raise Exception("Unknown type of key given. Must be a tuple, "
                            "list, or string")

        return keys, modifiers

    def __get_combinations_from_tuple(self, key):
        '''Get all the combinations of keys and modifiers for the
        given tuple.

        '''
        keys, modifiers = self.__get_keys_modifiers_from_tuple(key)

        # Grab the combinations for the key and modifiers
        return self.__get_key_combinations(keys, modifiers)

    def __combine_keys(self, keys):
        '''Combine all of the keys in the list to be a single key.'''
        return '><'.join(map(lambda val: str(val), keys))

    def __force_list(self, obj):
        '''Force the object to be a list of strings. If not fail.'''
        if type(obj) is type(str()):
            return [obj]

        # Ensure it is a list
        if type(obj) is not type(list()):
            raise Exception("Object must be a list!")

        return obj


if __name__ == '__main__':
    _KEYBOARD_DEVICE = "/dev/input/event3"
    ui = UserInput(_KEYBOARD_DEVICE)

    def stop(val):
        print "stop:", val

    ui.addCodes({(ui.KEY_SLASH, ui.MOD_SHIFT): '?',
                 (ui.KEY_1, ui.MOD_SHIFT): '!'})
    ui.addKeyList([ui.KEY_ALPHA_NUMERIC,
                   ui.KEY_PUNCTUATION,
                   (ui.KEY_SLASH, ui.MOD_SHIFT),
                   (ui.KEY_1, ui.MOD_SHIFT)], stop)

    try:
        while True:
            import time
            ui.handleKeyPress()
            time.sleep(0.01)
    except (KeyboardInterrupt, SystemExit):
        exit(0)
