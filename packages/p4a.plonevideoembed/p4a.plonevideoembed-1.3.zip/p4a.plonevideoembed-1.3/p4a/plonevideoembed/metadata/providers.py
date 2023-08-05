import sys, os, subprocess, itertools
from xml.dom import minidom

from zope import interface, component
try:
    from zope.app.event.interfaces import IObjectModifiedEvent
except:
    from zope.lifecycleevent.interfaces import IObjectModifiedEvent

import p4a.video.interfaces
import p4a.videoembed.interfaces
import p4a.plonevideoembed.interfaces
from p4a.videoembed.providers import bliptv
from p4a.videoembed import utils

import interfaces

class IProviderVideo(interface.Interface):
    """A video link from blip.tv"""

class IBlipTvVideo(IProviderVideo):
    """A video link from blip.tv"""

class IYoutubeVideo(IProviderVideo):
    """A video link from youtube"""

provider_map = {
    'bliptv': IBlipTvVideo,
    'youtube': IYoutubeVideo,
    }

def markProviderVideo(video):
    url = p4a.videoembed.interfaces.ILinkProvider(video.context).getLink()
    url_type = component.getUtility(
        p4a.videoembed.interfaces.IURLType)(url)
    assert not IProviderVideo.providedBy(video), (
        'IVideo adapter already provides IProviderVideo')
    if url_type in provider_map:
        interface.alsoProvides(video, provider_map[url_type])

@component.adapter(p4a.plonevideoembed.interfaces.IVideoLinkEnhanced,
                   IObjectModifiedEvent)
def extractVideoURLs(obj, event):
    if p4a.videoembed.interfaces.ILinkProvider(obj, None) is None:
        return
    video = p4a.video.interfaces.IVideo(obj)
    markProviderVideo(video)
    video.urls = tuple(itertools.chain(*component.subscribers(
        [obj, video], interfaces.IVideoURLExtractor)))

@interface.implementer(interfaces.IVideoURLExtractor)
@component.adapter(p4a.plonevideoembed.interfaces.IVideoLinkEnhanced,
                   IYoutubeVideo)
def extractYoutubeFLV(context, adapter):
    url = p4a.videoembed.interfaces.ILinkProvider(context).getLink()
    stdout, stderr = subprocess.Popen(
        [sys.executable,
         os.path.join(
             os.path.dirname(__file__), 'youtube-dl'),
         '-g', url],
        stdout=subprocess.PIPE).communicate()
    return (('video/x-flv', stdout[:-1]),)
    
@interface.implementer(interfaces.IVideoURLExtractor)
@component.adapter(p4a.plonevideoembed.interfaces.IVideoLinkEnhanced,
                   IBlipTvVideo)
def extractBlipTvURLs(context, adapter):
    url = p4a.videoembed.interfaces.ILinkProvider(context).getLink()
    data = p4a.videoembed.interfaces.VideoMetadata()
    rss = bliptv.remote_content(bliptv._rss_url(url))
    doc = minidom.parseString(rss)
    return tuple(
        (node.getAttribute('type'), node.getAttribute('url'))
        for node in utils.xpath_node(
            doc, 'rss/channel/item/media:group').childNodes
        if node is not None and isinstance(node, minidom.Element))
