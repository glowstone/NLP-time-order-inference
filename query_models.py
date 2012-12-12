from util import best_event_match


class QueryCollection(object):
    def __init__(self, filename):
        self.queries = []
        self.query_types = [TimeQuery, OrderQuery]
        self.load_query_collection(filename)

    def load_query_collection(self, filename):          
        f = open(filename, 'r')
        line = f.readline()
        while len(line) > 0:                                # Read to end of file
            if len(line) == 1:                              # Blank line with newline character
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

    def execute(self):
        for query in self.queries:
            query.execute()


class Query(object):
    def __init__(self):
        pass

class TimeQuery(Query):
    shorthand = 'TIME_QUERY'
    argument_lines = 1
    def __init__(self, events, event_desc_a):       # TODO this is kind of ugly to have to pass the events in here...
        self.events = events
        self.event_desc_a = event_desc_a

    def execute(self):
        event = best_event_match(self.events, self.event_desc_a, 0.10)
        if event:
            time = event.best_time
            if not time:
                return "No time estimate for this event"
            return str(time)
        else:
            return None

class OrderQuery(Query):
    shorthand = 'ORDER_QUERY'
    argument_lines = 2
    def __init__(self, events, event_desc_a, event_desc_b):
        self.events = events
        self.event_desc_a = event_desc_a
        self.event_desc_b = event_desc_b

    def execute(self):
        event1 = best_event_match(self.events, self.event_desc_a, 0.10)
        event2 = best_event_match(self.events, self.event_desc_b, 0.10)

        print event1
        print event2

        if event1 and event2:
            # If we can do the comparison based on absolute times, then do that
            if event1.absolute_times and event2.absolute_times:
                if event1.absolute_times[0] > event2.absolute_times[0]:
                    return "%s happened before %s" % (event2, event1)
                elif event1.absolute_times[0] < event2.absolute_times[0]:
                    return "%s happened before %s" % (event1, event2)
                else:
                    return "%s and %s happend at the same time, %s" % (event1, event2, event1.absolute_times[0])
        else:
            return None