
import sys
import os
import find_temporals
import getopt
import util
import config
import shelve
from query_models import QueryCollection, Query, TimeQuery, OrderQuery
from event_models import AbstractEvent, Event, ReferenceEvent
import nltk


class Sentence(object):
    def __init__(self, text):
        self.text = text.rstrip()
        self.parse_tree = None                   # Stanford Parse Tree
        self.pos_tagged = None                   # List of (word, Stanford Parse POS Tag) tuples
        self.entity_tagged = None                # NLTK tree.tree of entity tags
        self.leading_word_clues = []                        
        self.conjunction_word_clues = []            # Ordered list
        self.events = []                                # Ordered list

    def pprint(self):
        print "parse_tree", self.parse_tree
        print "pos_tagged", self.pos_tagged
        print "entity_tagged", self.entity_tagged
        print "leading_words", self.leading_words
        print "subordinating_conjunctions", self.subordinating_conjunctions

    def __repr__(self):
        return '<Sentence %s>' % self.text[:20]         # Show only first 20 characters


class TimeDataStore(object):
    def __init__(self):
        self.time_table = {}

class OrderDataStore(object):
    def __init__(self):
        self.order_table = {}


class TemporalAnalyzer(object):
    def __init__(self, filename):
        self.filename = filename                    
        self.time_data_store = TimeDataStore()
        self.order_data_store = OrderDataStore()
        self.sentences = []                           # All valid sentences
        self.all_events = []                          # All valid events
        
        # Initialization
        self.parse_textual_data(filename)

    def parse_textual_data(self, filename):
        """
        Reads given filename containing sentences, with optional comments

        returns None
        """
        f = open(filename, 'r')

        for line in f:
            sentence_text = line.split("#")[0].strip()
            if len(sentence_text) > 0:
                sentence = Sentence(sentence_text)
                (valid, event_list) = self.parse_sentence(sentence)
                if valid:
                    self.sentences.append(sentence)
                    self.all_events.extend(event_list)


    def parse_sentence(self, sentence):
        """
        Augments sentence with its Stanford Parse tree, POS tags from the Stanford Parser, and
        an the NLTK. Extracts Events from the sentence.

        returns (Boolean of whether Sentence is valid, list of events found in the sentence)
        """
        sentence.parse_tree = nltk.tree.ParentedTree(util.stanford_parse(sentence.text))
        sentence.pos_tagged = sentence.parse_tree.pos()                       # Get POS tags from Stanford Parse Tree.
        sentence.entity_tagged = util.entity_tag_sentence(sentence.pos_tagged)  
        # TODO entity tagging happens here and in Event.__init__

        # Search all SBAR and S phrases. Choose the one closest to root (but not the root itself) to divide the sentence.
        phrase_tree = util.aux_phrase_subtree(sentence.parse_tree, ['S', 'SBAR'])
        print 'phrase tree', phrase_tree

        # Extract phrase trees

        if phrase_tree:                               # Sentence is a 2 event sentence with an S-phrase 
            index_tuples = util.subsequence_search(phrase_tree.leaves(), sentence.parse_tree.leaves())
            (start, end) = index_tuples[0]            # Take first set of indicies where subseq matches
            
            ordered_event_trees = self.retrieve_remaining_event(sentence.parse_tree, phrase_tree, start, end)
            #event_phrase_trees = self.get_events_from_indices(sentence.parse_tree, start, end)
        else:
            event_phrase_trees = [sentence.parse_tree]

        # Process phrase trees

        print ordered_event_trees

        if len(event_phrase_trees) == 1:
            print 'event', event_phrase_trees[0].leaves()
            phrase_tree = event_phrase_trees[0]
            sentence.leading_word_clues = phrase_tree.leaves()[:1]   # Leading word of first Event phrase
            sentence.conjunction_word_clues = []                     # No conjunction clue words if sentence only contains one Event

        elif len(event_phrase_trees) == 2:
            print 'event', event_phrase_trees[0].leaves()
            # Which event occurred first??
            first_phrase_tree = event_phrase_trees[0]
            second_phrase_tree = event_phrase_trees[1]
            # Leading word of first Event phrase
            sentence.leading_word_clues = first_phrase_tree.leaves()[:1]     
            # Longest subordinating conjunction has 3 words such as 'as soon as'  
            sentence.conjunction_word_clues = second_phrase_tree.leaves()[:3]   
        else:
            # System only considers sentences with one or two events in them.
            return (False, [])

        #temporary
        return (True, [])

        # Construct events

        for event in events:
            best_match = util.best_event_match(self.all_events, " ".join(event.leaves()), 0.30)
            if best_match:
                print "REFERENCE EVENT!"
                e = ReferenceEvent(event)
                e.add_reference(best_match)
                print "%s refers to %s" % (e, best_match)
            else:
                e = Event(event)
            sentence.events.append(e)
            self.all_events.append(e)
        return (True, [e])

    def retrieve_remaining_event(self, tree, known_event, known_event_start, known_event_end):
        known_event_position = None        # Known Event is either the oth or 1th Event in the sentence parse tree.
        if known_event_start == 0:
            known_event_position = 0
        elif known_event_end == len(tree.leaves()):
            known_event_position = 1
        else:
            return (False, "Three or more events in a sentence are not currently handled")

        print known_event_position

        # treeposition_spanning_leaves gives the indices of tree that give the subtree spanning those leaves.
        # For example, if treeposition_spanning_leaves returns (0, 1, 2), the subtree spanning those leaves
        # would be tree[0][1][2]
        
        indices = tree.treeposition_spanning_leaves(start, end)
        print indicies

        # tree_copy will become the 
        tree_copy = tree                     
        # TODO, this is an alias, not a proper copy

        to_be_deleted = util.multi_access(tree_copy, indicies)
        del to_be_deleted

        if known_event_position == 0:
            return (True, [known_event, tree_copy])
        else:
            return (True, [tree_copy, known_event])    


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
    analyze(mode_args)
    
