from zope import component
from zope import interface
from p4a import subtyper
from p4a.video import interfaces
from Products.ATContentTypes import interface as atctifaces

class MediaActivator(object):
    """An adapter for seeing the activation status or toggling activation.
    """

    interface.implements(interfaces.IMediaActivator)
    component.adapts(atctifaces.IATLink)

    def __init__(self, context):
        self.context = context

    media_activated = subtyper.activated('p4a.video.VideoLink', 'context')
