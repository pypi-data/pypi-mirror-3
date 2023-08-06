from zope.schema import vocabulary

if not hasattr(vocabulary.SimpleVocabulary, 'fromDictionary'):
    
    def fromDictionary(cls, dict, *interfaces):
        """Construct a vocabulary from a list of (token, value) pairs.
    
        The order of the items is preserved as the order of the terms
        in the vocabulary.  Terms are created by calling the class
        method createTerm() with the pair (value, token).
        
        One or more interfaces may also be provided so that alternate
        widgets may be bound without subclassing.
        """
        terms = [cls.createTerm(token, token, value) for (token, value) in dict.items()]
        return cls(terms, *interfaces)
    fromDictionary = classmethod(fromDictionary)
    
    vocabulary.SimpleVocabulary.fromDictionary = fromDictionary
    
