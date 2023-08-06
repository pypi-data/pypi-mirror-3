from zope import interface
from zope import schema


class IDurationGroup(interface.Interface):
    name = schema.TextLine(title=u'Name')
    url = schema.TextLine(title=u'URL')

    def __iter__():
        """Return durations iterator."""

    def __len__():
        """Return number of durations"""


class IDuration(interface.Interface):
    name = schema.TextLine(title=u'Name')
    startdate = schema.Date(title=u'Start Date')
    enddate = schema.Date(title=u'End Date')
    work_hours = schema.Dict(title=u'Dictionary of items with hours')
    state = schema.TextLine(title=u'State of this duration')
    url = schema.TextLine(title=u'URL')
