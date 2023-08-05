from Products.Archetypes.interfaces import IVocabulary

class ISearchableVocabulary(IVocabulary):
    
    def search(self, query, instance):
        """
        """