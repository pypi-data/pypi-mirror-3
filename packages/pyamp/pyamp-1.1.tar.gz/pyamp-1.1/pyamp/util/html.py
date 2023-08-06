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
'''The http module contains utility methods for use with HTML data.'''


def lineBreaks(html):
    '''Replace new line characters with HTML line breaks.

    * html -- Either an HTML string that should have new line characters
              replaced with line breaks, or a list which should have element
              in the list joined by HTML line breaks

    '''
    # If it is a list, join the list with HTML line breaks, otherwise replace
    # new line characters with line breaks
    if type(html) is type(list()):
        # Substitute HTML line breaks for each item in the list
        output = '</BR>'.join([lineBreaks(item) for item in html])
    else:
        output = html.replace("\n", "</BR>")

    return output
