from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.component import getUtilitiesFor
from plone.app.vocabularies.catalog import SearchableTextSourceBinder, SearchableTextSource
from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder

def AvailableTemplatedViews(context):
    if hasattr(context, 'context'):
        context = context.context
    terms = []
    from wildcard.templatedviews.interfaces import ITemplated
    for name, utility in sorted(list(getUtilitiesFor(ITemplated)), key=lambda x: x[1].title):
        if not utility._for or utility._for.providedBy(context):
            title = utility.title or name
            terms.append(SimpleTerm(name, name, title))
            
    return SimpleVocabulary(terms)
            
class SettingsContextSourceBinder(SearchableTextSourceBinder):
    implements(IContextSourceBinder)
    def __call__(self, settings):
        if hasattr(settings, 'context'):
            context = settings.context
        else:
            context = settings
        return SearchableTextSource(context, base_query=self.query.copy(), default_query=self.default_query)
