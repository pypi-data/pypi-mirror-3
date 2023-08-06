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
'''The web module provides classes, and functions which provide
various functionality respective to websites.

'''
import urllib2

from pyamp.util import getStackTrace


__all__ = ["UrlRequest"]


class UrlRequest:
    '''The UrlRequest provides methods for requesting webpages.'''

    @classmethod
    def request(cls, url):
        '''Request a page.'''
        try:
            urllib2.urlopen(url)
            return True
        except urllib2.HTTPError:
            return False

    @classmethod
    def get(cls, url):
        '''Get the content of a page.'''
        try:
            pagehandle = urllib2.urlopen(url)
            content = pagehandle.read()
            pagehandle.close()
            return content
        except urllib2.HTTPError:
            print getStackTrace()

        return None

    @classmethod
    def authenticate(cls, username, password, url):
        '''Request a page that requires authentication.'''
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, url, username, password)

        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        urllib2.install_opener(urllib2.build_opener(authhandler))

        try:
            urllib2.urlopen(url)
            return True
        except urllib2.HTTPError:
            return False
