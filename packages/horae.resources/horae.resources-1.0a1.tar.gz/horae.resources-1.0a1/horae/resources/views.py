import grok
import calendar
import operator
from hashlib import sha1
from datetime import datetime, timedelta, date

from grokcore import message
from zope import component
from zope import schema
from zope.i18n import translate
from zope.formlib.widget import renderElement
from zope.security import checkPermission
from zope.session.interfaces import ISession
from megrok import navigation

from horae.core import utils
from horae.core.interfaces import ITextIdManager, ICurrencyFormatter
from horae.layout import _ as _l
from horae.layout import layout
from horae.layout import objects
from horae.layout import viewlets
from horae.layout.interfaces import IGlobalManageMenu, IContextualManageMenu, IActionsMenu, IObjectTableActionsProvider
from horae.timeaware import timeaware
from horae.timeaware import vocabulary
from horae.timeaware.interfaces import ITimeEntryContainer, ITimeEntry
from horae.ticketing.interfaces import ITicket

from horae.resources import _
from horae.resources import interfaces
from horae.resources import resources

# Resources


class Resources(objects.ObjectOverview):
    """ Overview of global resources
    """
    grok.context(interfaces.IGlobalResourcesHolder)
    grok.name('resources')
    navigation.sitemenuitem(IGlobalManageMenu, _(u'Resources'))

    label = _(u'Resources')
    add_label = _(u'Add resource')
    columns = [('name', _(u'Name')), ('description', _(u'Description')), ('type', _(u'Type')), ('actions', u'')]
    container_iface = interfaces.IGlobalResources

    def row_factory(self, object, columns, request):
        row = super(Resources, self).row_factory(object, columns, request)
        row.update({
            'name': object.name,
            'description': object.description,
            'type': object.type})
        return row

    def add(self):
        return self.url(self.container) + '/add-resource'

    def update(self):
        super(Resources, self).update()
        normalizer = component.getUtility(ITextIdManager)
        types = component.getUtility(interfaces.IResourceTypes).types()
        self.types = [dict(value=normalizer.normalize(type.type),
                           title=type.type) for type in types]


class AddResource(layout.AddForm):
    """ Add form of a resource
    """
    grok.context(interfaces.IGlobalResources)
    grok.require('horae.Manage')
    grok.name('add-resource')

    def __call__(self, type=None):
        self.type = self._findType(type)
        if self.type is not None:
            self.form_fields = grok.AutoFields(self.type).omit('id')
            normalizer = component.getUtility(ITextIdManager)
            self.additional = renderElement('input',
                                            type='hidden',
                                            name='type',
                                            value=normalizer.normalize(self.type.type))
        else:
            self.redirect(self.cancel_url())
        return super(AddResource, self).__call__()

    def _findType(self, type):
        if type is None:
            return None
        normalizer = component.getUtility(ITextIdManager)
        types = component.getUtility(interfaces.IResourceTypes).types()
        for t in types:
            if normalizer.normalize(t.type) == type:
                return t

    def object_type(self):
        return self.type.type

    def cancel_url(self):
        return self.url(self.context.__parent__) + '/resources'

    def next_url(self, obj=None):
        return self.cancel_url()

    def create(self, **data):
        return self.type()

    def add(self, obj):
        self.context.add_object(obj)


class EditResource(objects.EditObject):
    """ Edit form of a resource
    """
    grok.context(interfaces.IGlobalResources)
    grok.name('edit-resource')

    overview = 'resources'

    def object_type(self):
        return _(u'Resource')


class DeleteResource(objects.DeleteObject):
    """ Delete form of a resource
    """
    grok.context(interfaces.IGlobalResources)
    grok.name('delete-resource')

    overview = 'resources'

    def object_type(self):
        return _(u'Resource')


class ResourceActionsProvider(grok.MultiAdapter):
    """ Action provider for resources adding buttons to edit and delete
        the resource and view planned work time, absence and work time of
        the resource
    """
    grok.adapts(interfaces.IResource, Resources)
    grok.implements(IObjectTableActionsProvider)
    grok.name('horae.resources.objecttableactions.resource')

    def __init__(self, context, view):
        self.context = context
        self.view = view

    def actions(self, request):
        container_url = self.view.url(self.view.container)
        actions = [{'url': container_url + '/edit-resource?id=' + str(self.context.id),
                    'label': translate(_(u'Edit'), context=request),
                    'cssClass': ''},
                   {'url': container_url + '/delete-resource?id=' + str(self.context.id),
                    'label': translate(_(u'Delete'), context=request),
                    'cssClass': 'button-destructive delete'}]
        if interfaces.IPlannedWorkTimeHolder.providedBy(self.context):
            actions.append({'url': grok.url(request, interfaces.IPlannedWorkTime(self.context)),
                            'label': translate(_(u'Planned work time'), context=request),
                            'cssClass': 'button-alternative'})
        if interfaces.IAbsenceHolder.providedBy(self.context):
            actions.append({'url': grok.url(request, interfaces.IAbsence(self.context)),
                            'label': translate(_(u'Absence'), context=request),
                            'cssClass': 'button-alternative'})
        if interfaces.IEffectiveWorkTimeHolder.providedBy(self.context):
            actions.append({'url': grok.url(request, interfaces.IEffectiveWorkTime(self.context)),
                            'label': translate(_(u'Work time'), context=request),
                            'cssClass': 'button-alternative'})
        return actions


class PlannedWorkTime(grok.View):
    """ Overview of planned work time
    """
    grok.context(interfaces.IPlannedWorkTimeHolder)
    grok.name('plannedworktime')
    grok.require('horae.Manage')
    navigation.menuitem(IActionsMenu, _(u'Planned work time'))

    def render(self):
        return self.redirect(self.url(interfaces.IPlannedWorkTime(self.context)))


class Absence(grok.View):
    """ Overview of absences
    """
    grok.context(interfaces.IAbsenceHolder)
    grok.name('absence')
    grok.require('horae.Manage')
    navigation.menuitem(IActionsMenu, _(u'Absence'))

    def render(self):
        return self.redirect(self.url(interfaces.IAbsence(self.context)))


class WorkTime(grok.View):
    """ Overview of work time
    """
    grok.context(interfaces.IEffectiveWorkTimeHolder)
    grok.name('worktime')
    grok.require('horae.Manage')
    navigation.menuitem(IActionsMenu, _(u'Work time'))

    def render(self):
        return self.redirect(self.url(interfaces.IEffectiveWorkTime(self.context)))


# Cost units


class CostUnits(objects.ObjectOverview):
    """ Overview of cost units
    """
    grok.context(interfaces.ICostUnitsHolder)
    grok.name('costunits')
    navigation.sitemenuitem(IGlobalManageMenu, _(u'Cost units'))

    label = _(u'Cost units')
    add_label = _(u'Add cost unit')
    columns = [('name', _(u'Name')), ('rate', _(u'Hourly rate')), ('actions', u'')]
    container_iface = interfaces.ICostUnits

    def row_factory(self, object, columns, request):
        row = super(CostUnits, self).row_factory(object, columns, request)
        currency_formatter = component.getMultiAdapter((self.context, self.request), interface=ICurrencyFormatter)
        row.update({
            'name': object.name,
            'rate': currency_formatter.format(object.rate)})
        return row

    def add(self):
        return self.url(self.container) + '/add-costunit'


class AddCostUnit(layout.AddForm):
    """ Add form for cost units
    """
    grok.context(interfaces.ICostUnits)
    grok.require('horae.Manage')
    grok.name('add-costunit')

    form_fields = grok.AutoFields(interfaces.ICostUnit).omit('id')

    def object_type(self):
        return _(u'Cost unit')

    def cancel_url(self):
        return self.url(self.context.__parent__) + '/costunits'

    def next_url(self, obj=None):
        return self.cancel_url()

    def create(self, **data):
        return resources.CostUnit()

    def add(self, obj):
        self.context.add_object(obj)


class EditCostUnit(objects.EditObject):
    """ Edit form of a cost unit
    """
    grok.context(interfaces.ICostUnits)
    grok.name('edit-costunit')

    form_fields = grok.AutoFields(interfaces.ICostUnit).omit('id')
    overview = 'costunits'

    def object_type(self):
        return _(u'Cost unit')


class DeleteCostUnit(objects.DeleteObject):
    """ Delete form of a cost unit
    """
    grok.context(interfaces.ICostUnits)
    grok.name('delete-costunit')

    overview = 'costunits'

    def object_type(self):
        return _(u'Cost unit')


class CostUnitActionsProvider(grok.MultiAdapter):
    """ Action provider for cost units adding buttons to edit and delete
        the cost unit
    """
    grok.adapts(interfaces.ICostUnit, CostUnits)
    grok.implements(IObjectTableActionsProvider)
    grok.name('horae.resources.objecttableactions.costunit')

    def __init__(self, context, view):
        self.context = context
        self.view = view

    def actions(self, request):
        container_url = self.view.url(self.view.container)
        actions = [{'url': container_url + '/edit-costunit?id=' + str(self.context.id),
                    'label': translate(_(u'Edit'), context=request),
                    'cssClass': ''},
                   {'url': container_url + '/delete-costunit?id=' + str(self.context.id),
                    'label': translate(_(u'Delete'), context=request),
                    'cssClass': 'button-destructive delete'}]
        return actions


# Time entry container


class TimeEntries(objects.ObjectOverview):
    """ Overview of time entries
    """
    grok.context(ITimeEntryContainer)
    grok.name('index')

    columns = [('start', _(u'Start')), ('end', _(u'End')), ('repeat', _(u'Repeat')), ('repeat_until', _(u'Repeat until')), ('actions', u'')]
    container_iface = ITimeEntryContainer

    @property
    def label(self):
        if interfaces.IPlannedWorkTime.providedBy(self.container):
            return _(u'Planned work time')
        if interfaces.IEffectiveWorkTime.providedBy(self.container):
            return _(u'Work time')
        if interfaces.IAbsence.providedBy(self.container):
            return _(u'Absence')
        return _(u'Time entries')

    def row_factory(self, object, columns, request):
        row = super(TimeEntries, self).row_factory(object, columns, request)
        row.update({
            'start': utils.formatDateTime(object.date_start, self.request, ('dateTime', 'short')),
            'end': utils.formatDateTime(object.date_end, self.request, ('dateTime', 'short')),
            'repeat': object.repeat is not None and vocabulary.repeat_vocabulary_factory(object).getTerm(object.repeat).title or u'',
            'repeat_until': utils.formatDateTime(object.repeat_until, self.request, ('dateTime', 'short'))})
        return row

    def add(self):
        return None

    def start_end(self):
        session = ISession(self.request)
        key = sha1(self.url(self.context)).hexdigest()
        if session[key].get('yearmonth', None) is not None:
            year, month = session[key]['yearmonth']
        else:
            now = datetime.now()
            year, month = now.year, now.month
        sday, eday = calendar.monthrange(year, month)
        start = datetime(year, month, 1)
        end = datetime(year, month, eday) + timedelta(days=1)
        return start, end

    def update(self):
        super(objects.ObjectOverview, self).update()
        self.types = []
        self.back = self.url(self.context)
        self.container = self.container_iface(self.context)
        daterange = self.start_end()
        entries = self.container.objects(daterange)
        entries.sort(key=operator.attrgetter('date_start'))
        self.table = self.get_table(entries)
        self.table.caption = '%s %s' % (self.request.locale.dates.calendars['gregorian'].months[daterange[0].month][0], daterange[0].year)
        self.table = self.table()
        parent = utils.findParentByInterface(self.context, interfaces.IGlobalResourcesHolder)
        if checkPermission('horae.Manage', parent):
            self.back = self.url(parent) + '/resources'
        else:
            self.back = self.url(self.container.__parent__)


class TimeEntriesYearMonthSelectionForm(layout.Form):
    """ Form to select the year and month to be displayed
        by :py:class:`TimeEntries`
    """
    grok.context(ITimeEntryContainer)
    grok.require('horae.Manage')
    grok.name('yearmonthselection')
    id = 'year-month-selection'

    def update(self):
        session = ISession(self.request)
        key = sha1(self.url(self.context)).hexdigest()
        if session[key].get('yearmonth', None) is not None:
            year, month = session[key]['yearmonth']
        else:
            now = datetime.now()
            year, month = now.year, now.month
        fields = dict(
            year=schema.Choice(
                title=_(u'Year'),
                required=True,
                default=year,
                values=range(2011, datetime.now().year + 11)
            ),
            month=schema.Choice(
                title=_(u'Month'),
                required=True,
                default=month,
                vocabulary=schema.vocabulary.SimpleVocabulary([schema.vocabulary.SimpleTerm(id, id, names[0]) for id, names in self.request.locale.dates.calendars['gregorian'].months.items()])
            )
        )
        self.form_fields = grok.Fields(**fields)

    @grok.action(_(u'Show'))
    def handle_show(self, **data):
        session = ISession(self.request)
        key = sha1(self.url(self.context)).hexdigest()
        session[key]['yearmonth'] = (data['year'], data['month'])
        self.redirect(self.url(self.context))


class TimeEntriesYearMonthSelection(grok.Viewlet):
    """ Renders the :py:class:`TimeEntriesYearMonthSelectionForm`
    """
    grok.context(ITimeEntryContainer)
    grok.viewletmanager(viewlets.ContentBeforeManager)
    grok.view(TimeEntries)
    grok.name('horae.resources.timeentriesyearmonthselection')
    grok.order(0)

    def render(self):
        return component.getMultiAdapter((self.context, self.request), name='yearmonthselection')(plain=True)


class AddTimeEntry(layout.AddForm):
    """ Add form for time entries
    """
    grok.context(ITimeEntryContainer)
    grok.require('horae.Manage')
    grok.name('add-timeentry')
    cssClass = 'discreet'
    factory = timeaware.PersistentTimeEntry

    form_fields = grok.AutoFields(ITimeEntry).omit('id')

    def update(self):
        self.form_fields['date_end'].field.default = datetime.now()
        self.form_fields['date_start'].field.default = datetime.now()
        super(AddTimeEntry, self).update()

    def object_type(self):
        return _(u'Time entry')

    def cancel_url(self):
        return self.url(self.context)

    def next_url(self, obj=None):
        return self.cancel_url()

    def create(self, **data):
        return self.factory()

    def add(self, obj):
        self.context.add_object(obj)

    @grok.action(_l(u'Add'))
    def handle_add(self, **data):
        obj = self.create(**data)
        self.add(obj)
        self.apply(obj, **data)
        self.redirect(self.next_url(obj))
        message.send(_l(u'${object} successfully added', mapping={'object': self.object_type()}), u'info', u'session')
        return ''


class QuickAddTimeEntry(grok.Viewlet):
    """ Renders a quick add form for time entries
    """
    grok.context(ITimeEntryContainer)
    grok.viewletmanager(viewlets.ContentAfterManager)
    grok.view(TimeEntries)
    grok.name('horae.resources.quickaddtimeentry')
    grok.order(0)

    def render(self):
        return '<div class="quickadd">%s</div>' % component.getMultiAdapter((self.context, self.request), name='add-timeentry')(plain=True)


class EditTimeEntry(objects.EditObject):
    """ Edit form of a time entry
    """
    grok.context(ITimeEntryContainer)
    grok.name('edit-timeentry')

    form_fields = grok.AutoFields(ITimeEntry).omit('id')

    def setUpWidgets(self, ignore_request=False):
        super(EditTimeEntry, self).setUpWidgets(ignore_request)
        if not self.widgets['date_end'].hasInput():
            self.widgets['date_end'].setRenderedValue(datetime.now())
        if not self.widgets['date_start'].hasInput():
            self.widgets['date_start'].setRenderedValue(datetime.now())

    def object_type(self):
        return _(u'Time entry')

    def cancel_url(self):
        return self.url(self.context)


class DeleteTimeEntry(objects.DeleteObject):
    """ Delete form of a time entry
    """
    grok.context(ITimeEntryContainer)
    grok.name('delete-timeentry')

    def item_title(self):
        return utils.formatDateTimeRange(self.object.date_start, self.object.date_end, self.request, ('dateTime', 'short'), False)

    def object_type(self):
        return _(u'Time entry')

    def cancel_url(self):
        return self.url(self.context)


class TimeEntryActionsProvider(grok.MultiAdapter):
    """ Action provider for time entries adding buttons to edit and delete
        the time entry
    """
    grok.adapts(ITimeEntry, TimeEntries)
    grok.implements(IObjectTableActionsProvider)
    grok.name('horae.resources.objecttableactions.timeentry')

    def __init__(self, context, view):
        self.context = context
        self.view = view

    def actions(self, request):
        container_url = self.view.url(self.view.container)
        actions = [{'url': container_url + '/edit-timeentry?id=' + str(self.context.id),
                    'label': translate(_(u'Edit'), context=request),
                    'cssClass': ''},
                   {'url': container_url + '/delete-timeentry?id=' + str(self.context.id),
                    'label': translate(_(u'Delete'), context=request),
                    'cssClass': 'button-destructive delete'}]
        return actions


# Absence


class AbsenceEntries(TimeEntries):
    """ Overview of absence time entries
    """
    grok.context(interfaces.IAbsence)
    factory = resources.AbsenceTimeEntry

    columns = [('cause', _(u'Cause')), ('start', _(u'Start')), ('end', _(u'End')), ('repeat', _(u'Repeat')), ('repeat_until', _(u'Repeat until')), ('actions', u'')]

    def row_factory(self, object, columns, request):
        row = super(AbsenceEntries, self).row_factory(object, columns, request)
        row['cause'] = object.cause
        return row


class AddAbsenceTimeEntry(AddTimeEntry):
    """ Add form for absence time entries
    """
    grok.context(interfaces.IAbsence)

    form_fields = grok.AutoFields(interfaces.IAbsenceTimeEntry).omit('id')


class EditAbsenceTimeEntry(EditTimeEntry):
    """ Edit form of an absence time entry
    """
    grok.context(interfaces.IAbsenceTimeEntry)

    form_fields = grok.AutoFields(interfaces.IAbsenceTimeEntry).omit('id')


# Effective work time


class EffectiveWorkTimeEntries(TimeEntries):
    """ Overview of effective work time entries
    """
    grok.context(interfaces.IEffectiveWorkTime)

    columns = [('start', _(u'Start')), ('end', _(u'End')), ('hours', _(u'Hours')), ('actions', u'')]

    def row_factory(self, object, columns, request):
        row = super(EffectiveWorkTimeEntries, self).row_factory(object, columns, request)
        row['hours'] = utils.formatHours(object.hours(), request)
        return row

    def get_table(self, resources):
        table = super(EffectiveWorkTimeEntries, self).get_table(resources)
        table.footer = [[(1, u''), (1, u''), (1, utils.formatHours(self.context.hours(self.start_end()), self.request)), (1, u'')], ]
        return table


class AddEffectiveWorkTimeEntry(AddTimeEntry):
    """ Add form for effective work time entries
    """
    grok.context(interfaces.IEffectiveWorkTime)

    form_fields = grok.AutoFields(ITimeEntry).omit('id', 'repeat', 'repeat_until',)

    def update(self):
        self.form_fields = grok.Fields(date_hours=schema.Float(
                               title=_(u'Hours'),
                               required=False,
                               default=0.0
                           )) + self.form_fields
        super(AddEffectiveWorkTimeEntry, self).update()

    def setUpWidgets(self, ignore_request=False):
        super(AddEffectiveWorkTimeEntry, self).setUpWidgets(ignore_request)
        self.resource = utils.findParentByInterface(self.context, interfaces.IHumanResource)
        effectiveworktime = interfaces.IEffectiveWorkTime(self.resource)
        today = date.today()
        now = datetime(today.year, today.month, today.day)
        worktime = interfaces.IPlannedWorkTime(self.resource).subtract(interfaces.IAbsence(self.resource), (now, now + timedelta(days=1)))
        for entry in worktime.objects():
            if not len(effectiveworktime.entries((entry.date_start, entry.date_end))):
                if not self.widgets['date_start'].hasInput() or ignore_request:
                    self.widgets['date_start'].setRenderedValue(entry.date_start)
                if not self.widgets['date_end'].hasInput() or ignore_request:
                    self.widgets['date_end'].setRenderedValue(entry.date_end)
                break


class EditEffectiveWorkTimeEntry(EditTimeEntry):
    """ Edit form of an effective work time entry
    """
    grok.context(interfaces.IEffectiveWorkTime)

    form_fields = grok.AutoFields(ITimeEntry).omit('id', 'repeat', 'repeat_until')

    def update(self):
        self.form_fields = grok.Fields(date_hours=schema.Float(
                               title=_(u'Hours'),
                               required=False,
                               default=0.0
                           )) + self.form_fields
        super(EditEffectiveWorkTimeEntry, self).update()


# Planned resources


class PlannedResources(objects.ObjectOverview):
    """ Overview of planned resources
    """
    grok.context(interfaces.IPlannedResourcesHolder)
    grok.name('plannedresources')
    navigation.menuitem(IContextualManageMenu, _(u'Planned resources'))

    label = _(u'Planned resources')
    add_label = _(u'Add resource')
    columns = [('resource', _(u'Resource')), ('percentage', _(u'Percentage')), ('hours', _(u'Hours')), ('costunit', _(u'Cost unit')), ('rate', _(u'Hourly rate')), ('total', _(u'Total price')), ('actions', u'')]
    container_iface = interfaces.IPlannedResources

    def row_factory(self, object, columns, request):
        row = super(PlannedResources, self).row_factory(object, columns, request)
        formatter = self.request.locale.numbers.getFormatter('decimal')
        currency_formatter = component.getMultiAdapter((self.context, self.request), interface=ICurrencyFormatter)
        row.update({
            'resource': object.resource.name,
            'percentage': formatter.format(object.percentage) + '%',
            'hours': utils.formatHours(object.hours(), request),
            'costunit': object.costunit.name,
            'rate': currency_formatter.format(object.costunit.rate),
            'total': currency_formatter.format(object.price())})
        return row

    def get_table(self, resources):
        formatter = self.request.locale.numbers.getFormatter('decimal')
        currency_formatter = component.getMultiAdapter((self.context, self.request), interface=ICurrencyFormatter)
        table = super(PlannedResources, self).get_table(resources)
        table.footer = [[(1, '&nbsp;'),
                         (1, formatter.format(self.container.percentage()) + '%'),
                         (1, utils.formatHours(self.container.hours(), self.request)),
                         (1, '&nbsp;'),
                         (1, '&nbsp;'),
                         (1, currency_formatter.format(self.container.price())),
                         (1, '&nbsp;')]]
        return table

    def add(self):
        return self.container.percentage() < 100 and self.url(self.container) + '/add-plannedresource' or None


class PlannedResourceFormMixin(object):
    """ Mix in for forms of planned resources
    """

    form_fields = grok.AutoFields(interfaces.IPlannedResource).omit('id') + grok.Fields(
        hours=schema.Float(
            title=_(u'Hours'),
            required=False,
            min=0.0
        )
    )

    def update(self):
        estimated_hours = utils.findParentByInterface(self.context, ITicket).estimated_hours
        self.form_fields['percentage'].field.max = None
        percentage = 0.0
        for resource in self.context.objects():
            if not getattr(self, 'object', None) is resource:
                percentage += resource.percentage
        self.form_fields['percentage'].field.max = 100.0 - percentage
        self.form_fields['hours'].field.max = None
        self.form_fields['hours'].field.max = self.form_fields['percentage'].field.max * estimated_hours / 100.0
        super(PlannedResourceFormMixin, self).update()
        self.additional = getattr(self, 'additional', '') + \
                          renderElement('input',
                                        type='hidden',
                                        name='percentage_max',
                                        value=self.form_fields['percentage'].field.max) + \
                          renderElement('input',
                                        type='hidden',
                                        name='hours_max',
                                        value=self.form_fields['hours'].field.max) + \
                          renderElement('input',
                                        type='hidden',
                                        name='estimated',
                                        value=estimated_hours)


class AddPlannedResource(PlannedResourceFormMixin, layout.AddForm):
    """ Add form for planned resources
    """
    grok.context(interfaces.IPlannedResources)
    grok.require('horae.Edit')
    grok.name('add-plannedresource')

    def object_type(self):
        return _(u'Planned resource')

    def cancel_url(self):
        return self.url(self.context.__parent__) + '/plannedresources'

    def next_url(self, obj=None):
        return self.cancel_url()

    def create(self, **data):
        return resources.PlannedResource()

    def add(self, obj):
        self.context.add_object(obj)

    def apply(self, obj, **data):
        if not data['percentage'] and data['hours']:
            data['precentage'] = data['hours'] / utils.findParentByInterface(self.context, ITicket).estimated_hours * 100.0
        del data['hours']
        super(PlannedResourceFormMixin, self).apply(obj, **data)


class EditPlannedResource(PlannedResourceFormMixin, objects.EditObject):
    """ Edit form of a planned resource
    """
    grok.context(interfaces.IPlannedResources)
    grok.name('edit-plannedresource')

    dynamic_fields = False

    def object_type(self):
        return _(u'Planned resource')

    def cancel_url(self):
        return self.url(self.context.__parent__) + '/plannedresources'

    def apply(self, **data):
        if not data['percentage'] and data['hours']:
            data['precentage'] = data['hours'] / utils.findParentByInterface(self.context, ITicket).estimated_hours * 100.0
        del data['hours']
        super(PlannedResourceFormMixin, self).apply(**data)


class DeletePlannedResource(objects.DeleteObject):
    """ Delete form of a planned resource
    """
    grok.context(interfaces.IPlannedResources)
    grok.name('delete-plannedresource')

    def object_type(self):
        return _(u'Planned resource')

    def cancel_url(self):
        return self.url(self.context.__parent__) + '/plannedresources'

    def item_title(self):
        return self.object.resource.name


class PlannedResourceActionsProvider(grok.MultiAdapter):
    """ Action provider for planned resources adding buttons to edit and delete
        the planned resource
    """
    grok.adapts(interfaces.IPlannedResource, PlannedResources)
    grok.implements(IObjectTableActionsProvider)
    grok.name('horae.resources.objecttableactions.plannedresource')

    def __init__(self, context, view):
        self.context = context
        self.view = view

    def actions(self, request):
        container_url = self.view.url(self.view.container)
        actions = [{'url': container_url + '/edit-plannedresource?id=' + str(self.context.id),
                    'label': translate(_(u'Edit'), context=request),
                    'cssClass': ''},
                   {'url': container_url + '/delete-plannedresource?id=' + str(self.context.id),
                    'label': translate(_(u'Delete'), context=request),
                    'cssClass': 'button-destructive delete'}]
        return actions
