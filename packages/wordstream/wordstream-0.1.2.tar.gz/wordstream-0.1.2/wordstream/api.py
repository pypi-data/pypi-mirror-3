import urllib2
from random import shuffle

class Corpus(dict):

    def __init__(self, corpus=None):
        dict.__init__(corpus or {})

    def feed(self, word, association):
        self.setdefault(word, []).append(association)

    def eat(self, word):
        if word in self:
            if self[word]:
                return self[word].pop()
            else:
                del self[word]

    def feed_stream(self, stream):
        if isinstance(stream, basestring):
            stream = stream.split()
        while len(stream) > 1:
            self.feed(stream[-2], stream[-1])
            stream.pop()

    def feed_stuff(self, *args):
        for arg in args:
            if arg.startswith('https://') or arg.startswith('http://'):
                text = urllib2.urlopen(arg)
            else:
                text = file(arg).read()
            self.feed_stream(text)

    def scramble(self):
        for i in self:
            shuffle(self[i])

    def save(self, filename):
        named = False
        if isinstance(f, basestring):
            named = True
            f = file(f)
        for key in sorted(self.keys()):
            print >> f, "%s %s" % (key, ' '.join(self[key]))
        if named:
            f.close()
        
    def load(self, f):
        if isinstance(f, basestring):
            f = file(f)
        

    @classmethod
    def restore(cls, filename):
        corpus = cls()
        corpus.load(filename)
    
