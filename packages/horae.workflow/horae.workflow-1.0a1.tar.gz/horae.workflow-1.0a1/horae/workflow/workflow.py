import grok

from time import time
from grok import index
from zope import interface
from zope import schema
from zope.site.hooks import getSite
from zope.annotation.interfaces import IAttributeAnnotatable

from plone.memoize import instance, ram

from hurry.workflow import workflow
from hurry.workflow.interfaces import IWorkflowInfo

from horae.core import container
from horae.core import utils
from horae.core.interfaces import IHorae
from horae.ticketing import ticketing
from horae.ticketing.interfaces import IClient, IProject, IMilestone, ITicket

from horae.workflow import _
from horae.workflow import interfaces
from horae.workflow.utils import transitionAvailable

interface.classImplements(ticketing.Client, interfaces.IProjectWorkflowHolder, interfaces.IMilestoneWorkflowHolder, interfaces.ITicketWorkflowHolder, IAttributeAnnotatable)
interface.classImplements(ticketing.Project, interfaces.IMilestoneWorkflowHolder, interfaces.ITicketWorkflowHolder, IAttributeAnnotatable)
interface.classImplements(ticketing.Milestone, IAttributeAnnotatable)
interface.classImplements(ticketing.Ticket, IAttributeAnnotatable)


def cache_key(method, *args, **kwargs):
    return (getSite().__name__, method.__module__, method.__name__, args[0].__name__, args[0]._modification_date, args[1:], kwargs.items())


class Workflow(container.Container):
    """ A workflow
    """
    grok.implements(interfaces.IWorkflow)

    deactivated_states = schema.fieldproperty.FieldProperty(interfaces.IWorkflow['deactivated_states'])
    deactivated_transitions = schema.fieldproperty.FieldProperty(interfaces.IWorkflow['deactivated_transitions'])
    _initial_state = schema.fieldproperty.FieldProperty(interfaces.IWorkflow['initial_state'])
    _modification_date = 0

    @ram.cache(cache_key)
    def get_initial_state(self):
        if self._initial_state is None:
            parent = self.parent()
            if parent is not None:
                return self.parent().initial_state
        return self._initial_state

    def set_initial_state(self, state):
        self._modification_date = time()
        self._initial_state = str(state)
    initial_state = property(get_initial_state, set_initial_state)

    def deactivate_state(self, state):
        """ Deactivates the specified :py:class:`WorkflowState`
        """
        if state in self.deactivated_states:
            return
        self._modification_date = time()
        self.deactivated_states = set([state, ] + [s for s in self.deactivated_states])

    def activate_state(self, state):
        """ Activates the specified :py:class:`WorkflowState`
        """
        if not state in self.deactivated_states:
            return
        self._modification_date = time()
        self.deactivated_states = set([s for s in self.deactivated_states if not s == state])

    def deactivate_transition(self, transition):
        """ Deactivates the specified :py:class:`WorkflowTransition`
        """
        if transition in self.deactivated_transitions:
            return
        self._modification_date = time()
        self.deactivated_transitions = set([transition, ] + [t for t in self.deactivated_transitions])

    def activate_transition(self, transition):
        """ Activates the specified :py:class:`WorkflowTransition`
        """
        if not transition in self.deactivated_transitions:
            return
        self._modification_date = time()
        self.deactivated_transitions = set([t for t in self.deactivated_transitions if not t == transition])

    @instance.memoize
    def parent(self):
        if interfaces.IClientWorkflow.providedBy(self):
            holder, workflow = interfaces.IClientWorkflowHolder, interfaces.IClientWorkflow
        elif interfaces.IProjectWorkflow.providedBy(self):
            holder, workflow = interfaces.IProjectWorkflowHolder, interfaces.IProjectWorkflow
        elif interfaces.IMilestoneWorkflow.providedBy(self):
            holder, workflow = interfaces.IMilestoneWorkflowHolder, interfaces.IMilestoneWorkflow
        elif interfaces.ITicketWorkflow.providedBy(self):
            holder, workflow = interfaces.ITicketWorkflowHolder, interfaces.ITicketWorkflow
        else:
            return None
        parent = utils.findParentByInterface(self, holder, 1)
        if parent is not None:
            parent = workflow(parent)
        if parent is self:
            return None
        return parent

    @ram.cache(cache_key)
    def inherited_states(self, deactivated=False):
        """ Returns a list of inherited :py:class:`WorkflowState`s
        """
        parent = self.parent()
        if parent is None:
            return []
        return [state for state in parent.states() if deactivated or self.deactivated_states is None or not state.id in self.deactivated_states]

    @ram.cache(cache_key)
    def states(self, deactivated=False):
        """ Returns a list of :py:class:`WorkflowState`s (including inherited)
        """
        return [s for s in interfaces.IWorkflowStates(self).objects()] + self.inherited_states(deactivated)

    @ram.cache(cache_key)
    def get_state(self, id):
        """ Returns the specified :py:class:`WorkflowState`
        """
        states = interfaces.IWorkflowStates(self)
        if id in states:
            return states.get_object(id)
        parent = self.parent()
        if parent is not None:
            return parent.get_state(id)
        return None

    @ram.cache(cache_key)
    def inherited_transitions(self, deactivated=False):
        """ Returns a list of inherited :py:class:`WorkflowTransition`s
        """
        parent = self.parent()
        if parent is None:
            return []
        return [transition for transition in parent.transitions() if deactivated or self.deactivated_transitions is None or not transition.id in self.deactivated_transitions]

    @ram.cache(cache_key)
    def transitions(self, deactivated=False):
        """ Returns a list of :py:class:`WorkflowTransition`s (including inherited)
        """
        return [t for t in interfaces.IWorkflowTransitions(self).objects()] + self.inherited_transitions(deactivated)

    @ram.cache(cache_key)
    def get_transition(self, id):
        """ Returns the specified :py:class:`WorkflowTransition`
        """
        transitions = interfaces.IWorkflowTransitions(self)
        if id in transitions:
            return transitions.get_object(id)
        parent = self.parent()
        if parent is not None:
            return parent.get_transition(id)
        return None

    @ram.cache(cache_key)
    def workflow(self):
        """ Returns a :py:class:`hurry.workflow.workflow.Workflow` instance
        """
        transitions = []
        if self.initial_state:
            transitions.append(workflow.Transition(u'initialize', _(u'Initialize'), None, self.initial_state, trigger=workflow.AUTOMATIC))
        for transition in self.transitions():
            if not transitionAvailable(transition):
                continue
            for source in transition.sources:
                transitions.append(workflow.Transition(transition.id + '.' + source, transition.name, source, transition.destination))
        return workflow.Workflow(transitions)


@grok.subscribe(interfaces.IState, grok.IObjectModifiedEvent)
@grok.subscribe(interfaces.IState, grok.IObjectMovedEvent)
@grok.subscribe(interfaces.ITransition, grok.IObjectModifiedEvent)
@grok.subscribe(interfaces.ITransition, grok.IObjectMovedEvent)
def invalidate_cache(obj, event):
    """ Invalidates the cache of the :py:class:`Workflow` after a state or
        transition has been modified
    """
    workflow = utils.findParentByInterface(obj, interfaces.IWorkflow)
    workflow._modification_date = time()


class WorkflowInfo(workflow.WorkflowInfo, grok.Adapter):
    """ Specialized implementation of a :py:class:`hurry.workflow.interfaces.IWorkflowInfo`
        providing the possibility to access the associated
        :py:class:`Workflow`
    """
    grok.context(IAttributeAnnotatable)

    def __init__(self, context):
        self.context = context
        self.wf = None
        if self.workflow is not None:
            self.wf = self.workflow.workflow()

    @property
    def workflow(self):
        if hasattr(self, '_workflow'):
            return self._workflow
        self._workflow = None
        if IClient.providedBy(self.context):
            self._workflow = interfaces.IClientWorkflow(utils.findParentByInterface(self.context, interfaces.IClientWorkflowHolder))
        if IProject.providedBy(self.context):
            self._workflow = interfaces.IProjectWorkflow(utils.findParentByInterface(self.context, interfaces.IProjectWorkflowHolder))
        if IMilestone.providedBy(self.context):
            self._workflow = interfaces.IMilestoneWorkflow(utils.findParentByInterface(self.context, interfaces.IMilestoneWorkflowHolder))
        if ITicket.providedBy(self.context):
            self._workflow = interfaces.ITicketWorkflow(utils.findParentByInterface(self.context, interfaces.ITicketWorkflowHolder))
        return self._workflow


class WorkflowState(workflow.WorkflowState, grok.Adapter):
    """ Specialized implementation of a :py:class:`hurry.workflow.interfaces.IWorkflowState`
        to have the initial state returned if no state is set on a context
    """
    grok.context(IAttributeAnnotatable)

    def getState(self):
        state = super(WorkflowState, self).getState()
        if state is None:
            info = IWorkflowInfo(self.context)
            if info.workflow is not None:
                state = info.workflow.initial_state
        return state


@grok.adapter(interfaces.IClientWorkflowHolder)
@grok.implementer(interfaces.IClientWorkflow)
def client_workflow_of_holder(holder):
    """ Returns a client :py:class:`Workflow` if it does not yet exist
        one is created
    """
    if not 'client_workflow' in holder:
        holder['client_workflow'] = Workflow()
        interface.alsoProvides(holder['client_workflow'], interfaces.IClientWorkflow)
    return holder['client_workflow']


@grok.adapter(interfaces.IProjectWorkflowHolder)
@grok.implementer(interfaces.IProjectWorkflow)
def project_workflow_of_holder(holder):
    """ Returns a project :py:class:`Workflow` if it does not yet exist
        one is created
    """
    if not 'project_workflow' in holder:
        holder['project_workflow'] = Workflow()
        interface.alsoProvides(holder['project_workflow'], interfaces.IProjectWorkflow)
    return holder['project_workflow']


@grok.adapter(interfaces.IMilestoneWorkflowHolder)
@grok.implementer(interfaces.IMilestoneWorkflow)
def milestone_workflow_of_holder(holder):
    """ Returns a milestone :py:class:`Workflow` if it does not yet exist
        one is created
    """
    if not 'milestone_workflow' in holder:
        holder['milestone_workflow'] = Workflow()
        interface.alsoProvides(holder['milestone_workflow'], interfaces.IMilestoneWorkflow)
    return holder['milestone_workflow']


@grok.adapter(interfaces.ITicketWorkflowHolder)
@grok.implementer(interfaces.ITicketWorkflow)
def ticket_workflow_of_holder(holder):
    """ Returns a ticket :py:class:`Workflow` if it does not yet exist
        one is created
    """
    if not 'ticket_workflow' in holder:
        holder['ticket_workflow'] = Workflow()
        interface.alsoProvides(holder['ticket_workflow'], interfaces.ITicketWorkflow)
    return holder['ticket_workflow']


class WorkflowStates(container.Container):
    """ Container for workflow states
    """
    grok.implements(interfaces.IWorkflowStates)


@grok.adapter(interfaces.IWorkflow)
@grok.implementer(interfaces.IWorkflowStates)
def states_of_workflow(workflow):
    """ Returns a :py:class:`WorkflowStates` if it does not yet exist
        one is created
    """
    if not 'states' in workflow:
        workflow['states'] = WorkflowStates()
    return workflow['states']


class State(grok.Model):
    """ A workflow state
    """
    grok.implements(interfaces.IState)

    id = schema.fieldproperty.FieldProperty(interfaces.IState['id'])
    name = schema.fieldproperty.FieldProperty(interfaces.IState['name'])
    description = schema.fieldproperty.FieldProperty(interfaces.IState['description'])
    sorting = schema.fieldproperty.FieldProperty(interfaces.IState['sorting'])
    final = schema.fieldproperty.FieldProperty(interfaces.IState['final'])
    offer = schema.fieldproperty.FieldProperty(interfaces.IState['offer'])


class StatesCatalog(grok.Indexes):
    """ Provides indexes to search for workflow states
    """
    grok.site(IHorae)
    grok.context(interfaces.IState)
    grok.name('states')

    id = index.Field()
    name = index.Field()
    final = index.Value()
    offer = index.Value()


class WorkflowTransitions(container.Container):
    """ Container for workflow transitions
    """
    interface.implements(interfaces.IWorkflowTransitions)


@grok.adapter(interfaces.IWorkflow)
@grok.implementer(interfaces.IWorkflowTransitions)
def transitions_of_workflow(workflow):
    """ Returns a :py:class:`WorkflowTransitions` if it does not yet exist
        one is created
    """
    if not 'transitions' in workflow:
        workflow['transitions'] = WorkflowTransitions()
    return workflow['transitions']


class Transition(grok.Model):
    """ A workflow transition
    """
    interface.implements(interfaces.ITransition)

    id = schema.fieldproperty.FieldProperty(interfaces.ITransition['id'])
    name = schema.fieldproperty.FieldProperty(interfaces.ITransition['name'])
    description = schema.fieldproperty.FieldProperty(interfaces.ITransition['description'])
    sources = schema.fieldproperty.FieldProperty(interfaces.ITransition['sources'])
    destination = schema.fieldproperty.FieldProperty(interfaces.ITransition['destination'])
    users = schema.fieldproperty.FieldProperty(interfaces.ITransition['users'])
    groups = schema.fieldproperty.FieldProperty(interfaces.ITransition['groups'])
