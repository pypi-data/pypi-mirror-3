from zope import interface

class ICollections(interface.Interface):
    """ Provider for collections contained in an article
    """

    def getCollections(**kwargs):
        """ Returns a list of collections (catalog brains)
        """
