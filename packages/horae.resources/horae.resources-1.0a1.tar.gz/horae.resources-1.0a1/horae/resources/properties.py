import grok

from zope import component

from horae.core import utils
from horae.core.interfaces import ICurrencyFormatter
from horae.properties import interfaces
from horae.properties import properties
from horae.ticketing.interfaces import ITicket, IProject

from horae.resources import resources
from horae.resources.interfaces import GroupedChoice, ResourceCostunitGroups, ICostUnitsHolder, ICostUnits, IGlobalResourcesHolder, IGlobalResources, IPlannedResources
from horae.resources import _


def estimated_hourly_expense_property():
    """ Ticket property to define the estimated hourly expense
    """
    property = properties.PriceProperty()
    property.id = 'estimated_hourly_expense'
    property.name = _(u'Estimated hourly expense')
    property.order = 24
    property.min = 0.0
    property.initial = True
    property.editable = False
    property.searchable = False
    return property
grok.global_utility(estimated_hourly_expense_property, provides=interfaces.IDefaultTicketProperty, name='estimated_hourly_expense')


def estimated_onetime_expense_property():
    """ Ticket property to define the estimated one time expense
    """
    property = properties.PriceProperty()
    property.id = 'estimated_onetime_expense'
    property.name = _(u'Estimated one-time expense')
    property.order = 26
    property.min = 0.0
    property.initial = True
    property.editable = False
    property.searchable = False
    return property
grok.global_utility(estimated_onetime_expense_property, provides=interfaces.IDefaultTicketProperty, name='estimated_onetime_expenses')


class DefaultPlannedResourceProperty(properties.Property):
    """ Property to select a resource cost unit combination
    """

    type = _(u'Default planned resource')

    def render(self, value, context, request, widget=None):
        """ Returns the rendered value
        """
        if not value:
            return value
        try:
            resource, costunit = value.split('.')
            resource = IGlobalResources(utils.findParentByInterface(context, IGlobalResourcesHolder)).get(resource)
            costunit = ICostUnits(utils.findParentByInterface(context, ICostUnitsHolder)).get(costunit)
            return '%s, %s (%s)' % (resource.name, costunit.name, component.getMultiAdapter((context, request), ICurrencyFormatter).format(costunit.rate))
        except:
            return None

    def fields(self, context):
        """ Returns a list of fields (zope.formlib.interfaces.IField)
        """
        return self._prepare_fields([
            GroupedChoice(
                __name__=self.id,
                title=self.name,
                description=self.description,
                required=self.required,
                vocabulary='horae.resources.vocabulary.resourcecostunit',
                groups=ResourceCostunitGroups()
            ),
        ])


def default_planned_resource():
    """ Project property to define the default planned resource for newly
        created tickets
    """
    property = DefaultPlannedResourceProperty()
    property.id = 'default_planned_resource'
    property.name = _(u'Default resource and cost unit used for newly created tickets')
    property.order = 150
    property.initial = True
    property.editable = True
    property.searchable = False
    property.customizable = False
    return property
grok.global_utility(default_planned_resource, provides=interfaces.IDefaultProjectProperty, name='default_planned_resource')


@grok.subscribe(ITicket, grok.IObjectAddedEvent)
def add_default_planned_resource(ticket, event):
    """ Creates the planned resource defined by the **default_planned_resource**
        project property on ticket creation
    """
    resource_costunit = utils.findParentByInterface(ticket, IProject).get_property('default_planned_resource')
    if resource_costunit is None:
        return
    planned_resource = resources.PlannedResource()
    planned_resource.percentage = 100
    planned_resource.resource = resource_costunit.resource
    planned_resource.costunit = resource_costunit.costunit
    IPlannedResources(ticket).add_object(planned_resource)
