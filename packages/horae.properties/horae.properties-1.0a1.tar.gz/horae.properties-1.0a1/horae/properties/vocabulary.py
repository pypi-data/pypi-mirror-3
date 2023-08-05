from zope.schema import vocabulary

from horae.properties import _
from horae.properties import interfaces


def fields_vocabulary_factory(context):
    """ A vocabulary of all available fields registered as
        **horae.properties.vocabulary.fields**
    """
    terms = [vocabulary.SimpleTerm('ALL', 'ALL', _(u'All fields'))]
    for property in interfaces.IPropertied(context).properties():
        for field in property.fields(context):
            if not interfaces.IFieldsProperty.providedBy(field.property):
                terms.append(vocabulary.SimpleTerm(field.__name__, field.__name__, field.title))
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.properties.vocabulary.fields', fields_vocabulary_factory)
