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
'''The page module contains the definition of the BasePage class
which provides the base functionality for implementing a page that
can be served by an HTTP server.

This module also contains other classes for defining various types
of pages.

'''
import json
from os.path import join, basename

from pyamp.util import splitList
from pyamp.web.http.headers import Header
from pyamp.web.http.argument import Argument
from pyamp.patterns import RequiredProperties
from pyamp.exceptions import UndefinedPropertyError, UndefinedFunctionError


class BasePage(RequiredProperties):
    '''The BasePage class contains the basic functionality that is shared
    among all pages.

    '''

    urls = []
    '''The urls property defines the list of URLs that can be used to request
    this Page.

    .. note:: These URLs should all start with a forward slash.

    Example::

        urls = ['/index.html', /test/directory/main.html']

    '''

    errorCodes = []
    '''The errorCodes property defines the list of error codes that will
    respond with this Page in the event that any of the error codes are
    encountered.

    '''

    contentType = None
    '''The contentType property contains the type of content contained
    in this Page.

    '''

    arguments = {}
    '''The arguments class defines a dictionary mapping names of arguments
    to actual Argument objects that this Page accepts. These can be required,
    or optional arguments. This provides the ability to perform error
    checking on the request to the page to determine if the correct number of
    arguments was passed in the request.

    '''

    _requiredProperties = []
    '''The requiredProperties property allows concrete Pages to specify
    additional properties that will be required to be defined.

    '''

    __baseRequiredProperties = ["contentType"]
    '''The list of properties that are required to be defined for all pages.'''

    @classmethod
    def validatePage(cls):
        '''Validate all of the properties for this page.

        Return True to indicate success, False to indicate failure

        '''
        # Ensure that all of the required properties are defined, including
        # the base and subclass required properties
        cls._RequiredProperties = cls.__baseRequiredProperties + \
            cls._requiredProperties
        RequiredProperties.checkRequiredProperties(cls)

        # Add other validation procedures here

        return True

    @classmethod
    def get(cls, requestHandler, path, arguments):
        '''Get the page.

        * requestHandler -- The request handler object
        * path -- The requested path
        * arguments -- The request arguments dictionary

        '''
        cls._validateArguments(arguments)

        return cls._getContent(requestHandler, path, arguments)

    @classmethod
    def getUrls(cls):
        '''Get a list of URLs which this Page supports. These URLs are used
        in conjunction with the :attr:`urls` class property.

        .. note:: This function should be overridden by concrete Pages to
                  provide a set of dynamically configured URLs.

        '''
        return []

    @classmethod
    def _getContent(cls, _requestHandler, _path, _arguments):
        '''Get the content for the Page.

        * _requestHandler -- The request handler object
        * _path -- The requested path
        * _arguments -- The request arguments dictionary

        '''
        raise UndefinedFunctionError(cls, "_getContent")

    @classmethod
    def _validateArguments(cls, arguments):
        '''Validate the arguments passed in the request for this Page.
        This ensures that all required arguments are given, and that all
        arguments (required, and optional) are the expected types.

        * arguments -- The dictionary of arguments passed in the request

        '''
        required, optional = splitList(cls.arguments.items(),
                                       lambda tup: tup[1].isRequired())

        # Determine the required and optional arguments that are missing
        missingReq = [arg[0] for arg in required if arg[0] not in arguments]
        missingOpt = [arg for arg in optional if arg[0] not in arguments]

        if len(missingReq) > 0:
            # @todo: Use amp exception class
            missingStr = ', '.join(missingReq)
            raise Exception("[%s] is missing the following required " \
                                "arguments: %s" % (cls.__name__, missingStr))

        # Set the default value for all the missing optional arguments
        for name, argument in missingOpt:
            arguments[name] = argument.getDefaultValue()

        # Convert the value for all of the provided arguments
        for name, value in arguments.iteritems():
            argument = cls.arguments.get(name)
            if argument is not None:
                arguments[name] = argument.convertValue(value)


class HtmlPage(BasePage):
    '''The HtmlPage class provides a base class that returns
    a page containing text/html content.

    '''

    contentType = Header.textHtmlContent()
    '''Define the content type for the HtmlPage.'''


class JsonPage(BasePage):
    '''The HtmlPage class provides a base class that returns
    a page containing JSON content.

    '''

    contentType = Header.jsonContent()
    '''Define the content type for the JsonPage.'''

    @classmethod
    def get(cls, requestHandler, path, arguments):
        '''Override the get method to return JSON data.

        * requestHandler -- The request handler object
        * path -- The requested path
        * arguments -- The request arguments dictionary

        '''
        cls._validateArguments(arguments)

        content = cls._getContent(requestHandler, path, arguments)
        return json.dumps(content)


class FilePage(BasePage):
    '''The FilePage class implements a :class:`.BasePage` object which provides
    the ability for pages to return the content of a file.

    '''

    @classmethod
    def _getContent(cls, _requestHandler, path, _arguments):
        '''Get the content for the Page.

        * _requestHandler -- The request handler object
        * path -- The requested path
        * _arguments -- The request arguments dictionary

        '''
        # @todo: Error if file does not exist
        fd = file(cls._getFilename(path), 'r')
        contents = fd.read()
        fd.close()

        return contents

    @classmethod
    def _getFilename(cls, _path):
        '''Get the filename to return for this page.

        * _path -- The requested path

        '''
        return None


class DirectoryFilesPage(FilePage):
    '''The DirectoryFilesPage class provides an implementation of a FilePage
    which provides the ability to return any file contained within a specific
    directory.

    This class allows the path to the locally stored files to be defined, as
    well as the HTML directory where the files are located. This class also
    provides the ability to define a set of extensions used to filter the
    files returned. Any file that has an extension that is contained within
    the list of supported extensions will be requested using this Page.

    '''

    directoryPath = None
    '''The path to the locally stored files that this Page will return.'''

    htmlDirectory = None
    '''The HTML directory name where the files are stored. This is also the
    path that will be prefixed to all requests for these pages.


    '''

    extensions = None
    '''The list of extensions used to filter files that are returned.'''

    _requiredProperies = ["directoryPath", "htmlDirectory"]
    '''Define the list of required properties for this class.'''

    @classmethod
    def getUrls(cls):
        '''Get a list of URLs which this Page supports. These URLs are used
        in conjunction with the :attr:`urls` class property.

        '''
        return [join(cls.htmlDirectory, ".*\.%s" % cls.__getExtensions())]

    @classmethod
    def _getFilename(cls, path):
        '''Get the filename to return for this page.

        * _path -- The requested path

        '''
        return join(cls.directoryPath, basename(path))

    @classmethod
    def __getExtensions(cls):
        '''Get the regular expression to match all of the configured
        extensions.

        '''
        return "(%s)" % '|'.join(cls.extensions)
