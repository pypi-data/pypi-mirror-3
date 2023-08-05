from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from collective.doormat import doormatMessageFactory as _

def section_vocabulary_factory(context):
    return SimpleVocabulary((
                    SimpleTerm(value='section1', token='Section 1', title=_(u'Section 1')),
                    SimpleTerm(value='section2', token='Section 2', title=_(u'Section 2')),
                    SimpleTerm(value='section3', token='Section 3', title=_(u'Section 3')),
                    SimpleTerm(value='section4', token='Section 4', title=_(u'Section 4')),
                    SimpleTerm(value='section5', token='Section 5', title=_(u'Section 5')),
                    SimpleTerm(value='section6', token='Section 6', title=_(u'Section 6')),
                    SimpleTerm(value='section7', token='Section 7', title=_(u'Section 7')),
                    ))
