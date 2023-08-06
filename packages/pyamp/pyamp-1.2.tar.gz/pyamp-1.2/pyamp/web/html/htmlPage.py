# Copyright 2012 Brett Ponsler
# This file is part of pyamp.#

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
''' '''
from pyamp.web.html.baseElement import CssLink, Body, Head, Script, \
    Html, HtmlFiveDoctype, Title


class HtmlPage:

    def __init__(self, title, bodyElements=None):
        ''' '''
        self.__title = title
        self.__cssDependencies = []
        self.__jsDependencies = []
        self.__bodyElements = [] if bodyElements is None else bodyElements

    def addCssDependency(self, cssPath):
        ''' '''
        self.__cssDependencies.append(cssPath)

    def addJavaScriptDependency(self, jsPath):
        ''' '''
        self.__jsDependencies.append(jsPath)

    def addElement(self, element):
        ''' '''
        self.__bodyElements.append(element)

    def toHtml(self):
        ''' '''
        elements = [
            self.__getDocType(),
            self.__getHtmlElement(),
            ]

        return '\n'.join([element.toHtml() for element in elements])

    def __getDocType(self):
        ''' '''
        return HtmlFiveDoctype()

    def __getHtmlElement(self):
        ''' '''
        elements = [
            self.__getHeader(),
            self.__getBody()
            ]

        return Html(elements=elements)

    def __getHeader(self):
        elements = [
            self.__getTitle()
            ]

        # Add all of the CSS files
        for cssFile in self.__cssDependencies:
            elements.append(CssLink(href=cssFile))

        # Add all of the JavaScript files
        for jsFile in self.__jsDependencies:
            script = Script(src=jsFile)
            elements.append(script)

        return Head(elements=elements)

    def __getTitle(self):
        ''' '''
        return Title(self.__title)

    def __getBody(self):
        return Body(elements=self.__bodyElements)


if __name__ == '__main__':
    from pyamp.web.html.baseElement import Div, Anchor, Text

    content = Text("Google")
    anchor = Anchor("http://www.google.com", elements=[content])
    div = Div(elements=[anchor])
    bodyElements = [div]

    html = HtmlPage("This is the title of the page.",
                    bodyElements=bodyElements)

    print html.toHtml()
