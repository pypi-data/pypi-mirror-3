from plone.indexer.decorator import indexer
from Products.ATContentTypes.interface import IATContentType


@indexer(IATContentType)
def responsibleperson_indexer(obj):
    """A method for indexing 'responsible person' field of content
    """
    field = obj.Schema().getField('responsibleperson')
    if field is not None:
    	# Setting _initializing_ to True means: do not under any circumstances
    	# allow the default value to be set when getting the value of this
    	# field. Otherwise, a field.set will take place, which will call
    	# changeOwnership, which will cause the object to be reindexed. Since
    	# we are *already* indexing right now, that'll lead to broken catalog
    	# internals.
        return field.get(obj, _initializing_=True)
    else:
        raise AttributeError
