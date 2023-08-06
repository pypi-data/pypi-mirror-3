import calendar
from xml.dom import minidom
from datetime import date
from datetime import timedelta

ONEWEEK = timedelta(days=7)
ONEDAY = timedelta(days=1)
ONEMONTH = timedelta(days=28)
TWOMONTHS = timedelta(days=ONEMONTH.days*2)
THREEMONTHS = timedelta(days=ONEMONTH.days*3)


def make_id(text):
    s = ''
    for x in text:
        if x.isalpha():
            s += x.lower()
        elif x.isdigit():
            s += x
        elif not s.endswith('-'):
            s += '-'

    if s.endswith('-'):
        s = s[:-1]

    return s


def total_days(d1, d2):
    if d1 > d2:
        d = d1 - d2
    else:
        d = d2 - d1

    return d.days


class HTMLGanttRenderer(object):

    now_factory = staticmethod(date.today)
    max_width = 600

    def __init__(self, duration_groups):
        self.duration_groups = duration_groups

    def render(self):
        impl = minidom.getDOMImplementation()
        self.doc = doc = impl.createDocument(None, "top", None)
        duration_groups = self.duration_groups

        self.table = table = doc.createElement('table')
        table.setAttribute('class', 'gantt-chart')
        table.setAttribute('cellspacing', '0')
        table.setAttribute('cellpadding', '0')

        thead = doc.createElement('thead')
        table.appendChild(thead)
        tr = doc.createElement('tr')
        tr.setAttribute('class', 'time-row')
        thead.appendChild(tr)

        th = doc.createElement('th')
        tr.appendChild(th)
        th.appendChild(doc.createTextNode(' '))

        earliest = self.now_factory()
        currentstartweek = earliest
        # find the monday of "this" week
        while calendar.weekday(currentstartweek.year, currentstartweek.month,
                               currentstartweek.day) != 0:
            currentstartweek -= ONEDAY

        # need to figure out some scaling by seeing how many items
        # and earliest/latest dates
        latest = earliest
        for duration_group in duration_groups:
            for duration in duration_group:
                if duration.startdate is not None and \
                       duration.startdate < earliest:
                    earliest = duration.startdate
                if duration.enddate is not None and duration.enddate > latest:
                    latest = duration.enddate

        # make sure the first day is the first monday before (or on) the
        # earliest date
        while calendar.weekday(earliest.year, earliest.month,
                               earliest.day) != 0:
            earliest -= ONEDAY
        # make sure the last day is the last sunday after (or on) the latest
        # date
        while calendar.weekday(latest.year, latest.month, latest.day) != 6:
            latest += ONEDAY

        if earliest < (currentstartweek - ONEMONTH):
            earliest = currentstartweek - ONEMONTH

        if latest > (currentstartweek + THREEMONTHS):
            latest = currentstartweek + THREEMONTHS

        self.earliest = earliest
        self.latest = latest

        days = total_days(earliest, latest)
        day_size = int(self.max_width / days) # how many pixels is one day?
        self.day_size = day_size

        th = doc.createElement('th')
        tr.appendChild(th)
        div = doc.createElement('div')
        th.appendChild(div)
        div.setAttribute('style', 'height: 2em; position: relative; ' + \
                                  'width: %ipx' % self.max_width)
        div.setAttribute('class', 'timeline')

        somedate = earliest
        weekwidth = day_size * 7
        totalwidth = 0
        weeks = {}
        while somedate < latest:
            weekdiv = doc.createElement('div')
            div.appendChild(weekdiv)
            weekdiv.setAttribute('class', 'week')
            w = weekwidth
            if totalwidth + w > self.max_width:
                w = self.max_width - totalwidth
            weekdiv.setAttribute('style',
                                 'overflow: hidden; height: 2em; ' + \
                                 'position: absolute; bottom: 0; ' + \
                                 'left: %ipx; width: %ipx'
                                 % (totalwidth, (w-5)))
            weekdiv.appendChild(doc.createTextNode(str(somedate)))
            weeks[somedate] = {}
            somedate += ONEWEEK
            totalwidth += w


        self.tbody = tbody = self.tbody = doc.createElement('tbody')
        table.appendChild(tbody)

        self._generate_duration_rows()
        self._generate_hours_rows(weeks)

        return table.toprettyxml('  ')

    def _build_member_structure(self, weeks):
        # the main part of complication here is that we need to
        # setup a data structure where we can iterate over members
        # first and then by weeks

        # first off we need a complete list of all members that have any
        # hours during the displayed weeks
        members = {}
        for dg in self.duration_groups:
            for d in dg:
                for w in d.work_hours:
                    members[w] = {}

        # next we need to assign a 0 value to each week for each member
        for startdate in weeks:
            for memberid, w in members.items():
                w[startdate] = 0.0

        # Now we finally go through the weeks and update the member's
        # hours based on averaging.
        # The way the averaging works is:
        #   1. iterate over weeks
        #     a) iterate over each duration (iteration) period
        #       i) figure out the average hours spent by a member on that
        #          iteration for one day
        #       ii) figure out how many days of the iteration fall within
        #           the date range we're looking at
        #       iii) multiply days times avg and add it to the member's
        #            total hours for that week across all iterations
        for startdate, week in weeks.items():
            enddate = startdate + timedelta(days=6)

            for dg in self.duration_groups:
                for d in dg:
                    if d.enddate is not None and d.startdate is not None \
                           and startdate < d.enddate and enddate > d.startdate:
                        avg = {}
                        durationdays = total_days(d.startdate, d.enddate)
                        for memberid, work_hours in d.work_hours.items():
                            avg[memberid] = float(work_hours) \
                                            / float(durationdays)
                        d1 = startdate
                        if d.startdate > d1:
                            d1 = d.startdate
                        d2 = enddate
                        if d.enddate < d2:
                            d2 = d.enddate
                        days = total_days(d2, d1)

                        for memberid in d.work_hours:
                            cur = week.get(memberid, 0.0)
                            weektotal = cur + (days * avg[memberid])
                            week[memberid] = weektotal
                            members[memberid][startdate] = weektotal
        return members

    def _generate_hours_rows(self, weeks):
        members = self._build_member_structure(weeks)

        tbody = self.tbody
        doc = self.doc

        # now that we've built the complicated data structure, just
        # iterate over everything and build up the HTML
        tr = None
        for memberid in sorted(members):
            tr = doc.createElement('tr')
            tbody.appendChild(tr)
            tr.setAttribute('class', 'member')

            td = doc.createElement('td')
            td.setAttribute('class', 'left-col')
            tr.appendChild(td)
            td.appendChild(doc.createTextNode(memberid))

            td = doc.createElement('td')
            tr.appendChild(td)

            div = doc.createElement('div')
            td.appendChild(div)
            div.setAttribute('style', 'height: 2em; width: %ipx; ' \
                                      'position: relative' % self.max_width)

            weekwidth = self.day_size * 7
            totalwidth = 0
            for somedate in sorted(members[memberid]):
                hours = members[memberid][somedate]
                weekdiv = doc.createElement('div')
                div.appendChild(weekdiv)
                weekdiv.setAttribute('class', 'week')
                w = weekwidth
                if totalwidth + w > self.max_width:
                    w = self.max_width - totalwidth
                weekdiv.setAttribute('style',
                                     'overflow: hidden; height: 2em; ' + \
                                     'position: absolute; ' + \
                                     'left: %ipx; width: %ipx'
                                     % (totalwidth, (w-5)))
                s = '%.1f' % hours
                weekdiv.appendChild(doc.createTextNode(s))
                totalwidth += w

        if tr is not None:
            tr.setAttribute('class', tr.getAttribute('class') + ' last')

    def _generate_duration_rows(self):
        tr = None
        tbody = self.tbody
        doc = self.doc
        earliest = self.earliest
        latest = self.latest
        day_size = self.day_size

        for duration_group in self.duration_groups:
            tr = doc.createElement('tr')
            tbody.appendChild(tr)

            td = doc.createElement('td')
            tr.appendChild(td)
            n = doc.createTextNode(duration_group.name)
            if duration_group.url:
                link = doc.createElement('a')
                link.setAttribute('href', duration_group.url)
                link.appendChild(n)
                n = link
            td.appendChild(n)
            td.setAttribute('class', 'left-col')

            td = doc.createElement('td')
            tr.appendChild(td)
            td.setAttribute('class', 'duration-group-wrapper')

            div = doc.createElement('div')
            td.appendChild(div)
            div.setAttribute('style', 'width: %ipx' % self.max_width)
            div.setAttribute('class', 'duration-group')

            rows = []
            for duration in duration_group:
                end = duration.enddate
                start = duration.startdate
                if end is not None and start is not None:
                    if ((start > latest and end > latest)
                        or (start < earliest and end < earliest)):
                        continue
                end = end or latest
                start = start or earliest

                found = None
                for row in rows:
                    if len(row) == 0:
                        continue

                    lastend = row[-1].enddate or latest

                    if start >= lastend:
                        found = row
                        break

                if found is None:
                    found = []
                    rows.append(found)

                found.append(duration)

            for row in rows:
                durdiv = doc.createElement('div')
                div.appendChild(durdiv)
                durdiv.setAttribute('class', 'duration')

                curearliest = earliest
                curlatest = latest
                for duration in row:
                    start = duration.startdate
                    if start is None or start < curearliest:
                        start = curearliest
                    end = duration.enddate
                    if end is None or end > curlatest:
                        end = curlatest

                    if end < start:
                        start = curearliest
                        end = curlatest

                    # always include the actual day we end on
                    end += ONEDAY

                    days = total_days(curearliest, start)
                    pixels = int(days * day_size)
                    if days > 0:
                        leading = doc.createElement('div')
                        durdiv.appendChild(leading)
                        leading.appendChild(doc.createTextNode('space'))
                        leading.setAttribute('class', 'space')
                        s = 'float: left; width: %ipx' % pixels
                        leading.setAttribute('style', s)

                    bar = doc.createElement('div')
                    durdiv.appendChild(bar)
                    n = doc.createTextNode(duration.name)
                    if duration.url:
                        link = doc.createElement('a')
                        link.appendChild(n)
                        link.setAttribute('href', duration.url)
                        linktitle = ''
                        if duration.startdate:
                            linktitle = str(duration.startdate) + ' - '
                        if duration.enddate:
                            linktitle += str(duration.enddate)
                        if linktitle.endswith(' - '):
                            linktitle = linktitle[:-3]
                        link.setAttribute('title', linktitle)
                        n = link
                    bar.appendChild(n)
                    c = 'bar'
                    if (duration.enddate is None
                        or duration.startdate is None
                        or duration.enddate < duration.startdate):
                        c += ' invalid-date'
                    if duration.state:
                        c += ' ' + make_id(duration.state)
                    bar.setAttribute('class', c)
                    days = total_days(start, end)
                    pixels = int(days * day_size)
                    bar.setAttribute('style', 'float: left; width: %ipx' % pixels)
                    curearliest = end

                br = doc.createElement('br')
                durdiv.appendChild(br)
                br.setAttribute('style', 'clear: both')

        # get last table row
        if tr is not None:
            tr.setAttribute('class', 'last')


class GanttChartBuilder(object):

    renderers = {'html': HTMLGanttRenderer}

    def __init__(self):
        self.duration_groups = []

    def generate(self, render_type):
        builder = self.renderers[render_type](self.duration_groups)
        return builder.render()

    def add_duration_group(self, d):
        self.duration_groups.append(d)


def generate_chart(duration_groups, render_type='html'):
    """Generate the HTML for a gantt chart."""

    builder = GanttChartBuilder()

    for duration_group in duration_groups:
        builder.add_duration_group(duration_group)

    return builder.generate(render_type)
