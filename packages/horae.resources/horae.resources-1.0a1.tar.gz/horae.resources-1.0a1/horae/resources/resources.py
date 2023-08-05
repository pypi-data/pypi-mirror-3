import grok

from zope import schema
from zope import component

from zope.event import notify
from zope.copypastemove.interfaces import IObjectMover
from zope.app.intid.interfaces import IIntIds
from zope.location.interfaces import ILocationInfo
from zope.formlib.widget import CustomWidgetFactory
from zope.lifecycleevent import ObjectModifiedEvent
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.publisher.interfaces.browser import IBrowserRequest
from z3c.relationfield import RelationValue

from hurry import query

from horae.core import utils
from horae.core import container
from horae.core.interfaces import IHorae
from horae.layout.widgets import ObjectWidget
from horae.layout.widgets import ListSequenceWidget
from horae.layout import layout
from horae.timeaware import timeaware
from horae.timeaware.interfaces import ITimeAware
from horae.properties.interfaces import IPropertied

from horae.resources import _
from horae.resources import interfaces


class GlobalResources(container.Container):
    """ Container for global resources
    """
    grok.implements(interfaces.IGlobalResources)

    def id_key(self):
        return 'resource'


class GlobalResourcesBreadcrumbs(layout.BaseBreadcrumbs):
    """ Adapter making an object visible in the breadcrumbs
    """
    grok.adapts(interfaces.IGlobalResources, IBrowserRequest)

    @property
    def name(self):
        return _(u'Resources')

    @property
    def url(self):
        return grok.url(self.request, utils.findParentByInterface(self.context, IHorae), 'resources')


@grok.adapter(interfaces.IGlobalResourcesHolder)
@grok.implementer(interfaces.IGlobalResources)
def global_resources_of_holder(holder):
    """ Returns a global resources container if it does not yet
        exist one is created
    """
    if not 'global_resources' in holder:
        holder['global_resources'] = GlobalResources()
    return holder['global_resources']


class ResourceTypes(object):
    """ Provider for available resource types
    """
    grok.implements(interfaces.IResourceTypes)

    def __init__(self):
        self._types = []

    def add(self, type):
        if not interfaces.IResource:
            raise ValueError(type)
        self._types.append(type)

    def types(self):
        """ Returns a list of available resource types
        """
        return self._types

resource_types = ResourceTypes()


def resource_types_singleton():
    """ Returns the :py:class:`ResourceTypes` singleton
    """
    return resource_types
grok.global_utility(resource_types_singleton, interfaces.IResourceTypes)


class Resource(grok.Model):
    """ A resource
    """
    grok.baseclass()

    id = schema.fieldproperty.FieldProperty(interfaces.IResource['id'])
    name = schema.fieldproperty.FieldProperty(interfaces.IResource['name'])
    description = schema.fieldproperty.FieldProperty(interfaces.IResource['description'])
    users = schema.fieldproperty.FieldProperty(interfaces.IResource['users'])
    groups = schema.fieldproperty.FieldProperty(interfaces.IResource['groups'])


class HumanResource(grok.Container, Resource):
    """ A human resource
    """
    grok.implements(interfaces.IHumanResource,
                    interfaces.IEffectiveWorkTimeHolder,
                    interfaces.IPlannedWorkTimeHolder,
                    interfaces.IAbsenceHolder)

    type = _(u'Human resource')

    user = schema.fieldproperty.FieldProperty(interfaces.IHumanResource['user'])
    costunits = schema.fieldproperty.FieldProperty(interfaces.IHumanResource['costunits'])
    default_costunit = schema.fieldproperty.FieldProperty(interfaces.IHumanResource['default_costunit'])
resource_types.add(HumanResource)


class HumanResourceBreadcrumbs(layout.BaseBreadcrumbs):
    """ Adapter making a human resources visible in the breadcrumbs
    """
    grok.adapts(interfaces.IHumanResource, IBrowserRequest)

    @property
    def name(self):
        return self.context.name


@grok.subscribe(interfaces.IHumanResource, grok.IObjectModifiedEvent)
def assign_owner(obj, event):
    """ Assignes the horae.Owner role to the user linked to the
        human resource
    """
    manager = IPrincipalRoleManager(obj)
    principals = manager.getPrincipalsForRole('horae.Owner')
    for principal, setting in principals:
        manager.unsetRoleForPrincipal('horae.Owner', principal)
    if obj.user is not None:
        manager.assignRoleToPrincipal('horae.Owner', obj.user)


class PlannedWorkTime(timeaware.TimeEntryContainer):
    """ The planned work time of a human resource
    """
    grok.implements(interfaces.IPlannedWorkTime)


class PlannedWorkTimeBreadcrumbs(layout.BaseBreadcrumbs):
    """ Adapter making an object visible in the breadcrumbs
    """
    grok.adapts(interfaces.IPlannedWorkTime, IBrowserRequest)

    name = _(u'Planned work time')


class EffectiveWorkTime(timeaware.TimeEntryContainer):
    """ The effective work time of a human resource
    """
    grok.implements(interfaces.IEffectiveWorkTime)


class EffectiveWorkTimeBreadcrumbs(layout.BaseBreadcrumbs):
    """ Adapter making an object visible in the breadcrumbs
    """
    grok.adapts(interfaces.IEffectiveWorkTime, IBrowserRequest)

    name = _(u'Work time')


@grok.adapter(interfaces.IPlannedWorkTimeHolder)
@grok.implementer(interfaces.IPlannedWorkTime)
def planned_worktime_of_holder(holder):
    """ Returns the :py:class:`PlannedWorkTime` of the holder if it
        does not yet exist one is created
    """
    if not 'planned_worktime' in holder:
        holder['planned_worktime'] = PlannedWorkTime()
    return holder['planned_worktime']


@grok.adapter(interfaces.IEffectiveWorkTimeHolder)
@grok.implementer(interfaces.IEffectiveWorkTime)
def effective_worktime_of_holder(holder):
    """ Returns the :py:class:`EffectiveWorkTime` of the holder if it
        does not yet exist one is created
    """
    if not 'effective_worktime' in holder:
        holder['effective_worktime'] = EffectiveWorkTime()
    return holder['effective_worktime']


class Absence(timeaware.TimeEntryContainer):
    """ The absence of a human resource
    """
    grok.implements(interfaces.IAbsence)


class AbsenceBreadcrumbs(layout.BaseBreadcrumbs):
    """ Adapter making an object visible in the breadcrumbs
    """
    grok.adapts(interfaces.IAbsence, IBrowserRequest)

    name = _(u'Absence')


class AbsenceTimeEntry(timeaware.PersistentTimeEntry):
    """ An absence time entry additionally storing the cause of the absence
    """
    grok.implements(interfaces.IAbsenceTimeEntry)

    cause = schema.fieldproperty.FieldProperty(interfaces.IAbsenceTimeEntry['cause'])


@grok.adapter(interfaces.IAbsenceHolder)
@grok.implementer(interfaces.IAbsence)
def absence_of_holder(holder):
    """ Returns the :py:class:`Absence` of the holder if it
        does not yet exist one is created
    """
    if not 'absence' in holder:
        holder['absence'] = Absence()
    return holder['absence']


class HourlyResource(Resource):
    """ A resource based on an hourly rate
    """
    grok.implements(interfaces.IHourlyResource)

    type = _(u'Hourly resource')

    rate = schema.fieldproperty.FieldProperty(interfaces.IHourlyResource['rate'])
resource_types.add(HourlyResource)


class OnetimeResource(Resource):
    """ A one-time resource
    """
    grok.implements(interfaces.IOnetimeResource)

    type = _(u'One-time resource')
resource_types.add(OnetimeResource)


class PlannedResources(container.Container):
    """ Container for planned resources
    """
    grok.implements(interfaces.IPlannedResources)

    def id_key(self):
        return 'planned_resource'

    def hours(self):
        """ The hours planned for this resource
        """
        hours = 0.0
        for resource in self.objects():
            hours += resource.hours()
        return hours

    def percentage(self):
        """ The total percentage of the planned resources
        """
        percentage = 0.0
        for resource in self.objects():
            percentage += resource.percentage
        return percentage

    def price(self):
        """ The price of this object
        """
        price = 0.0
        for resource in self.objects():
            price += resource.price()
        return price


@grok.adapter(interfaces.IPlannedResourcesHolder)
@grok.implementer(interfaces.IPlannedResources)
def planned_resources_of_holder(holder):
    """ Returns the :py:class:`PlannedResources` of the holder if it
        does not yet exist one is created
    """
    if not 'planned_resources' in holder:
        holder['planned_resources'] = PlannedResources()
    return holder['planned_resources']


class ResourceCostunit(object):
    """ A combination of a human resource and an associated cost unit
    """
    grok.implements(interfaces.IResourceCostunit)

    _costunit = None
    costunit_rate = 0.0
    costunit_name = u''
    costunit_id = None
    _resource = None
    resource_name = u''
    resource_id = None

    def set_resource(self, obj):
        self._resource = obj
        self.resource_id = obj.id
        self.resource_name = obj.name

    def get_resource(self):
        return self._resource
    resource = property(get_resource, set_resource)

    def set_costunit(self, obj):
        self._costunit = obj
        self.costunit_id = obj.id
        self.costunit_name = obj.name
        self.costunit_rate = obj.rate

    def get_costunit(self):
        return self._costunit
    costunit = property(get_costunit, set_costunit)


class RelationResourceCostunitMixin(ResourceCostunit):
    """ A combination of human resource and an
    """

    resource_rel = None
    _v_resource = None
    costunit_rel = None
    _v_costunit = None

    def set_resource(self, obj):
        intids = component.getUtility(IIntIds)
        self.resource_rel = RelationValue(intids.queryId(obj))
        self.resource_id = obj.id
        self.resource_name = obj.name
        self._v_resource = obj
        notify(ObjectModifiedEvent(self))

    def get_resource(self):
        if self.resource_rel is None:
            return None
        try:
            if self._v_resource is None:
                self._v_resource = self.resource_rel.to_object
            return self._v_resource
        except:
            return None
    resource = property(get_resource, set_resource)

    def set_costunit(self, obj):
        intids = component.getUtility(IIntIds)
        self.costunit_rel = RelationValue(intids.queryId(obj))
        self.costunit_id = obj.id
        self.costunit_name = obj.name
        self.costunit_rate = obj.rate
        self._v_costunit = obj
        notify(ObjectModifiedEvent(self))

    def get_costunit(self):
        if self.costunit_rel is None:
            return None
        try:
            if self._v_costunit is None:
                self._v_costunit = self.costunit_rel.to_object
            return self._v_costunit
        except:
            return None
    costunit = property(get_costunit, set_costunit)


class PlannedResource(grok.Model, RelationResourceCostunitMixin):
    """ A planned resource
    """
    grok.implements(interfaces.IRelationPlannedResource)

    id = schema.fieldproperty.FieldProperty(interfaces.IPlannedResource['id'])
    percentage = schema.fieldproperty.FieldProperty(interfaces.IPlannedResource['percentage'])

    def hours(self):
        """ The hours planned for this resource
        """
        parent = utils.findParentByInterface(self, interfaces.IPlannedResourcesHolder)
        if parent.estimated_hours is None:
            return 0
        return parent.estimated_hours * self.percentage / 100

    def price(self):
        """ The price of this object
        """
        return self.costunit.rate * self.hours()


@grok.adapter(interfaces.IPlannedResource)
@grok.implementer(interfaces.IHumanResource)
def human_resource_of_holder(planned_resource):
    """ Returns the :py:class:`HumanResource` of the
        :py:class:`PlannedResource`
    """
    return planned_resource.resource


class CostUnits(container.Container):
    """ Container for cost units
    """
    grok.implements(interfaces.ICostUnits)

    def id_key(self):
        return 'cost_unit'


@grok.adapter(interfaces.ICostUnitsHolder)
@grok.implementer(interfaces.ICostUnits)
def cost_units_of_holder(holder):
    """ Returns the :py:class:`CostUnit` of the
        :py:class:`PlannedResource`
    """
    if not 'cost_units' in holder:
        holder['cost_units'] = CostUnits()
    return holder['cost_units']


class CostUnit(grok.Model):
    """ A cost unit
    """
    grok.implements(interfaces.ICostUnit)

    id = schema.fieldproperty.FieldProperty(interfaces.ICostUnit['id'])
    name = schema.fieldproperty.FieldProperty(interfaces.ICostUnit['name'])
    rate = schema.fieldproperty.FieldProperty(interfaces.ICostUnit['rate'])

    @property
    def title(self):
        return _(u'${name} (${price})', mapping=dict(name=self.name, price=str(self.rate)))

    def price(self):
        """ The price of this object
        """
        return self.rate


class Expense(grok.Model):
    """ A general expense
    """
    grok.baseclass()

    propertychange_rel = None
    deactivate_propertychange_rel = None
    resource_rel = None

    def set_resource(self, obj):
        intids = component.getUtility(IIntIds)
        self.resource_rel = RelationValue(intids.queryId(obj))
        self.resource_name = obj.name
        notify(ObjectModifiedEvent(self))

    def get_resource(self):
        if self.resource_rel is None:
            return None
        return self.resource_rel.to_object
    resource = property(get_resource, set_resource)

    def set_propertychange(self, obj):
        intids = component.getUtility(IIntIds)
        self.propertychange_rel = RelationValue(intids.queryId(obj))
        notify(ObjectModifiedEvent(self))

    def get_propertychange(self):
        if self.propertychange_rel is None:
            return None
        return self.propertychange_rel.to_object
    propertychange = property(get_propertychange, set_propertychange)

    def set_deactivate_propertychange(self, obj):
        intids = component.getUtility(IIntIds)
        self.deactivate_propertychange_rel = RelationValue(intids.queryId(obj))
        notify(ObjectModifiedEvent(self))

    def get_deactivate_propertychange(self):
        if self.deactivate_propertychange_rel is None:
            return None
        return self.deactivate_propertychange_rel.to_object
    deactivate_propertychange = property(get_deactivate_propertychange, set_deactivate_propertychange)

    def _move(self, holder, container):
        parent = utils.findParentByInterface(self, holder)
        if parent is None:
            return # holder not found
        IObjectMover(self).moveTo(container(parent))

    def deactivate(self):
        """ Deactivates this expense
        """
        if interfaces.IDeactivatedExpensesContainer.providedBy(self.__parent__):
            return # already deactivated
        self._move(interfaces.IDeactivatedExpensesContainerHolder, interfaces.IDeactivatedExpensesContainer)


class WorkExpenses(grok.Adapter, timeaware.TimeAware):
    """ An object aware of work expenses
    """
    grok.context(interfaces.IWorkExpensesAware)
    grok.implements(interfaces.IWorkExpenses)
    grok.provides(interfaces.IWorkExpenses)

    def workexpenses(self):
        return [interfaces.IWorkExpensesContainer(holder) for holder in component.getUtility(query.interfaces.IQuery).searchResults(
                    query.And(query.set.AnyOf(('catalog', 'implements'), [interfaces.IWorkExpensesContainerHolder.__identifier__, ]),
                              query.set.AnyOf(('catalog', 'path'), [ILocationInfo(self.context).getPath(), ])))]

    def get_entries(self):
        entries = []
        for expense in self.workexpenses():
            entries.extend(expense._entries)
        return entries

    def set_entries(self, value):
        pass # not allowed
    _entries = property(get_entries, set_entries)

    def price(self):
        """ The price of this object
        """
        price = 0.0
        for expense in self.workexpenses():
            price += expense.price()
        return price


class WorkExpensesContainer(container.Container, timeaware.TimeAware):
    """ A container for work expenses
    """
    grok.implements(interfaces.IWorkExpensesContainer)

    def id_key(self):
        return 'workexpense'

    def get_entries(self):
        return [expense.timeentry for expense in self.objects() if expense.timeentry is not None]

    def set_entries(self, value):
        pass # not allowed
    _entries = property(get_entries, set_entries)

    def price(self):
        """ The price of this object
        """
        price = 0.0
        for expense in self.objects():
            price += expense.price()
        return price


@grok.adapter(interfaces.IWorkExpensesContainerHolder)
@grok.implementer(interfaces.IWorkExpensesContainer)
def workexpenses_of_holder(holder):
    """ Returns the :py:class:`WorkExpenseContainer` of the holder if it
        does not yet exist one is created
    """
    if not 'workexpenses' in holder:
        holder['workexpenses'] = WorkExpensesContainer()
    return holder['workexpenses']


class WorkExpenseFormProxy(grok.Adapter):
    """ Proxy to store work expenses and link them to the
        current :py:class:`horae.properties.interfaces.IPropertyChange`
    """
    grok.context(interfaces.IWorkExpensesContainerHolder)
    grok.implements(interfaces.IWorkExpenseForm)

    def __init__(self, context):
        super(WorkExpenseFormProxy, self).__init__(context)
        self.__parent__ = self.context

    def set_workexpense(self, workexpense):
        expense = WorkExpense()
        interfaces.IWorkExpensesContainer(self.context).add_object(expense)
        expense.costunit = workexpense.costunit
        expense.resource = workexpense.resource
        expense.propertychange = IPropertied(self.context).current()

    def get_workexpense(self):
        return None
    workexpense = property(get_workexpense, set_workexpense)


class WorkExpense(Expense, RelationResourceCostunitMixin):
    """ A work expense
    """
    grok.implements(interfaces.IRelationWorkExpense)

    id = schema.fieldproperty.FieldProperty(interfaces.IWorkExpense['id'])
    timeentry = schema.fieldproperty.FieldProperty(interfaces.IWorkExpense['timeentry'])

    def price(self):
        """ The price of this object
        """
        if not self.timeentry:
            return 0.0
        return self.timeentry.hours() * self.costunit_rate


class HourlyExpenses(grok.Adapter, timeaware.TimeAware):
    """ An object aware of hourly expenses
    """
    grok.context(interfaces.IHourlyExpensesAware)
    grok.implements(interfaces.IHourlyExpenses)
    grok.provides(interfaces.IHourlyExpenses)

    def hourlyexpenses(self):
        return [interfaces.IHourlyExpensesContainer(holder) for holder in component.getUtility(query.interfaces.IQuery).searchResults(
                    query.And(query.set.AnyOf(('catalog', 'implements'), [interfaces.IHourlyExpensesContainerHolder.__identifier__, ]),
                              query.set.AnyOf(('catalog', 'path'), [ILocationInfo(self.context).getPath(), ])))]

    def get_entries(self):
        entries = []
        for expense in self.hourlyexpenses():
            entries.extend(expense._entries)
        return entries

    def set_entries(self, value):
        pass # not allowed
    _entries = property(get_entries, set_entries)

    def price(self):
        """ The price of this object
        """
        price = 0.0
        for expense in self.hourlyexpenses():
            price += expense.price()
        return price


class HourlyExpensesContainer(container.Container, timeaware.TimeAware):
    """ A container for hourly expenses
    """
    grok.implements(interfaces.IHourlyExpensesContainer)

    def id_key(self):
        return 'hourlyexpense'

    def get_entries(self):
        return [expense.timeentry for expense in self.objects()]

    def set_entries(self, value):
        pass # not allowed
    _entries = property(get_entries, set_entries)

    def price(self):
        """ The price of this object
        """
        price = 0.0
        for expense in self.objects():
            price += expense.price()
        return price


@grok.adapter(interfaces.IHourlyExpensesContainerHolder)
@grok.implementer(interfaces.IHourlyExpensesContainer)
def hourlyexpenses_of_holder(holder):
    """ Returns the :py:class:`HourlyExpensesContainer` of the holder if it
        does not yet exist one is created
    """
    if not 'hourlyexpenses' in holder:
        holder['hourlyexpenses'] = HourlyExpensesContainer()
    return holder['hourlyexpenses']


class HourlyExpensesFormProxy(grok.Adapter):
    """ Proxy to store hourly expenses and link them to the
        current :py:class:`horae.properties.interfaces.IPropertyChange`
    """
    grok.context(interfaces.IHourlyExpensesContainerHolder)
    grok.implements(interfaces.IHourlyExpensesForm)

    def __init__(self, context):
        super(HourlyExpensesFormProxy, self).__init__(context)
        self.__parent__ = self.context

    def set_hourlyexpenses(self, hourlyexpenses):
        propertychange = IPropertied(self.context).current()
        container = interfaces.IHourlyExpensesContainer(self.context)
        for expense in hourlyexpenses:
            container.add_object(expense)
            expense.propertychange = propertychange

    def get_hourlyexpenses(self):
        return []
    hourlyexpenses = property(get_hourlyexpenses, set_hourlyexpenses)


class HourlyExpense(Expense, timeaware.TimeAware):
    """ An hourly expense
    """
    grok.implements(interfaces.IRelationHourlyExpense)

    id = schema.fieldproperty.FieldProperty(interfaces.IHourlyExpense['id'])
    date_start = schema.fieldproperty.FieldProperty(interfaces.IHourlyExpense['date_start'])
    date_end = schema.fieldproperty.FieldProperty(interfaces.IHourlyExpense['date_end'])

    resource_rate = 0.0

    def set_resource(self, obj):
        super(HourlyExpense, self).set_resource(obj)
        self.resource_rate = obj.rate

    def get_resource(self):
        return super(HourlyExpense, self).get_resource()
    resource = property(get_resource, set_resource)

    def get_entries(self):
        entry = timeaware.TimeEntry()
        entry.date_start = self.date_start
        entry.date_end = self.date_end
        return [entry, ]

    def set_entries(self, value):
        pass # not allowed
    _entries = property(get_entries, set_entries)

    def price(self):
        """ The price of this object
        """
        return self.hours() * self.resource_rate

HourlyExpensesWidget = CustomWidgetFactory(ListSequenceWidget, subwidget=CustomWidgetFactory(ObjectWidget, HourlyExpense))


class OnetimeExpenses(grok.Adapter):
    """ An object aware of one-time expenses
    """
    grok.context(interfaces.IOnetimeExpensesAware)
    grok.implements(interfaces.IOnetimeExpenses)
    grok.provides(interfaces.IOnetimeExpenses)

    def price(self):
        """ The price of this object
        """
        price = 0.0
        for holder in component.getUtility(query.interfaces.IQuery).searchResults(
            query.And(query.set.AnyOf(('catalog', 'implements'), [interfaces.IOnetimeExpensesContainerHolder.__identifier__, ]),
                      query.set.AnyOf(('catalog', 'path'), [ILocationInfo(self.context).getPath(), ]))):
            price += interfaces.IOnetimeExpensesContainer(holder).price()
        return price


class OnetimeExpensesContainer(container.Container):
    """ A container for one-time expenses
    """
    grok.implements(interfaces.IOnetimeExpensesContainer)

    def id_key(self):
        return 'onetimeexpense'

    def price(self):
        """ The price of this object
        """
        price = 0.0
        for expense in self.objects():
            price += expense.price()
        return price


@grok.adapter(interfaces.IOnetimeExpensesContainerHolder)
@grok.implementer(interfaces.IOnetimeExpensesContainer)
def onetimeexpenses_of_holder(holder):
    """ Returns the :py:class:`OnetimeExpensesContainer` of the holder if it
        does not yet exist one is created
    """
    if not 'onetimeexpenses' in holder:
        holder['onetimeexpenses'] = OnetimeExpensesContainer()
    return holder['onetimeexpenses']


class OnetimeExpensesFormProxy(grok.Adapter):
    """ Proxy to store one time expenses and link them to the
        current :py:class:`horae.properties.interfaces.IPropertyChange`
    """
    grok.context(interfaces.IOnetimeExpensesContainerHolder)
    grok.implements(interfaces.IOnetimeExpensesForm)

    def __init__(self, context):
        super(OnetimeExpensesFormProxy, self).__init__(context)
        self.__parent__ = self.context

    def set_onetimeexpenses(self, onetimeexpenses):
        propertychange = IPropertied(self.context).current()
        container = interfaces.IOnetimeExpensesContainer(self.context)
        for expense in onetimeexpenses:
            container.add_object(expense)
            expense.propertychange = propertychange

    def get_onetimeexpenses(self):
        return []
    onetimeexpenses = property(get_onetimeexpenses, set_onetimeexpenses)


class OnetimeExpense(Expense):
    """ A one-time expense
    """
    grok.implements(interfaces.IRelationOnetimeExpense)

    id = schema.fieldproperty.FieldProperty(interfaces.IOnetimeExpense['id'])
    name = schema.fieldproperty.FieldProperty(interfaces.IOnetimeExpense['name'])
    description = schema.fieldproperty.FieldProperty(interfaces.IOnetimeExpense['description'])
    onetimeprice = schema.fieldproperty.FieldProperty(interfaces.IOnetimeExpense['onetimeprice'])

    def price(self):
        """ The price of this object
        """
        return self.onetimeprice

OnetimeExpensesWidget = CustomWidgetFactory(ListSequenceWidget, subwidget=CustomWidgetFactory(ObjectWidget, OnetimeExpense))


class DeactivatedExpensesContainer(container.Container):
    """ A container for deactivated expenses
    """
    grok.implements(interfaces.IDeactivatedExpensesContainer)

    def id_key(self):
        return 'deactivatedexpense'

    def add_object(self, obj):
        """ Adds a new object and returns the generated id
        """
        if not obj.id:
            obj.id = component.getUtility(interfaces.IIntIdManager).nextId(self.id_key())
        self._last = obj
        self[str(obj.id)] = obj
        return obj.id


@grok.adapter(interfaces.IDeactivatedExpensesContainerHolder)
@grok.implementer(interfaces.IDeactivatedExpensesContainer)
def deactivatedexpenses_of_holder(holder):
    """ Returns the :py:class:`DeactivatedExpensesContainer` of the holder if it
        does not yet exist one is created
    """
    if not 'deactivatedexpenses' in holder:
        holder['deactivatedexpenses'] = DeactivatedExpensesContainer()
    return holder['deactivatedexpenses']


class DeactivateExpensesFormProxy(grok.Adapter):
    """ Proxy to deactivate expenses and link them to the
        current :py:class:`horae.properties.interfaces.IPropertyChange`
    """
    grok.context(interfaces.IDeactivatedExpensesContainerHolder)
    grok.implements(interfaces.IDeactivateExpensesForm)

    def __init__(self, context):
        super(DeactivateExpensesFormProxy, self).__init__(context)
        self.__parent__ = self.context

    def _deactivate_expenses(self, expenses):
        propertychange = IPropertied(self.context).current()
        for expense in expenses:
            expense.deactivate()
            expense.deactivate_propertychange = propertychange

    def set_deactivate_workexpenses(self, workexpenses):
        self._deactivate_expenses(workexpenses)
        timeaware = utils.findParentByInterface(self.context, ITimeAware)
        for expense in workexpenses:
            timeaware.remove(expense.timeentry)

    def get_deactivate_workexpenses(self):
        return []
    deactivate_workexpenses = property(get_deactivate_workexpenses, set_deactivate_workexpenses)

    def set_deactivate_hourlyexpenses(self, hourlyexpenses):
        self._deactivate_expenses(hourlyexpenses)

    def get_deactivate_hourlyexpenses(self):
        return []
    deactivate_hourlyexpenses = property(get_deactivate_hourlyexpenses, set_deactivate_hourlyexpenses)

    def set_deactivate_onetimeexpenses(self, onetimeexpenses):
        self._deactivate_expenses(onetimeexpenses)

    def get_deactivate_onetimeexpenses(self):
        return []
    deactivate_onetimeexpenses = property(get_deactivate_onetimeexpenses, set_deactivate_onetimeexpenses)
