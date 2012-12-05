
import sys
import os
import find_temporals
import getopt
import util
from hack import get_parse
import shelve
from query_models import QueryCollection, Query, TimeQuery, OrderQuery
from event_models import AbstractEvent, Event, ReferenceEvent
import nltk

import difflib


class Sentence(object):
    def __init__(self, text):
        self.text = text.rstrip()
        self.pos_tagged = None
        self.entity_tagged = None
        self.parse_tree = None
        self.leading_words = []                         
        self.subordinating_conjunctions = []            # Ordered list
        self.events = []                                # Ordered list

    def __repr__(self):
        return str(self.__dict__)

        
class TemporalAnalyzer(object):
    def __init__(self, filename):
        self.sentences = []
        self.load_textual_data(filename)
        self.study_tree(self.sentences[1])

    def load_textual_data(self, filename):
        f = open(filename, 'r')
        for line in f:
            self.sentences.append(Sentence(line))

        for sent in self.sentences:
            sent.pos_tagged = util.pos_tag_sentence(sent.text)
            sent.entity_tagged = util.entity_tag_sentence(sent.pos_tagged)
            sent.parse_tree = get_parse(sent.text)

            # print sent
            # print sent.text
            # print sent.pos_tagged
            # print sent.entity_tagged
            #print find_temporals.find_temporals(sentence.text)
            # print "\n\n"

    def study_tree(self, sent):
        print sent
        tree = nltk.tree.ParentedTree(sent.parse_tree)
        print tree
        print dir(tree)

        all_leaves = tree.leaves()
        print "Subtrees!!!!!!!!!!!!!!"
        subtrees = [subtree for subtree in tree.subtrees(lambda x: x.node == "SBAR")]
        print subtrees
        print len(subtrees)
        for subtree in subtrees:
            special = subtree.leaves()
            print subtree.height()

        print tree.pos()

        print "Comparison"
        print all_leaves
        print special

        # Naive subsequence matching implementation
        sent_leaves = tree.leaves()
        subseq = special
        print sent_leaves
        print subseq
        result =  filter(lambda (start, end): sent_leaves[start:end] == subseq, [(start,start+len(subseq)) for start in range(len(sent_leaves) - len(subseq) + 1)])

        (start, end) = result[0]
        print sent_leaves[0:start]
        print sent_leaves[end:]
        
        # print tree.subtrees().next()
        # print tree.pos()
        # print tree[0]
        # print tree[0][0]
        # print tree[0][1]
        # print tree[0][1][0]
        # print len(tree)
        



    def dump_data(self):
        for sent in self.sentences:
            print sent
            
    def process_text(filename=None):
        """
        Takes in the input file and builds the DataStructure to support queries
        Assumptions:"""
        pass

    def get_events():
        """
        Returns an unordered array of all events found in the text"""
        pass


    def estimate_time(event_id):
        """Returns the best available information about Event event_id"""
        pass

    def estimate_order(event_id):
        """Returns the estimate of the order of the Event with event_id"""
        pass

    def shelve_processed_data(self, filename):
        """Stores a TemporalInference object in a persistent shelve file database."""
        d = shelve.open(filename)
        d['temporal_analyzer'] = self
        d.close()

def bootstrap(config):
    if config['bootstrap_mode'] == 'input':
        #Create a TemporalAnalyzer instance
        analyzer= TemporalAnalyzer(config['bootstrap_data'])
        print analyzer
    elif config['bootstrap_mode'] == 'load':
        pass
    else:
        error("Invalid Bootstrapping Mode")


def analyze(config):
    if config['analysis_mode'] == 'query':
        query_collection = QueryCollection(config['analysis_data'])
        #query_collection.execute()
    elif config['analysis_mode'] == 'interactive':
        os.system('clear')
        sys.ps1 = "interpreter>>"
        os.environ['PYTHONINSPECT'] = 'True'
    else:
        error("Invalid Analysis Mode")


def error(message):
    print message
    sys.exit(2)


if __name__ == "__main__":
    try:
        options, remaining = getopt.gnu_getopt(sys.argv[1:], "f:s:q:v", ["filename=", "load_shelve=", "query=", "verbose"])
    except getopt.GetoptError:
        # Invalid Argument was provided
        print "python temporal_analysis.py [-f <filename> / --filename <filename> / -l <shelve> / --load_shelve <shelve>] [-q <queryfile> | Default Interactive Mode][-v / --verbose]"
        sys.exit(2)

    config = {
              "bootstrap_mode": None,
              "bootstrap_data": None,
              "analysis_mode": None,
              "analysis_data": None, 
              "verbose_mode": False,    
              }

    for option in options:
        name, argument = option

        if name == '-f' or name == 'filename':
            config['bootstrap_mode'] = "input"
            config['bootstrap_data'] = argument     # Filename of textual data file
        elif name == '-l' or name == 'load_shelve':
            config['bootstrap_mode'] = "load"
            config['bootstrap_data'] = argument     # Filename of shelve of pre-processed data

        if name == '-q' or name == 'query':
            config['analysis_mode'] = "query"
            config['analysis_data'] = argument      # Filename of file specifying queries to perform
        else:
            config['analysis_mode'] = "interactive"

        if name == '-v' or name == '--verbose':
            config['verbose_mode'] = True

    bootstrap(config)
    #analyze(config)

    match = [0,1]
    full = [0,1,2,3]

    # Naive subsequence matching implementation
    #(start, stop) for i in range(len(full)) for j in range(len(match), len(full))

    for start in range(len(full)-len(match)+1):
        print full[start:start+len(match)]
        if full[start:start+len(match)] == match:
            print "Found!!"

    full = ['the', 'cat', 'in', 'the', 'hat']
    subseq = ['cat', 'in']
    print filter(lambda (start, end): full[start:end] == subseq, [(start,start+len(subseq)) for start in range(len(full) - len(subseq) + 1)])



    
