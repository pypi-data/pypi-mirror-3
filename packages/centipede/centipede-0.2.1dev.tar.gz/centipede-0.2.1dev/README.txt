================
Centipede 0.2dev
================

Centipede is a WSGI microframework with a simple decorator based router. It's strength is that it models the technology in use and tries not to confuse developers with complex patterns and tricks. It inherits strongly from urlrelay_.

Installation
============
::

    $ pip install centipede

Defining handlers
=================
With Centipede you expose functions to urls. Functions either return a **string** or a **tuple**. A string is treated as the document body, http status is set to *200 OK* and returned to the browser. Should you return a tuple, *status code*, *body* and *headers* are expected. The expose decorator also supports a few arguments.

::

    from centipede import expose, app

    @expose('^/$')
    def index(request):
        """ Simple Hello IgglePigglePartyPants
        """
        return 'Hello IgglePigglePartyPants!'

    @expose('^/google$')
    def index(request):
        """ A redirect
        """
        return (307, '', {'Location':'http://google.com'})
 
    import json
 
    @expose('^/twitter$', 'GET', content_type='application/json')
    def twitter(request):
        """ Return your twitter status
        """
        return json.dumps({
            'status' : 'My awesome and insightful twitter status. #blah'
        })
    
    application = app()

Expose arguments
================
The expose decorator looks like this::

    expose(url_pattern, method=None, content_type='text/html', charset='UTF-8')

Request
=======
The parameter passed to the functions exposed - in the examples above named request - is the WSGI environ_ dictionary.

Templates
=========
I would recommend keeping your html templates static on the client side and use a javascript template library. But if you really need some server side templating, have a look at mako.

Deployment
==========
For deployment it is a good idea to run your centipede application behind a good WSGI server. There is a bunch_. Gunicorn_ is good. I usually end up running uwsgi_ behind nginx.


enjoy.

.. _urlrelay: http://pypi.python.org/pypi/urlrelay/
.. _environ: http://www.python.org/dev/peps/pep-0333/#environ-variables
.. _Gunicorn: http://gunicorn.org/
.. _uwsgi: http://projects.unbit.it/uwsgi/
.. _bunch: http://www.wsgi.org/en/latest/servers.html