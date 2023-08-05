import grok
import calendar
from hashlib import sha1
from datetime import datetime, timedelta

from zope import interface
from zope import component
from zope import schema
from zope.i18n import translate
from zope.session.interfaces import ISession

from horae.layout import layout
from horae.layout.interfaces import IDisplayView
from horae.core.interfaces import IWorkdays
from horae.core.utils import formatDateTime

from horae.calendar import _
from horae.calendar import interfaces

grok.templatedir('templates')


class Calendar(layout.View):
    """ A calendar providing a month, week and day view
    """
    grok.context(interface.Interface)
    grok.implements(interfaces.ICalendar, IDisplayView)
    grok.name('calendar')

    _daterange = None

    format = schema.fieldproperty.FieldProperty(interfaces.ICalendar['format'])
    start = schema.fieldproperty.FieldProperty(interfaces.ICalendar['start'])
    navigation = schema.fieldproperty.FieldProperty(interfaces.ICalendar['navigation'])
    nextprevious = schema.fieldproperty.FieldProperty(interfaces.ICalendar['nextprevious'])
    base_url = schema.fieldproperty.FieldProperty(interfaces.ICalendar['base_url'])
    _session_key = schema.fieldproperty.FieldProperty(interfaces.ICalendar['session_key'])
    _start = None

    def __init__(self, context, request):
        super(Calendar, self).__init__(context, request)
        self.session = ISession(self.request)
        self.providers = [provider for name, provider in component.getAdapters((self.context,), interfaces.ICalendarEntries)]
        self.calendar_base = self.url(self.context) + '/calendar'
        self.base_url = self.calendar_base
        self.workdays = component.getUtility(IWorkdays).workdays()

    def get_start(self):
        if self._start is None:
            self._start = self.get('start', None)
            if self._start is not None:
                try:
                    self._start = datetime(*map(int, self._start.split('-')))
                except:
                    self.set('start', None)
            if self._start is None and self.start is not None:
                self._start = self.start
            if self.start is None:
                self._start = datetime.now()
        return self._start

    def set_session_key(self, key):
        self._session_key = key

    def get_session_key(self):
        if not self._session_key:
            return sha1(self.base_url).hexdigest()
        return self._session_key
    session_key = property(get_session_key, set_session_key)

    def get(self, name, default=None):
        if self.request.form.get(self.session_key + '.' + name, None) is not None:
            self.session[self.session_key][name] = self.request.form.get(self.session_key + '.' + name)
        return self.session[self.session_key].get(name, default)

    def set(self, name, value):
        self.session[self.session_key][name] = value

    def entries(self, daterange):
        entries = []
        i = 1
        for provider in self.providers:
            for entry in provider.entries(daterange):
                entries.append((entry, provider, i))
            i += 1
        entries.sort(key=lambda x: x[0].date_start)
        return entries

    def update(self):
        try:
            self.format = self.get('format', self.format)
        except:
            # not a valid format
            pass
        if hasattr(self, self.format + '_calculate'):
            getattr(self, self.format + '_calculate')()
        self.next = getattr(self, self.format + '_next')()
        self.previous = getattr(self, self.format + '_previous')()
        self.caption = getattr(self, self.format + '_caption')()
        self.headings = getattr(self, self.format + '_headings')()
        self.rows = getattr(self, self.format + '_rows')()

    def entry(self, entry, provider, i):
        content, cssClass = provider.render(entry, self.request, self.format)
        return {'content': content,
                'cssClass': provider.cssClass + ' provider' + str(i) + ' ' + cssClass}

    # month methods

    def month_next(self):
        start = self.get_start()
        month = start.month + 1
        if month > 12:
            return datetime(start.year + 1, 1, 1)
        return datetime(start.year, month, 1)

    def month_previous(self):
        start = self.get_start()
        month = start.month - 1
        if month < 1:
            return datetime(start.year - 1, 12, 1)
        return datetime(start.year, month, 1)

    def month_caption(self):
        start = self.get_start()
        return '%s %s' % (self.request.locale.dates.calendars['gregorian'].months[start.month][0], start.year)

    def month_headings(self):
        headings = [{'content': _(u'CW')}, ]
        for i in range(1, 8):
            headings.append({'content': self.request.locale.dates.calendars['gregorian'].days[i][0]})
        return headings

    def month_rows(self):
        start = self.get_start()
        rows = []
        #next = self.month_next()
        prev = self.month_previous()
        prev = datetime(prev.year, prev.month, calendar.monthrange(prev.year, prev.month)[1])
        for week in calendar.monthcalendar(start.year, start.month):
            row1 = []
            row2 = []
            wstart = datetime(start.year, start.month, min([day for day in week if day is not 0]))
            row1.append({
                'content': '<a href="%s?%s.start=%s&%s.format=week">%s</a>' % (self.base_url, self.session_key, wstart.date().isoformat(), self.session_key, wstart.isocalendar()[1]),
                'heading': True,
                'cssClass': 'cw',
                'rowspan': 2
            })
            beginning = True
            i = 0
            for day in week:
                if day is 0:
                    if beginning:
                        i += 1
                        ddate = prev - timedelta(days=week.count(0) - i)
                    else:
                        ddate = ddate + timedelta(days=1)
                else:
                    beginning = False
                    ddate = datetime(start.year, start.month, day)
                row1.append({
                    'content': '<a href="%s?%s.start=%s&%s.format=day">%s</a>' % (self.base_url, self.session_key, ddate.date().isoformat(), self.session_key, ddate.day),
                    'heading': True,
                    'cssClass': (day is 0 and 'leap' or '') + (ddate.isocalendar()[2] in self.workdays and ' workday' or '')
                })
                row2.append({
                    'entries': [self.entry(entry, provider, i) for entry, provider, i in self.entries((ddate, ddate + timedelta(days=1)))]
                })
            rows.append(row1)
            rows.append(row2)
        return rows

    # week methods

    def week_next(self):
        return self.get_start() + timedelta(days=7)

    def week_previous(self):
        return self.get_start() - timedelta(days=7)

    def week_caption(self):
        start = self.get_start()
        return '%s - %s <small>%s %s</small>' % (formatDateTime(start, self.request, ('date', 'long')), formatDateTime(start + timedelta(6), self.request, ('date', 'long')), translate(_(u'CW'), context=self.request), start.isocalendar()[1])

    def week_headings(self):
        return self._week_headings

    def week_rows(self):
        return self._week_rows

    def week_calculate(self):
        self._week_headings = [{'content': _(u'Time')}]
        self._week_rows = []
        start = self.get_start()
        start = datetime(start.year, start.month, start.day) - timedelta(days=start.weekday())
        for minutes in range(0, 24 * 60, 15):
            self._week_rows.append([{'content': formatDateTime(datetime(start.year, start.month, start.day, minutes / 60, minutes - minutes / 60 * 60), self.request, ('time', 'short'), False),
                                     'heading': True,
                                     'cssClass': minutes % 60 == 0 and 'hour' or ''}, ])
        for d in range(0, 7):
            day = start + timedelta(days=d)
            rows, colspan = self.day_get_rows(day)
            for row_id in range(0, len(self._week_rows)):
                self._week_rows[row_id].extend(rows[row_id])
            self._week_headings.append({'content': '<a href="%s?%s.start=%s&%s.format=day">%s</a>' % (self.base_url, self.session_key, day.date().isoformat(), self.session_key, formatDateTime(day, self.request, ('date', 'long'))),
                                        'colspan': colspan})

    # day methods

    def day_next(self):
        return self.get_start() + timedelta(days=1)

    def day_previous(self):
        return self.get_start() - timedelta(days=1)

    def day_caption(self):
        return formatDateTime(self.get_start(), self.request, ('date', 'long'))

    def day_headings(self):
        return self._day_headings

    def day_rows(self):
        return self._day_rows

    def day_get_rows(self, day):
        colspan = 1
        rows = []
        entries = self.entries((day, day + timedelta(days=1)))
        entry_map = {}
        row_id = 0
        for minutes in range(0, 24 * 60, 15):
            row = []
            entry_id = 0
            for entry, provider, i in entries:
                entry_id += 1
                if entry.date_end <= day + timedelta(minutes=minutes):
                    continue
                if entry.date_start > day + timedelta(minutes=minutes):
                    break
                if not entry_id in entry_map:
                    entry_map[entry_id] = {'entry': (entry, provider, i),
                                           'rows': [row_id, ]}
                else:
                    entry_map[entry_id]['rows'].append(row_id)
                row.append(entry_id)
            row_id += 1
            rows.append(row)
        columns = max([len(row) for row in rows] + [1, ])
        for entry_id, entry in entry_map.items():
            colspan = columns / max([len(rows[row_id]) for row_id in entry['rows']])
            cell = self.entry(*entry['entry'])
            cell['colspan'] = colspan
            cell['rowspan'] = len(entry['rows'])
            cell['cssClass'] += ' entry'
            rows[entry['rows'][0]].insert(rows[entry['rows'][0]].index(entry_id), cell)
            rows[entry['rows'][0]].remove(entry_id)
        fill = [columns, ] * len(rows)
        for row_id in range(0, len(rows)):
            rows[row_id] = [cell for cell in rows[row_id] if not isinstance(cell, int)]
            for cell in rows[row_id]:
                if row_id % 4 == 0:
                    cell['cssClass'] += ' hour'
                for r in range(0, cell['rowspan']):
                    fill[r] -= cell['colspan']
            f = len(fill) and fill.pop(0) or 0
            while f > 0:
                f -= 1
                rows[row_id].append({'content': u'',
                                     'cssClass': row_id % 4 == 0 and u'hour' or u''})
            if len(rows[row_id]):
                rows[row_id][-1]['cssClass'] += u' last'
        return rows, columns

    def day_calculate(self):
        self._day_headings = [{'content': _(u'Time')}]
        self._day_rows = []
        start = self.get_start()
        start = datetime(start.year, start.month, start.day)
        for minutes in range(0, 24 * 60, 15):
            self._day_rows.append([{'content': formatDateTime(datetime(start.year, start.month, start.day, minutes / 60, minutes - minutes / 60 * 60), self.request, ('time', 'short'), False),
                                    'heading': True,
                                    'cssClass': minutes % 60 == 0 and 'hour' or ''}, ])
        rows, colspan = self.day_get_rows(start)
        for row_id in range(0, len(self._day_rows)):
            self._day_rows[row_id].extend(rows[row_id])
        self._day_headings.append({'content': '<a href="%s?%s.start=%s&%s.format=day">%s</a>' % (self.base_url, self.session_key, start.date().isoformat(), self.session_key, formatDateTime(start, self.request, ('date', 'long'))),
                                   'colspan': colspan})
