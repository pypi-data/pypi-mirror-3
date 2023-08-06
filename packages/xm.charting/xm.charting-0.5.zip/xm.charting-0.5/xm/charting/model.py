from xm.charting import interfaces
from zope import interface


class DurationGroup(object):
    interface.implements(interfaces.IDurationGroup)

    def __init__(self, name, url=None):
        self.name = name
        self.url = url
        self._iterations = []

    def __iter__(self):
        return iter(self._iterations)

    def __len__(self):
        return len(self._iterations)


class Duration(object):
    interface.implements(interfaces.IDuration)

    def __init__(self, name, start, end, state=None, url=None):
        self.name = name
        self.startdate = start
        self.enddate = end
        self.work_hours = {}
        self.state = state
        self.url = url
