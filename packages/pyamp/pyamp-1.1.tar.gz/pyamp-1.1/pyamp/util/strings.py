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
'''Contains utility methods pertaining to strings.'''


__all__ = ["levenshtein"]


def levenshtein(str1, str2, case=True):
    '''Calculate the Levenshtein distance between two strings.

    * str1 -- The first string
    * str2 -- The second string
    * case -- True for case sensitivity, False otherwise

    '''
    # If case insensitive compare, then make both strings lowercase
    if not case:
        str1 = str1.lower()
        str2 = str2.lower()

    len1, len2 = len(str1), len(str2)

    # Make sure n <= m, to use O(min(n,m)) space
    if len1 > len2:
        # Swap the strings, and lengths
        str1, str2 = str2, str1
        len1, len2 = len2, len1

    current = range(len1 + 1)
    for i in range(1, len2 + 1):
        previous, current = current, [i] + [0] * len1

        for j in range(1, len1 + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]

            if str1[j - 1] != str2[i - 1]:
                change = change + 1

            current[j] = min(add, delete, change)

    return current[len1]
