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
    def __init__(self, tree):
        super(Event, self).__init__(tree)
        self.absolute_times = find_temporals(self.text)
        if len(self.absolute_times) > 0:
            self.best_time = sorted(self.absolute_times, key=lambda x: x.precision(), reverse=True)[0]
        else:
            self.best_time = None

    def __repr__(self):
        return '<Event %s>' % self.text


class ReferenceEvent(AbstractEvent):
    def __init__(self, tree, event):
        super(ReferenceEvent, self).__init__(tree)
        self.reference = event
        self.reference_times = []               # Estimate of time of the referred to Event
        self.sync_times()

    def add_reference(self, event):
        self.reference = event

    def sync_times(self):
        """
        Attempts to convey any extra temporal information from this event to its reference, and vice versa (with the
        more precise of the two times taking precedence).
        """
        times = find_temporals(self.text)
        if len(times) > 0:
            self.best_time = sorted(times, key=lambda x: x.precision(), reverse=True)[0]
            precision = self.best_time.precision()
            try:
                other_precision = self.reference.best_time.precision()
            except AttributeError:  # There is no best_time on the reference, so anything is better!
                other_precision = 0
            if precision > other_precision:
                self.reference.best_time = self.best_time
            else:
                self.best_time = self.reference.best_time
        else:
            if self.reference.best_time:
                self.best_time = self.reference.best_time
            else:
                self.best_time = None
                

    def __repr__(self):
        return '<ReferenceEvent %s>' % self.text


# Just for testing
test_events = [Event(ParentedTree(stanford_parse("Eisenhower joined the 1919 Motor Transport Corps convoy at Frederick, Maryland, after the 1st days travel"))),
               Event(ParentedTree(stanford_parse("Eisenhower was promoted to the permanent rank of lieutenant colonel in 1936"))),
               Event(ParentedTree(stanford_parse("John went to the store at 9:00 am on February 13, 2003")))]
