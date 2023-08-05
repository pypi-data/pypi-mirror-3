from zope import component
from zope import interface
from p4a.videoembed import interfaces as baseifaces
from p4a.video import interfaces as vidifaces
import Acquisition

def attempt_videolink_activation(obj):
    """Determine if the link in question contains information that videoembed
    knows about, and if so, activate the link as media_activated=True.
    """

    activation = vidifaces.IMediaActivator(obj)

    if activation.media_activated:
        return False

    find_type = component.getUtility(baseifaces.IURLType)
    provider = baseifaces.ILinkProvider(Acquisition.aq_base(obj))
    url = provider.getLink()

    found = find_type(url)
    if found:
        activation.media_activated = True

    return activation.media_activated

def autoactivation_handler(obj, event):
    attempt_videolink_activation(obj)
