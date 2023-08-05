from zope import interface
from zope import schema

from horae.core.interfaces import IContainer

from horae.timeaware import _

REPEAT_YEARLY = 'horae.core.repeat.yearly'
REPEAT_MONTHLY = 'horae.core.repeat.monthly'
REPEAT_4WEEKS = 'horae.core.repeat.4weeks'
REPEAT_WEEKLY = 'horae.core.repeat.weekly'
REPEAT_WORKDAYS = 'horae.core.repeat.workdays'
REPEAT_DAILY = 'horae.core.repeat.daily'


class ITimeRange(interface.Interface):
    """ An object providing fields for storing a date time range
    """

    date_start = schema.Datetime(
        title=_(u'Start date'),
        required=True
    )

    date_end = schema.Datetime(
        title=_(u'End date'),
        required=True
    )

    @interface.invariant
    def endDateAfterStart(time_entry):
        if time_entry.date_start and time_entry.date_end and time_entry.date_start > time_entry.date_end:
            raise interface.Invalid(_(u'End date before start date'))


class ITimeRanges(ITimeRange):
    """ An object providing fields for storing repeating date time ranges
    """

    repeat = schema.Choice(
        title=_(u'Repeat'),
        vocabulary='horae.timeaware.vocabulary.repeat',
        required=False
    )

    repeat_until = schema.Datetime(
        title=_(u'Repeat until'),
        required=False
    )


class ITimeAware(interface.Interface):
    """ An object which is aware of time
    """

    def hours(daterange=None):
        """ Returns the sum of the hours of the contained time entries
        """

    def __add__(timeaware):
        """ Returns a new ITimeAware instance combining the ones to be added
        """

    def __sub__(timeaware):
        """ Returns a ITimeAware instance of time entries with the ones provided by the ITimeAware subtracted
            raises a ValueError if one of the entries is repeating and has no repeat end date
            set
        """

    def objects(daterange=None):
        """ Returns a list of all contained time entries
        """

    def entries(daterange=None):
        """ Returns a list of non repeating and non overlapping time entries to cover the provided date range
        """

    def extend(timeentries):
        """ Extends the object by the provided list of ITimeEntry objects
        """

    def append(timeentry):
        """ Extends the object by the provided list of ITimeEntry objects
        """

    def subtract(timeaware, daterange=None):
        """ Returns a ITimeAware instance of time entries with the ones provided by the ITimeAware subtracted
        """

    def remove(timeentry):
        """ Removes the given timeentry
        """


class ITimeEntryFactory(ITimeAware, ITimeRanges):
    """ An object which holds time entries
    """

    def create():
        """ Creates a new time entry from the values currently stored on the object and returns it
            if a start and end date is provided and they are not equal otherwise returns None
        """


class ITimeEntryContainer(ITimeAware, IContainer):
    """ A container for time entries
    """


class ITimeEntry(ITimeRanges):
    """ A time entry
    """

    def subtract(timeaware, daterange=None):
        """ Returns a list of time entries with the ones provided by the timeaware provided subtracted
        """

    def __sub__(timeaware):
        """ Returns a list of time entries with the ones provided by the timeaware subtracted
            raises a ValueError if the entry is repeating and has no repeat end date set
        """

    def hours(daterange=None):
        """ Returns the hours of this time entry [in the provided date range]
        """

    def entries(daterange):
        """ Returns a list of non repeating and non overlapping time entries to cover the provided date range
        """
