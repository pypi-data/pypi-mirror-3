from zope.interface import implements
from Products.CMFCore.utils import getToolByName

from quintagroup.portlet.cumulus.interfaces import ITagsRetriever

class GlobalTags(object):
    implements(ITagsRetriever)

    def __init__(self, context):
        self.context = context
        portal_properties = getToolByName(self.context, 'portal_properties')
        self.default_charset = portal_properties.site_properties.getProperty('default_charset', 'utf-8')
        portal = getToolByName(context, 'portal_url').getPortalObject()
        self.portal_url = portal.absolute_url()

    def getTags(self, number=None):
        """ Entries of 'Categories' archetype field on content are assumed to be tags.
        """
        cat = getToolByName(self.context, 'portal_catalog')
        index = cat._catalog.getIndex('Subject')
        tags = []
        for name in index._index.keys():
            try:
                number_of_entries = len(index._index[name])
            except TypeError:
                number_of_entries = 1
            name = name.decode(self.default_charset)
            url = '%s/search?Subject:list=%s' % (self.portal_url, name)
            tags.append((name, number_of_entries, url))

        return tags
