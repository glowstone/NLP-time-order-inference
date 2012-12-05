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
        self.reference_times = []               # Estimate of time of the referred to Event

    def __repr__(self):
        return '<ReferenceEvent %s>' % id(self)