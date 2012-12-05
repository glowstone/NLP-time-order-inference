
import sys
import os
import find_temporals
import getopt
import util
from hack import get_parse
import shelve


class AbstractEvent(object):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return '<AbstractEvent %s>' % id(self)


class Event(AbstractEvent):
    def __init__(self, text):
        super(Event, self).__init__(text)
        self.absolute_times = []

    def __repr__(self):
        return '<Event %s>' % id(self)


class ReferenceEvent(AbstractEvent):
    def __init__(self):
        self.reference_times = []         # Estimate of time of the referred to Event

    def __repr__(self):
        return '<ReferenceEvent %s>' % id(self)

class Sentence(object):
    def __init__(self, text):
        self.text = text
        self.pos_tagged = ""
        self.entity_tagged = ""
        self.subordinating_conjunctions = []            # Ordered list
        self.abstract_events = []                       # Ordered list
        
class TemporalAnalyzer(object):
    def __init__(self, filename):
        self.sentences = []

        f = open(filename, 'r')
        for line in f:
            self.sentences.append(Sentence(line))

        for sentence in self.sentences:
            sentence.pos_tagged = util.pos_tag_sentence(sentence.text)
            sentence.entity_tagged = util.entity_tag_sentence(sentence.pos_tagged)
            print sentence
            print (sentence.text).strip("\n")
            print sentence.pos_tagged
            print sentence.entity_tagged
            print find_temporals.find_temporals(sentence.text)
            print "\n\n"
            

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
        query_config = open(config['analysis_data'], 'r')
        query_collection = QueryCollection(query_config)
        #query_collection.execute()
        # TODO prevent other output from being printed so this can be piped to an output file if desired.
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
    analyze(config)



    


    # d = shelve.open('shelve_test')
    # print analyzer.__dict__
    # d['data'] = analyzer.__dict__
    # d.close()
