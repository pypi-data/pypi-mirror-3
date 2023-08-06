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
'''The coroutine module contains methods pertaining to creating
coroutines.

'''


def coroutine(func):
    '''Decorator to create a coroutine and call next on it.

    * function -- The function to decorate

    '''
    def start(*args, **kwargs):
        '''Start the coroutine.

        * args -- The arguments
        * kwargs -- The keyword arguments

        '''
        cr = func(*args, **kwargs)
        cr.next()

        return cr

    return start
