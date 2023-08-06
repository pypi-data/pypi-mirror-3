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
'''Contains the Hacking class which provides functions pertaining
to hacking web sites.

'''
from os.path import exists, join

from pyamp.web import UrlRequest


__all__ = ["Hacking"]


class Hacking:
    '''Contains methods pertaining to Hacking.'''

    @classmethod
    def findAdminPage(cls, baseUrl, adminFile=None):
        '''Attempt to find an admin page for a website using
        the configured list of possible admin names.

        * baseUrl - The base URL to look for an admin page
        * adminFile - The list of possible admin names
        '''
        if adminFile is None:
            adminFile = join("/usr", "local", "pyamp", "files", "admin.txt")

        # Ensure the admin file exists
        if exists(adminFile):
            attempts = file(adminFile).read().split("\n")
            for attempt in attempts:
                url = "%s/%s" % (baseUrl.rstrip("/"), attempt.strip("/"))

                # If the request works, we found the admin page
                if UrlRequest.request(url):
                    return url

        # No admin page was found
        return None
