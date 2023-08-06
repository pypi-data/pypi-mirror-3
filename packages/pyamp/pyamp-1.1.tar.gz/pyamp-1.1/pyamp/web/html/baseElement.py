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
''' '''
from pyamp.util import filterNone


class CloseTagType:
    NoTag = "NoCloseTag"
    Separate = "SeparateCloseTag"
    Joined = "JoinedCloseTag"


class BaseHtmlElement:
    name = None
    closeTagType = CloseTagType.Separate

    def __init__(self, properties=None, elements=None):
        ''' '''
        self.__properties = {} if properties is None else properties
        self.__elements = [] if elements is None else elements

    def toHtml(self, spacing=""):
        ''' '''
        lines = []

        start = self.__getStartTag(spacing)
        subElements = self.__getSubElements(spacing + "    ") 
        end = self.__getEndTag(spacing)

        if len(subElements) > 0:
            lines.append(start)
            lines.extend(subElements)

            if end is not None:
                lines.append(end)
        else:
            end = "" if end is None else end
            lines.append(start + end.strip())

        lines = filterNone(lines)
        return '\n'.join(lines)

    def __getStartTag(self, spacing):
        ''' '''
        isNotJoined = self.closeTagType != CloseTagType.Joined
        endTag = None if isNotJoined else "/"
        parts = [self.name, self.__getProperties(), endTag]

        # Filter out any values that are None
        parts = filterNone(parts)

        return "%s<%s>" % (spacing, " ".join(parts))

    def __getProperties(self):
        ''' '''
        properties = []

        for key, value in self.__properties.iteritems():
            if value is not None:
                propStr = "%s='%s'" % (key, value)
            else:
                propStr = "%s" % key

            properties.append(propStr)

        if len(properties) > 0:
            properties = ' '.join(properties)
        else:
            properties = None

        return properties

    def __getSubElements(self, spacing):
        ''' '''
        return [el.toHtml(spacing) for el in self.__elements]

    def __getEndTag(self, spacing):
        ''' '''
        closeTag = "%s</%s>" % (spacing, self.name)

        isSeparate = self.closeTagType == CloseTagType.Separate
        return None if not isSeparate else closeTag


class HtmlFiveDoctype(BaseHtmlElement):
    name = "!DOCTYPE"
    closeTagType = CloseTagType.NoTag

    def __init__(self):
        ''' '''
        properties = {'html': None}
        BaseHtmlElement.__init__(self, properties)


class Div(BaseHtmlElement):
    name = "div"


class Html(BaseHtmlElement):
    name = "html"


class Title(BaseHtmlElement):
    name = "title"

    def __init__(self, title):
        ''' '''
        properties = {'title': title}
        BaseHtmlElement.__init__(self, properties)


class Head(BaseHtmlElement):
    name = "head"


class Body(BaseHtmlElement):
    name = "body"


class Text(BaseHtmlElement):
    name = None

    def __init__(self, content):
        ''' '''
        self._content = content
        BaseHtmlElement.__init__(self)

    def toHtml(self, spacing=''):
        ''' '''
        return "%s%s" % (spacing, self._content)


class Anchor(BaseHtmlElement):
    name = "a"

    def __init__(self, href=None, properties=None, elements=None):
        ''' '''
        properties = {} if properties is None else properties

        if href is not None:
            properties['href'] = href

        BaseHtmlElement.__init__(self, properties, elements)


class Image(BaseHtmlElement):
    name = "img"
    closeTagType = CloseTagType.Joined

    def __init__(self, src=None, properties=None, elements=None):
        ''' '''
        properties = {} if properties is None else properties

        if src is not None:
            properties['src'] = src

        BaseHtmlElement.__init__(self, properties, elements)


class Script(BaseHtmlElement):
    name = "script"

    def __init__(self, src):
        ''' '''
        properties = {'src': src}
        BaseHtmlElement.__init__(self, properties)


class Link(BaseHtmlElement):
    name = "link"
    closeTagType = CloseTagType.Joined

    def __init__(self, href, rel, linkType):
        properties = {
            'href': href,
            'rel': rel,
            'type': linkType
            }

        BaseHtmlElement.__init__(self, properties)


class CssLink(Link):
    name = "link"

    def __init__(self, href):
        ''' '''
        link.__init__(self, href, "stylesheet", "text/css")


if __name__ == '__main__':
    img = image("http://www.google.com/images/whatever.jpg")
    content = text("Google")
    link = anchor(href="http://www.google.com", elements=[img, content])
    b = div({"class": "hello"}, elements=[link])
    c = div(elements=[b])
    d = div({'id': "thisismyid"}, elements=[c])
    print d.toHtml()
