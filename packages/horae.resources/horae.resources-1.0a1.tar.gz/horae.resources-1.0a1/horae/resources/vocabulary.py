from zope.schema import vocabulary
from zope.schema.interfaces import IField
from zope.site.hooks import getSite
from zope import component
from zope.i18n import translate

from horae.core import utils
from horae.core.interfaces import ICurrencyFormatter
from horae.ticketing import _ as _t

from utils import resourceAvailable
from horae.resources.resources import ResourceCostunit
from horae.resources import interfaces


def resources_vocabulary_factory(context):
    """ A vocabulary of all available resources registered as
        **horae.resources.vocabulary.resources**
    """
    parent = utils.findParentByInterface(context, interfaces.IGlobalResourcesHolder)
    terms = []
    if parent is not None:
        for resource in interfaces.IGlobalResources(parent).objects():
            terms.append(vocabulary.SimpleTerm(resource, resource.id, resource.name or resource.id))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.resources.vocabulary.resources', resources_vocabulary_factory)


def humanresources_vocabulary_factory(context):
    """ A vocabulary of all available human resources registered as
        **horae.resources.vocabulary.humanresources**
    """
    parent = utils.findParentByInterface(context, interfaces.IGlobalResourcesHolder)
    terms = []
    if parent is not None:
        for resource in interfaces.IGlobalResources(parent).objects():
            if interfaces.IHumanResource.providedBy(resource):
                terms.append(vocabulary.SimpleTerm(resource, resource.id, resource.name or resource.id))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.resources.vocabulary.humanresources', humanresources_vocabulary_factory)


def humanresourcesid_vocabulary_factory(context):
    """ A vocabulary of all available human resources keyed by ID
        registered as **horae.resources.vocabulary.humanresourcesid**
    """
    parent = utils.findParentByInterface(context, interfaces.IGlobalResourcesHolder)
    terms = []
    if parent is not None:
        for resource in interfaces.IGlobalResources(parent).objects():
            if interfaces.IHumanResource.providedBy(resource):
                terms.append(vocabulary.SimpleTerm(resource.id, resource.id, resource.name or resource.id))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.resources.vocabulary.humanresourcesid', humanresourcesid_vocabulary_factory)


def currentusers_humanresources_vocabulary_factory(context):
    """ A vocabulary of all human resources available for the
        current user registered as
        **horae.resources.vocabulary.currentusershumanresources**
    """
    request = utils.getRequest(None)
    terms = []
    if request is not None:
        parent = utils.findParentByInterface(context, interfaces.IGlobalResourcesHolder)
        if parent is not None:
            for resource in interfaces.IGlobalResources(parent).objects():
                if interfaces.IHumanResource.providedBy(resource) and resource.user == request.principal.id:
                    terms.append(vocabulary.SimpleTerm(resource, resource.id, resource.name or resource.id))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.resources.vocabulary.currentusershumanresources', currentusers_humanresources_vocabulary_factory)


def hourlyresources_vocabulary_factory(context):
    """ A vocabulary of all available hourly resources registered as
        **horae.resources.vocabulary.hourlyresources**
    """
    if context is None:
        context = getSite()
    if IField.providedBy(context):
        context = context.context
    parent = utils.findParentByInterface(context, interfaces.IGlobalResourcesHolder)
    terms = []
    if parent is not None:
        for resource in interfaces.IGlobalResources(parent).objects():
            if interfaces.IHourlyResource.providedBy(resource) and resourceAvailable(resource):
                terms.append(vocabulary.SimpleTerm(resource, resource.id, resource.name or resource.id))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.resources.vocabulary.hourlyresources', hourlyresources_vocabulary_factory)


def onetimeresources_vocabulary_factory(context):
    """ A vocabulary of all available one time resources registered as
        **horae.resources.vocabulary.onetimeresources**
    """
    if context is None:
        context = getSite()
    if IField.providedBy(context):
        context = context.context
    parent = utils.findParentByInterface(context, interfaces.IGlobalResourcesHolder)
    terms = []
    if parent is not None:
        for resource in interfaces.IGlobalResources(parent).objects():
            if interfaces.IOnetimeResource.providedBy(resource) and resourceAvailable(resource):
                terms.append(vocabulary.SimpleTerm(resource, resource.id, resource.name or resource.id))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.resources.vocabulary.onetimeresources', onetimeresources_vocabulary_factory)


def plannedresources_vocabulary_factory(context):
    """ A vocabulary of all available planned resources registered as
        **horae.resources.vocabulary.plannedresources**
    """
    parent = utils.findParentByInterface(context, interfaces.IPlannedResourcesHolder)
    terms = []
    if parent is not None:
        for resource in interfaces.IPlannedResources(parent).objects():
            terms.append(vocabulary.SimpleTerm(resource, resource.resource.id, resource.resource.name or resource.resource.id))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.resources.vocabulary.plannedresources', plannedresources_vocabulary_factory)


def costunits_vocabulary_factory(context):
    """ A vocabulary of all available cost units registered as
        **horae.resources.vocabulary.costunits**
    """
    parent = utils.findParentByInterface(context, interfaces.ICostUnitsHolder)
    terms = []
    if parent is not None:
        for costunit in interfaces.ICostUnits(parent).objects():
            terms.append(vocabulary.SimpleTerm(costunit, costunit.id, costunit.title or costunit.id))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.resources.vocabulary.costunits', costunits_vocabulary_factory)


def resource_costunit_vocabulary_factory(context):
    """ A vocabulary of all available resource cost unit combinations
        registered as **horae.resources.vocabulary.resourcecostunit**
    """
    resources = plannedresources_vocabulary_factory(context)
    if not len(resources):
        resources = humanresources_vocabulary_factory(context)
    terms = []
    for resource in resources:
        resource = resource.value
        if interfaces.IPlannedResource.providedBy(resource):
            costunits = [resource.costunit, ]
            resource = resource.resource
        else:
            costunits = resource.costunits
        if not resourceAvailable(resource):
            continue
        for costunit in costunits:
            expense = ResourceCostunit()
            expense.__parent__ = context.__parent__
            expense.costunit = costunit
            expense.resource = resource
            terms.append(vocabulary.SimpleTerm(expense, '.'.join((str(resource.id), str(costunit.id))), costunit.title or costunit.id))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.resources.vocabulary.resourcecostunit', resource_costunit_vocabulary_factory)


def workexpenses_vocabulary_factory(context):
    """ A vocabulary of all available work expenses registered as
        **horae.resources.vocabulary.workexpenses**
    """
    parent = utils.findParentByInterface(context, interfaces.IWorkExpensesContainerHolder)
    terms = []
    try:
        request = utils.getRequest()
        formatter = component.getMultiAdapter((context, request), ICurrencyFormatter)
        if parent is not None:
            for expense in interfaces.IWorkExpensesContainer(parent).objects():
                if expense.timeentry is None:
                    continue
                terms.append(vocabulary.SimpleTerm(expense, expense.id, u'%(timerange)s (%(hours)s %(hours_label)s, %(price)s) - %(resource)s, %(costunit)s (%(rate)s)' % {
                    'resource': expense.resource_name,
                    'costunit': expense.costunit_name,
                    'rate': formatter.format(expense.costunit_rate),
                    'timerange': utils.formatDateTimeRange(expense.timeentry.date_start, expense.timeentry.date_end, request, html=False),
                    'hours': utils.formatHours(expense.timeentry.hours(), request),
                    'hours_label': translate(_t(u'Hours'), context=request),
                    'price': formatter.format(expense.price())}))
    except:
        pass # no request found
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.resources.vocabulary.workexpenses', workexpenses_vocabulary_factory)


def hourlyexpenses_vocabulary_factory(context):
    """ A vocabulary of all available hourly expenses registered as
        **horae.resources.vocabulary.hourlyexpenses**
    """
    parent = utils.findParentByInterface(context, interfaces.IHourlyExpensesContainerHolder)
    terms = []
    try:
        formatter = component.getMultiAdapter((context, utils.getRequest()), ICurrencyFormatter)
        if parent is not None:
            for expense in interfaces.IHourlyExpensesContainer(parent).objects():
                terms.append(vocabulary.SimpleTerm(expense, expense.id, u'%s (%s)' % (expense.resource_name, formatter.format(expense.price()))))
    except:
        pass # no request found
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.resources.vocabulary.hourlyexpenses', hourlyexpenses_vocabulary_factory)


def onetimeexpenses_vocabulary_factory(context):
    """ A vocabulary of all available one time expenses registered as
        **horae.resources.vocabulary.onetimeexpenses**
    """
    parent = utils.findParentByInterface(context, interfaces.IOnetimeExpensesContainerHolder)
    terms = []
    try:
        formatter = component.getMultiAdapter((context, utils.getRequest()), ICurrencyFormatter)
        if parent is not None:
            for expense in interfaces.IOnetimeExpensesContainer(parent).objects():
                terms.append(vocabulary.SimpleTerm(expense, expense.id, u'%s (%s)' % (expense.name, formatter.format(expense.price()))))
    except:
        pass # no request found
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.resources.vocabulary.onetimeexpenses', onetimeexpenses_vocabulary_factory)
