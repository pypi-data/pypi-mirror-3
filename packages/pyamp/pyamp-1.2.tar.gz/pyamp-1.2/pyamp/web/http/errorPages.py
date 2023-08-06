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
'''The errorPages class defined various error pages which are used
in the request handler to provide data in the event of specific errors.

'''
from pyamp.util import html
from pyamp.web.http.page import HtmlPage
from pyamp.web.http.constants import StatusCodes, Keys


class NotFoundPage(HtmlPage):
    '''The NotFoundPage is displayed in the event that a requested page was
    not found.

    '''
    errorCodes = [StatusCodes.FileNotFound]
    '''Define the list of error codes which will display this page.'''

    @classmethod
    def _getContent(cls, _requestHandler, path, _arguments):
        '''Get the content for this Page.

        * _requestHandler -- The request handler object
        * path -- The requested path
        * _arguments -- The dictionary of arguments passed in the request

        '''
        return "Could not find <b>%s</b>!" % path


class InternalServerErrorPage(HtmlPage):
    '''The InternalServerErrorPage is displayed in the event that an
    internal server error is encountered during processing. It provides
    the ability to display the encountered error to the user.

    '''
    errorCodes = [StatusCodes.InternalServerError]
    '''Define the list of error codes which will display this page.'''

    @classmethod
    def _getContent(cls, _requestHandler, path, arguments):
        '''Get the content for this Page.

        * _requestHandler -- The request handler object
        * path -- The requested path
        * arguments -- The dictionary of arguments passed in the request

        '''
        # Grab the error message from the arguments
        errorMessage = arguments.get(Keys.ErrorMessage, "--Unknown error--")

        # Create the lines that will be displayed to the user
        lines = [
            "Encountered the following error in request for [%s]:" % path,
            "",
            errorMessage
            ]

        return html.lineBreaks(lines)
