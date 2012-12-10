
import sys
import os
import find_temporals
import getopt
import util
from hack import get_parse
import config
import shelve
from query_models import QueryCollection, Query, TimeQuery, OrderQuery
from event_models import AbstractEvent, Event, ReferenceEvent
import nltk

# Constants



class Sentence(object):
    def __init__(self, text):
        self.text = text.rstrip()
        self.entity_tagged = None
        self.parse_tree = None
        self.pos_tagged = None
        self.leading_words = []                         
        self.subordinating_conjunctions = []            # Ordered list
        self.events = []                                # Ordered list

    def pprint(self):
        print self.entity_tagged
        print self.parse_tree

    def __repr__(self):
        return '<Sentence %s>' % self.text[:20]

class TimeDataStore(object):
    def __init__(self):
        self.time_table = {}

class OrderDataStore(object):
    def __init__(self):
        self.order_table = {}


        
class TemporalAnalyzer(object):
    def __init__(self, filename):
        self.filename = filename
        self.sentences = []
        self.time_data_store = TimeDataStore()
        self.order_data_store = OrderDataStore()
        # Initialization
        self.load_textual_data(filename)
        self.all_events = []                  # Copy of all seen Events
        for sentence in self.sentences:
            self.study_tree(sentence)

    def load_textual_data(self, filename):
        f = open(filename, 'r')

        for sent in self.sentences:
            sent.parse_tree = nltk.tree.ParentedTree(get_parse(sent.text))
            sent.pos_tagged = sent.parse_tree.pos()
            sent.entity_tagged = util.entity_tag_sentence(sent.pos_tagged)  # TODO entity tagging happens here and in Event.__init__

            # if ok:

            #     self.sentences.append(sentence)
            #     self.all_events.append(??)

    def analyze(self, sent):
        """
        return True/False
        """
        sentence_tree = sent.parse_tree
       
        # Find all SBAR and S phrases and choose the one closest to root (greatest height) to divide the sentence
        secondary_event_tree = util.secondary_event_subtree(sentence_tree, ['S', 'SBAR'])
        print secondary_event_tree

        if secondary_event_tree:
            index_tuples = util.subsequence_search(secondary_event_tree.leaves(), sentence_tree.leaves())
            print index_tuples
            (start, end) = index_tuples[0]
            events = self.get_events_from_indices(tree, start, end)
        else:
            events = [sent.parse_tree]

        for event in events:
            best_match = util.best_event_match(self.all_events, " ".join(event.leaves()), 0.30)
            if best_match:
                print "REFERENCE EVENT!"
                e = ReferenceEvent(event)
                e.add_reference(best_match)
                print "%s refers to %s" % (e, best_match)
            else:
                e = Event(event)
            sent.events.append(e)
            self.all_events.append(e)
    


    def get_events_from_indices(self, tree, start, end):
        """
        Given a tree and the start/end indices of an event within that tree, returns both the event specified by start
        and end AND the event that falls outside that region. Basically, splits the tree up into two subtrees
        corresponding to the two events.

        tree is and instance of ParentedTree
        start and end are ints

        returns: a list of [ParentedTree, ParentedTree]
        """
        # treeposition_spanning_leaves gives the indices of tree that give the subtree spanning those leaves.
        # For example, if treeposition_spanning_leaves returns (0, 1, 2), then you need to take the 0 index
        # of tree, then the 1 index of that subtree, then the 2 index of that sub-subtree to get the tree 
        # spanning those leaves
        indices = tree.treeposition_spanning_leaves(start, end)

        subtree = tree
        for i in indices:
            subtree = subtree[i]

        tree_copy = tree
        # Now do almost the same thing, but delete the subtree from the main tree
        for i in indices[:-1]:
            tree_copy = tree_copy[i]
        del tree_copy[indices[-1]]

        return [tree, subtree]

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
            filename = config.PATH_TO_SHELVE + self.filename.split("/")[-1]
        print filename
        d = shelve.open(filename)
        d['temporal_analyzer'] = self
        d.close()

    def __repr__(self):
        return '<TemporalAnalyzer %s>' % self.sentences


def bootstrap(mode_args):
    if mode_args['bootstrap_mode'] == 'input':
        #Create a TemporalAnalyzer instance
        text_filename = mode_args['bootstrap_data']
        analyzer= TemporalAnalyzer(text_filename)
        analyzer.shelve_processed_data()
        print analyzer
    elif mode_args['bootstrap_mode'] == 'load':
        shelve_filename = mode_args['bootstrap_data']
        d = shelve.open(config.PATH_TO_SHELVE + shelve_filename)
        analyzer = d['temporal_analyzer']
        print analyzer
    else:
        error("Invalid Bootstrapping Mode")


def analyze(mode_args):
    if mode_args['analysis_mode'] == 'query':
        query_collection = QueryCollection(mode_args['analysis_data'])
        #query_collection.execute()
    elif mode_args['analysis_mode'] == 'interactive':
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

    mode_args = {
              "bootstrap_mode": None,
              "bootstrap_data": None,
              "analysis_mode": None,
              "analysis_data": None, 
              "verbose_mode": False,    
              }

    for option in options:
        name, argument = option

        if name == '-f' or name == 'filename':
            mode_args['bootstrap_mode'] = "input"
            mode_args['bootstrap_data'] = argument     # Filename of textual data file
        elif name == '-l' or name == 'load_shelve':
            mode_args['bootstrap_mode'] = "load"
            mode_args['bootstrap_data'] = argument     # Filename of shelve of pre-processed data

        if name == '-q' or name == 'query':
            mode_args['analysis_mode'] = "query"
            mode_args['analysis_data'] = argument      # Filename of file specifying queries to perform
        else:
            mode_args['analysis_mode'] = "interactive"

        if name == '-v' or name == '--verbose':
            mode_args['verbose_mode'] = True

    bootstrap(mode_args)
    #analyze(mode_args)
    
