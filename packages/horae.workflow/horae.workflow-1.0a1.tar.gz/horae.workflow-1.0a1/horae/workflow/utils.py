from plone.memoize import ram

from horae.ticketing.utils import getObjectType
from horae.auth.utils import getUser
from horae.core.utils import getRequest

from hurry.workflow.interfaces import IWorkflowInfo


def transitionAvailable(transition):
    """ Returns whether a :py:class:`horae.workflow.workflow.Transition`
        is available for the current user or not
    """
    user = None
    try:
        request = getRequest()
        user = getUser(request.principal.id)
    except:
        pass
    if (not transition.groups and not transition.users) or \
       (transition.users and user in transition.users):
        return True
    if user is None:
        return None
    for group in transition.groups:
        if transition.groups and group in transition.groups:
            return True
    return False


def state_info_key(method, *args, **kwargs):
    return (method.__module__, method.__name__, str(getObjectType(args[0])), args[0].id, args[2], len(args) > 3 and args[3] or None)


@ram.cache(state_info_key)
def _stateInfo(context, value, info=None, attr=None):
    if info is None:
        info = IWorkflowInfo(context)
    if not value:
        return ''
    transition = None
    if '.' in value:
        name = '.'.join(value.split('.')[:-1])
        transition = info.workflow.get_transition(name)
        if transition is None:
            return name
        state = info.workflow.get_state(transition.destination)
    else:
        state = info.workflow.get_state(value)
    if state is None and transition is not None:
        return transition.destination
    if attr is None:
        return state
    return getattr(state, attr, '')


def stateId(context, value, info=None):
    """ Returns the ID of the :py:class:`horae.workflow.workflow.State`
        currently set on the given context
    """
    return _stateInfo(context, value, info, 'id')


def stateName(context, value, info=None):
    """ Returns the name of the :py:class:`horae.workflow.workflow.State`
        currently set on the given context
    """
    return _stateInfo(context, value, info, 'name')


def stateObj(context, value, info=None):
    """ Returns the :py:class:`horae.workflow.workflow.State`
        currently set on the given context
    """
    return _stateInfo(context, value, info)
