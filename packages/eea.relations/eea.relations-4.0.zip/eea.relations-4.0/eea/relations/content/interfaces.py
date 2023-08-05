""" Content interfaces
"""
from zope.interface import Interface

class IContentType(Interface):
    """ Content type
    """

class IRelation(Interface):
    """ Relation between 2 content types
    """

class IRelationsTool(Interface):
    """ portal_relations tool
    """

class IToolAccessor(Interface):
    """ portal_relations tool accessor
    """
    def relations(proxy):
        """
        Returns defined possible relation.

        If proxy=True returns catalog brains
        """

    def types(proxy):
        """ Returns defined content types. If proxy=True returns catalog brains
        """
