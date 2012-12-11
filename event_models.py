from util import extract_entities
from find_temporals import find_temporals
from util import stanford_parse
from nltk.tree import ParentedTree


class AbstractEvent(object):
    def __init__(self, tree):
        self.tree = tree
        self.text = " ".join(tree.leaves())
        self.pos_tagged = tree.pos()
        self.entities = extract_entities(self)

    def __repr__(self):
        return '<AbstractEvent %s>' % id(self)


class Event(AbstractEvent):
    def __init__(self, tree):
        super(Event, self).__init__(tree)
        self.absolute_times = find_temporals(self.text)

    def __repr__(self):
        return '<Event %s>' % self.text


class ReferenceEvent(AbstractEvent):
    def __init__(self, tree):
        super(ReferenceEvent, self).__init__(tree)
        self.reference_times = []               # Estimate of time of the referred to Event

    def __repr__(self):
        return '<ReferenceEvent %s>' % self.text

    def add_reference(self, event):
        self.reference = event


# Just for testing
test_events = [Event(ParentedTree(stanford_parse("Eisenhower joined the 1919 Motor Transport Corps convoy at Frederick, Maryland, after the 1st days travel"))),
               Event(ParentedTree(stanford_parse("Eisenhower was promoted to the permanent rank of lieutenant colonel in 1936"))),
               Event(ParentedTree(stanford_parse("John went to the store at 9:00 am on February 13, 2003")))]