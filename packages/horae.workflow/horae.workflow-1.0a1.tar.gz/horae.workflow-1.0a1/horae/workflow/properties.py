# -*- coding: utf-8 -*-
import grok

from zope import interface
from zope import component
from zope import schema
from zope.location.interfaces import ILocationInfo
from zope.catalog.interfaces import ICatalog
from zope.intid.interfaces import IIntIds

from hurry import query
from hurry.workflow.interfaces import IWorkflowInfo, IWorkflowState

from horae.core.interfaces import IHorae
from horae.search.interfaces import ISortingProvider, IColumnProvider
from horae.search.properties import BaseSearchableProperty
from horae.ticketing.interfaces import IClient, IProject, IMilestone, ITicket
from horae.properties.interfaces import IPropertied, IDefaultGlobalProperty, IComplete, IOffer
from horae.properties.properties import ChoiceProperty
from horae.autocomplete import fields

from horae.workflow.utils import stateName
from horae.workflow import interfaces
from horae.workflow import _


class WorkflowProperty(ChoiceProperty):
    """ A workflow property
    """
    interface.implements(interfaces.IWorkflowProperty)
    type = _(u'Workflow')

    initial = False

    def apply(self, obj, **data):
        """ Applies the data to the obj
        """
        info = self.workflowInfo(obj)
        transition = data.get(self.id, None)
        if transition is None:
            return
        info.fireTransition(data[self.id])

    def render(self, value, context, request, widget=None):
        """ Returns the rendered value
        """
        if not value:
            value = IWorkflowState(context).getState()
        return stateName(context, value)

    def process(self, **data):
        """ Processes the input coming from the form and returns a new data dictionary
        """
        if 'workflow' in data and data['workflow'] is None:
            del data['workflow']
        return data

    def workflowInfo(self, context):
        return IWorkflowInfo(context)

    def convertValue(self, value):
        return value

    def getVocabulary(self, context):
        """ Returns the vocabulary used by the field
        """
        info = self.workflowInfo(context)
        transitions = info.getManualTransitionIds()
        terms = []
        state = info.state(context).getState()
        for value in transitions:
            converted = self.convertValue(value)
            transition = info.workflow.get_transition(value[:(-len(state) - 1)])
            if transition is None:
                continue
            terms.append(schema.vocabulary.SimpleTerm(converted, converted, transition.name))
        return schema.vocabulary.SimpleVocabulary(terms)

    def fields(self, context):
        """ Returns a list of fields (zope.formlib.interfaces.IField)
        """
        if not len(self.getVocabulary(context)):
            return []
        return super(WorkflowProperty, self).fields(context)


class SearchableWorkflowProperty(BaseSearchableProperty):
    """ A searchable workflow property
    """
    grok.context(interfaces.IWorkflowProperty)
    holders = ((interfaces.IClientWorkflowHolder, interfaces.IClientWorkflow),
               (interfaces.IProjectWorkflowHolder, interfaces.IProjectWorkflow),
               (interfaces.IMilestoneWorkflowHolder, interfaces.IMilestoneWorkflow),
               (interfaces.ITicketWorkflowHolder, interfaces.ITicketWorkflow))

    def fields(self, catalog, context, request):
        """ Returns a list of fields used to search for values of this property
        """
        seen = []
        states = component.getUtility(ICatalog, name='states').searchResults(final={'any_of': (0, 1)})
        terms = []
        if states is not None:
            for state in states:
                if state.id in seen:
                    continue
                seen.append(state.id)
                terms.append(schema.vocabulary.SimpleTerm(state.id, state.id, state.name))
        if not len(terms):
            return []
        return self.context._prepare_fields([fields.AutocompleteList(
                __name__=self.context.id,
                title=self.context.name,
                description=self.context.description,
                value_type=schema.Choice(
                    vocabulary=schema.vocabulary.SimpleVocabulary(terms),
                ),
                required=False,
            ), ])

    def index(self, value, field, context):
        if not value:
            value = IWorkflowState(context).getState()
        return value

    def query(self, **data):
        """ Returns query
        """
        if self.context.id in data and data[self.context.id] is not None:
            return query.In(('properties', self.context.id), data[self.context.id])
        return None


def workflow_property():
    """ Global property providing a field to select a workflow transition to
        perform on the given object
    """
    property = WorkflowProperty()
    property.id = 'workflow'
    property.name = _(u'State')
    property.order = 20
    property.display = True
    property.customizable = False
    return property
grok.global_utility(workflow_property, provides=IDefaultGlobalProperty, name='workflow')


class BaseComplete(grok.Adapter):
    """ Base implementation of an adapter to determine whether an object has
        been completed or not
    """
    grok.baseclass()
    grok.implements(IComplete)

    def __call__(self):
        """ Returns whether the object has been completed or not
        """
        info = IWorkflowInfo(self.context)
        state = IWorkflowState(self.context).getState()
        if info.workflow is None:
            return False
        state = info.workflow.get_state(state)
        return state is not None and state.final


class ClientComplete(BaseComplete):
    """ Adapter to determine whether a client has been completed or not
    """
    grok.context(IClient)


class ProjectComplete(BaseComplete):
    """ Adapter to determine whether a project has been completed or not
    """
    grok.context(IProject)


class MilestoneComplete(BaseComplete):
    """ Adapter to determine whether a milestone has been completed or not
    """
    grok.context(IMilestone)


class TicketComplete(BaseComplete):
    """ Adapter to determine whether a ticket has been completed or not
    """
    grok.context(ITicket)


class BaseOffer(grok.Adapter):
    """ Base implementation of an adapter to determine whether an object
        is in the offer phase or not
    """
    grok.baseclass()
    grok.implements(IOffer)

    def __call__(self):
        """ Returns whether the object is in the offer phase or not
        """
        context = self.context
        while not IHorae.providedBy(context):
            info = IWorkflowInfo(context)
            state = IWorkflowState(context).getState()
            if info.workflow is not None:
                state = info.workflow.get_state(state)
                if state is not None and state.offer:
                    return True
            context = context.__parent__
        return False


class ClientOffer(BaseOffer):
    """ Adapter to determine whether a client is in the offer phase or not
    """
    grok.context(IClient)


class ProjectOffer(BaseOffer):
    """ Adapter to determine whether a project is in the offer phase or not
    """
    grok.context(IProject)


class MilestoneOffer(BaseOffer):
    """ Adapter to determine whether a milestone is in the offer phase or not
    """
    grok.context(IMilestone)


class TicketOffer(BaseOffer):
    """ Adapter to determine whether a ticket is in the offer phase or not
    """
    grok.context(ITicket)


@grok.subscribe(IPropertied, grok.IObjectModifiedEvent)
def reindex_on_workflow_change(obj, event):
    """ Reindexes the offer index for all childs of an object
        if the workflow state changed
    """
    properties = [name for name, value in obj.current().properties()]
    if not 'workflow' in properties:
        return
    catalog = component.getUtility(ICatalog, 'catalog')
    intid = component.getUtility(IIntIds, context=catalog)
    results = component.getUtility(query.interfaces.IQuery).searchResults(query.set.AnyOf(('catalog', 'path'), [ILocationInfo(obj).getPath(), ]))
    index = catalog['offer']
    for ob in results:
        index.index_doc(intid.queryId(ob), ob)


class BaseWorkflowSortingProvider(grok.Adapter):
    """ Base implementation of a sorting provider moving completed objects
        to the bottom of any lists
    """
    grok.baseclass()
    grok.implements(ISortingProvider)

    def add(self):
        """ Returns an integer to be added to the sorting
        """
        return 0

    def adjust(self, sorting):
        """ Adjusts the sorting after all providers sorting where added and returns the adjusted sorting
        """
        if sorting == 0:
            return sorting
        info = IWorkflowInfo(self.context)
        state = IWorkflowState(self.context).getState()
        if info.workflow is None:
            return sorting
        state = info.workflow.get_state(state)
        if state is None:
            return sorting
        if state.final:
            return -1 / sorting
        return sorting * state.sorting


class ClientWorkflowSortingProvider(BaseWorkflowSortingProvider):
    """ Sorting provider moving completed clients to the bottom of any lists
    """
    grok.context(IClient)
    grok.name('horae.workflow.sorting.client')


class ProjectWorkflowSortingProvider(BaseWorkflowSortingProvider):
    """ Sorting provider moving completed projects to the bottom of any lists
    """
    grok.context(IProject)
    grok.name('horae.workflow.sorting.project')


class MilestoneWorkflowSortingProvider(BaseWorkflowSortingProvider):
    """ Sorting provider moving completed milestones to the bottom of any lists
    """
    grok.context(IMilestone)
    grok.name('horae.workflow.sorting.milestone')


class TicketWorkflowSortingProvider(BaseWorkflowSortingProvider):
    """ Sorting provider moving completed tickets to the bottom of any lists
    """
    grok.context(ITicket)
    grok.name('horae.workflow.sorting.ticket')


class StateColumnProvider(grok.Adapter):
    """ Column provider adding the workflow state
    """
    grok.implements(IColumnProvider)
    grok.context(interface.Interface)
    grok.name('horae.workflow.column.state')

    name = 'workflow'
    title = _(u'State')
    sortable = 'workflow'
    insert_after = '*'

    def __init__(self, context):
        self.context = context

    def filterable(self):
        """ Returns a vocabulary for filtering the column or None if no filtering is available
        """
        seen = []
        states = component.getUtility(ICatalog, name='states').searchResults(final={'any_of': (0, 1)})
        terms = []
        if states is not None:
            for state in states:
                if state.id in seen:
                    continue
                seen.append(state.id)
                terms.append(schema.vocabulary.SimpleTerm(state.id, state.id, state.name))
        if not len(terms):
            return None
        return schema.vocabulary.SimpleVocabulary(terms)

    def factory(self, object, request):
        """ Returns the value to be displayed for the given object
        """
        return stateName(object, IWorkflowState(object).getState())

    def cache_key(self, key, *args, **kwargs):
        """ Modifies the cache key if needed and returns it
        """
        return key
