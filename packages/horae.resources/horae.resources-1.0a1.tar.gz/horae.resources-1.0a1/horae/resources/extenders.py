import grok

from zope import component
from zope.i18n import translate
from zope.schema import vocabulary
from zope.interface import classImplements
from zope.security import checkPermission
from zope.app.intid.interfaces import IIntIds
from zope.annotation import IAnnotations
from zc.relation.interfaces import ICatalog

from horae.core import utils
from horae.core.interfaces import ICurrencyFormatter
from horae.layout.interfaces import IViewExtender
from horae.properties.interfaces import IHistoryPropertiesProvider, IPropertiedDisplayWidgetsProvider, IComplete, IOffer
from horae.properties import views
from horae.properties import properties
from horae.timeaware.interfaces import ITimeAware, ITimeEntry
from horae.ticketing.interfaces import IClient, IProject, IMilestone, ITicket, ITicketContainer, IProjectContainer, ITicketChangedEvent
from horae.ticketing.views import ChangeTicket
from horae.ticketing import ticketing, _ as _t

from horae.resources import _
from horae.resources.resources import HourlyExpensesWidget, OnetimeExpensesWidget
from horae.resources import interfaces

classImplements(ticketing.Client, interfaces.IExpensesAware)
classImplements(ticketing.Project, interfaces.IExpensesAware)
classImplements(ticketing.Milestone, interfaces.IExpensesAware)
classImplements(ticketing.Ticket, interfaces.IExpensesContainerHolder, interfaces.IPlannedResourcesHolder)


class BaseEstimatedExpenses(grok.Adapter):
    """ Base implementation of estimated expenses
    """
    grok.baseclass()
    grok.implements(interfaces.IEstimatedExpenses)

    _key_prefix = 'horae.resources.estimation.'

    def __init__(self, context):
        super(BaseEstimatedExpenses, self).__init__(context)
        self._storage = IAnnotations(self.context)

    def _get(self, name):
        if not self._key_prefix + name in self._storage:
            self.update()
        value = self._storage.get(self._key_prefix + name, 0.0)
        if value is None:
            return 0.0
        return value

    def _set(self, name, value):
        self._storage[self._key_prefix + name] = value

    def onetime(self):
        return self._get('onetime')

    def hourly(self):
        return self._get('hourly')

    def hours(self):
        return self._get('hours')

    def workcost(self):
        return self._get('workcost')

    def childs(self):
        raise NotImplementedError(u'concrete classes must implement childs()')

    def update(self):
        onetime = 0.0
        hourly = 0.0
        hours = 0.0
        workcost = 0.0
        for child in self.childs():
            estimation = interfaces.IEstimatedExpenses(child)
            onetime += estimation.onetime()
            hourly += estimation.hourly()
            hours += estimation.hours()
            workcost += estimation.workcost()
        self._set('onetime', onetime)
        self._set('hourly', hourly)
        self._set('hours', hours)
        self._set('workcost', workcost)


class ClientEstimatedExpenses(BaseEstimatedExpenses):
    """ Estimated expenses of clients
    """
    grok.context(IClient)

    def childs(self):
        return IProjectContainer(self.context).objects()


class ProjectEstimatedExpenses(BaseEstimatedExpenses):
    """ Estimated expenses of projects
    """
    grok.context(IProject)

    def childs(self):
        return ITicketContainer(self.context).objects()


class MilestoneEstimatedExpenses(BaseEstimatedExpenses):
    """ Estimated expenses of milestones
    """
    grok.context(IMilestone)

    def childs(self):
        container = ITicketContainer(utils.findParentByInterface(self.context, IProject), None)
        if container is None:
            return []
        return [ticket for ticket in container.objects() if ticket.get_property('milestone', None) is self.context]


class TicketEstimatedExpenses(grok.Adapter):
    """ Estimated expenses of tickets
    """
    grok.context(ITicket)
    grok.implements(interfaces.IEstimatedExpenses)

    def _get_property(self, name):
        value = self.context.get_property('estimated_onetime_expense', 0.0)
        if value is None:
            return 0.0
        return value

    def onetime(self):
        return self._get_property('estimated_onetime_expense')

    def hourly(self):
        return self._get_property('estimated_hourly_expense')

    def hours(self):
        return self._get_property('estimated_hours')

    def workcost(self):
        return interfaces.IPlannedResources(self.context).price()


@grok.subscribe(ITicket, ITicketChangedEvent)
def update_estimations(ticket, event):
    """ Updates estimations of milestone, project and client on
        ticket change
    """
    update = []
    milestone = ticket.get_property('milestone', None)
    if milestone is not None:
        update.append(milestone)
    update.append(utils.findParentByInterface(ticket, IProject))
    update.append(utils.findParentByInterface(ticket, IClient))
    for obj in update:
        interfaces.IEstimatedExpenses(obj).update()


@grok.subscribe(ITimeEntry, grok.IObjectAddedEvent)
def timeentry_creation(obj, event):
    """ Links the created time entry with the latest work expense
    """
    if ITicket.providedBy(event.newParent):
        workexpense = interfaces.IWorkExpensesContainer(event.newParent).last()
        if workexpense is not None and workexpense.timeentry is None:
            workexpense.timeentry = obj


class ExpenseTicketChangeExtender(grok.Adapter):
    """ Extends the ticket change form with the fields to create
        work, hourly and one time expenses and to deactivate them
    """
    grok.context(ChangeTicket)
    grok.implements(IViewExtender)
    grok.name('horae.resources.ticket.change')

    def pre_update(self):
        completed = IComplete(self.context.context, lambda: False)()
        offer = IOffer(self.context.context, lambda: False)()
        if completed or offer:
            return
        registry = vocabulary.getVocabularyRegistry()
        if len(registry.get(self.context.context, 'horae.resources.vocabulary.resourcecostunit')):
            self.context.form_fields = self.context.form_fields + grok.AutoFields(interfaces.IWorkExpenseForm)
            self.context.form_fields['workexpense'].field.order = 110
        if len(registry.get(self.context.context, 'horae.resources.vocabulary.hourlyresources')):
            self.context.form_fields = self.context.form_fields + grok.AutoFields(interfaces.IHourlyExpensesForm)
            self.context.form_fields['hourlyexpenses'].field.order = 195
        if len(registry.get(self.context.context, 'horae.resources.vocabulary.onetimeresources')):
            self.context.form_fields = self.context.form_fields + grok.AutoFields(interfaces.IOnetimeExpensesForm)
            self.context.form_fields['onetimeexpenses'].field.order = 196
        if checkPermission('horae.Edit', self.context.context):
            self.context.form_fields = self.context.form_fields + grok.AutoFields(interfaces.IDeactivateExpensesForm)
            self.context.form_fields['deactivate_workexpenses'].field.order = 197
            self.context.form_fields['deactivate_hourlyexpenses'].field.order = 198
            self.context.form_fields['deactivate_onetimeexpenses'].field.order = 199
            if not len(registry.get(self.context.context, 'horae.resources.vocabulary.workexpenses')):
                self.context.form_fields = self.context.form_fields.omit('deactivate_workexpenses')
            if not len(registry.get(self.context.context, 'horae.resources.vocabulary.hourlyexpenses')):
                self.context.form_fields = self.context.form_fields.omit('deactivate_hourlyexpenses')
            if not len(registry.get(self.context.context, 'horae.resources.vocabulary.onetimeexpenses')):
                self.context.form_fields = self.context.form_fields.omit('deactivate_onetimeexpenses')

    def pre_setUpWidgets(self, ignore_request=False):
        if self.context.form_fields.get('hourlyexpenses') is not None:
            self.context.form_fields['hourlyexpenses'].custom_widget = HourlyExpensesWidget
        if self.context.form_fields.get('onetimeexpenses') is not None:
            self.context.form_fields['onetimeexpenses'].custom_widget = OnetimeExpensesWidget

    def post_update(self):
        completed = IComplete(self.context.context)()
        offer = IOffer(self.context.context, lambda: False)()
        if completed or offer:
            return
        if self.context.form_fields.get('workexpense') is not None:
            self.context.form_fields['workexpense'].field = self.context.form_fields['workexpense'].field.bind(self.context.context)
            resource = self.context.widgets['workexpense'].getInputValue() if self.context.widgets['workexpense'].hasInput() else None
            for term in self.context.form_fields['workexpense'].field.vocabulary:
                if resource is None:
                    resource = term.value
                    self.context.widgets['workexpense'].setRenderedValue(term.value)
                if resource.resource == term.value.resource and \
                   resource.resource.default_costunit == term.value.costunit:
                    self.context.widgets['workexpense'].setRenderedValue(term.value)
                if term.value.resource.user is not None and self.context.request.principal.id == term.value.resource.user and \
                   term.value.costunit == term.value.resource.default_costunit:
                    self.context.widgets['workexpense'].setRenderedValue(term.value)
                    break

    def apply(self, obj, **data):
        pass

    def validate(self, action, data):
        return ()


class ExpenseAndHoursWidgetProvider(grok.Adapter):
    """ Base widget provider adding cost and hours widgets for display views
    """
    grok.baseclass()
    grok.implements(IPropertiedDisplayWidgetsProvider)

    def __init__(self, context):
        self.context = context

    def widgets(self, widgets, request):
        index = 0
        for widget in widgets:
            if widget.name[len(getattr(widget, 'prefix', getattr(widget, '_prefix', ''))):].startswith('estimated'):
                index = max(index, widgets.index(widget) + 1)
        if index == 0:
            index = len(widgets)
        estimation = interfaces.IEstimatedExpenses(self.context)
        ecost = 0.0
        enum = 0
        hours = estimation.hours()
        if hours > 0 and not ITicket.providedBy(self.context):
            estimatedhours = properties.FloatProperty()
            estimatedhours.id = 'estimated_hours'
            estimatedhours.name = _t(u'Estimated hours')
            widgets.insert(index, views.PropertyDisplayWidget(estimatedhours, hours, self.context, request))
            index += 1
        hourly = estimation.hourly()
        onetime = estimation.onetime()
        if hourly > 0.0:
            ecost += hourly
            enum += 1
            if not ITicket.providedBy(self.context):
                estimatedhourly = properties.PriceProperty()
                estimatedhourly.id = 'estimated_hourly_expense'
                estimatedhourly.name = _(u'Estimated hourly expense')
                widgets.insert(index, views.PropertyDisplayWidget(estimatedhourly, hourly, self.context, request))
                index += 1
        if onetime > 0.0:
            ecost += onetime
            enum += 1
            if not ITicket.providedBy(self.context):
                estimatedonetime = properties.PriceProperty()
                estimatedonetime.id = 'estimated_onetime_expense'
                estimatedonetime.name = _(u'Estimated one-time expense')
                widgets.insert(index, views.PropertyDisplayWidget(estimatedonetime, onetime, self.context, request))
                index += 1
        eworkexpense = properties.PriceProperty()
        eworkexpense.id = 'estimated_cost'
        eworkexpense.name = _(u'Estimated work expense')
        workcost = estimation.workcost()
        if workcost > 0.0:
            ecost += workcost
            enum += 1
            widgets.insert(index, views.PropertyDisplayWidget(eworkexpense, workcost, self.context, request))
            index += 1
        if enum > 1:
            estimated = properties.PriceProperty()
            estimated.id = 'estimated_expense'
            estimated.name = _(u'Total estimated expense')
            widgets.insert(index, views.PropertyDisplayWidget(estimated, ecost, self.context, request, None, 'total'))
            index += 1
        timeaware = ITimeAware(self.context, None)
        if timeaware is not None:
            totalhours = properties.FloatProperty()
            totalhours.id = 'hours'
            totalhours.name = _(u'Work hours')
            hours = timeaware.hours()
            if hours > 0:
                widgets.insert(index, views.PropertyDisplayWidget(totalhours, hours, self.context, request))
                index += 1
        total = 0.0
        workexpenses = interfaces.IWorkExpenses(self.context, None)
        if workexpenses is not None:
            workexpense = properties.PriceProperty()
            workexpense.id = 'workexpense'
            workexpense.name = _(u'Work expense')
            cost = workexpenses.price()
            total += cost
            if cost > 0:
                widgets.insert(index, views.PropertyDisplayWidget(workexpense, cost, self.context, request))
                index += 1
        hourlyexpenses = interfaces.IHourlyExpenses(self.context)
        if hourlyexpenses is not None:
            hourlyexpense = properties.PriceProperty()
            hourlyexpense.id = 'hourlyexpense'
            hourlyexpense.name = _(u'Hourly expense')
            cost = hourlyexpenses.price()
            total += cost
            if cost > 0:
                widgets.insert(index, views.PropertyDisplayWidget(hourlyexpense, cost, self.context, request))
                index += 1
        onetimeexpenses = interfaces.IOnetimeExpenses(self.context)
        if onetimeexpenses is not None:
            onetimeexpense = properties.PriceProperty()
            onetimeexpense.id = 'onetimeexpense'
            onetimeexpense.name = _(u'One-time expense')
            cost = onetimeexpenses.price()
            total += cost
            if cost > 0:
                widgets.insert(index, views.PropertyDisplayWidget(onetimeexpense, cost, self.context, request))
                index += 1
        if total > 0:
            totalexpense = properties.PriceProperty()
            totalexpense.id = 'total'
            totalexpense.name = _(u'Total expense')
            widgets.insert(index, views.PropertyDisplayWidget(totalexpense, total, self.context, request, None, total > ecost > 0 and 'negative total' or (total < ecost > 0 and 'positive total' or 'total')))
            index += 1
            if ecost > 0:
                difference = properties.PriceProperty()
                difference.id = 'difference'
                difference.name = _(u'Estimation difference')
                widgets.insert(index, views.PropertyDisplayWidget(difference, ecost - total, self.context, request, None, total > ecost and 'negative' or (total < ecost and 'positive' or None)))
                index += 1
        return widgets


class ProjectExpenseAndHoursWidgetProvider(ExpenseAndHoursWidgetProvider):
    """ Widget provider adding cost and hours widgets for the display view of projects
    """
    grok.name('horae.resources.project.expenseandhours')
    grok.context(IProject)


class MilestoneExpenseAndHoursWidgetProvider(ExpenseAndHoursWidgetProvider):
    """ Widget provider adding cost and hours widgets for the display view of milestones
    """
    grok.name('horae.resources.milestone.expenseandhours')
    grok.context(IMilestone)


class TicketExpenseAndHoursWidgetProvider(ExpenseAndHoursWidgetProvider):
    """ Widget provider adding cost and hours widgets for the display view of tickets
    """
    grok.name('horae.resources.ticket.expenseandhours')
    grok.context(ITicket)


class ExpenseAndHoursPropertiesProvider(grok.Adapter):
    """ Properties provider adding hours and workexpense to the ticket history
    """
    grok.context(ITicket)
    grok.implements(IHistoryPropertiesProvider)
    grok.name('horae.resources.ticket.history.expenseandhours')

    def _time(self, timeentry, properties, request):
        if timeentry:
            properties.append({'cssClass': 'separate',
                               'name': _(u'Hours'),
                               'value': '%s <span class="discreet">%s</span>' % (utils.formatHours(timeentry.hours(), request),
                                                                                 utils.formatDateTimeRange(timeentry.date_start, timeentry.date_end, request, html=False))})
        return properties

    def _workexpenses(self, workexpenses, properties, request, negative=False):
        if len(workexpenses):
            expenses = []
            hours = []
            for expense in workexpenses:
                price = expense.price()
                if price == 0:
                    continue
                if negative:
                    hours.append('%s <span class="discreet">%s</span>' % (utils.formatHours(-expense.timeentry.hours(), request),
                                                                          utils.formatDateTimeRange(expense.timeentry.date_start, expense.timeentry.date_end, request, html=False)))
                    price = -price
                self.gnum += 1
                self.total += price
                expenses.append('%s <span class="discreet">%s, %s (%s)</span>' % (self.currency_formatter.format(price),
                                                                                  expense.resource_name,
                                                                                  expense.costunit_name,
                                                                                  self.currency_formatter.format(expense.costunit_rate)))
            if len(hours) > 0:
                properties.append({'cssClass': 'separate negative',
                                   'name': _(u'Hours'),
                                   'value': '<ul class="expenses work"><li>%s</li>' % u'</li><li>'.join(hours)})
            if len(expenses) > 0:
                properties.append({'cssClass': 'separate' + (' negative' if negative else ''),
                                   'name': _(u'Work expense'),
                                   'value': '<ul class="expenses work"><li>%s</li></ul>' % (u'</li><li>'.join(expenses))})
        return properties

    def _hourlyexpenses(self, hourlyexpenses, properties, request, negative=False):
        if len(hourlyexpenses):
            expenses = []
            hourlyexpense = 0.0
            for expense in hourlyexpenses:
                price = expense.price()
                if price == 0:
                    continue
                if negative:
                    price = -price
                self.total += price
                self.gnum += 1
                hourlyexpense += price
                expenses.append('%s <span class="discreet">%s (%s)</span>' % (self.currency_formatter.format(price),
                                                                              expense.resource_name,
                                                                              self.currency_formatter.format(expense.resource_rate)))
            if len(expenses) > 0:
                properties.append({'cssClass': 'separate' + (' negative' if negative else ''),
                                   'name': _(u'Hourly expense'),
                                   'value': '<ul class="expenses hourly"><li>%s</li>%s</ul>' % (u'</li><li>'.join(expenses),
                                                                                                u'<li class="total">%s <span class="discreet">%s</span></li>' % (self.currency_formatter.format(hourlyexpense),
                                                                                                                                                                 translate(_(u'Total'), context=request)) if len(expenses) > 1 else u'')})
        return properties

    def _onetimeexpenses(self, onetimeexpenses, properties, request, negative=False):
        if len(onetimeexpenses):
            expenses = []
            onetimeexpense = 0.0
            for expense in onetimeexpenses:
                price = expense.price()
                if price == 0:
                    continue
                if negative:
                    price = -price
                self.total += price
                self.gnum += 1
                onetimeexpense += price
                expenses.append('%s <span class="discreet">%s, %s</span>' % (self.currency_formatter.format(price),
                                                                             expense.name,
                                                                             expense.resource_name))
            if len(expenses) > 0:
                properties.append({'cssClass': 'separate' + (' negative' if negative else ''),
                                   'name': _(u'One-time expense'),
                                   'value': '<ul class="expenses onetime"><li>%s</li>%s</ul>' % (u'</li><li>'.join(expenses),
                                                                                                 u'<li class="total">%s <span class="discreet">%s</span></li>' % (self.currency_formatter.format(onetimeexpense),
                                                                                                                                                                  translate(_(u'Total'), context=request)) if len(expenses) > 1 else u'')})
        return properties

    def properties(self, change, properties, request):
        """ Returns a modified or extended list of properties for the provided property change
        """
        self.currency_formatter = component.getMultiAdapter((self.context, request), interface=ICurrencyFormatter)
        catalog = component.getUtility(ICatalog)
        intids = component.getUtility(IIntIds)
        expenses = catalog.findRelations({'to_id': intids.getId(change)})
        workexpenses = []
        deactivated_workexpenses = []
        hourlyexpenses = []
        deactivated_hourlyexpenses = []
        onetimeexpenses = []
        deactivated_onetimeexpenses = []
        for expense in expenses:
            deactivated = expense.from_attribute.startswith('deactivate')
            expense = expense.from_object
            if interfaces.IWorkExpense.providedBy(expense):
                if deactivated:
                    deactivated_workexpenses.append(expense)
                else:
                    workexpenses.append(expense)
            if interfaces.IHourlyExpense.providedBy(expense):
                if deactivated:
                    deactivated_hourlyexpenses.append(expense)
                else:
                    hourlyexpenses.append(expense)
            if interfaces.IOnetimeExpense.providedBy(expense):
                if deactivated:
                    deactivated_onetimeexpenses.append(expense)
                else:
                    onetimeexpenses.append(expense)
        self.total = 0.0
        self.gnum = 0
        properties = self._time(change.get_property('timeentry'), properties, request)
        properties = self._workexpenses(workexpenses, properties, request)
        properties = self._workexpenses(deactivated_workexpenses, properties, request, True)
        properties = self._hourlyexpenses(hourlyexpenses, properties, request)
        properties = self._hourlyexpenses(deactivated_hourlyexpenses, properties, request, True)
        properties = self._onetimeexpenses(onetimeexpenses, properties, request)
        properties = self._onetimeexpenses(deactivated_onetimeexpenses, properties, request, True)
        if self.gnum > 1:
            properties.append({'cssClass': 'separate' + (' negative' if self.total < 0 else u''),
                               'name': _(u'Total expense'),
                               'value': '<span class="total">%s</span>' % self.currency_formatter.format(self.total)})
        return properties
