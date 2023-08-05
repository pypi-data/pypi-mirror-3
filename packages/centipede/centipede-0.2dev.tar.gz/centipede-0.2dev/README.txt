=========
Centipede
=========
v0.2dev

Centipede is a WSGI microframework with a simple decorator based router. It's strength is that it models the technology in use and tries not to confuse developers with complex patterns and tricks. It inherits strongly from urlrelay.

Installation
============
::

    $ pip install centipede

Defining handlers
=================
With Centipede you expose functions to urls. Functions either return a string or a tuple. A string is treated as the document body, http status code is set to 200 OK and returned to the browser. Should you return a tuple, status_code, body and headers are expected. The expose decorator also takes a few arguments.

::

    from centipede import expose, app

    @expose('^/$')
    def index(request, response):
        """ Simple Hello IgglePigglePartyPants
        """
        return 'Hello IgglePigglePartyPants!'

    @expose('^/google$')
    def index(request, response):
        """ A redirect
        """
        return (307, '', {'Location':'http://google.com'})
 
    import json
 
    @expose('^/twitter$', 'GET', content_type='application/json')
    def twitter(request, response):
        """ Return your twitter status
        """
        return json.dumps({
            'status' : 'My awesome and insightful twitter status. #blah'
        })
    
    application = app()

Expose arguments
================
The expose decorator looks like this::

    def expose(url_pattern, method=None, content_type='text/html', charset='UTF-8'):
        """ Expose this function to the world, matching the given URL pattern and, optionally, HTTP method, ContentType and Charset.
        """

* url_pattern  - Regexp url pattern matcher
* method       - HTTP method
* content_type - ContentType HTTP header
* charset      - Charset HTTP header

Templates
=========
I would recommend keeping your html templates static on the client side and use a javascript template library. But if you really need some server side templating, have a look at mako.

Deployment
==========
For deployment it is not a good idea to use the wsgiref simple_server that the run script uses. A much better idea is to run your centipede application behind a WSGI server. There is a bunch. I recommend running uwsgi behind nginx if you are deploying on your own server. Or have a look at heroku.


enjoy.

