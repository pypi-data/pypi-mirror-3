"""  Map view
"""
from Products.Five.browser import BrowserView
import json
import urllib
from Products.CMFCore.utils import getToolByName


class MapView(BrowserView):
    """ Map View faceted navigation logic
    """

    def map_points(self, brains):
        """ Return geotags information found on brains
        """
        res = []
        props = getToolByName(self.context, 'portal_properties').site_properties
        for brain in brains:
            if brain.geotags:
                # we only need the features items
                features = json.loads(brain.geotags).get('features')
                for feature in features:
                    location = feature['properties']['description']
                    feature['properties']['description'] = urllib.quote(
                                        location.encode('utf-8'))
                    feature.update({"itemDescription":
                                        urllib.quote(brain.Description)})
                    feature.update({"itemUrl": brain.getURL()})
                    feature.update({"itemTitle":
                                        urllib.quote(brain.Title)})
                    feature.update({"itemType": brain.Type})
                    feature.update({"itemIcon": brain.getIcon})
                    start_date = brain.start.strftime(props.localLongTimeFormat)
                    end_date = brain.end.strftime(props.localLongTimeFormat)
                    feature.update({"itemDate": '%s to %s' % (
                                                        start_date, end_date)})
                    feature = json.dumps(feature)
                    res.append(feature)
        return res
