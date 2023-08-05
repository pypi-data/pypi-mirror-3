from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.vocabularies.catalog import SearchableTextSource

class MineSearchableTextSourceBinder(SearchableTextSourceBinder):
    
    def __call__(self, context):
        # context is adapter from PloneSite -> ISiteRSSSchema. 
        # SearchableTextSourceBinder failed with acquiring portal_catalog so 
        # I rewrote this method and get real context
        return SearchableTextSource(context.context, base_query=self.query.copy(),
                                    default_query=self.default_query)
    
