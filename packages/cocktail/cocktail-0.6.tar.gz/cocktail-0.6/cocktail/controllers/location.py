#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from __future__ import with_statement
from cgi import parse_qs
from urllib import urlencode
from urlparse import urlparse
import cherrypy
from cocktail.modeling import getter
from cocktail.translations import translations, get_language, language_context
from cocktail.controllers.uriutils import try_decode, percent_encode_uri
from cocktail.controllers.viewstate import get_state
from cocktail.controllers.dispatcher import StopRequest


class Location(object):

    method = "GET"
    scheme = "http"
    host = "localhost"
    port = None
    path_info = "/"
    query_string = None
    form_data = None
    relative = False

    def __init__(self, url = None):
        self.query_string = {}
        self.form_data = {}

        if url:
            parts = urlparse(url)
            self.scheme = parts.scheme
            self.host = parts.hostname
            self.port = parts.port
            self.path_info = parts.path
            self.query_string = parse_qs(parts.query)

    @classmethod
    def get_current_host(cls):

        location = cls()
        location.method = "GET"
        
        headers = cherrypy.request.headers
        base = cherrypy.request.base

        if base:
            scheme, rest = base.split("://")
            location.scheme = headers.get('X-Forwarded-Scheme') or scheme
            pos = rest.find(":")
            if pos == -1:
                location.host = rest
            else:
                location.host = rest[:pos]
                location.port = rest[pos+1:]

        elif cherrypy.server.socket_host:
            location.scheme = headers.get('X-Forwarded-Scheme', 'http')
            location.host = cherrypy.server.socket_host
            port = cherrypy.server.socket_port
            if port:
                default_ports = {"http": 80, "https": 443}
                if port != default_ports.get(location.scheme):
                    location.port = port

        return location

    @classmethod
    def get_current(cls, relative = True):
        
        request = cherrypy.request
        query_string = get_state()

        location = cls.get_current_host()
        location.relative = relative
        location.method = request.method
        location.path_info = try_decode(request.path_info)        
        location.query_string.update(query_string)
        location.form_data.update(
            (key, value)
            for key, value in request.params.iteritems()
            if key not in query_string
        )

        return location

    def join_path(self, *args):
        
        parts = [self.path_info]
        parts.extend(args)

        self.path_info = "/" + "/".join(
            unicode(part).strip("/")
            for part in parts
        )

    def pop_path(self):
        steps = self.path_info.strip("/").split("/")
        step = steps.pop()
        self.path_info = "/" + "/".join(steps)
        return step

    def __unicode__(self):

        if self.relative or self.host is None:
            url = u""
        else:
            url = self.scheme + u"://" + self.host

            if self.port:
                url += u":" + unicode(self.port)

        url += percent_encode_uri(self.path_info)

        if self.query_string:
            url += u"?" + urlencode(self.query_string, True)

        return url

    def __str__(self):
        return unicode(self).encode("utf-8")

    @getter
    def params(self):
        if self.method == "GET":
            return self.query_string
        else:
            return self.form_data
    
    def go(self, method = None):
        method = method or self.method
        if method == "POST":
            cherrypy.response.status = 200
            cherrypy.response.body = self.get_form()
            raise StopRequest()
        else:
            raise cherrypy.HTTPRedirect(str(self))

    def get_form(self):
        with language_context(get_language() or "en"):
            return """
    <html>	
        <head>
            <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
            <title>%(title)s</title>
            <script type="text/javascript">
                <!--
                onload = function () {
                    try {
                        var form = document.getElementById("redirectionForm");
                        form.submit();
                    }
                    catch (ex) {}
                }
                //-->
            </script>
        </head>
        
        <body>
            <p>
                %(explanation)s
            </p>
            <form id="redirectionForm" method="%(method)s" action="%(action)s">
                %(data)s
                <input type="submit" value="%(button)s">
            </form>
        </body>

    </html>
                """ % {
                    "title": translations("Redirecting"),
                    "explanation": translations("Redirection explanation"),
                    "method": self.method,
                    "action": str(self),
                    "data": "\n".join(
                        """<input type="hidden" name="%s" value="%s">"""
                        % (key, value)
                        for key, value in self.form_data.iteritems()
                    ),
                    "button": translations("Redirection button")
                }

    @classmethod
    def require_http(cls):
        location = cls.get_current(relative = False)
        if location.scheme != "http":
            location.scheme = "http"
            location.go()

    @classmethod
    def require_https(cls):
        location = cls.get_current(relative = False)
        if location.scheme != "https":
            location.scheme = "https"
            location.go()

