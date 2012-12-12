from util import extract_entities
from find_temporals import find_temporals
from date_models import Date
from util import stanford_parse
from nltk.tree import ParentedTree


class AbstractEvent(object):
    def __init__(self, tree):
        self.text = " ".join(tree.leaves())
        self.parse_tree = tree
        self.pos_tagged = tree.pos()
        self.entities = extract_entities(self)

    def __repr__(self):
        return '<AbstractEvent %s>' % id(self)


class Event(AbstractEvent):
    time_data_store = None      # Static TimeDataStore
    
    def __init__(self, tree):
        super(Event, self).__init__(tree)
        self.find_best_time()

    def find_best_time(self):
        absolute_times = find_temporals(self.text)
        if len(absolute_times) > 0:
            Event.time_data_store.record_event(self, sorted(absolute_times, key=lambda x: x.precision(), reverse=True)[0])
        else:
            Event.time_data_store.add_event(self)

    def get_best_time(self):
        return Event.time_data_store.query_time(self)

    def set_best_time(self, time):
        Event.time_data_store.record_event(self, time)

    def __repr__(self):
        return '<Event %s>' % self.text


class ReferenceEvent(AbstractEvent):
    def __init__(self, tree, event):
        super(ReferenceEvent, self).__init__(tree)
        assert(isinstance(event, Event))           # Cannot refer to another ReferenceEvent
        self.reference = event                     # The referenced Event
        self.reference_times = []                  
        self.sync_times()

    def refers_to(self):
        """
        Returns the Event the ReferenceEvent refers to. 
        """
        return self.reference

    def sync_times(self):
        """
        Attempts to convey any extra temporal information from this event to its reference, and vice versa (with the
        more precise of the two times taking precedence).
        """
        times = find_temporals(self.text)
        if len(times) > 0:
            best_time = sorted(times, key=lambda x: x.precision(), reverse=True)[0]
            precision = best_time.precision()

            try:
                other_precision = self.reference.get_best_time().precision()

            except AttributeError:  # There is no best_time on the reference, so anything is better!
                other_precision = 0

            if precision > other_precision:
                self.reference.set_best_time(best_time)

            else:
                best_time = self.reference.get_best_time()


    def get_best_time(self):
        return self.reference.get_best_time()

    def __repr__(self):
        return '<ReferenceEvent %s>' % self.text
