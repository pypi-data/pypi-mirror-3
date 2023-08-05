from zope import interface
from zope import schema

from z3c.relationfield import Relation
from z3c.relationfield.interfaces import IHasRelations

from horae.core import interfaces
from horae.groupselect.field import GroupedChoice
from horae.groupselect.interfaces import IGroups
from horae.timeaware.interfaces import ITimeEntryContainer, ITimeAware, ITimeEntry, ITimeRange

from horae.resources import _


class IGlobalResources(interfaces.IContainer):
    """ Global resources
    """


class IGlobalResourcesHolder(interface.Interface):
    """ Marker interface for objects adaptable to IGlobalResources
    """


class IResourceTypes(interface.Interface):
    """ Provider for available resource types
    """

    def types():
        """ Returns a list of available resource types
        """


class IResource(interfaces.IIntId, IHasRelations):
    """ A resource
    """

    type = interface.Attribute(u'Type of resource')

    name = schema.TextLine(
        title=_(u'Name'),
        required=True
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False
    )

    users = schema.Set(
        title=_(u'Users'),
        description=_(u'Users allowed to enter work of this resource'),
        required=False,
        value_type=schema.Choice(
            vocabulary='horae.auth.vocabulary.usernames'
        )
    )

    groups = schema.Set(
        title=_(u'Groups'),
        description=_(u'Groups allowed to enter work of this resource'),
        required=False,
        value_type=schema.Choice(
            vocabulary='horae.auth.vocabulary.groupids'
        )
    )


class IHumanResource(IResource):
    """ A human resource
    """

    user = schema.Choice(
        title=_(u'User'),
        description=_(u'The user this resource is bound to'),
        required=False,
        vocabulary='horae.auth.vocabulary.usernames'
    )

    costunits = schema.Set(
        title=_(u'Cost units'),
        description=_(u'The available cost units'),
        required=False,
        value_type=schema.Choice(
            vocabulary='horae.resources.vocabulary.costunits'
        )
    )

    default_costunit = schema.Choice(
        title=_(u'Default cost unit'),
        required=False,
        vocabulary='horae.resources.vocabulary.costunits'
    )

    @interface.invariant
    def defaultCostunitOfCostunits(human_resource):
        if not human_resource.default_costunit in human_resource.costunits:
            raise interface.Invalid(_(u'Default cost unit not part of the available cost units'))


class IHourlyResource(IResource):
    """ A resource based on an hourly rate
    """

    rate = schema.Float(
        title=_(u'Hourly rate'),
        required=True,
        default=0.0,
        min=0.0
    )


class IWorkTime(ITimeEntryContainer):
    """ A container for work time
    """


class IPlannedWorkTimeHolder(interface.Interface):
    """ Marker interface for objects adaptable to IPlannedWorkTime
    """


class IPlannedWorkTime(IWorkTime):
    """ The planned work time of a human resource
    """


class IEffectiveWorkTimeHolder(interface.Interface):
    """ Marker interface for objects adaptable to IEffectiveWorkTime
    """


class IEffectiveWorkTime(IWorkTime):
    """ The effective work time of a human resource
    """


class IAbsenceHolder(interface.Interface):
    """ Marker interface for objects adaptable to IAbsence
    """


class IAbsence(ITimeEntryContainer):
    """ The absence of a human resource
    """


class IAbsenceTimeEntry(ITimeEntry):
    """ An absence time entry additionally storing the cause of the absence
    """

    cause = schema.Text(
        title=_(u'Cause of the absence'),
        required=False
    )


class IOnetimeResource(IResource):
    """ A one-time resource
    """


class IPlannedResourcesHolder(interface.Interface):
    """ Marker interface for objects adaptable to IPlannedResources
    """

    estimated_hours = interface.Attribute('estimated_hours')


class IPlannedResources(interfaces.IContainer, interfaces.IPriced):
    """ Container for planned resources
    """

    def percentage():
        """ The total percentage of the planned resources
        """


class ResourceCostunitGroups(object):
    """ Groups the provided vocabulary by resource
    """
    interface.implements(IGroups)

    def groups(self, vocabulary):
        """
        Converts the given vocabulary into a list of groups::

            return (('Group 1', (term1, term2, term3)),
                    ('Group 2', (term6, term5, term6)),)
        """
        groups = {}
        for term in vocabulary:
            if not term.value.resource_name in groups:
                groups[term.value.resource_name] = ()
            groups[term.value.resource_name] = groups[term.value.resource_name] + (term,)
        return groups.items()


class IResourceCostunit(interface.Interface):
    """ A combination of a human resource and an associated cost unit
    """

    resource = schema.Choice(
        title=_(u'The associated human resource'),
        required=True,
        vocabulary='horae.resources.vocabulary.humanresources'
    )

    costunit = schema.Choice(
        title=_(u'The associated cost unit'),
        required=True,
        vocabulary='horae.resources.vocabulary.costunits'
    )

    costunit_rate = interface.Attribute('costunit_rate')
    costunit_name = interface.Attribute('costunit_name')
    resource_name = interface.Attribute('resource_name')

    @interface.invariant
    def costunitOfResource(planned_resource):
        if not planned_resource.costunit in planned_resource.resource.costunits:
            raise interface.Invalid(_(u'The selected cost unit is not part of the selected resource'))


class IPlannedResource(interfaces.IIntId, interfaces.IPriced, IResourceCostunit):
    """ A planned resource
    """

    percentage = schema.Float(
        title=_(u'Percentage'),
        required=True,
        min=0.0,
        max=100.0
    )

    def hours():
        """ The hours planned for this resource
        """


class IRelationPlannedResource(IPlannedResource):
    """ A planned resource using zc.relation to reference the resource and cost unit
    """

    resource_rel = Relation()
    costunit_rel = Relation()


class ICostUnitsHolder(interface.Interface):
    """ Marker interface for objects adaptable to ICostUnits
    """


class ICostUnits(interfaces.IContainer):
    """ Container for cost units
    """


class ICostUnit(interfaces.IIntId, interfaces.IPriced):
    """ A cost unit
    """

    name = schema.TextLine(
        title=_(u'Name'),
        required=True
    )

    rate = schema.Float(
        title=_(u'Hourly rate'),
        required=True,
        min=0.0
    )

    title = interface.Attribute('title')


class IExpense(interface.Interface):
    """ A general expense
    """

    resource = schema.Field(
        title=_(u'The associated resource'),
        required=True
    )

    propertychange = interface.Attribute('propertychange',
        """ The associated property change
        """
    )

    deactivate_propertychange = interface.Attribute('deactivate_propertychange',
        """ The property change which deactivated this expense
        """
    )

    resource_name = interface.Attribute('resource_name')

    def deactivate():
        """ Deactivates this expense
        """


class IRelationExpense(IExpense, IHasRelations):
    """ A general expense which references a property change using zc.relations
    """

    propertychange_rel = Relation()
    deactivate_propertychange_rel = Relation()


class IWorkExpensesAware(interface.Interface):
    """ Marker interface for objects adaptable to IWorkExpenses
    """


class IWorkExpenses(ITimeAware, interfaces.IPriced):
    """ An object aware of work expenses
    """


class IWorkExpensesContainerHolder(interface.Interface):
    """ Marker interface for objects adaptable to IWorkExpensesContainer
    """


class IWorkExpensesContainer(interfaces.IContainer, IWorkExpenses):
    """ A container for work expenses
    """


class IWorkExpense(IExpense, interfaces.IIntId, interfaces.IPriced, IResourceCostunit):
    """ A work expense
    """

    timeentry = schema.Object(
        title=_(u'The associated time entry'),
        required=True,
        schema=ITimeEntry
    )


class IRelationWorkExpense(IWorkExpense, IRelationExpense):
    """ A work expense using zc.relation to reference the resource and cost unit
    """

    resource_rel = Relation()
    costunit_rel = Relation()


class IWorkExpenseForm(interface.Interface):
    """ A form to select the desired resource and cost unit for a work expense
    """

    workexpense = GroupedChoice(
        title=_(u'Resource and cost unit'),
        required=True,
        vocabulary='horae.resources.vocabulary.resourcecostunit',
        groups=ResourceCostunitGroups()
    )


class IHourlyExpensesAware(interface.Interface):
    """ Marker interface for objects adaptable to IHourlyExpenses
    """


class IHourlyExpenses(ITimeAware, interfaces.IPriced):
    """ An object aware of hourly expenses
    """


class IHourlyExpensesContainerHolder(interface.Interface):
    """ Marker interface for objects adaptable to IHourlyExpensesContainer
    """


class IHourlyExpensesContainer(interfaces.IContainer, IHourlyExpenses):
    """ A container for hourly expenses
    """


class IHourlyExpenseBase(IExpense, ITimeRange, ITimeAware):
    """ Basic hourly expense schema
    """

    resource = schema.Choice(
        title=_(u'The associated hourly resource'),
        required=True,
        vocabulary='horae.resources.vocabulary.hourlyresources'
    )


class IHourlyExpense(IHourlyExpenseBase, interfaces.IIntId, interfaces.IPriced):
    """ An hourly expense
    """

    resource_rate = interface.Attribute('resource_rate')


class IRelationHourlyExpense(IHourlyExpense, IRelationExpense):
    """ An hourly expense using zc.relation to reference the resource
    """

    resource_rel = Relation()


class IHourlyExpensesForm(interface.Interface):
    """ A form to add, edit and remove hourly expenses
    """

    hourlyexpenses = schema.List(
        title=_(u'Hourly expense'),
        required=False,
        value_type=schema.Object(
            schema=IHourlyExpenseBase
        )
    )


class IOnetimeExpensesAware(interface.Interface):
    """ Marker interface for objects adaptable to IOnetimeExpenses
    """


class IOnetimeExpenses(interfaces.IPriced):
    """ An object aware of one-time expenses
    """


class IOnetimeExpensesContainerHolder(interface.Interface):
    """ Marker interface for objects adaptable to IOnetimeExpensesContainer
    """


class IOnetimeExpensesContainer(interfaces.IContainer, IOnetimeExpenses):
    """ A container for one-time expenses
    """


class IOnetimeExpenseBase(IExpense):
    """ Basic one-time expense schema
    """

    name = schema.TextLine(
        title=_(u'Name'),
        required=True
    )

    resource = schema.Choice(
        title=_(u'The associated resource'),
        required=True,
        vocabulary='horae.resources.vocabulary.onetimeresources'
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False
    )

    onetimeprice = schema.Float(
        title=_(u'Price'),
        required=True,
        min=0.0,
        default=0.0
    )


class IOnetimeExpense(IOnetimeExpenseBase, interfaces.IIntId, interfaces.IPriced):
    """ A one-time expense
    """


class IRelationOnetimeExpense(IOnetimeExpense, IRelationExpense):
    """ A one-time expense using zc.relation to reference the resource
    """

    resource_rel = Relation()


class IOnetimeExpensesForm(interface.Interface):
    """ A form to add, edit and remove one-time expenses
    """

    onetimeexpenses = schema.List(
        title=_(u'One-time expense'),
        required=False,
        value_type=schema.Object(
            schema=IOnetimeExpenseBase
        )
    )


class IDeactivatedExpensesContainerHolder(interface.Interface):
    """ Marker interface for objects adaptable to IDeactivatedExpensesContainer
    """


class IDeactivatedExpensesContainer(interfaces.IContainer):
    """ A container for deactivated expenses
    """


class IDeactivateExpensesForm(interface.Interface):
    """ A form to deactivate expenses
    """

    deactivate_workexpenses = schema.Set(
        title=_(u'Deactivate work expense'),
        required=False,
        value_type=schema.Choice(
            vocabulary='horae.resources.vocabulary.workexpenses'
        )
    )

    deactivate_hourlyexpenses = schema.Set(
        title=_(u'Deactivate hourly expense'),
        required=False,
        value_type=schema.Choice(
            vocabulary='horae.resources.vocabulary.hourlyexpenses'
        )
    )

    deactivate_onetimeexpenses = schema.Set(
        title=_(u'Deactivate one-time expense'),
        required=False,
        value_type=schema.Choice(
            vocabulary='horae.resources.vocabulary.onetimeexpenses'
        )
    )


class IExpensesAware(IWorkExpensesAware, IHourlyExpensesAware, IOnetimeExpensesAware):
    """ Objects aware of work, hourly and one-time expenses
    """


class IExpensesContainerHolder(IWorkExpensesContainerHolder, IHourlyExpensesContainerHolder, IOnetimeExpensesContainerHolder, IDeactivatedExpensesContainerHolder):
    """ Marker interfaces for objects adaptable to :py:class:`IWorkExpensesContainer`,
        :py:class:`IHourlyExpensesContainer`, :py:class:`IOnetimeExpensesContainer`,
        :py:class:`IDeactivatedExpensesContainer`
    """


class IEstimatedExpenses(interface.Interface):
    """ Objects holding estimated expenses
    """

    def onetime():
        """ The estimated one time expense
        """

    def hourly():
        """ The estimated hourly expense
        """

    def hours():
        """ The estimated work hours
        """

    def workcost():
        """ The estimated work cost
        """
