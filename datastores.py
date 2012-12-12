


class TimeDataStore(object):
    def __init__(self):
        self.time_table = {}

    def add_event(self, event):         
        """
        Adds the event as a key in the time_table of the TimeDataStore
        Initializes the list of events that follow as empty.
        """
        if event not in self.time_table:
            self.time_table[event] = {}


    def record_event(self, event, time_object):            # Takes Tommy's time object of some sort?
        """
        Sets the time_object to be the value at the given event key in time_table

        Creates an 'event' key in time_table if it does not exist.
        """
        if event not in self.time_table:
            self.time_table[event] = time_object


    def update_time(self, event, later_event):
        """
        Record the relationship in which prior_event precedes later_event

        Adds later_event to the list of events that follow prior_event
        """
        if event in self.time_table:
            #merged_time = util.merge_time(self.time_table[event], )# Call to merge our date objects if that exists
            merged_time = {}
            self.time_table[event] = merged_time


    def query_time(self, event):
        """
        returns the Date Object representing all learned information about when the specified event occurred.
        If event not found in time_table, returns None
        """
        if event in self.time_table:
            return self.time_table[event]
        else:
            return None


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
        elif b_before_a:
            return "after"
        else:
            return  "not enough info"

    def depth_first_search(self, event_a, event_b):
        """
        The most basic DFS implementation I could think of. Returns True if there's some path that says event_a is 
        before event_b, False otherwise.

        event_a and event_b are instances of AbstractEvent

        returns a boolean
        """
        if event_a == event_b:
            return True
        for event in self.order_table[event_a]:
            if self.depth_first_search(event, event_b):
                return True
        return False

    def __repr__(self):
        return str(self.order_table)
