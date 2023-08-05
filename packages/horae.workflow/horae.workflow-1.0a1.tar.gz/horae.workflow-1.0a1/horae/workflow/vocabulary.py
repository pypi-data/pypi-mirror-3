from zope.schema import vocabulary

from horae.core import utils

from horae.workflow import interfaces


def states_vocabulary_factory(context):
    """ A vocabulary of all available states registered as
        **horae.workflow.vocabulary.states**
    """
    parent = utils.findParentByInterface(context, interfaces.IWorkflow)
    terms = []
    if parent is not None:
        for state in parent.states():
            terms.append(vocabulary.SimpleTerm(state.id, state.id, state.name or state.id))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.workflow.vocabulary.states', states_vocabulary_factory)


def transitions_vocabulary_factory(context):
    """ A vocabulary of all available transitions registered as
        **horae.workflow.vocabulary.transitions**
    """
    parent = utils.findParentByInterface(context, interfaces.IWorkflow)
    terms = []
    if parent is not None:
        for transition in parent.transitions():
            terms.append(vocabulary.SimpleTerm(transition.id, transition.id, transition.name or transition.id))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.workflow.vocabulary.transitions', transitions_vocabulary_factory)
