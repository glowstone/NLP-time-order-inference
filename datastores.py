


class TimeDataStore(object):
    def __init__(self):
        self.time_table = {}


class OrderDataStore(object):
    def __init__(self):
        self.order_table = {}

    def get_events(self):
        """
        returns the list of all events for which ordering relationships were recorded
        """
        return self.order_tables.keys()


    def add_event(self, event):
        """
        Adds the event as a key in the order_table of the OrderDataStore
        Initializes the list of events that follow as empty.
        """
        if event not in self.order_table:
            self.order_table[event] = []


    def record_order(self, prior_event, later_event):
        """
        Record the relationship in which prior_event precedes later_event
        Adds later_event to the list of events that follow prior_event
        """
        self.order_table[prior_event].append(later_event)


    def query_order(self, event_a, event_b):
        """
        returns string X drawn from 'before', 'after', 'conflicting', 'not enough info' to 
        describe whether event_a happens X event_b.
        """
        a_before_b = event_b in self.order_table[event_a]
        b_before_a = event_a in self.order_table[event_b]
        if a_before_b and b_before_a:
            return "conflicting"
        elif a_before_b:
            return "before"
        elif b_after_a:
            return "after"
        else:
            return  "not enough info"

    def __repr__(self):
        return str(self.order_table)
