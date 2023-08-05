import zope.component
import zope.interface
from p4a.plonevideoembed.interfaces import IVideoLinkEnhanced
from Products.fatsyndication.adapters import BaseFeedEntry
from Products.basesyndication.interfaces import IFeedEntry
from Products.basesyndication.interfaces import IEnclosure

class VideoLinkFeedEntry(BaseFeedEntry):
    zope.interface.implements(IFeedEntry)
    zope.component.adapts(IVideoLinkEnhanced)
    
    def __init__(self, *args, **kwargs):
        BaseFeedEntry.__init__(self, *args, **kwargs)
    
    def getBody(self):
        """See IFeedEntry.
        """
        return ''
    
    def getEnclosure(self):
        return IEnclosure(self.context)
    
    def getTitle(self):
        # XXX get title from metadata directly ?
        return self.context.Title()

class ATLinkEnclosure(object):
    zope.interface.implements(IEnclosure)
    zope.component.adapts(IVideoLinkEnhanced)
    
    def __init__(self, context):
        self.context = context
    
    def getURL(self):
        # XXX use remote url
        return self.context.absolute_url()

    def getLength(self):
       # XXX
       return 0

    def __len__(self):
        return self.getLength()

    def getMajorType(self):
        # XXX
        return ''

    def getMinorType(self):
        # XXX
        return ''

    def getType(self):
        # XXX
        return ''
