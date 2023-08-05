"""
request handlers:
these are instantiated for every request, then called
"""

import urllib2

from pprint import pprint
from urlparse import urlparse
from webob import Response, exc
from StringIO import StringIO
from wordstream.api import Corpus
from wordstream.dissociate import dissociate

class HandlerMatchException(Exception):
    """the handler doesn't match the request"""

class Handler(object):

    methods = set(['GET']) # methods to listen to
    handler_path = [] # path elements to match        

    @classmethod
    def match(cls, app, request):

        # check the method
        if request.method not in cls.methods:
            return None

        # check the path
        if request.environ['path'][:len(cls.handler_path)] != cls.handler_path:
            return None

        try:
            return cls(app, request)
        except HandlerMatchException:
            return None
    
    def __init__(self, app, request):
        self.app = app
        self.request = request
        self.application_path = urlparse(request.application_url)[2]

    def link(self, path=(), permanant=False):
        if isinstance(path, basestring):
            path = [ path ]
        path = [ i.strip('/') for i in path ]
        if permanant:
            application_url = [ self.request.application_url ]
        else:
            application_url = [ self.application_path ]
        path = application_url + path
        return '/'.join(path)

    def redirect(self, location):
        return exc.HTTPSeeOther(location=location)

class GenshiHandler(Handler):

    def __init__(self, app, request):
        Handler.__init__(self, app, request)
        self.data = { 'request': request,
                      'link': self.link }

    def __call__(self):
        return getattr(self, self.request.method.title())()

    def Get(self):
        # needs to have self.template set
        template = self.app.loader.load(self.template)
        return Response(content_type='text/html',
                        body=template.generate(**self.data).render('html'))

class Index(GenshiHandler):
    template = 'index.html'
    methods=set(['GET'])

    @classmethod
    def match(cls, app, request):
        if not request.path_info.strip('/'):
            return cls(app, request)

class ViewCorpus(GenshiHandler):
    template = 'corpus.html'
    handler_path = ['corpus']

    def Get(self):
        buffer = StringIO()
        pprint(self.app.corpus, buffer)
        self.data['corpus'] = buffer.getvalue()
        return GenshiHandler.Get(self)

class Eat(Handler):

    methods = set(['GET'])

    @classmethod
    def match(cls, app, request):

        # check the method
        if request.method not in cls.methods:
            return None

        if len(request.environ['path']) == 1:
            return cls(app, request)

    def __call__(self):
        word = self.request.path_info.strip('/')
        association = self.app.corpus.eat(word) or ''
        return Response(content_type='text/plain',
                        body=association)

        

class Feed(Handler):
    
    methods = set(['POST'])

    @classmethod
    def match(cls, app, request):

        # check the method
        if request.method not in cls.methods:
            return None

        if len(request.environ['path']) > 1:
            return cls(app, request)

    def __call__(self):
        self.app.corpus.feed_stream(self.request.environ['path'])
        return exc.HTTPOk()


class Dissociate(GenshiHandler):
    template = 'post.html'
    methods = set(['GET', 'POST'])

    
    @classmethod
    def match(cls, app, request):

        # check the method
        if request.method not in cls.methods:
            return None

        return cls(app, request)

    def Get(self):
        if 'url' in self.request.GET:
            try:
                contents = self.url_contents(self.request.GET['url'])
            except:
                return GenshiHandler.Get(self)
            dissociation = self.dissociation(contents)
            return Response(content_type='text/html',
                            body='<html><body>%s</body></html>' % dissociation)


        return GenshiHandler.Get(self)

    def url_contents(self, url):
        return urllib2.urlopen(url).read()

    def dissociation(self, contents):
        corpus = Corpus()
        corpus.feed_stream(contents)
        corpus.scramble()
        buffer = StringIO()
        dissociate(corpus, buffer)
        return buffer.getvalue()

    def Post(self):
        if 'url' in self.request.POST:
            try:
                contents = self.url_contents(self.request.POST['url'])
            except:
                return GenshiHandler.Get(self)
        elif 'text' in self.request.POST:
            contents = self.request.POST['text']
        elif 'file' in self.request.POST:
            contents = self.request.POST['file'].file.read()
        dissociation = self.dissociation(contents)
        return Response(content_type='text/html',
                        body='<html><body>%s</body></html>' % dissociation)
