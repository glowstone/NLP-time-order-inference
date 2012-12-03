
import sys
import timex
import getopt
import util


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
    def __init__(self, filename, config):
        self.sentences = []

        f = open(filename, 'r')
        for line in f:
            self.sentences.append(Sentence(line))

        for sentence in self.sentences:
            sentence.pos_tagged = util.pos_tag_sentence(sentence.text)
            sentence.entity_tagged = util.entity_tag_sentence(sentence.pos_tagged)
            print sentence
            print sentence.text
            print sentence.pos_tagged
            print sentence.entity_tagged
            

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





if __name__ == "__main__":
    try:
        options, remaining = getopt.gnu_getopt(sys.argv[1:], "f:s:v", ["filename=", "start=", "verbose"])
    except getopt.GetoptError:
        # Invalid Argument was provided
        print "python temporal_analysis.py -f <filename> [-v / --verbose] [-s ISO / --start ISO]"
        sys.exit(2)

    config = {"start_mode": False,
              "start": None,
              "verbose_mode": False}
    for option in options:
        name, argument = option
        if name == '-f' or name == 'filename':
            filename = argument
        if name == '-v' or name == '--verbose':
            config['verbose_mode'] = True
        if name == '-s' or name == '--start':
            config['start_mode'] = True
            config['start'] = argument

    #Create a TemporalAnalyzer instance
    analyzer= TemporalAnalyzer(filename, config)
    print analyzer

    # Analyzer now supports queries