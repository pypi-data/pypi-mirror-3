import grok

from zope.schema import vocabulary

from horae.core import utils
from horae.cache.vocabulary import cache_contextual_parent, invalidate_contextual_parent

from horae.ticketing import interfaces


@cache_contextual_parent(interfaces.IMilestoneContainerHolder)
def milestones_vocabulary_factory(context):
    """ A vocabulary of all available milestones registered as
        **horae.properties.vocabulary.milestones**
    """
    parent = utils.findParentByInterface(context, interfaces.IMilestoneContainerHolder)
    terms = []
    if parent is not None:
        for milestone in interfaces.IMilestoneContainer(parent).objects():
            terms.append(vocabulary.SimpleTerm(milestone, milestone.id, milestone.name or milestone.id))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.properties.vocabulary.milestones', milestones_vocabulary_factory)


@grok.subscribe(interfaces.IMilestone, grok.IObjectModifiedEvent)
@grok.subscribe(interfaces.IMilestone, grok.IObjectMovedEvent)
def invalidate_milestone_vocabulary_cache(obj, event):
    invalidate_contextual_parent(obj, interfaces.IMilestoneContainerHolder, milestones_vocabulary_factory)
