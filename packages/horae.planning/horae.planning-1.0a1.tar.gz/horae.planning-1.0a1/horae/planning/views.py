import grok
import calendar
from hashlib import sha1
from datetime import datetime, date, timedelta, MINYEAR

from zope import component
from zope.session.interfaces import ISession
from zope.i18n import translate

from plone.memoize import forever
from megrok import navigation
from hurry import query

from horae.core import utils
from horae.core.interfaces import IHorae, ICurrencyFormatter
from horae.auth.utils import getUser
from horae.auth.interfaces import IUser
from horae.search.utils import normalizeDatetime
from horae.layout import layout
from horae.layout.interfaces import IDisplayView, IViewsMenu, IMainActionsMenu
from horae.ticketing import _ as _t
from horae.ticketing.interfaces import IClient, IProject, IMilestone, ITicket
from horae.resources import _ as _r
from horae.resources.interfaces import IGlobalResources, IGlobalResourcesHolder, ICostUnitsHolder, ICostUnits, IPlannedResources, IHumanResource
from horae.timeaware import timeaware

from horae.planning import _
from horae.planning import interfaces
from horae.planning import resource

grok.templatedir('templates')

_marker = object()


class NoMilestone(object):
    id = u'None'
    name = None


class PlanningOverview(layout.View):
    """ Base class of a view rendering a planning overview
    """
    grok.baseclass()
    grok.require('horae.Plan')
    grok.implements(interfaces.ITimeRangedView, IDisplayView)
    grok.name('planning.overview')
    grok.template('overview')
    navigation.menuitem(IViewsMenu, _(u'Planning overview'))
    navigation.menuitem(IMainActionsMenu, _(u'Planning overview'))

    client = None
    project = None
    milestone = None
    ticket = None
    user = None

    default_range = 2
    _resource = _marker
    _costunit = _marker
    _level = None
    _range = None
    _calendar_weeks = None
    _calendar_week_cells = None
    _calendar_days = None
    _calendar_day_cells = None

    # Those are here solely to have them captured by i18ndude
    diagram = _(u'Chart')

    def __call__(self):
        resource.graph.need()
        self.calculate_range()
        self.calculate_rows()
        return super(PlanningOverview, self).__call__()

    @property
    @forever.memoize
    def query(self):
        return component.getUtility(query.query.interfaces.IQuery)

    @property
    @forever.memoize
    def currency(self):
        return component.getMultiAdapter((self.context, self.request), interface=ICurrencyFormatter)

    @property
    def resource(self):
        if self._resource is _marker:
            session = ISession(self.request)
            if self.request.form.get('form.resource', None) is not None:
                session[self.session_key]['resource'] = self.request.form.get('form.resource')
            if session[self.session_key].get('resource', None):
                self._resource = IGlobalResources(utils.findParentByInterface(self.context, IGlobalResourcesHolder)).get_object(session[self.session_key]['resource'])
            else:
                self._resource = None
        return self._resource

    @property
    def costunit(self):
        if self._costunit is _marker:
            session = ISession(self.request)
            if self.request.form.get('form.costunit', None) is not None:
                session[self.session_key]['costunit'] = self.request.form.get('form.costunit')
            if session[self.session_key].get('costunit', None):
                self._costunit = ICostUnits(utils.findParentByInterface(self.context, ICostUnitsHolder)).get_object(session[self.session_key]['costunit'])
            else:
                self._costunit = None
        return self._costunit

    def calculate_range(self):
        end = None
        start = None
        session = ISession(self.request)
        if self.request.form.get('form.start', None) is not None:
            session[self.session_key]['start'] = self.request.form.get('form.start', None)
        if self.request.form.get('form.end', None) is not None:
            session[self.session_key]['end'] = self.request.form.get('form.end', None)
        formatter = self.request.locale.dates.getFormatter('date', 'short')
        calc = component.queryAdapter(self.context, interfaces.ICachedCalculator, 'simple')
        centries, cstart, cend = None, None, None
        try:
            start = formatter.parse(session[self.session_key].get('start'))
            start = datetime(start.year, start.month, start.day)
        except:
            start = interfaces.IEstimatedExecution(self.context, None)
            try:
                centries, cstart, cend = calc.entries(self.context)
            except:
                pass
            if start is not None:
                start = start.start()
            if cstart is not None:
                start = min(start, cstart) if start is not None else cstart
            if start is None:
                start = datetime.now()
            start -= timedelta(days=(self.weeks and 28 or 2))
        try:
            end = formatter.parse(session[self.session_key].get('end'))
            end = datetime(end.year, end.month, end.day)
        except:
            if not IClient.providedBy(self.context) and not IHorae.providedBy(self.context):
                end = interfaces.IEstimatedExecution(self.context, None)
                try:
                    if centries is None:
                        centries, cstart, cend = calc.entries(self.context)
                except:
                    pass
                if end is not None:
                    end = end.end()
                if cend is not None:
                    end = min(end, cend) if end is not None else cend
            if end is not None:
                end += timedelta(days=(self.weeks and 28 or 7))
        if end is None or end <= start:
            i = self.default_range
            year, month = start.year, start.month
            while i:
                month += 1
                if month > 12:
                    year += 1
                    month = 1
                i -= 1
            end = datetime(year, month, min(calendar.monthrange(year, month)[1], start.day))
        if self.weeks:
            start = start - timedelta(days=start.weekday())
            if start.weekday() > 0:
                end = end + timedelta(days=7 - start.weekday())
        self._range = (start, end)

    def range(self):
        """ Returns the range (start date, end date tuple) currently displayed by the view
        """
        return self._range

    def caption(self):
        return _(u'Planning overview')

    @property
    def session_key(self):
        return sha1(self.url(self.context) + '/@@planning.overview').hexdigest()

    @property
    def level(self):
        if self._level is None:
            if IHorae.providedBy(self.context) or IClient.providedBy(self.context):
                self._level = 0
            if IProject.providedBy(self.context):
                self._level = 1
            if IMilestone.providedBy(self.context):
                self._level = 2
            if ITicket.providedBy(self.context):
                self._level = 3
        return self._level

    @property
    def weeks(self):
        return self.level < 3

    def calendar_weeks(self):
        start, end = self.range()
        if self._calendar_weeks is None:
            self._calendar_weeks = []
            start = start - timedelta(days=start.isocalendar()[2] - 1)
            cw = start.isocalendar()[:2]
            cw_last = end.isocalendar()[:2]
            while cw < cw_last:
                self._calendar_weeks.append((cw, (datetime(start.year, start.month, start.day), datetime(start.year, start.month, start.day) + timedelta(days=7))))
                start = datetime(start.year, start.month, start.day) + timedelta(days=7)
                cw = start.isocalendar()[:2]
        return self._calendar_weeks

    def calendar_days(self):
        start, end = self.range()
        if self._calendar_days is None:
            self._calendar_days = []
            while start.date() < end.date():
                self._calendar_days.append((start.date(), (datetime(start.year, start.month, start.day), datetime(start.year, start.month, start.day) + timedelta(days=1))))
                start += timedelta(days=1)
        return self._calendar_days

    def tickets(self):
        if self.ticket is not None:
            return [self.ticket, ]
        start, end = self.range()
        queries = [query.set.AnyOf(('catalog', 'implements'), [ITicket.__identifier__, ]),
                   query.Or(
                       query.And(
                           query.Ge(('planning', 'execution_start'), normalizeDatetime(start)),
                           query.Le(('planning', 'execution_start'), normalizeDatetime(end))
                       ),
                       query.And(
                           query.Ge(('planning', 'forecast_start'), normalizeDatetime(start)),
                           query.Le(('planning', 'forecast_start'), normalizeDatetime(end))
                       )
                   ),
                   query.Or(
                       query.Ge(('planning', 'execution_end'), normalizeDatetime(start)),
                       query.Ge(('planning', 'forecast_end'), normalizeDatetime(start))
                   ),
                   query.Eq(('catalog', 'complete'), 0)]
        if self.client is not None:
            queries.append(query.Eq(('catalog', 'client'), self.client.id))
        if self.project is not None:
            queries.append(query.Eq(('catalog', 'project'), self.project.id))
        if self.milestone is not None:
            queries.append(query.Eq(('catalog', 'milestone'), self.milestone.id))
        if self.resource is not None:
            queries.append(query.set.AnyOf(('planning', 'plannedresources'), [self.resource.id, ]))
        if self.user is not None:
            resources = IGlobalResources(utils.findParentByInterface(self.context, IGlobalResourcesHolder)).objects()
            queries.append(query.set.AnyOf(('planning', 'plannedresources'), [resource.id for resource in resources if IHumanResource.providedBy(resource) and resource.user == self.user.username]))
        if self.resource is None:
            sort_field = ('planning', 'position')
            reverse = 1
        else:
            sort_field = ('planning', 'position_%s' % self.resource.id)
            reverse = 1
        return self.query.searchResults(query.And(*queries), sort_field=sort_field, reverse=reverse)

    def headings(self):
        headings = []
        row1 = []
        row2 = []
        levels = []
        if self.level < 1:
            levels.append(_t(u'Client'))
        if self.level < 2:
            levels.append(_t(u'Project'))
        if self.level < 3 and self.has_milestones:
            levels.append(_t(u'Milestone'))
        levels.append(_t(u'Ticket'))
        for level in levels:
            row1.append({'content': level,
                         'colspan': 2,
                         'cssClass': 'noborder'})
            row2.append({'content': _(u'No'),
                         'cssClass': 'discreet'})
            row2.append({'content': _t(u'Name'),
                         'cssClass': 'discreet'})

        row1.append({'content': _r(u'Resource'),
                     'rowspan': 2})
        row1.append({'content': _r(u'Cost unit'),
                     'rowspan': 2})
        row1.append({'content': _r(u'Estimated work expense'),
                     'rowspan': 2})
        row1.append({'content': _r(u'Hourly rate'),
                     'rowspan': 2})
        if self.has_perweek:
            row1.append({'content': _t('Estimated hours'),
                         'colspan': 2,
                         'cssClass': 'noborder'})
            row2.append({'content': _(u'total'),
                         'cssClass': 'discreet'})
            row2.append({'content': _(u'per week'),
                         'cssClass': 'discreet'})
        else:
            row1.append({'content': _t('Estimated hours'),
                         'rowspan': 2})
        row1.append({'content': _(u'Worked hours'),
                     'rowspan': 2})

        if self.weeks:
            calendar_weeks = self.calendar_weeks()
            row1.append({'content': _(u'CW'),
                         'colspan': len(calendar_weeks),
                         'cssClass': 'cw noborder'})
            current = datetime.now().isocalendar()[:2]
            for week, range in calendar_weeks:
                row2.append({'content': '<time title="%s" date="%s">%s</time>' % (utils.formatDateTime(range[0].date(), self.request, ('date', 'long'), False), range[0].date().isoformat(), week[1]),
                             'cssClass': 'cw discreet' + (current == week and ' current' or '')})
        else:
            current = date.today()
            yearmonth = None
            cols = 0
            for day, range in self.calendar_days():
                if yearmonth is None:
                    yearmonth = (day.year, day.month)
                if (day.year, day.month) != yearmonth:
                    row1.append({'content': '%s %s' % (self.request.locale.dates.calendars['gregorian'].months[yearmonth[1]][0], yearmonth[0]),
                                 'colspan': cols,
                                 'cssClass': 'cw noborder'})
                    yearmonth = (day.year, day.month)
                    cols = 0
                cols += 1
                row2.append({'content': '<time title="%s" date="%s">%s</time>' % (utils.formatDateTime(day, self.request, ('date', 'long'), False), day.isoformat(), day.day),
                             'cssClass': 'cw discreet' + (current == day and ' current' or '')})
            if cols > 0:
                row1.append({'content': '%s %s' % (self.request.locale.dates.calendars['gregorian'].months[yearmonth[1]][0], yearmonth[0]),
                             'colspan': cols,
                             'cssClass': 'cw noborder'})

        headings.append(row1)
        headings.append(row2)
        return headings

    def no_and_name(self, obj, rowspan=None, name=None):
        if isinstance(obj, NoMilestone):
            return [{'content': u'',
                     'rowspan': rowspan},
                    {'content': _(u'No Milestone'),
                     'rowspan': rowspan,
                     'cssClass': 'name'}]
        return [{'content': '<a class="id" href="%s/planning.overview"%s>#%s</a>' % (self.url(obj), (name is not None and ' name="' + name + '"' or ''), obj.id),
                 'rowspan': rowspan},
                {'content': '<a href="%s/planning.overview">%s</a>' % (self.url(obj), obj.name),
                 'rowspan': rowspan,
                 'cssClass': 'name'}]

    def get_calendar_week_cells(self, deadline=None):
        if self._calendar_week_cells is None:
            self._calendar_week_cells = []
            current = datetime.now().isocalendar()[:2]
            for week, daterange in self.calendar_weeks():
                self._calendar_week_cells.append({'content': u'',
                                                  'cssClass': 'cw' + (week == current and ' current' or '')})
        if deadline is not None:
            cells = []
            current = datetime.now().isocalendar()[:2]
            for week, daterange in self.calendar_weeks():
                cells.append({'content': u'',
                              'cssClass': 'cw' + (week == current and ' current' or '') + \
                                                 (deadline > daterange[0] and deadline <= daterange[1] and ' deadline' or '')})
            return cells
        return self._calendar_week_cells

    def get_calendar_day_cells(self, deadline=None):
        if self._calendar_day_cells is None:
            self._calendar_day_cells = []
            current = date.today()
            for day, daterange in self.calendar_days():
                self._calendar_day_cells.append({'content': u'',
                                                 'cssClass': 'cw' + (day == current and ' current' or '')})
        if deadline is not None:
            cells = []
            current = date.today()
            for day, daterange in self.calendar_days():
                cells.append({'content': u'',
                              'cssClass': 'cw' + (day == current and ' current' or '') + \
                                                 (deadline > daterange[0] and deadline <= daterange[1] and ' deadline' or '')})
            return cells
        return self._calendar_day_cells

    def get_planned_resources(self, ticket):
        return [resource for resource in IPlannedResources(ticket).objects() if (self.resource is None or resource.resource.id == self.resource.id) and \
                                                                                (self.costunit is None or resource.costunit.id == self.costunit.id) and \
                                                                                (self.user is None or resource.resource.user == self.user.username)]

    def get_execution_row(self, title, aware, resource, cssClass=u'', deadline=None):
        if self.weeks:
            list = self.calendar_weeks()
            current = datetime.now().isocalendar()[:2]
        else:
            list = self.calendar_days()
            current = date.today()
        has_entry = False
        row = [{'content': u''}] * ((4 - self.level) * 2) + \
              [{'content': title,
                'colspan': 4}] + [{'content': u''}] * 3
        for cmp, daterange in list:
            if interfaces.IEstimatedExecution.providedBy(aware) or interfaces.ICachedEstimatedExecution.providedBy(aware):
                hours = aware.hours(daterange, human_resource=resource.resource.id, costunit=resource.costunit.id)
            else:
                hours = aware.hours(daterange)
            if hours <= 0.0:
                hours = None
            else:
                has_entry = True
            row.append({'content': utils.formatHours(hours, self.request),
                        'cssClass': 'cw' + (hours is not None and ' occupied' or '') + \
                                           (current == cmp and ' current' or '') + \
                                           (deadline is not None and deadline > daterange[0] and deadline <= daterange[1] and ' deadline' or '')})
        if not has_entry:
            return None
        return {'cells': row,
                'cssClass': 'execution ' + cssClass}

    def get_info(self, execution):
        username = execution.user()
        info = ''
        if username is not None:
            user = getUser(username)
            info = user is not None and user.name or username
        message = execution.message().replace('"', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        if message is not None:
            info += (info and ': ' or '') + message
        return info

    def get_object_row(self, obj, level, cssClass=u'', work_expense=None, estimated_hours=None, hours=None, deadline=None):
        row = [{'content': u''}] * ((level - self.level) * 2) + self.no_and_name(obj) + [{'content': u''}] * (8 - level * 2)
        row.append({'content': work_expense is not None and self.currency.format(work_expense, False) or u''})
        row.append({'content': u''})
        row.append({'content': estimated_hours is not None and utils.formatHours(estimated_hours, self.request) or u''})
        row.append({'content': u''})
        row.append({'content': hours is not None and utils.formatHours(hours, self.request) or u''})
        row.extend((self.weeks and self.get_calendar_week_cells(deadline) or self.get_calendar_day_cells(deadline)))
        return {'cells': row,
                'cssClass': cssClass}

    def get_ticket_rows(self, ticket):
        rows = []
        start, end = self.range()
        execution = interfaces.IEstimatedExecution(ticket)
        calculator = component.getAdapter(ticket, interfaces.ICalculator, 'simple')
        deadline = execution.due_date()
        try:
            if int(self.request.form.get('ticket', None)) == ticket.id:
                hide = self.request.form.get('hidehistory', None)
                if hide is not None:
                    try:
                        hide = datetime(*map(int, hide.split(':')))
                        execution.hide_history_entry(hide)
                    except:
                        pass
                show = self.request.form.get('showhistory', None)
                if show is not None:
                    execution.show_history_entries()
        except:
            pass
        ticket_work_expense = 0.0
        ticket_estimated_hours = 0.0
        ticket_hours = 0.0
        resources = self.get_planned_resources(ticket)
        for planned_resource in resources:
            resource = planned_resource.resource
            costunit = planned_resource.costunit
            rkey, cukey = resource.id, costunit.id
            resource_start = len(rows)
            estart, eend = execution.start(human_resource=rkey, costunit=cukey), execution.end(human_resource=rkey, costunit=cukey)

            estimated_hours = planned_resource.hours()
            work_expense = estimated_hours * costunit.rate
            hours = 0.0
            effective = None
            effective_entries = calculator.effective(ticket, resource, costunit)
            if len(effective_entries):
                effective = timeaware.TimeAware()
                effective._flatten = False
                effective.extend(effective_entries)
                hours += effective.hours()
            ticket_work_expense += work_expense
            ticket_estimated_hours += estimated_hours
            ticket_hours += hours
            max_week_hours = calculator.max_week_hours(ticket)
            if max_week_hours is not None:
                self.has_perweek = True

            absence = calculator.absence(resource)
            worktime = calculator.worktime(ticket, resource)

            # Add absences
            absrow = None
            if absence is not None:
                abs = timeaware.TimeAware()
                abs.extend(timeaware.flatten_entries(absence.subtract(absence.subtract(worktime, (start, end)), (start, end)).entries()))
                abs._flatten = False
                absrow = self.get_execution_row(_(u'Absence'), abs, resource, 'absence', deadline)

            # Add planning history
            history = reversed([date for date in execution.history_dates()])
            i = 0
            for date in history:
                i += 1
                current_execution = execution.history_before(date)
                if current_execution is not None:
                    row = self.get_execution_row(_(u'Planned (${date})', mapping={'date': utils.formatDateTime(current_execution.calculated(), self.request, ('dateTime', 'short'))}), current_execution, planned_resource, 'planned', deadline)
                    if row is not None:
                        info = self.get_info(current_execution)
                        if info:
                            row['cells'][(3 - self.level) * 2] = {'content': '<small class="info" title="%s">%s</small>' % (info, translate(_(u'Info'), context=self.request))}
                        row['cells'][(4 - self.level) * 2 - 1] = {'content': '<a href="%s?hidehistory=%s&ticket=%s#ticket%s" class="button button-destructive button-discreet">%s</a>' % (self.request.getURL(), ':'.join(map(str, date.timetuple()[:6] + (date.microsecond,))), ticket.id, ticket.id, translate(_(u'Hide'), context=self.request))}
                        rows.append(row)
            if execution.calculated() != datetime(MINYEAR, 1, 1):
                row = self.get_execution_row(_(u'Planned (${date})', mapping={'date': utils.formatDateTime(execution.calculated(), self.request, ('dateTime', 'short'))}), execution, planned_resource, 'planned current', deadline)
                if row is not None:
                    info = self.get_info(execution)
                    if info:
                        row['cells'][(3 - self.level) * 2] = {'content': '<small class="info" title="%s">%s</small>' % (info, translate(_(u'Info'), context=self.request))}
                    if i < len([date for date in execution.history_dates(True)]):
                        row['cells'][(4 - self.level) * 2 - 1] = {'content': '<a href="%s?showhistory=1&ticket=%s#ticket%s" class="button button-discreet">%s</a>' % (self.request.getURL(), ticket.id, ticket.id, translate(_(u'Show all'), context=self.request))}
                    rows.append(row)

            # Add effective worked time
            if effective is not None:
                row = self.get_execution_row(_(u'Effective'), effective, planned_resource, 'effective', deadline)
                if row is not None:
                    rows.append(row)

            # Add forecasts
            for calc in self.calculators:
                if not calc.available(ticket, planned_resource):
                    continue
                row = self.get_execution_row(calc.title, calc.entries_by_planned_resource(ticket, planned_resource)[0], planned_resource, 'forecast ' + calc.cssClass, deadline)
                if row is not None:
                    rows.append(row)

            if len(rows) > resource_start:

                if absrow is not None:
                    rows.insert(resource_start, absrow)

                row = [{'content': u''}] * ((4 - self.level) * 2) + \
                      [{'content': '<a href="%s/planning.overview">%s</a>' % (self.url(resource), resource.name),
                        'cssClass': 'name'},
                       {'content': costunit.name,
                        'cssClass': 'name'},
                       {'content': self.currency.format(work_expense)},
                       {'content': self.currency.format(costunit.rate)},
                       {'content': utils.formatHours(estimated_hours, self.request)},
                       {'content': utils.formatHours(max_week_hours, self.request)},
                       {'content': utils.formatHours(hours, self.request)}] + (self.weeks and self.get_calendar_week_cells(deadline) or self.get_calendar_day_cells(deadline))
                rows.insert(resource_start, {'cells': row,
                                             'cssClass': 'resource'})
        if len(rows):
            rows.insert(0, self.get_object_row(ticket, 3, 'ticket', ticket_work_expense, ticket_estimated_hours, ticket_hours, deadline))
        return rows

    def get_milestone_rows(self, project, milestone):
        rows = []
        tickets = self.tickets(project.id, milestone.id)
        for ticket in tickets:
            ticket_rows = self.get_ticket_rows(ticket)
            rows.extend(ticket_rows)
        if len(rows) and (not isinstance(milestone, NoMilestone) or self.has_milestones):
            if not isinstance(milestone, NoMilestone):
                self.has_milestones = True
            rows.insert(0, self.get_object_row(milestone, 2, 'milestone'))
        return rows

    def get_project_rows(self, project):
        rows = []
        no_milestone = NoMilestone()
        milestones = self.milestones(project.id)
        for milestone in milestones:
            milestone_rows = self.get_milestone_rows(project, milestone)
            rows.extend(milestone_rows)

        # add tickets with no milestone
        milestone_rows = self.get_milestone_rows(project, no_milestone)
        rows.extend(milestone_rows)

        if len(rows):
            rows.insert(0, self.get_object_row(project, 1, 'project'))
        return rows

    def get_client_rows(self, client):
        rows = []
        projects = self.projects(client.id)
        for project in projects:
            project_rows = self.get_project_rows(project)
            rows.extend(project_rows)
        if len(rows):
            rows.insert(0, self.get_object_row(client, 0, 'client'))
        return rows

    def calculate_rows(self):
        rows = []
        no_milestone = NoMilestone()
        self.calculators = [calculator for name, calculator in component.getAdapters((self.context,), interfaces.ICalculator)]
        self.has_milestones = False
        self.has_perweek = False
        tickets = self.tickets()
        prev_client, prev_project, prev_milestone = None, None, None
        for ticket in tickets:
            ticket_rows = self.get_ticket_rows(ticket)
            if not len(ticket_rows):
                continue
            ticket_row = ticket_rows[0]
            if self.level < 3:
                milestone = ticket.milestone
                milestone_due = None
                if milestone is not None:
                    milestone_due = interfaces.IEstimatedExecution(milestone).due_date()
                else:
                    milestone = no_milestone
                ticket_row['cssClass'] += ' milestone' + str(milestone.id)
                if milestone is not prev_milestone:
                    ticket_rows.insert(0, self.get_object_row(ticket.milestone, 2, 'milestone', deadline=milestone_due))
                    if not isinstance(milestone, NoMilestone):
                        self.has_milestones = True
                prev_milestone = milestone
            if self.level < 2:
                project = utils.findParentByInterface(ticket, IProject)
                ticket_row['cssClass'] += ' project' + str(project.id)
                if project is not prev_project:
                    ticket_rows.insert(0, self.get_object_row(project, 1, 'project', deadline=interfaces.IEstimatedExecution(project).due_date()))
                prev_project = project
            if self.level < 1:
                client = utils.findParentByInterface(project, IClient)
                ticket_row['cssClass'] += ' client' + str(client.id)
                if client is not prev_client:
                    ticket_rows.insert(0, self.get_object_row(client, 0, 'client'))
                prev_client = client
            rows.extend(ticket_rows)
        self._rows = self.adjust_rows(rows)

    def adjust_rows(self, rows):
        if not self.has_milestones or not self.has_perweek:
            for row in rows:
                if not self.has_perweek:
                    if row.get('cssClass', '').startswith('execution'):
                        row['cells'].pop((4 - self.level) * 2 + 1)
                    else:
                        row['cells'].pop((4 - self.level) * 2 + 5)
                if not self.has_milestones and self.level < 3:
                    row['cells'].pop((2 - self.level) * 2)
                    row['cells'].pop((2 - self.level) * 2)
        return rows

    def rows(self):
        return self._rows


class GlobalPlanningOverview(PlanningOverview):
    """ Global planning overview
    """
    grok.context(IHorae)
    grok.implements(interfaces.IResourceCostunitRangedView)


class ClientPlanningOverview(PlanningOverview):
    """ Planning overview of a client
    """
    grok.context(IClient)
    grok.implements(interfaces.IResourceCostunitRangedView)

    @property
    def client(self):
        return self.context


class ProjectPlanningOverview(PlanningOverview):
    """ Planning overview of a project
    """
    grok.context(IProject)
    grok.implements(interfaces.IResourceCostunitRangedView)

    @property
    def project(self):
        return self.context


class MilestonePlanningOverview(PlanningOverview):
    """ Planning overview of a milestone
    """
    grok.context(IMilestone)
    grok.implements(interfaces.IResourceCostunitRangedView)

    @property
    def milestone(self):
        return self.context


class TicketPlanningOverview(PlanningOverview):
    """ Planning overview of a ticket
    """
    grok.context(ITicket)
    grok.implements(interfaces.IResourceCostunitRangedView)

    @property
    def ticket(self):
        return self.context


class ResourcePlanningOverview(PlanningOverview):
    """ Planning overview of a human resource
    """
    grok.context(IHumanResource)

    _level = 0
    weeks = False

    @property
    def resource(self):
        return self.context


class UserPlanningOverview(PlanningOverview):
    """ Planning overview of a user
    """
    grok.context(IUser)
    _level = 0
    weeks = False

    @property
    def user(self):
        return self.context


class ResolveConflicts(layout.View):
    grok.baseclass()
    grok.require('horae.Plan')
    grok.name('resolve-conflicts')
    grok.template('resolveconflicts')


class ResolveTicketConflicts(ResolveConflicts):
    grok.context(ITicket)


class ResolveMilestoneConflicts(ResolveConflicts):
    grok.context(IMilestone)


class ResolveProjectConflicts(ResolveConflicts):
    grok.context(IProject)
