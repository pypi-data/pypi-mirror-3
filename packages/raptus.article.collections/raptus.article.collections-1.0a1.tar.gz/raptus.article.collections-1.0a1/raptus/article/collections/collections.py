from zope import interface, component

from Products.CMFCore.utils import getToolByName

from raptus.article.core.interfaces import IArticle
from raptus.article.collections.interfaces import ICollections

class Collections(object): 
    """ Provider for collections contained in an article
    """
    interface.implements(ICollections)
    component.adapts(IArticle)

    def __init__(self, context):
        self.context = context

    def getCollections(self, **kwargs):
        """ Returns a list of collections (catalog brains)
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(portal_type='Topic', path={'query': '/'.join(self.context.getPhysicalPath()),
                                                  'depth': 1}, sort_on='getObjPositionInParent', **kwargs)
