
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

PATH_TO_SHELVE = 'shelved_data/'


class Sentence(object):
    def __init__(self, text):
        self.text = text.rstrip()
        self.pos_tagged = None
        self.entity_tagged = None
        self.parse_tree = None
        self.leading_words = []                         
        self.subordinating_conjunctions = []            # Ordered list
        self.events = []                                # Ordered list

    def pprint(self):
        print self.pos_tagged
        print self.entity_tagged
        print self.parse_tree

    def __repr__(self):
        return '<Sentence %s>' % self.text[:20]

class TimeDataStore(object):
    def __init__(self):
        pass

class OrderDataStore(object):
    def __init__(self):
        pass
        
class TemporalAnalyzer(object):
    def __init__(self, filename):
        self.filename = filename
        self.sentences = []
        self.time_data_store = TimeDataStore()
        self.order_data_store = OrderDataStore()
        # Initialization
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
        # print dir(tree)

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

    def shelve_processed_data(self, filename=None):
        """
        Stores a TemporalInference object in a persistent shelve file database. 
        Stores in provided filename. Otherwise, stores in the PATH_TO_SHELVE folder with 
        a filename to match the filename of the original text file
        """
        if not filename:
            filename = PATH_TO_SHELVE + self.filename.split("/")[-1]
        print filename
        d = shelve.open(filename)
        d['temporal_analyzer'] = self
        d.close()

    def __repr__(self):
        return '<TemporalAnalyzer %s>' % self.sentences


def bootstrap(config):
    if config['bootstrap_mode'] == 'input':
        #Create a TemporalAnalyzer instance
        text_filename = config['bootstrap_data']
        analyzer= TemporalAnalyzer(text_filename)
        analyzer.shelve_processed_data()
        print analyzer
    elif config['bootstrap_mode'] == 'load':
        shelve_filename = config['bootstrap_data']
        d = shelve.open(PATH_TO_SHELVE + shelve_filename)
        analyzer = d['temporal_analyzer']
        print analyzer
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
        options, remaining = getopt.gnu_getopt(sys.argv[1:], "f:l:q:v", ["filename=", "load_shelve=", "query=", "verbose"])
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
    
