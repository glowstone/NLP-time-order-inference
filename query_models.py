from util import best_event_match, error


class QueryCollection(object):
    def __init__(self, filename):
        self.queries = []
        self.query_types = [TimeQuery, OrderQuery]
        self.load_query_collection(filename)

    def load_query_collection(self, filename):          
        f = open(filename, 'r')
        line = f.readline()
        while len(line) > 0:                                # Read to end of file
            line = line.split("#")[0].strip()
            if len(line) <= 1:                              # Blank line with newline character
                line = f.readline()
                continue
            query_kinds = filter(lambda x: x.shorthand == line.rstrip(), self.query_types)
            if not len(query_kinds) == 1:
                error("Valid Queries are %s. You used %s" % ([x.shorthand for x in self.query_types], line))

            arguments = []
            for i in range(query_kinds[0].argument_lines):
                arguments.append(f.readline())
            self.queries.append(query_kinds[0](*arguments))     #Instantiate TimeQuery or OrderQuery
            line = f.readline()

    def execute(self, all_events, order_data_store, time_data_store):
        for query in self.queries:
            query.execute(all_events, order_data_store, time_data_store)
           

class Query(object):
    def __init__(self, text):
        self.text = text

class TimeQuery(Query):
    shorthand = 'TIME_QUERY'
    argument_lines = 1
    def __init__(self, event_desc_a):       # TODO this is kind of ugly to have to pass the events in here...
        self.event_desc_a = event_desc_a

    def execute(self, events, order_data_store, time_data_store):
        event = best_event_match(events, self.event_desc_a, 0.10)

        result = time_data_store.query_time(event)
        if result:
            print "%s occured %s" % (event, result)
        else:
            print "Sorry, TimeQuery failed."

class OrderQuery(Query):
    shorthand = 'ORDER_QUERY'
    argument_lines = 2
    def __init__(self, event_desc_a, event_desc_b):
        self.event_desc_a = event_desc_a
        self.event_desc_b = event_desc_b

    def execute(self, events, order_data_store, time_data_store):
        event1 = best_event_match(events, self.event_desc_a, 0.10)
        event2 = best_event_match(events, self.event_desc_b, 0.10)

        # Events descriptions correspond to known events
        if event1 and event2:
            result = order_data_store.query_order_augmented(event1, event2, time_data_store)
            if result:
                print result
            else:
                print "Sorry, OrderQuery failed."
        else:
            if not event1:
                print "Sorry, event description 1 did not correspond to en Event"
            if not event2:
                print "Sorry, event description 2 did not correspond to en Event"