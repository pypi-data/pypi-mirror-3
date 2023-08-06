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
'''The requests module contains classes pertaining to creating
various types of objects to handle HTTP requests.

'''
import re
from urllib import unquote
from BaseHTTPServer import BaseHTTPRequestHandler

from pyamp.util import getStackTrace
from pyamp.web.http.headers import Header
from pyamp.web.http.constants import StatusCodes, Keys

from pyamp.web.http.errorPages import NotFoundPage, InternalServerErrorPage


# @todo: I need a GOOD way of registering a single page to handle a series of
#        URLs...e.g., one page to handle /css/* URL requests...


class BaseRequestHandler(BaseHTTPRequestHandler):
    '''The BaseRequestHandler class provides the basic functionality that
    is shared among all HTTP request handlers.

    '''
    pageClasses = []
    '''The pageClasses property contains the list of :class:`Page` classes
    which this request handler is able to provide. The request handler will
    be able to return requests based on the configured list of URLs for each
    page, as well as any supported error codes each Page defines.

    '''

    __basePageClasses = [
        NotFoundPage,
        InternalServerErrorPage
        ]
    '''The basePageClasses property defines the default pages for the request
    handler. These Pages are overwritten by any Pages defined in the
    pageClasses property which have defined URLs or error codes that overlap
    with the Pages defined in this property.

    '''

    # @todo: somehow use a logger!

    @classmethod
    def initialize(cls, *args, **kwargs):
        '''Initialize the request handler.

        * args -- Additional arguments
        * kwargs -- Additional keyword arguments

        '''
        cls.__urlMap = {}
        cls.__urlPatternMap = {}
        cls.__errorCodeMap = {}

        # First set up the base pages, and then set up the child page classes.
        # This allows the child definable classes to override any overlapping
        # base pages
        cls.__setupPages(cls.__basePageClasses)
        cls.__setupPages(cls.pageClasses)

        # Print out information for debugging
        print "Loaded the following pages:"
        for url, page in cls.__urlMap.iteritems():
            print "    [%s]: %s" % (page.__name__, url)

        for errorCode, page in cls.__errorCodeMap.iteritems():
            print "    [%s]: %d" % (page.__name__, errorCode)

    def do_GET(self):
        '''Process a GET request.'''
        exception = None
        content = None

        # Get the path and the arguments for this request
        path, arguments = self.__getPathAndArguments()

        # Attemp to display the requested page
        page = self.__findPage(path)
        if page is not None:
            try:
                # Request the page with the path, and arguments
                content = page.get(self, path, arguments)
            except Exception, e:
                stackTrace = getStackTrace()
                self.logError("%s\n%s" % (stackTrace, e))
                exception = (StatusCodes.InternalServerError, stackTrace)

        if exception is None and content is None:
            exception = (StatusCodes.FileNotFound, "File not found")

        # Display an error page if an error was encountered
        if exception is not None:
            errorCode = exception[0]
            errorMessage = exception[1]

            page = self.__findErrorPage(errorCode)
            if page is not None:
                # Add the error message to the arguments for the error page
                arguments[Keys.ErrorMessage] = errorMessage

                content = page.get(self, path, arguments)
            else:
                self.logError("Unable to locate error page for [%s]" % \
                                  errorCode)

        if page is not None and content is not None:
            self.__sendResponse(page, content, exception)

    def do_POST(self):
        '''Process a POST request.'''
        # @todo: complete this function
        pass

    def logError(self, message):
        '''Log an error message.

        * message -- The message to log

        '''
        print "Error: %s" % message

    ##### Private functions #####

    @classmethod
    def __setupPages(cls, pageClasses):
        '''Set up the dictionaries which map URLs and error codes to
        the corresponding Pages that should be loaded for each.

        * pageClasses -- The list of page classes that should be used

        '''
        # Add each page to the dictionary mapping supported URLs to
        # the corresponding Page objects
        for page in pageClasses:
            if page.validatePage():
                # Add entries for all the URLs supported by the page
                for url in page.urls + page.getUrls():
                    cls.__urlMap[url] = page
                    cls.__urlPatternMap[re.compile(url)] = page

                # Add entries for all the error codes supported by the page
                for errorCode in page.errorCodes:
                    cls.__errorCodeMap[errorCode] = page
            else:
                # @todo
                raise Exception("[%s] Page failed to invalidate" % page.name)

    def __getPathAndArguments(self):
        '''Get the actual path name, and a dictionary of the arguments
        passed in the path.

        '''
        # Unquote the path to get rid of http encoding
        path = unquote(self.path)
        arguments = {}

        # Find the start of the URL arguments
        if path.find("?") != -1:
            path, strArguments = path.split("?")

            # Add each argument to the argument dictionary
            for argument in strArguments.split("&"):
                if argument.find("=") != -1:
                    name, value = argument.split("=")

                    # Note: Convert all argument names to lowercase
                    arguments[name.lower()] = value

        return path, arguments

    def __findPage(self, path):
        '''Find a page with the given path.

        * path -- The path for the page

        '''
        foundPage = None
        for pattern, page in self.__urlPatternMap.iteritems():
            if pattern.match(path) is not None:
                foundPage = page
                break

        return foundPage

    def __findErrorPage(self, errorCode):
        '''Find an error page with the given error code.

        * errorCode -- The error code for the page

        '''
        return self.__errorCodeMap.get(errorCode)

    def __sendResponse(self, page, content, exception):
        '''Send the response for the current request.

        * page -- The page to return
        * content -- The page content to return
        * exception -- The exception tuple (errorCode, errorMessage) or None

        '''
        statusCode = StatusCodes.OK if exception is None else exception[0]

        # Write the status code
        self.send_response(statusCode)

        # Write all of the page headers
        headers = [Header.contentType(page.contentType)]
        for header in [header for header in headers if header is not None]:
            self.send_header(header.getId(), header.getValue())
        self.end_headers()

        # Finally write the page data
        self.wfile.write(content)


class StoppableRequestHandler(BaseRequestHandler):
    '''The StoppableRequestHandler class provides an implementation of
    an HTTP request handler that handles the quit message send by a
    server when it is trying to stop itself.

    '''

    def do_QUIT(self):
        '''Handle a QUIT message.'''
        self.send_response(200)
        self.end_headers()
