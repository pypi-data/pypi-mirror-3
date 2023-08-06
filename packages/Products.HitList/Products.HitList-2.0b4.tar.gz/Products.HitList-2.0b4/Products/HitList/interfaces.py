from zope.interface.interface import Interface

class IHitList(Interface):
    """ A users hitlist
    """
    pass

class IHitListContent(Interface):
    """marker interface for content-types addable to the hitlist
    """
    pass