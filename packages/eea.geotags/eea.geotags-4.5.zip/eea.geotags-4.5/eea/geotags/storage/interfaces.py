""" Interfaces
"""
from zope import schema
from zope.interface import Interface

class IGeoTaggable(Interface):
    """ Marker interface for content objects that can be geo tagged
    """

class IGeoTags(Interface):
    """ Accessor/Mutator for geo tags annotations
    """
    tags = schema.Dict(title=u"Geojson tags")
