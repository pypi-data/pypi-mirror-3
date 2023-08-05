from clwapp import View
from paste.httpexceptions import HTTPExceptionHandler

def factory(global_conf, **app_conf):
    """create a webob view and wrap it in middleware"""

    config = [ 'command' ]
    key_str = 'clwapp.%s'
    args = dict([(key, app_conf[ key_str % key]) for key in config
                 if app_conf.has_key(key_str % key) ])
    app = View(**args)
    return HTTPExceptionHandler(app)
    
