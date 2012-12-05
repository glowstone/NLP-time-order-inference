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
    def __init__(self, event_desc_a):
        self.event_desc_a = event_desc_a

    def execute(self):
        pass

class OrderQuery(Query):
    shorthand = 'ORDER_QUERY'
    argument_lines = 2
    def __init__(self, event_desc_a, event_desc_b):
        self.event_desc_a = event_desc_a
        self.event_desc_b = event_desc_b

    def execute(self):
        pass