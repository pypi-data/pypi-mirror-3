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
'''The server module contains various classes pertaining to
creating HTTP servers.

'''
import errno
import select
import httplib
from BaseHTTPServer import HTTPServer

from pyamp.processes import Thread
from pyamp.web.http.argument import Argument
from pyamp.exceptions import UndefinedFunctionError


class HttpServer(HTTPServer):
    '''Create a basic HTTP server.

    Example::

        from BaseHTTPServer import BaseHTTPRequestHandler


        class RequestHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                ''' '''
                print "GET:", self.path

        server = HttpServer(12345, RequestHandler)
        server.serve_forever()

    '''

    def __init__(self, port, requestHandlerClass, host=''):
        '''
        * port -- The port for the server
        * requestHandlerClass -- The class used to handle requests
        * host -- The host name for the server

        '''
        # Initialize the request handler
        requestHandlerClass.initialize()

        HTTPServer.__init__(self, (host, port), requestHandlerClass)


class HttpServerThread(Thread):
    '''The HttpServerThread class provides an implementation of an
    HttpServer that runs in its own thread.

    Example::

        from time import sleep

        from pyamp.web.http.requests import StoppableRequestHandler


        server = HttpServerThread(12345, StoppableRequestHandler)
        server.start()

        while True:
            try:
                sleep(0.1)
            except (KeyboardInterrupt, SystemExit):
                print "Stopping server!"
                server.shutdown()
                break

        print "Done."

    '''

    def __init__(self, port, requestHandlerClass, host=''):
        '''
        * port -- The port for the server
        * requestHandlerClass -- The class used to handle requests
        * host -- The host name for the server

        '''
        # Ensure that the request handler can handle the quit action
        if not hasattr(requestHandlerClass, "do_QUIT"):
            raise UndefinedFunctionError(requestHandlerClass, "do_QUIT")

        self.__host = host
        self.__port = port

        Thread.__init__(self)
        self.__server = HttpServer(port, requestHandlerClass, host)

    def onCycle(self, _i):
        '''Called once during every cycle of the thread.

        * _i -- The current cycle number

        '''
        while True:
            try:
                self.__server.handle_request()
                return
            except (OSError, select.error) as e:
                if e.args[0] != errno.EINTR:
                    raise

    def onShutdown(self):
        '''Called in the event that the Thread is shut down.'''
        # Send a QUIT message to the server to indicate that it should stop
        conn = httplib.HTTPConnection("%s:%d" % (self.__host, self.__port))
        conn.request("QUIT", "/")
        conn.getresponse()

    def onStop(self):
        '''Called in the event that the Thread is stopped.'''
        self.__server.socket.close()


if __name__ == '__main__':
    from time import sleep

    from pyamp.web.http import StoppableRequestHandler, StatusCodes, \
        HtmlPage, JsonPage

    class NotFoundPage(HtmlPage):
        '''Test not found page.'''
        errorCodes = [404]

        @classmethod
        def _getContent(cls, _requestHandler, path, _arguments):
            '''Returnt test content.'''
            return "I'm sorry, but we could not find: %s" % path

    class HtmlExample(HtmlPage):
        '''Test HTML page.'''
        urls = ["/index.html"]

        arguments = {
            "name": Argument(str, required=True),
            "age": Argument(int, required=False, default=123)
            }

        @classmethod
        def _getContent(cls, _requestHandler, _path, arguments):
            '''Return test content.'''
            name = arguments.get("name")
            age = arguments.get("age", 20)

            lines = [
                "Hello, %s, welcome to my <b>HTML</b> page!" % name,
                "Hello, you are <b>%d</b> years old!" % age,
                "<br>(Set your name with the 'name' argument)",
                     ]
            return "<br>".join(lines)

    class JsonExample(JsonPage):
        '''Test HTML page.'''
        urls = ["/json.html"]

        @classmethod
        def _getContent(cls, _requestHandler, _path, _arguments):
            '''Return test content.'''
            return {"key1": 1,
                    "key2": {"key3": False,
                             "key4": [1, 2, 3, 4]},
                    "key5": "value6"}

    class ExampleRequestHandler(StoppableRequestHandler):
        '''Test request handler.'''
        pageClasses = [
            HtmlExample,
            JsonExample,
            NotFoundPage
            ]

    server = HttpServerThread(12345, ExampleRequestHandler)
    server.start()

    while True:
        try:
            sleep(0.1)
        except (KeyboardInterrupt, SystemExit):
            print "Stopping!"
            server.shutdown()
            break

    print "Done!"
