#!/usr/bin/env python

import sys

import urllib2

from optparse import OptionParser
from pprint import pprint
from wordstream.api import Corpus

def main(args=sys.argv[1:]):
    parser = OptionParser('%prog [options] <path_or_url> <path_or_url> <...>')
    parser.add_option('--print-corpus', dest='print_corpus', default=False,
                      action='store_true',
                      help="print the given corpus of associations")
    parser.add_option('-n', type='int', dest='n', default=1,
                      help='number of words to eat per munch')
    options, args = parser.parse_args()

    corpus = Corpus()

    corpus.feed_stuff(*args)
    if options.print_corpus:
        pprint(corpus)
        sys.exit(0)

    n = 1

    while 1:
        stream = raw_input()
        splitstream = stream.split()
        if splitstream:
            for i in range(n):
                word = corpus.eat(splitstream[-1])
                if not word:
                    break
                print word

if __name__ == '__main__':
    main()
