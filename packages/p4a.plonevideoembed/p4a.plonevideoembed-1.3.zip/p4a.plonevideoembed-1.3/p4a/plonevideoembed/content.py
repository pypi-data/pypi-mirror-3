from zope import interface
from p4a.plonevideoembed import interfaces
from OFS.SimpleItem import SimpleItem

class VideoLinkSupport(SimpleItem):
    """Simple persistent utility that indicates video link functionality
    is available.

      >>> VideoLinkSupport('foo').support_enabled
      True

    """

    interface.implements(interfaces.IVideoLinkSupport)

    @property
    def support_enabled(self):
        return True
