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
'''The constants module contains classes which define constants relating
to HTTP data.

'''


class HeaderIds:
    '''The HeaderIds class contains constants pertaining to header
    identifiers.

    '''
    # @todo: define the rest of the header ids

    ContentType = "Content-Type"
    '''The content type header id.'''

    Location = "Location"
    '''The location header id.'''

    UserAgent = "User-Agent"
    '''The user agent header id.'''


class StatusCodes:
    '''The StatusCodes class contains constants pertaining to
    HTTP status codes.

    '''
    # @todo: add the rest of the status codes
    # http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
    OK = 202
    '''The OK status code.'''

    MovedPermanently = 301
    '''The moved permanently status code.'''

    Found = 302
    '''The found status code.'''

    FileNotFound = 404
    '''The file not found status code.'''

    InternalServerError = 500
    '''The internal server error status code.'''


class ContentTypes:
    '''The ContentTypes class contains constants pertaining to
    different types of content.

    '''
    Bmp = "image/bmp"
    '''A BMP image content.'''

    Gif = "image/png"
    '''A GIF image content.'''

    Ico = "image/ico"
    '''An ICO image content.'''

    Png = "image/png"
    '''An PNG image content.'''

    TextHtml = "text/html"
    '''Standard text HTML content.'''

    Json = "application/json"
    '''JSON content.'''

    Css = "text/css"
    '''CSS content.'''

    JavaScript = "text/javascript"
    '''JavaScript content.'''


class OperatingSystems:
    '''The OperatingSystems class contains constants pertaining to
    the strings used to identify various operating systems.

    '''
    Windows3_11 = "Windows 3.11"
    '''The Windows 3.11 OS.'''

    Windows95 = "Windows 95"
    '''The Windows 95 OS.'''

    Windows98 = "Windows 98"
    '''The Windows 98 OS.'''

    Windows2000 = "Windows 2000"
    '''The Windows 2000 OS.'''

    WindowsXP = "Windows XP"
    '''The Windows XP OS.'''

    WindowsServer2003 = "Windows Server 2003"
    '''The Windows Server 2003 OS.'''

    WindowsVista = "Windows Vista"
    '''The Windows Vista OS.'''

    Windows7 = "Windows 7"
    '''The Windows 7 OS.'''

    WindowsNT4 = "Windows NT 4.0"
    '''The Windows NT 4.0 OS.'''

    WindowsME = "Windows ME"
    '''The Windows ME OS.'''

    OpenBSD = "Open BSD"
    '''The OpenBSD OS.'''

    SunOS = "Sun OS"
    '''The Sun OS OS.'''

    Linux = "Linux"
    '''The Linux OS.'''

    MacOS = "Mac OS"
    '''The Mac OS.'''

    QNX = "QNX"
    '''The QNX OS.'''

    BeOS = "BeOS"
    '''The BeOS OS.'''

    OS2 = "OS/2"
    '''The OS/2 OS.'''

    SearchBot = "Search Bot"
    '''The SearchBot OS.'''


class Keys:
    '''The Keys class defines constants that are used as keys to
    access certain dictionary values.

    '''

    ErrorMessage = "errorMessage"
    '''The key for the entry containing the error message.'''
