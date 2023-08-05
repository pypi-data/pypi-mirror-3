from zope.schema import vocabulary

from horae.core import _

from horae.timeaware import interfaces


def repeat_vocabulary_factory(context):
    """ A vocabulary of all available repeating possibilities registered as
        **horae.timeaware.vocabulary.repeat**
    """
    return vocabulary.SimpleVocabulary((
        vocabulary.SimpleTerm(interfaces.REPEAT_YEARLY, interfaces.REPEAT_YEARLY, _(u'Yearly')),
        vocabulary.SimpleTerm(interfaces.REPEAT_MONTHLY, interfaces.REPEAT_MONTHLY, _(u'Monthly')),
        vocabulary.SimpleTerm(interfaces.REPEAT_4WEEKS, interfaces.REPEAT_4WEEKS, _(u'Every four weeks')),
        vocabulary.SimpleTerm(interfaces.REPEAT_WEEKLY, interfaces.REPEAT_WEEKLY, _(u'Weekly')),
        vocabulary.SimpleTerm(interfaces.REPEAT_WORKDAYS, interfaces.REPEAT_WORKDAYS, _(u'On work days')),
        vocabulary.SimpleTerm(interfaces.REPEAT_DAILY, interfaces.REPEAT_DAILY, _(u'Daily'))
    ))
vocabulary.getVocabularyRegistry().register('horae.timeaware.vocabulary.repeat', repeat_vocabulary_factory)
