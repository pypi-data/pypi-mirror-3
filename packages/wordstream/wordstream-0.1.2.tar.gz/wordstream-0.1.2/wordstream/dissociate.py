#!/usr/bin/env python

import random
import sys
import urllib2

from optparse import OptionParser
from pprint import pprint
from wordstream.api import Corpus

def dissociate(corpus, output=sys.stdout):
    while corpus:
        word = random.choice(corpus.keys())
        inedible = True
        while corpus.get(word):
            inedible = False
            print>> output,  word,
            word = corpus.eat(word)
        if inedible: # eat it anyway
            corpus.eat(word)
    

def main(args=sys.argv[1:]):
    parser = OptionParser('%prog <path_or_url> <path_or_url> <...>')
    options, args = parser.parse_args()

    corpus = Corpus()
    if args:
        corpus.feed_stuff(*args)
    else:
        corpus.feed_stream(sys.stdin.read())
    corpus.scramble()
    dissociate(corpus)

if __name__ == '__main__':
    main()
