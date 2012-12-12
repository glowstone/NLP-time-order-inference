
from event_models import AbstractEvent, Event, ReferenceEvent

class TimeDataStore(object):
    def __init__(self):
        self.time_table = {}

    def add_event(self, event):         
        """
        Adds the event as a key in the time_table of the TimeDataStore
        Initializes the list of events that follow as empty.
        """
        if event not in self.time_table:
            self.time_table[event] = None


    def get_events(self):
        """
        returns the list of all events for which time information was recorded
        """
        return self.time_table.keys()


    def record_event(self, event, time_object):            # Takes Tommy's time object of some sort?
        """
        Sets the time_object to be the value at the given event key in time_table

        Creates an 'event' key in time_table if it does not exist.
        """
        self.time_table[event] = time_object


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
        return self.order_table.keys()

    def following_events(self, event):
        """
        returns the list of events that follow the given event if found, otherwise []
        """
        if event in self.order_table:
            return self.order_table[event]
        else:
            return []


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
        self.order_table[prior_event.get_real_event()].append(later_event.get_real_event())


    def query_order(self, event_a, event_b):
        """
        returns string X drawn from 'before', 'after', 'conflicting', 'not enough info' to 
        describe whether event_a happens X event_b based on the order_data_store information.
        """
        a_before_b = self.depth_first_search(event_a, event_b)
        b_before_a = self.depth_first_search(event_b, event_a)
        if a_before_b and b_before_a:
            return "Ordering information about these events conflicts: %s %s" % (event_a, event_b)
        elif a_before_b:
            return "%s occurred before %s" % (event_a, event_b)
        elif b_before_a:
            return "%s occurred after %s" % (event_a, event_b)
        else:
            return  "Not enough info to determine order between %s and %s" % (event_a, event_b)


    def query_order_augmented(self, event_a, event_b, time_data_store):
        """
        Describes whether event_a or event_b happened first using the order_data_store and 
        using augmenting information from the time_data_store if available for both events
        and if one time is greater
        Otherwise, uses infers the order based on order_data_store.

        returns string X drawn from 'before', 'after', 'conflicting', 'not enough info' to 
        """
        if time_data_store.query_time(event_a) and time_data_store.query_time(event_b):
            time_a = time_data_store.query_time(event_a)
            time_b = time_data_store.query_time(event_b)
            if time_a > time_b:
                return "%s occurred before %s" % (event_a, event_b)
            elif time_a < time_b:
                return "%s occurred after %s" % (event_a, event_b)
            else:
                return self.query_order(event_a, event_b)
        else:
            return self.query_order(event_a, event_b)


    def depth_first_search(self, event_a, event_b, count=0):
        """
        The most basic DFS implementation I could think of. Returns True if there's some path 
        that says event_a is before event_b, False otherwise.

        event_a and event_b are instances of AbstractEvent

        returns a boolean
        """
        if count >= 10:                # Don't search more than 10 levels deep
            return False
        if event_a == event_b:
            return True
        for event in self.order_table[event_a]:
            count+=1
            if self.depth_first_search(event, event_b, count):
                return True
        return False

    def is_logical(self):
        """
        Iterates over the entire ordre_data_store order_store to look for 
        conflicts which indicate logical inconsistences in the processed text.

        returns True if no conflicts found, False if logical conflict found
        """
        # A -> [B]
        # B -> [A]
        for event_a in self.get_events():
            for event_b in self.get_events():
                if event_a != event_b:
                    a_before_b = self.depth_first_search(event_a, event_b)
                    b_before_a = self.depth_first_search(event_b, event_a)
                    if a_before_b and b_before_a:
                        print event_a
                        print event_b
                        return False
        return True

    def __repr__(self):
        return str(self.order_table)
