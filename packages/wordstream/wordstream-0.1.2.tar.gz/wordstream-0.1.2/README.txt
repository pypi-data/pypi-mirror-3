wordstream
==========

wordstream is a simple corpus of text associations and tools to use them. Feeding the corpus text will grow a stack of left to right word associations on a per word basis. Words are defined (for now) as the bits that sit between whitespace. The corpus can then be eaten: given a word, pop the top of its stack.

There are two interfaces to the corpus in the wordstream package:
wordstream and dissociate.  Additional applications of wordstream can
also be imagined.

The wordstream source is at http://k0s.org/hg/wordstream


wordstream interface
--------------------

An interactive interface for eating and feeding the corpus. Wordstream has a command line interface, ``wordstream``, and a web interface usable by running ``paster serve wordstream.ini`` .  In both cases, the usage is the same. From an initial corpus, the user types lines of text. wordstream will eat the corpus and print a response to the text and feed the user's lines to the corpus


dissociate interface
--------------------

Named after emacs' ``M-x dissociated-press`` (try it!), dissociate will feed documents to a corpus, scramble the corpus (shuffle the stack order for each word), and output the corpus eating itself, selecting random words, eating their associations, and then eating the associations of the associations until the corpus is empty.  Dissociate has a command line interface (install the software and run ``dissociate --help`` for usage), and a web interface usable via paster serve dissociate.ini.

Applications
------------

While the wordstream corpus is a simple model, the basic idea can be
used to 

 * Thesaurus: By feeding the corpus synonyms, wordstream could be used
   as a thesaurus program.  Synonymity could be indicated via either
   word count or by position towards the top of the stack.  The
   thesaurus could be displayed as a web interface to allow automatic
   suggestions while writing

 * Writing analysis:  The amount of text on the web is vast.
   Wordstream could be used to present what is being talked about most
   within a number of websites and what is associated to it.

 * Collaborative fiction: Since wordstream can use a collective corpus
   that is fed by interacting with it, several authors could
   simultaneously iteract with the wordstream web interface each
   feeding the collective corpus and literally eating each others'
   words

