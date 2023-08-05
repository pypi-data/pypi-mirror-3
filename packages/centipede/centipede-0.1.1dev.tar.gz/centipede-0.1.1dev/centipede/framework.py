##
#                  ,           /)   
#   _   _ __  _/_   __    _  _(/  _ 
#  (___(/_/ (_(___(_/_)__(/_(_(__(/_
#                .-/                
#               (_/     
#
#  http://code.google.com/p/centipede/
#  Understanding & simplicity
#  Copyright 2010, Asbjorn Enge. All rights reserved.
#
#  LICENSE.txt
#
##
#
#  The expose decorator is inspired by the bespin project.
#  http://mozillalabs.com/bespin/
#
##
#
#  Framework
#
##

from webob import Request, Response
from urlrelay import url, URLRelay
from static import Cling

## Expose urls
#

def expose(url_pattern, method=None, content_type='text/html', charset='UTF-8', auth=True, skip_token_check=False, profile=False):
    """Expose this function to the world, matching the given URL pattern
    and, optionally, HTTP method."""
    def entangle(func):
        @url(url_pattern, method)
        def wrapped(environ, start_response):

            request = Request(environ)
            response = Response()
                
            start_response('200 OK', [('Content-type', '%s; charset=%s' % (content_type, charset))])

            return [func(request, response)]

    return entangle

## Make the application
#

def app(static=None):
    """ Return wsgi app
    """
    if static != None:
        static = Cling(static)
        app = URLRelay(default=static_app)
    else:
        app = URLRelay()
    return app

