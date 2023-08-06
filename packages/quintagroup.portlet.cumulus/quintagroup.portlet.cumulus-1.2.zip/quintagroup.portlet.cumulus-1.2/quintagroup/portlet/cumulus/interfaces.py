from zope.interface import Interface

class ITagsRetriever(Interface):

    def getTags(number=None):
        """ Get list of (tag, number_or_entries, url) tuples.

            number - the number of actual tags to return (all tags if omitted)
        """
