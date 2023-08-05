""" Field
"""
import logging
import json
from Acquisition import aq_get
from zope.i18nmessageid import Message
from zope.i18n import translate
from zope.component import queryAdapter
from Products.Archetypes import atapi
from Products.Archetypes import PloneMessageFactory as _
from eea.geotags.interfaces import IGeoTags

logger = logging.getLogger('eea.geotags.field')

class GeotagsFieldMixin(object):
    """ Add methods to get/set json tags
    """
    @property
    def multiline(self):
        """ Multiline
        """
        return isinstance(self, atapi.LinesField)

    def getJSON(self, instance, **kwargs):
        """ Get GeoJSON tags from instance annotations using IGeoTags adapter
        """
        geo = queryAdapter(instance, IGeoTags)
        if not geo:
            return ''
        return json.dumps(geo.tags)

    def setJSON(self, instance, value, **kwargs):
        """ Set GeoJSON tags to instance annotations using IGeoTags adapter
        """
        geo = queryAdapter(instance, IGeoTags)
        if not geo:
            return

        if not isinstance(value, dict) and value:
            try:
                value = json.loads(value)
            except Exception, err:
                logger.exception(err)
                return

        geo.tags = value

    def json2list(self, geojson, attr='description'):
        """ Util method to extract human readable geo tags from geojson struct
        """
        if not geojson:
            return

        try:
            value = json.loads(geojson)
        except Exception, err:
            logger.exception(err)
            return

        features = value.get('features', [])
        if not features:
            return

        for feature in features:
            properties = feature.get('properties', {})
            yield properties.get(attr, properties.get('title', ''))

    def json2string(self, geojson, attr='description'):
        """ Util method to extract human readable geo tag from geojson struct
        """
        items = self.json2list(geojson, attr)
        for item in items:
            return item
        return ''

    def validate_required(self, instance, value, errors):
        """ Validate
        """
        value = [item for item in self.json2list(value)]
        if not value:
            request = aq_get(instance, 'REQUEST')
            label = self.widget.Label(instance)
            name = self.getName()
            if isinstance(label, Message):
                label = translate(label, context=request)
            error = _(u'error_required',
                      default=u'${name} is required, please correct.',
                      mapping={'name': label})
            error = translate(error, context=request)
            errors[name] = error
            return error
        return None

class GeotagsStringField(GeotagsFieldMixin, atapi.StringField):
    """ Single geotag field
    """
    def set(self, instance, value, **kwargs):
        """ Set
        """
        self.setJSON(instance, value, **kwargs)
        tag = self.json2string(value)
        return atapi.StringField.set(self, instance, tag, **kwargs)

class GeotagsLinesField(GeotagsFieldMixin, atapi.LinesField):
    """ Multiple geotags field
    """
    def set(self, instance, value, **kwargs):
        """ Set
        """
        self.setJSON(instance, value, **kwargs)
        tags = [tag for tag in self.json2list(value)]
        return atapi.LinesField.set(self, instance, tags, **kwargs)
