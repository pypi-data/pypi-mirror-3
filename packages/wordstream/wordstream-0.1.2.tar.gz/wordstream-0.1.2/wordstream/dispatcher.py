"""
request dispatcher:
data persisting across requests should go here
"""

import os

from handlers import Index, Feed, Eat, ViewCorpus, Dissociate

from genshi.template import TemplateLoader
from paste.fileapp import FileApp
from pkg_resources import resource_filename
from webob import Request, Response, exc
from wordstream.api import Corpus

class Dispatcher(object):

    ### class level variables
    defaults = { 'auto_reload': 'False',
                 'jquery': 'jquery.js',
                 'template_dirs': '',
                 'seed': '' }

    def __init__(self, **kw):

        # set instance parameters from kw and defaults
        for key in self.defaults:
            setattr(self, key, kw.get(key, self.defaults[key]))
        self.auto_reload = self.auto_reload.lower() == 'true'
        self.corpus = Corpus()
        self.corpus.feed_stuff(*self.seed.split())

        # request handlers
        self.handlers = [ Index, ViewCorpus, Feed, Eat ]

        # template loader
        self.template_dirs = self.template_dirs.split()
        self.template_dirs.append(resource_filename(__name__, 'templates'))
        self.loader = TemplateLoader(self.template_dirs,
                                     auto_reload=self.auto_reload)

    def __call__(self, environ, start_response):

        # get a request object
        request = Request(environ)

        # get the path 
        path = request.path_info.strip('/').split('/')
        if path == ['']:
            path = []
        request.environ['path'] = path

        # match the request to a handler
        for h in self.handlers:
            handler = h.match(self, request)
            if handler is not None:
                break
        else:
            handler = exc.HTTPNotFound

        # add data to handler
        if hasattr(handler, 'data'):
            handler.data['jquery'] = self.jquery

        # get response
        res = handler()
        return res(environ, start_response)


class Scrambler(object):

    ### class level variables
    defaults = { 'auto_reload': 'False',
                 'template_dirs': '', }

    def __init__(self, **kw):

        # set instance parameters from kw and defaults
        for key in self.defaults:
            setattr(self, key, kw.get(key, self.defaults[key]))
        self.auto_reload = self.auto_reload.lower() == 'true'

        # request handlers
        self.handlers = [ Dissociate ]

        # template loader
        self.template_dirs = self.template_dirs.split()
        self.template_dirs.append(resource_filename(__name__, 'templates'))
        self.loader = TemplateLoader(self.template_dirs,
                                     auto_reload=self.auto_reload)

    def __call__(self, environ, start_response):

        # get a request object
        request = Request(environ)

        # get the path 
        path = request.path_info.strip('/').split('/')
        if path == ['']:
            path = []
        request.environ['path'] = path

        # match the request to a handler
        for h in self.handlers:
            handler = h.match(self, request)
            if handler is not None:
                break
        else:
            handler = exc.HTTPNotFound

        # get response
        res = handler()
        return res(environ, start_response)
