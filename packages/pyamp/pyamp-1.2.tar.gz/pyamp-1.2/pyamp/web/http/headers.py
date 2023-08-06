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
'''The headers module contains a class which provides the ability
to create a specific HTTP header.

'''
import re

from pyamp.web.http.constants import OperatingSystems as OS
from pyamp.web.http.constants import HeaderIds, ContentTypes


class Header:
    '''The Header class provides the ability to create a specific
    HTTP header.

    '''
    def __init__(self, identifier, value):
        '''
        * identifier -- The header identifier
        * value -- The value for the header

        '''
        self.__id = identifier
        self.__value = value

    def getId(self):
        '''Get the ID for this header.'''
        return self.__id

    def getValue(self):
        '''Get the value for this header.'''
        return self.__value

    ##### Content type methods #####

    @classmethod
    def contentType(cls, contentType):
        '''Create a content type header.

        * contentType -- The type of content

        '''
        return Header(HeaderIds.ContentType, contentType)

    @classmethod
    def textHtmlContent(cls):
        '''Create an text/html content type header.'''
        return Header.contentType(ContentTypes.TextHtml)

    @classmethod
    def jsonContent(cls):
        '''Create a JSON content type header.'''
        return Header.contentType(ContentTypes.Json)

    ##### Location methods #####

    @classmethod
    def location(cls, location):
        '''Create a location header.

        * location -- The location

        '''
        return Header(HeaderIds.Location, location)

    ##### Methods for retreiving data from headers #####

    @classmethod
    def getOperatingSystem(cls, headers):
        '''Get the operating system from the given headers.

        * headers -- The headers

        '''
        osMatches = [
            (OS.Windows3_11, 'Win16'),
            (OS.Windows95, '(Windows 95)|(Win95)|(Windows_95)'),
            (OS.Windows98, '(Windows 98)|(Win98)'),
            (OS.Windows2000, '(Windows NT 5.0)|(Windows 2000)'),
            (OS.WindowsXP, '(Windows NT 5.1)|(Windows XP)'),
            (OS.WindowsServer2003, '(Windows NT 5.2)'),
            (OS.WindowsVista, '(Windows NT 6.0)'),
            (OS.Windows7, '(Windows NT 7.0)'),
            (OS.WindowsNT4, '(Windows NT 4.0)|(WinNT4.0)|(WinNT)|' \
                 '(Windows NT)'),
            (OS.WindowsME, 'Windows ME'),
            (OS.OpenBSD, 'OpenBSD'),
            (OS.SunOS, 'SunOS'),
            (OS.Linux, '(Linux)|(X11)'),
            (OS.MacOS, '(Mac_PowerPC)|(Macintosh)'),
            (OS.QNX, 'QNX'),
            (OS.BeOS, 'BeOS'),
            (OS.OS2, 'OS/2'),
            (OS.SearchBot, '(nuhk)|(Googlebot)|(Yammybot)|(Openbot)|(Slurp)' \
                 '|(MSNBot)|(Ask Jeeves/Teoma)|(ia_archiver)')
            ]

        userAgent = headers.getheader(HeaderIds.UserAgent)

        # Traverse all of the operating system types and determine if
        # any of them are found within the user agent string
        for (system, matchText) in osMatches:
            regex = re.compile(matchText)
            if regex.search(userAgent):
                return system
