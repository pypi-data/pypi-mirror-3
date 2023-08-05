"""
clwapp: Command Line Web APP

clwapp is configured with clwapp.command in paste's .ini file
arguments are passed in the query string.  That is, if clwapp.command = ls,
one could do http://localhost:9999/?-l&-a to pass the '-l' and '-a' arguments.

DO NOT USE THIS (WITHOUT AUTH) WITH PROGRAMS THAT CAN ADVERSELY AFFECT THE
SYSTEM OR EXPOSE SENSITIVE DATA!  subprocess.Popen is used, so that limit to
the shell is restricted, but programs that can alter your system can be
exploited.  clwapp works well with programs that display information (provided
their access is restricted from secure information), and less well with
programs that change the state of the server.
*NEVER* use with Popen(shell=True) unless you are sure of your security.

"""

import os
import subprocess
import utils

from webob import Request, Response, exc

class View(object):

    ### class level variables
    defaults = {}

    def __init__(self, command, **kw):
        self.command = utils.shargs(command)
        print self.command
        for key in self.defaults:
            setattr(self, key, kw.get(key, self.defaults[key]))
        self.response_functions = { 'GET': self.get }

    ### methods dealing with HTTP
    def __call__(self, environ, start_response):
        self.request = Request(environ)
        res = self.make_response(self.request.method)
        return res(environ, start_response)

    def make_response(self, method):
        return self.response_functions.get(method, self.error)()

    def get_response(self, text, content_type='text/html'):
        res = Response(content_type=content_type, body=text)
        res.content_length = len(res.body)
        return res

    def get(self):
        """
        return response to a GET requst
        """
        args = self.command + self.request.GET.keys()
        process = subprocess.Popen(args, stdout=subprocess.PIPE)
        output = process.communicate()[0]
        output = output.decode('utf-8', 'ignore')
        title = ' '.join([os.path.basename(args[0])] + args[1:])
        return self.get_response("""<html><head><title>%s</title></head><body><pre>
%s
</pre></body></html>
        """ % (title, output) )

    def error(self):
        """deal with non-supported methods"""
        return exc.HTTPMethodNotAllowed("Only %r operations are allowed" % self.response_functions.keys())

