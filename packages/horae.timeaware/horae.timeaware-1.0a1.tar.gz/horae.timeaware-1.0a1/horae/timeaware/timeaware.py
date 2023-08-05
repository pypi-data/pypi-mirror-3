import grok
import operator
import calendar
import math
from datetime import datetime, timedelta

from persistent import Persistent
from persistent.list import PersistentList

from zope import schema
from zope import component
from zope.lifecycleevent import ObjectAddedEvent
from zope.event import notify

from horae.core import container
from horae.core.interfaces import IWorkdays

from horae.timeaware import interfaces


class DatetimeFieldProperty(schema.fieldproperty.FieldProperty):

    def __set__(self, inst, value):
        if isinstance(value, datetime):
            value = datetime(value.year, value.month, value.day, value.hour, value.minute)
        super(DatetimeFieldProperty, self).__set__(inst, value)


class TimeRanges(object):
    """ An object providing fields for storing repeating date time ranges
    """
    grok.implements(interfaces.ITimeRanges)

    date_start = DatetimeFieldProperty(interfaces.ITimeEntry['date_start'])
    date_end = DatetimeFieldProperty(interfaces.ITimeEntry['date_end'])
    repeat = schema.fieldproperty.FieldProperty(interfaces.ITimeEntry['repeat'])
    repeat_until = DatetimeFieldProperty(interfaces.ITimeEntry['repeat_until'])


class TimeEntry(object):
    """ A time entry
    """
    grok.implements(interfaces.ITimeEntry)

    date_start = None
    date_end = None
    repeat = None
    repeat_until = None

    _v_workdays = None

    @property
    def workdays(self):
        if self._v_workdays is None:
            self._v_workdays = component.getUtility(IWorkdays)
        return self._v_workdays

    def _intersect(self, entry, daterange):
        start, end = daterange
        if entry.date_start >= start and entry.date_end <= end:
            return entry
        if entry.date_end <= start or entry.date_start >= end:
            return None
        new = TimeEntry()
        new.date_start = max(entry.date_start, start)
        new.date_end = min(entry.date_end, end)
        return new

    def _next_date_delta(self, date, repeat=None):
        if repeat is None:
            repeat = self.repeat
        if repeat == interfaces.REPEAT_YEARLY:
            return calendar.isleap(date.year) and timedelta(days=366) or timedelta(days=365)
        if repeat == interfaces.REPEAT_MONTHLY:
            f, delta = calendar.monthrange(date.year, date.month)
            return timedelta(days=delta)
        if repeat == interfaces.REPEAT_4WEEKS:
            return timedelta(days=28)
        if repeat == interfaces.REPEAT_WEEKLY:
            return timedelta(days=7)
        if repeat == interfaces.REPEAT_WORKDAYS:
            workdays = self.workdays.workdays()
            i = 1
            while True:
                delta = timedelta(days=i)
                if (date + delta).isoweekday() in workdays:
                    return delta
                i += 1
                if i > 7:
                    return None
            return delta
        if repeat == interfaces.REPEAT_DAILY:
            return timedelta(days=1)
        return None

    def _next_entry_delta(self, entry, repeat=None):
        delta_start = self._next_date_delta(entry.date_start, repeat)
        delta_end = self._next_date_delta(entry.date_end, repeat)
        if delta_start is None or delta_end is None:
            return None
        return max(delta_start, delta_end)

    def _next_entry(self, entry, repeat=None):
        new = TimeEntry()
        delta = self._next_entry_delta(entry, repeat)
        if delta is None:
            return None
        new.date_end = entry.date_end + delta
        new.date_start = entry.date_start + delta
        return new

    def _subtract_entries(self, entry, subtract):
        if entry.hours() <= 0.0:
            return []
        rsubtract = subtract[:]
        while rsubtract:
            sub = rsubtract.pop(0)
            if sub.date_start >= entry.date_end: # subtract entry starts after the entry ends as will all proceeding subtract entries since we sorted them by start date
                break
            if sub.date_end <= entry.date_start: # subtract entry ends before the entry begins proceed to the next one
                continue
            if sub.date_start <= entry.date_start: # subtract entry is at the beginning of the time entry
                if sub.date_end >= entry.date_end: # subtract entry covers the whole time entry
                    return []
                end = TimeEntry()
                end.date_start = sub.date_end
                end.date_end = entry.date_end
                return self._subtract_entries(end, rsubtract[:])
            if sub.date_end >= entry.date_end: # subtract entry is at the end of the time entry
                beginning = TimeEntry()
                beginning.date_start = entry.date_start
                beginning.date_end = sub.date_start
                return self._subtract_entries(beginning, rsubtract[:])
            # subtract entry is in the middle of the time entry
            before = TimeEntry()
            before.date_start = entry.date_start
            before.date_end = sub.date_start
            after = TimeEntry()
            after.date_start = sub.date_end
            after.date_end = entry.date_end
            return self._subtract_entries(before, rsubtract[:]) + self._subtract_entries(after, rsubtract[:])
        return [entry, ]

    def subtract(self, timeaware, daterange=None):
        """ Returns a list of time entries with the ones provided by the timeaware provided subtracted
        """
        entries = self.entries(daterange)
        subtract = timeaware.entries(daterange)
        if not subtract:
            return entries[:]
        subtracted = []
        subtract = sorted(subtract, key=operator.attrgetter('date_start'))
        for entry in entries:
            subtracted.extend(self._subtract_entries(entry, subtract))
        return subtracted

    def __sub__(self, timeaware):
        """ Returns a list of time entries with the ones provided by the timeaware subtracted
            raises a ValueError if the entry is repeating and has no repeat end date set
        """
        return self.subtract(timeaware)

    def hours(self, daterange=None):
        """ Returns the hours of this time entry [in the provided date range]

            Raises a ValueError for infinite repeating events if no daterange is provided
        """
        if self.repeat is None:
            if daterange is None:
                delta = self.date_end - self.date_start
                return ((delta.microseconds + (delta.seconds + delta.days * 24 * 3600) * 10 ** 6) / 10 ** 6) / 3600.0
            else:
                intersected = self._intersect(self, daterange)
                if intersected is None:
                    return 0.0
                return intersected.hours()
        else:
            hours = 0.0
            for entry in self.entries(daterange):
                hours += entry.hours()
            return hours

    def entries(self, daterange=None):
        """ Returns a list of non repeating and non overlapping time entries to cover the provided date range

            Raises a ValueError for infinite repeating events if no daterange is provided
        """
        if daterange is None:
            if self.repeat is None:
                return [self, ]
            elif self.repeat_until is None:
                raise ValueError('daterange', 'daterange required for infinite repeating events')
        if self.repeat is None:
            entry = self._intersect(self, daterange)
            if entry is not None:
                return [entry, ]
            return []
        else:
            entries = []
            if daterange is not None:
                start, end = daterange
                start = max(self.date_start, start)
            else:
                start, end = self.date_start, self.date_end
            if self.repeat_until is not None:
                if daterange is not None:
                    end = min(self.repeat_until, end)
                else:
                    end = self.repeat_until
            entry = TimeEntry()
            delta = start - self.date_start
            if self.repeat == interfaces.REPEAT_YEARLY:
                entry.date_start = self.date_start + (datetime(start.year, 1, 1) - datetime(self.date_start.year, 1, 1))
            if self.repeat == interfaces.REPEAT_MONTHLY:
                month = start.month
                year = start.year
                while True:
                    f, delta = calendar.monthrange(year, month)
                    if start.day <= delta:
                        break
                    month += 1
                    if month > 12:
                        month = 1
                        year += 1
                entry.date_start = datetime(year, month, self.date_start.day, self.date_start.hour, self.date_start.minute, self.date_start.second, self.date_start.microsecond)
            if self.repeat == interfaces.REPEAT_4WEEKS:
                entry.date_start = self.date_start + timedelta(days=math.floor(delta.days / 28.0) * 28.0)
            if self.repeat == interfaces.REPEAT_WEEKLY:
                entry.date_start = self.date_start + timedelta(days=math.floor(delta.days / 7.0) * 7.0)
            if self.repeat == interfaces.REPEAT_WORKDAYS:
                date = self.date_start + timedelta(days=math.floor(delta.days / 7.0) * 7.0 - 1)
                workdays = self.workdays.workdays()
                i = 1
                while True:
                    delta = timedelta(days=i)
                    if (date + delta).isoweekday() in workdays:
                        break
                    i += 1
                    if i > 7:
                        break
                entry.date_start = date + delta
            if self.repeat == interfaces.REPEAT_DAILY:
                entry.date_start = self.date_start + timedelta(days=math.floor(delta.days))
            entry.date_end = entry.date_start + (self.date_end - self.date_start)
            while entry.date_end <= start:
                entry = self._next_entry(entry)
            if entry.date_start > end:
                return entries
            entries.append(self._intersect(entry, daterange))
            entry = self._next_entry(entry)
            while entry.date_start < end and entry is not None:
                entries.append(self._intersect(entry, daterange))
                entry = self._next_entry(entry)
            return flatten_entries(entries)

    def __repr__(self):
        str = '%s - %s' % (self.date_start, self.date_end)
        if self.repeat:
            str += ', %s' % self.repeat
            if self.repeat_until:
                str += ' (%s)' % self.repeat_until
        return str


class PersistentTimeEntry(Persistent, TimeEntry):
    """ A persistent TimeEntry
    """

    _date_start = None
    _date_end = None
    _repeat_until = None

    _v_date_start = None
    _v_date_end = None
    _v_repeat_until = None

    def _get_date(self, name):
        if getattr(self, '_v_' + name, None) is None:
            args = getattr(self, '_' + name, None)
            if args is None:
                return None
            setattr(self, '_v_' + name, datetime(*args))
        return getattr(self, '_v_' + name, None)

    def _set_date(self, name, value):
        setattr(self, '_v_' + name, value)
        if isinstance(value, datetime):
            setattr(self, '_' + name, (value.year, value.month, value.day, value.hour, value.minute, value.second, value.microsecond, value.tzinfo))

    def get_date_start(self):
        return self._get_date('date_start')

    def set_date_start(self, value):
        return self._set_date('date_start', value)
    date_start = property(get_date_start, set_date_start)

    def get_date_end(self):
        return self._get_date('date_end')

    def set_date_end(self, value):
        return self._set_date('date_end', value)
    date_end = property(get_date_end, set_date_end)

    def get_repeat_until(self):
        return self._get_date('repeat_until')

    def set_repeat_until(self, value):
        return self._set_date('repeat_until', value)
    repeat_until = property(get_repeat_until, set_repeat_until)


def flatten_entries(entries):
    """ Function taking a list of :py:class:`horae.timeaware.interfaces.ITimeEntry`
        and returns a new list with all overlapping time entries combined
    """
    entries = sorted(entries, key=operator.attrgetter('date_start'))
    new = []
    while len(entries):
        entry = entries.pop(0)
        if not len(entries):
            new.append(entry)
            break
        next = entries[0]
        if next.date_start > entry.date_end:
            new.append(entry)
            continue
        newentry = TimeEntry()
        newentry.date_start = entry.date_start
        newentry.date_end = max(entry.date_end, next.date_end)
        entries.pop(0)
        entries.insert(0, newentry)
    return new


class TimeAware(object):
    """ An object which is aware of time
    """
    grok.implements(interfaces.ITimeAware)

    _entries = []
    _flatten = True

    def __init__(self):
        self._entries = []

    def hours(self, daterange=None):
        """ Returns the sum of the hours of the contained time entries
        """
        hours = 0.0
        for entry in self.entries(daterange):
            hours += entry.hours()
        return hours

    def __add__(self, timeaware):
        """ Returns a new ITimeAware instance combining the ones to be added
        """
        new = TimeAware()
        new.extend(self._entries[:])
        new.extend(timeaware.objects()[:])
        return new

    def objects(self, daterange=None):
        """ Returns a list of all contained time entries
        """
        if daterange is None:
            if isinstance(self._entries, list):
                return self._entries
            return list(self._entries)
        return [entry for entry in self._entries if len(entry.entries(daterange))]

    def entries(self, daterange=None):
        """ Returns a list of non repeating and non overlapping time entries to cover the provided date range
        """
        entries = []
        for entry in self._entries:
            entries.extend(entry.entries(daterange))
        if self._flatten:
            return flatten_entries(entries)
        return entries

    def extend(self, timeentries):
        """ Extends the object by the provided list of ITimeEntry objects
        """
        self._entries.extend(timeentries)

    def append(self, timeentry):
        """ Extends the object by the provided list of ITimeEntry objects
        """
        self._entries.append(timeentry)

    def subtract(self, timeaware, daterange=None):
        """ Returns a ITimeAware instance of time entries with the ones provided by the ITimeAware provided subtracted
        """
        new = TimeAware()
        for entry in self._entries:
            new.extend(entry.subtract(timeaware, daterange))
        return new

    def remove(self, timeentry):
        """ Removes the given timeentry
        """
        if timeentry in self._entries:
            self._entries.remove(timeentry)

    def __sub__(self, timeaware):
        """ Returns a ITimeAware instance of time entries with the ones provided by the ITimeAware subtracted
            raises a ValueError if one of the entries is repeating and has no repeat end date
            set
        """
        return self.subtract(timeaware)


class TimeEntryContainer(container.Container, TimeAware):
    """ A container for time entries
    """
    grok.implements(interfaces.ITimeEntryContainer)

    def id_key(self):
        return 'timeentry'

    def get_entries(self):
        return self.values()

    def set_entries(self, value):
        pass # not allowed
    _entries = property(get_entries, set_entries)

    objects = TimeAware.objects

    def extend(self, timeentries):
        """ Extends the object by the provided list of ITimeEntry objects
        """
        raise NotImplementedError('Adding new timeentries using the extend method is not allowed')

    def append(self, timeentry):
        """ Extends the object by the provided list of ITimeEntry objects
        """
        raise NotImplementedError('Adding new timeentries using the append method is not allowed')


class TimeEntryFactory(TimeAware, TimeRanges):
    """ A factory for time entries
    """
    grok.implements(interfaces.ITimeEntryFactory)
    factory = TimeEntry

    def get_entries(self):
        if not hasattr(self, '_TimeEntryFactory__entries') or not isinstance(self._TimeEntryFactory__entries, PersistentList):
            self.__entries = PersistentList()
        return self._TimeEntryFactory__entries

    def set_entries(self, value):
        pass # not allowed
    _entries = property(get_entries, set_entries)

    def create(self):
        """ Creates a new time entry from the values currently stored on the object and returns it
            if a start and end date is provided and they are not equal otherwise returns None
        """
        entry = None
        if self.date_start and self.date_end and not self.date_start == self.date_end:
            entry = self.factory()
            entry.date_start = self.date_start
            entry.date_end = self.date_end
            entry.repeat = self.repeat
            entry.repeat_until = self.repeat_until
            self._entries.append(entry)
            notify(ObjectAddedEvent(entry, self, u''))
        if 'date_start' in self.__dict__:
            del self.__dict__['date_start']
        if 'date_end' in self.__dict__:
            del self.__dict__['date_end']
        if 'repeat' in self.__dict__:
            del self.__dict__['repeat']
        if 'repeat_until' in self.__dict__:
            del self.__dict__['repeat_until']
        return entry


class PersistentTimeEntryFactory(TimeEntryFactory):
    """ A factory for persistent time entries
    """
    factory = PersistentTimeEntry
