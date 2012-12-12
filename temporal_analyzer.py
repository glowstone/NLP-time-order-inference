
# System Modules
import sys, os, getopt
import nltk
import shelve

# Local Modules
import util
import config
import find_temporals
from query_models import QueryCollection, Query, TimeQuery, OrderQuery
from event_models import AbstractEvent, Event, ReferenceEvent
from datastores import TimeDataStore, OrderDataStore


class Sentence(object):
    def __init__(self, text):
        self.text = text.rstrip(' .')            # Remove trailing whitespace and period
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
        print "leading_word_clues", self.leading_word_clues
        print "conjunction_word_clues", self.conjunction_word_clues
        for event in self.events:
            print "Event:"
            print event

    def __repr__(self):
        return '<Sentence %s>' % self.text[:20]         # Show only first 20 characters


class TemporalAnalyzer(object):
    def __init__(self, filename):
        self.filename = filename                    
        self.time_data_store = TimeDataStore()
        self.order_data_store = OrderDataStore()
        self.sentences = []                           # All valid sentences
        self.events = []                              # All valid events
        
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
                (valid, event_list, msg) = self.parse_sentence(sentence)
                if valid:
                    self.sentences.append(sentence)
                    self.events.extend(event_list)


    def parse_sentence(self, sentence):
        """
        Augments sentence with its Stanford Parse tree, POS tags from the Stanford Parser, and
        an the NLTK. Extracts Events from the sentence.

        mutates sentence by adding data to its fields

        returns (Boolean of whether Sentence is valid, list of events found in the sentence)
        """
        sentence.parse_tree = nltk.tree.Tree(util.stanford_parse(sentence.text))
        sentence.pos_tagged = sentence.parse_tree.pos()                       # Get POS tags from Stanford Parse Tree.
        sentence.entity_tagged = util.entity_tag_sentence(sentence.pos_tagged)  
        # TODO entity tagging happens here and in Event.__init__

        (success, ordered_event_trees) = self.extract_events(sentence)
        if not success:
            return (False, [], "Events could not be extracted from this sentence.")
        self.construct_events(sentence, ordered_event_trees)           
        self.ordering_analysis(sentence)
        self.temporal_analysis(sentence)
        self.process_relative_times(sentence)

        return (True, sentence.events, None)


    def retrieve_remaining_event(self, tree, known_event, known_event_start, known_event_end):
        """
        Given parse tree, a known event subtree, and the start/end indices of the known event in the tree
        Splits the tree into two subtrees corresponding to the two events.

        Does NOT mutate the tree or known_event

        returns: ordered list [Tree, Tree] (one of which will be known_event)
        """
        # treeposition_spanning_leaves gives the indices of tree that give the subtree spanning those leaves.
        # Ex. If (0, 1, 2) returned by function, the subtree spanning those leaves would be tree[0][1][2]
        
        indices = tree.treeposition_spanning_leaves(known_event_start, known_event_end)
        tree_copy = tree.copy(True)                      # Deep copy the parse tree             
        util.nested_pop(tree_copy, indices)              # Mutate the copied parse tree

        if known_event_start == 0:                       # Known event should be first
            return (True, [known_event, tree_copy])
        elif known_event_end == len(tree.leaves()):      # Known event should be last of the two
            return (True, [tree_copy, known_event])
        else:
            return (False, "Three or more events in a sentence are not currently handled")


    def extract_events(self, sentence):
        """
        Seeks to find the one or two Events contained inside a sentence by searching over 'S' and 'SBAR'
        subtrees and constructing two parse trees for the two Events

        Does NOT mutate sentence, or its properties such as sentence.parse_tree

        returns (boolean of whether sentence was valid, [ordered list of the event phrase trees as they occur in the sentence])
        """
        # Search all SBAR and S phrases. Choose the one closest to root (but not the root itself) to divide the sentence.
        phrase_tree = util.aux_phrase_subtree(sentence.parse_tree, ['S', 'SBAR'])

        if phrase_tree:                               # Sentence is a 2 event sentence with an S-phrase 
            index_tuples = util.subsequence_search(phrase_tree.leaves(), sentence.parse_tree.leaves())
            (start, end) = index_tuples[0]            # Take first set of indicies where subseq matches
            (success, ordered_event_trees) = self.retrieve_remaining_event(sentence.parse_tree, phrase_tree, start, end)
            if not success:
                return (False, [])
            #event_phrase_trees = self.get_events_from_indices(sentence.parse_tree, start, end)
        else:
            ordered_event_trees = [sentence.parse_tree]

        return (True, ordered_event_trees)


    def construct_events(self, sentence, event_tree_list):
        """
        Creates Event or ReferenceEvent instances from each of the event trees

        DOES mutate sentence to fill out the sentence.events list

        returns [list of event instances]
        """
        event_instances = []
        for event_tree in event_tree_list:
            prior_event_matched = util.best_event_match(self.events, " ".join(event_tree.leaves()), 0.30)
            if prior_event_matched:
                e = ReferenceEvent(event_tree, prior_event_matched)
                #print "%s refers to %s" % (e, best_match)
            else:
                e = Event(event_tree, self.time_data_store)
            event_instances.append(e)
        sentence.events = event_instances
        return event_instances

    def ordering_analysis(self, sentence):
        """
        Takes a Sentence with its sentence.events filled out with events in order. Identifies leading
        and subordinating conjunction clue words that give ordering information. 
        Infers an ordering of the Events and updates the OrderDataStore.

        Mutates sentence.leading_word_clues, sentence.conjunction_word_clues, OrderDataStore

        returns None
        """
        ordered_events = sentence.events

        if len(ordered_events) == 1:
            event = ordered_events[0]
            sentence.leading_word_clues = event.parse_tree.leaves()[:1]      # Leading word
            sentence.conjunction_word_clues = []                             # No conjunction clue words
        
            print "Ordering not yet supported for this sentence, but it will be."
            # sentence.pprint()

        elif len(ordered_events) == 2:
            first_event = ordered_events[0]
            second_event = ordered_events[1]
            sentence.leading_word_clues = first_event.parse_tree.leaves()[:1]   # Leading word    
            # Longest subordinating conjunction has 3 words such as 'as soon as'  
            sentence.conjunction_word_clues = second_event.parse_tree.leaves()[:3]

            (leading, conjunction) = (sentence.leading_word_clues, sentence.conjunction_word_clues) 
            chronological = util.infer_ordering(leading, conjunction, first_event, second_event)

            self.order_data_store.add_event(first_event)
            self.order_data_store.add_event(second_event)
            if chronological:
                self.order_data_store.record_order(first_event, second_event)
            else:
                self.order_data_store.record_order(second_event, first_event)

            # sentence.pprint()
            print self.order_data_store

        else:
            print "More than two Event phrases (should have caught this earlier)!!"


    def temporal_analysis(self, sentence):
        """
        Takes a Sentence with its sentence.events property populated. Analyzes Events to extract out
        syntactic time information and updates the TimeDataStore.

        Mutates TimeDataStore
    
        returns None
        """

        pass

    def process_relative_times(self, sentence):
        """
        Takes a Sentence with its sentence.events property populated. Analyzes Events to find relative time information
        of the form "two weeks before <ReferenceEvent>, <AbstractEvent>". This allows an absolute time to be given to
        the AbstractEvent based on the absolute time of the ReferenceEvent.

        Mutates Event.best_time for the Event referred to by the ReferenceEvent

        returns None
        """
        if len(sentence.events) == 2:
            first_event = sentence.events[0]
            second_event = sentence.events[1]
            if isinstance(first_event, ReferenceEvent):
                util.event_timex_analysis(first_event, second_event)
            if isinstance(second_event, ReferenceEvent):
                util.event_timex_analysis(second_event, first_event)


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

    # Setters/Getters
    ###########################################################################

    def get_sentences(self):
        """
        returns ordered list of all valid, parsable sentences in the processed text(s).
        """
        return self.sentences

    def get_events(self):
        """
        returns ordered list of all events found in valid, parsable sentences in the processed text(s).
        """
        return self.events

    def get_timestore(self):
        """
        returns a queryable TimeDataStore which contains temporal information about Events from the processed text(s).
        """
        return self.time_data_store

    def get_orderstore(self):
        """
        returns a queryable OrderDataStore which contains ordering information about Events from the processed text(s).
        """
        return self.order_data_store



def bootstrap(mode_args):
    if mode_args['bootstrap_mode'] == 'input':
        #Create a TemporalAnalyzer instance
        text_filename = mode_args['bootstrap_data']
        analyzer= TemporalAnalyzer(text_filename)
        analyzer.shelve_processed_data()
    elif mode_args['bootstrap_mode'] == 'load':
        shelve_filename = mode_args['bootstrap_data']
        d = shelve.open(config.PATH_TO_SHELVE + shelve_filename)
        analyzer = d['temporal_analyzer']
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
    
