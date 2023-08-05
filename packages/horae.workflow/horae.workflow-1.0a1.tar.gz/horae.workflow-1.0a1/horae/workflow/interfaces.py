from zope import interface
from zope import schema

from horae.core import interfaces
from horae.properties.interfaces import IProperty

from horae.workflow import _


class IWorkflowHolder(interface.Interface):
    """ Marker interface for objects holding any kind of workflow
    """


class IWorkflow(interface.Interface):
    """ A workflow
    """

    deactivated_states = schema.Set(
        title=_(u'Deactivated states'),
        default=set([]),
        required=False
    )

    deactivated_transitions = schema.Set(
        title=_(u'Deactivated transitions'),
        default=set([]),
        required=False
    )

    initial_state = schema.ASCIILine(
        title=_(u'Initial state'),
        required=True
    )

    def deactivate_state(state):
        """ Deactivates the specified :py:class:`IState`
        """

    def activate_state(state):
        """ Activates the specified :py:class:`IState`
        """

    def deactivate_transition(transition):
        """ Deactivates the specified :py:class:`ITransition`
        """

    def activate_transition(transition):
        """ Activates the specified :py:class:`ITransition`
        """

    def inherited_states(deactivated=False):
        """ Returns a list of inherited :py:class:`IState` s
        """

    def states(deactivated=False):
        """ Returns a list of :py:class:`IState` s (including inherited)
        """

    def get_state(id):
        """ Returns the specified :py:class:`IState`
        """

    def inherited_transitions(deactivated=False):
        """ Returns a list of inherited :py:class:`ITransition` s
        """

    def transitions(deactivated=False):
        """ Returns a list of :py:class:`ITransition` s (including inherited)
        """

    def get_transition(id):
        """ Returns the specified :py:class:`ITransition`
        """

    def workflow():
        """ Returns a :py:class:`hurry.workflow.workflow.Workflow` instance
        """


class IWorkflowProperty(IProperty):
    """ A workflow property
    """

    initial = interface.Attribute('initial',
        """ Always returns false
        """
    )


class IClientWorkflow(IWorkflow):
    """ A client workflow
    """


class IProjectWorkflow(IWorkflow):
    """ A project workflow
    """


class IMilestoneWorkflow(IWorkflow):
    """ A milestone workflow
    """


class ITicketWorkflow(IWorkflow):
    """ A ticket workflow
    """


class IClientWorkflowHolder(IWorkflowHolder):
    """ An object holding a client workflow
    """


class IProjectWorkflowHolder(IWorkflowHolder):
    """ An object holding a project workflow
    """


class IMilestoneWorkflowHolder(IWorkflowHolder):
    """ An object holding a milestone workflow
    """


class ITicketWorkflowHolder(IWorkflowHolder):
    """ An object holding a ticket workflow
    """


class IWorkflowStates(interfaces.IContainer):
    """ Container for workflow states
    """


class IWorkflowTransitions(interfaces.IContainer):
    """ Container for workflow transitions
    """


class IState(interfaces.ITextId):
    """ A workflow state
    """

    name = schema.TextLine(
        title=_(u'Name'),
        required=True
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False
    )

    sorting = schema.Int(
        title=_(u'Sorting factor'),
        default=1,
        required=True
    )

    final = schema.Bool(
        title=_(u'Completed'),
        default=0,
        required=False
    )

    offer = schema.Bool(
        title=_(u'Offer'),
        default=0,
        required=False
    )


class ITransition(interfaces.ITextId):
    """ A workflow transition
    """

    name = schema.TextLine(
        title=_(u'Name'),
        required=True
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False
    )

    sources = schema.Set(
        title=_(u'Source states'),
        required=True,
        value_type=schema.Choice(
            vocabulary='horae.workflow.vocabulary.states'
        )
    )

    destination = schema.Choice(
        title=_(u'Destination state'),
        required=True,
        vocabulary='horae.workflow.vocabulary.states'
    )

    users = schema.Set(
        title=_(u'Users'),
        description=_(u'Users this transition is available for'),
        required=False,
        value_type=schema.Choice(
            vocabulary='horae.auth.vocabulary.users'
        )
    )

    groups = schema.Set(
        title=_(u'Groups'),
        description=_(u'Groups this transition is available for'),
        required=False,
        value_type=schema.Choice(
            vocabulary='horae.auth.vocabulary.groups'
        )
    )
