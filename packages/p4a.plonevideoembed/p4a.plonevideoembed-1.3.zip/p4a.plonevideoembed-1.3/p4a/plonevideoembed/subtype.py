from zope import interface
from p4a.plonevideoembed import interfaces
from p4a.subtyper.interfaces import (IPortalTypedDescriptor,
                                     IPortalTypedFolderishDescriptor)

class VideoLinkDescriptor(object):
    interface.implements(IPortalTypedDescriptor)

    title = u'Video Link'
    description = u'Video-based media content'
    type_interface = interfaces.IVideoLinkEnhanced
    for_portal_type = 'Link'
