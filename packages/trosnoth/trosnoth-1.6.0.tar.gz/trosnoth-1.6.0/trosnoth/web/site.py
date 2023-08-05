# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2011 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import uuid

from twisted.web import server, resource
from twisted.internet import defer

class PageSet(object):
    def __init__(self):
        self.pages = {}

    def addPage(self, url, allOrigins=False):
        def pagefn(fn):
            fn._allOrigins = allOrigins
            self.pages[url] = fn
            return fn
        return pagefn

class ServerState(object):
    def __init__(self, pageSet):
        self.uuid = uuid.uuid4()
        self.pageSet = pageSet
        self.site = self._createSite()

    def _createSite(self):
        resources = Resources(self)
        return server.Site(resources)

class Resources(resource.Resource):
    isLeaf = True

    def __init__(self, state):
        resource.Resource.__init__(self)
        self.state = state
        self.pageSet = state.pageSet

    def render_POST(self, request):
        return self.render_GET(request)

    def render_GET(self, request):
        try:
            page = self.pageSet.pages[request.path]
        except KeyError:
            request.setResponseCode(404)
            return '<html><body><h1>Not found</h1></body></html>'

        if hasattr(page, '_allOrigins') and page._allOrigins:
            request.setHeader('Access-Control-Allow-Origin', '*')

        d = page(self.state, request)
        if isinstance(d, defer.Deferred):
            d.addCallback(self._requestComplete, request)
            return server.NOT_DONE_YET
        d = self._setRequestCharset(request, d)
        return d

    def _requestComplete(self, result, request):
        if result:
            result = self._setRequestCharset(request, result)
            request.write(result)
        request.finish()

    def _setRequestCharset(self, request, contents):
        if isinstance(contents, str):
            return contents
        assert isinstance(contents, unicode)

        for value in request.responseHeaders.getRawHeaders('Content-Type'):
            if value.startswith('text/'):
                break
        else:
            raise TypeError('Cannot set encoding of non-text document')
        request.responseHeaders.addRawHeader('Content-Type', 'charset=utf-8')
        contents = contents.encode('utf-8')
        return contents

class Template(object):
    def __init__(self, string, defaults):
        self.string = string
        self.defaults = defaults

    def apply(self, **args):
        d = dict(self.defaults)
        d.update(args)
        return self.string % d
