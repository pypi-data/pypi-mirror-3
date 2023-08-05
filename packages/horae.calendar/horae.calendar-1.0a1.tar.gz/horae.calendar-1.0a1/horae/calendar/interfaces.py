from zope import interface
from zope import schema


class ICalendar(interface.Interface):
    """ A calendar view
    """

    format = schema.Choice(
        default='month',
        values=('month', 'week', 'day')
    )
    start = schema.Date()
    navigation = schema.Bool(
        default=True
    )
    nextprevious = schema.Bool(
        default=True
    )
    base_url = schema.URI()
    session_key = schema.ASCIILine()

    def __call__():
        """ Renders the calendar
        """


class ICalendarEntries(interface.Interface):
    """ Entries to be displayed in the calendar
    """

    cssClass = interface.Attribute('The css class to be set on entries of this provider')

    def render(entry, request, format):
        """ Renders the given entry
        """

    def entries(daterange):
        """ Returns a list of non repeating and non overlapping time entries to cover the provided date range
        """
