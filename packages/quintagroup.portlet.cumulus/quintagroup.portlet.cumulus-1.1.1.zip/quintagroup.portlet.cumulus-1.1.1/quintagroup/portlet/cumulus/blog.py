from zope.interface import implements
from Products.CMFCore.utils import getToolByName

from quills.core.interfaces import IWeblogLocator

from quintagroup.portlet.cumulus.interfaces import ITagsRetriever
from quintagroup.portlet.cumulus.catalog import GlobalTags

class QuillsBlogTags(GlobalTags):
    implements(ITagsRetriever)

    def getTags(self, number=None):
        """ Get Quills blog's tags.
        """
        weblog = self.getWeblog()
        if weblog == []:
            return super(QuillsBlogTags, self).getTags(number)

        topics = weblog.getTopics()
        tags = []
        for topic in topics:
            title = topic.getTitle()
            # Before this issue http://plone.org/products/quills/issues/209 in
            # Quills was fixed, topic title was not a unicode string
            if not isinstance(title, unicode):
                title = title.decode(self.default_charset)
            tags.append((title, len(topic), topic.absolute_url()))

        return tags

    def getWeblog(self):
        locator = IWeblogLocator(self.context)
        weblog = locator.find()
        return weblog
