import grok

from zope import component
from zope.i18n import translate
from megrok import navigation

from horae.layout.interfaces import IContextualManageMenu, IObjectTableActionsProvider
from horae.layout import layout
from horae.layout import objects

from horae.workflow import _
from horae.workflow import interfaces
from horae.workflow import workflow

grok.templatedir('templates')


class Workflows(layout.View):
    """ Overview of the available workflows
    """
    grok.context(interfaces.IWorkflowHolder)
    grok.require('horae.Manage')
    grok.name('workflows')
    navigation.menuitem(IContextualManageMenu, _(u'Workflows'))

    def update(self):
        super(Workflows, self).update()
        self.workflows = []
        if interfaces.IClientWorkflowHolder.providedBy(self.context):
            self.workflows.append({'title': _(u'Client workflow'),
                                   'description': _(u'Workflow for clients'),
                                   'url': self.url(interfaces.IClientWorkflow(self.context))})
        if interfaces.IProjectWorkflowHolder.providedBy(self.context):
            self.workflows.append({'title': _(u'Project workflow'),
                                   'description': _(u'Workflow for projects'),
                                   'url': self.url(interfaces.IProjectWorkflow(self.context))})
        if interfaces.IMilestoneWorkflowHolder.providedBy(self.context):
            self.workflows.append({'title': _(u'Milestone workflow'),
                                   'description': _(u'Workflow for milestones'),
                                   'url': self.url(interfaces.IMilestoneWorkflow(self.context))})
        if interfaces.ITicketWorkflowHolder.providedBy(self.context):
            self.workflows.append({'title': _(u'Ticket workflow'),
                                   'description': _(u'Workflow for tickets'),
                                   'url': self.url(interfaces.ITicketWorkflow(self.context))})


class Workflow(layout.View):
    """ View of a workflow rendering an overview of the available
        states and transitions
    """
    grok.context(interfaces.IWorkflow)
    grok.name('index')
    grok.require('horae.Manage')
    grok.template('workflow')

    def label(self):
        if interfaces.IClientWorkflow.providedBy(self.context):
            return _(u'Client workflow')
        if interfaces.IProjectWorkflow.providedBy(self.context):
            return _(u'Project workflow')
        if interfaces.IMilestoneWorkflow.providedBy(self.context):
            return _(u'Milestone workflow')
        if interfaces.ITicketWorkflow.providedBy(self.context):
            return _(u'Ticket workflow')

    def update(self):
        super(Workflow, self).update()
        self.back = self.url(self.context.__parent__) + '/workflows'
        self.states = component.getMultiAdapter((self.context, self.request), name=u'states')(plain=True)
        self.transitions = component.getMultiAdapter((self.context, self.request), name=u'transitions')(plain=True)


class States(objects.ObjectOverview):
    """ Overview of all states
    """
    grok.context(interfaces.IWorkflow)
    grok.name('states')
    grok.require('horae.Manage')

    label = _(u'States')
    add_label = _(u'Add state')
    columns = [('name', _(u'Name')), ('description', _(u'Description')), ('initial', _(u'Initial')), ('actions', u'')]
    container_iface = interfaces.IWorkflowStates

    def row_factory(self, object, columns, request):
        row = super(States, self).row_factory(object, columns, request)
        row['name'] = object.name
        row['description'] = object.description
        row['initial'] = object.id == self.context.initial_state and _(u'Initial state') or ''
        return row

    def add(self):
        return self.url(self.container) + '/add-state'

    def update(self):
        super(objects.ObjectOverview, self).update()
        self.types = []
        self.back = None
        self.container = self.container_iface(self.context)
        self.table = self.get_table(self.context.states(True))()


class StatesActionsProvider(grok.MultiAdapter):
    """ Action provider for states adding buttons to edit, delete
        activate, deactivate and set as initial state the state
    """
    grok.adapts(interfaces.IState, States)
    grok.implements(IObjectTableActionsProvider)
    grok.name('horae.workflow.objecttableactions.state')

    def __init__(self, context, view):
        self.context = context
        self.view = view

    def actions(self, request):
        actions = []
        container_url = self.view.url(self.view.container)
        deactivated = self.view.context.deactivated_states
        if self.context.__parent__ == self.view.container:
            actions.append({'url': container_url + '/edit-state?id=' + self.context.id,
                            'label': translate(_(u'Edit'), context=request),
                            'cssClass': ''})
            actions.append({'url': container_url + '/delete-state?id=' + self.context.id,
                            'label': translate(_(u'Delete'), context=request),
                            'cssClass': 'button-destructive delete'})
        else:
            if deactivated is not None and self.context.id in deactivated:
                actions.append({'url': self.view.url(self.view.context) + '/activate-state?id=' + self.context.id,
                                'label': translate(_(u'Activate'), context=request),
                                'cssClass': ''})
            else:
                actions.append({'url': self.view.url(self.view.context) + '/deactivate-state?id=' + self.context.id,
                                'label': translate(_(u'Deactivate'), context=request),
                                'cssClass': 'button-destructive'})
        if not self.context.id == self.view.context.initial_state:
            actions.append({'url': self.view.url(self.view.context) + '/initial-state?id=' + self.context.id,
                            'label': translate(_(u'Set as initial state'), context=request),
                            'cssClass': 'button-alternative'})
        return actions


class Transitions(objects.ObjectOverview):
    """ Overview of all transitions
    """
    grok.context(interfaces.IWorkflow)
    grok.name('transitions')
    grok.require('horae.Manage')

    label = _(u'Transitions')
    add_label = _(u'Add transition')
    columns = [('name', _(u'Name')), ('description', _(u'Description')), ('sources', _('Source states')), ('destination', _('Destination state')), ('actions', u'')]
    container_iface = interfaces.IWorkflowTransitions

    def row_factory(self, object, columns, request):
        row = super(Transitions, self).row_factory(object, columns, request)
        row['name'] = object.name
        row['description'] = object.description
        row['sources'] = ', '.join([self.context.get_state(s).name for s in object.sources if self.context.get_state(s) is not None])
        row['destination'] = self.context.get_state(object.destination).name if self.context.get_state(s) is not None else u''
        return row

    def add(self):
        return self.url(self.context) + '/add-transition'

    def update(self):
        super(objects.ObjectOverview, self).update()
        self.types = []
        self.back = None
        self.container = self.container_iface(self.context)
        self.table = self.get_table(self.context.transitions(True))()


class TransitionsActionsProvider(grok.MultiAdapter):
    """ Action provider for transitions adding buttons to edit, delete
        activate and deactivate the transition
    """
    grok.adapts(interfaces.ITransition, Transitions)
    grok.implements(IObjectTableActionsProvider)
    grok.name('horae.workflow.objecttableactions.transition')

    def __init__(self, context, view):
        self.context = context
        self.view = view

    def actions(self, request):
        actions = []
        container_url = self.view.url(self.view.container)
        deactivated = self.view.context.deactivated_transitions
        if self.context.__parent__ == self.view.container:
            actions.append({'url': container_url + '/edit-transition?id=' + self.context.id,
                            'label': translate(_(u'Edit'), context=request),
                            'cssClass': ''})
            actions.append({'url': container_url + '/delete-transition?id=' + self.context.id,
                            'label': translate(_(u'Delete'), context=request),
                            'cssClass': 'button-destructive delete'})
        else:
            if deactivated is not None and self.context.id in deactivated:
                actions.append({'url': self.view.url(self.view.context) + '/activate-transition?id=' + self.context.id,
                                'label': translate(_(u'Activate'), context=request),
                                'cssClass': ''})
            else:
                actions.append({'url': self.view.url(self.view.context) + '/deactivate-transition?id=' + self.context.id,
                                'label': translate(_(u'Deactivate'), context=request),
                                'cssClass': 'button-destructive'})
        return actions


class AddState(layout.AddForm):
    """ Add form for states
    """
    grok.context(interfaces.IWorkflowStates)
    grok.require('horae.Manage')
    grok.name('add-state')

    overview = 'index'

    form_fields = grok.AutoFields(interfaces.IState).omit('id')

    def object_type(self):
        return _(u'State')

    def cancel_url(self):
        return self.url(self.context.__parent__)

    def next_url(self, obj=None):
        return self.cancel_url()

    def create(self, **data):
        state = workflow.State()
        state.name = data['name']
        return state

    def add(self, obj):
        self.context.add_object(obj)


class EditState(objects.EditObject):
    """ Edit form of a state
    """
    grok.context(interfaces.IWorkflowStates)
    grok.require('horae.Manage')
    grok.name('edit-state')

    overview = 'index'

    def object_type(self):
        return _(u'State')


class DeleteState(objects.DeleteObject):
    """ Delete form of a state
    """
    grok.context(interfaces.IWorkflowStates)
    grok.require('horae.Manage')
    grok.name('delete-state')

    overview = 'index'

    def object_type(self):
        return _(u'State')


class ActivateState(grok.View):
    """ View activating a state
    """
    grok.context(interfaces.IWorkflow)
    grok.require('horae.Manage')
    grok.name('activate-state')

    def __call__(self, id):
        if isinstance(id, unicode):
            self.context.activate_state(id)
        self.redirect(self.url(self.context))

    def render(self):
        return ''


class DeactivateState(grok.View):
    """ View deactivating a state
    """
    grok.context(interfaces.IWorkflow)
    grok.require('horae.Manage')
    grok.name('deactivate-state')

    def __call__(self, id):
        if isinstance(id, unicode):
            self.context.deactivate_state(id)
        self.redirect(self.url(self.context))

    def render(self):
        return ''


class InitialState(grok.View):
    """ View setting a state as initial state
    """
    grok.context(interfaces.IWorkflow)
    grok.require('horae.Manage')
    grok.name('initial-state')

    def __call__(self, id):
        if isinstance(id, basestring):
            self.context.initial_state = id
        self.redirect(self.url(self.context))

    def render(self):
        return ''


class AddTransition(layout.AddForm):
    """ Add form for transitions
    """
    grok.context(interfaces.IWorkflowTransitions)
    grok.require('horae.Manage')
    grok.name('add-transition')

    overview = 'index'

    form_fields = grok.AutoFields(interfaces.ITransition).omit('id')

    def object_type(self):
        return _(u'Transition')

    def cancel_url(self):
        return self.url(self.context.__parent__)

    def next_url(self, obj=None):
        return self.cancel_url()

    def create(self, **data):
        transition = workflow.Transition()
        transition.name = data['name']
        return transition

    def add(self, obj):
        self.context.add_object(obj)


class EditTransition(objects.EditObject):
    """ Edit form of a transition
    """
    grok.context(interfaces.IWorkflowTransitions)
    grok.require('horae.Manage')
    grok.name('edit-transition')

    overview = 'index'

    def object_type(self):
        return _(u'Transition')


class DeleteTransition(objects.DeleteObject):
    """ Delete form of a transition
    """
    grok.context(interfaces.IWorkflowTransitions)
    grok.require('horae.Manage')
    grok.name('delete-transition')

    overview = 'index'

    def object_type(self):
        return _(u'Transition')


class ActivateTransition(grok.View):
    """ View activating a transition
    """
    grok.context(interfaces.IWorkflow)
    grok.require('horae.Manage')
    grok.name('activate-transition')

    def __call__(self, id):
        if isinstance(id, unicode):
            self.context.activate_transition(id)
        self.redirect(self.url(self.context))

    def render(self):
        return ''


class DeactivateTransition(grok.View):
    """ View deactivating a transition
    """
    grok.context(interfaces.IWorkflow)
    grok.require('horae.Manage')
    grok.name('deactivate-transition')

    def __call__(self, id):
        if isinstance(id, unicode):
            self.context.deactivate_transition(id)
        self.redirect(self.url(self.context))

    def render(self):
        return ''
