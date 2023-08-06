""" Basic geotags storage
"""
import logging
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from zope.interface import implements
from zope.component import queryAdapter
from eea.geotags.config import ANNO_TAGS
from eea.geotags.storage.interfaces import IGeoTags

logger = logging.getLogger('eea.geotags.storage')

class GeoTags(object):
    """ Geo tags storage
    """
    implements(IGeoTags)

    def __init__(self, context):
        self.context = context

    @property
    def tags(self):
        """ Get tags
        """
        anno = queryAdapter(self.context, IAnnotations)
        if anno is None:
            logger.exception('%s is not Annotable',
                             self.context.absolute_url())
            return {}
        return dict(anno.get(ANNO_TAGS, {}))

    @tags.setter
    def tags(self, value):
        """ Set tags
        """
        anno = queryAdapter(self.context, IAnnotations)
        if anno is None:
            logger.exception('%s is not Annotable',
                             self.context.absolute_url())
            return
        anno[ANNO_TAGS] = PersistentDict(value)
