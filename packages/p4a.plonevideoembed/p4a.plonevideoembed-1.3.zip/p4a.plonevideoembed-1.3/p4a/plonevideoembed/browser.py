import Acquisition
from zope import component
from zope.formlib import form
from zope import interface
from zope import schema
from p4a.plonevideoembed import interfaces
from p4a.plonevideoembed import media
from p4a.video import interfaces as videoifaces
from p4a.videoembed import interfaces as embedifaces
from p4a.common import at
from p4a.common import feature
import p4a.video.browser.video
from p4a.video.browser.video import has_contenttagging_support
from p4a.video.browser.video import has_contentrating_support

class IContextualVideoLinkSupport(interface.Interface):
    can_activate_video_link = schema.Bool(title=u'Can Activate Video Link',
                                          readonly=True)
    can_deactivate_video_link = schema.Bool(title=u'Can Deactivate Video Link',
                                            readonly=True)

class Support(object):
    """A view that returns certain information regarding p4avideoembed status.
    """

    interface.implements(IContextualVideoLinkSupport)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    @property
    def support_enabled(self):
        """Check to make sure an IVideoLinkSupport utility is available and
        if so, query it to determine if support is enabled.
        """
        
        support = component.queryUtility(interfaces.IVideoLinkSupport)
        if support is None:
            return False

        return support.support_enabled

    @property
    def _basic_can(self):
        if not self.support_enabled:
            return False

        if not interfaces.IAnyVideoLinkCapable.providedBy(self.context):
            return False

        return True

    @property
    def can_activate_video_link(self):
        if not self._basic_can:
            return False
        
        mediaconfig = component.getMultiAdapter((self.context, self.request),
                                                name='video-link-config.html')
        return not mediaconfig.media_activated

    @property
    def can_deactivate_video_link(self):
        if not self._basic_can:
            return False

        mediaconfig = component.getMultiAdapter((self.context, self.request),
                                                name='video-link-config.html')
        return mediaconfig.media_activated

_marker = object()

class ToggleEnhancementsView(object):
    """
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        was_activated = self.media_activated
        self.media_activated = not was_activated
        response = self.request.response

        if was_activated:
            activated = 'Media+deactivated'
        else:
            activated = 'Media+activated'

        baseurl = self.context.absolute_url()
        response.redirect(baseurl+'/view?portal_status_message='+activated)

    def _set_media_activated(self, v):
        videoifaces.IMediaActivator(self.context).media_activated = v
    def _get_media_activated(self):
        return videoifaces.IMediaActivator(self.context).media_activated
    media_activated = property(_get_media_activated, _set_media_activated)

class VideoLinkView(object):
    """The view for a video link object.
    """

    def has_contentrating_support(self):
        return has_contentrating_support(Acquisition.aq_inner(self.context))

    def has_contenttagging_support(self):
        return has_contenttagging_support(Acquisition.aq_inner(self.context))

    def video_author(self):
        video = videoifaces.IVideo(Acquisition.aq_inner(self.context))
        return getattr(video, 'video_author', '')

    def video_width(self):
        video = videoifaces.IVideo(Acquisition.aq_inner(self.context))
        return getattr(video, 'width', 0)

    def video_height(self):
        video = videoifaces.IVideo(Acquisition.aq_inner(self.context))
        return getattr(video, 'height', 0)

    def url(self):
        holder = component.getAdapter(self.context, interfaces.ILinkHolder)
        return holder.url

class VideoLinkEditForm(p4a.video.browser.video.VideoEditForm):
    """Edit video link"""

    form_fields = form.Fields(
        videoifaces.IVideo['title'],
        interfaces.ILinkHolder['url'],
        videoifaces.IVideo['description'],
        videoifaces.IVideo['rich_description'],
        videoifaces.IVideo['video_image'],
        videoifaces.IVideo['video_author'],
        videoifaces.IVideo['width'],
        )
    form_fields['rich_description'].custom_widget = at.RichTextEditWidget

    priority_fields = ['title', 'url']
