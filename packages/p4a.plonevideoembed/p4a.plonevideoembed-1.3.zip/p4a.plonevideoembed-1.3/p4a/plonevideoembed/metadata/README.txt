;-*-Doctest-*-

============================
p4a.plonevideoembed.metadata
============================

Adding video metadata via subscribers

URL extraction subscribers
--------------------------

Provide a handler for IObjectModifiedEvent that that marks the adapter
to p4a.video.interfaces.IVideo with a provider specific interface,
IBlipTvVideo for example, using p4a.videoembed.interfaces.IURLChecker.

The IVideo.urls attribute is populated by subscribers to
IVideoURLExtractor.  An IVideoURLExtractor is a callable that returns
a tuple of mimetype and URL pairs for retrieving the video from the
provider in that format.

Start with a link with a blip.tv url that is not yet activated as a
p4a.video.Video:

    >>> from p4a.plonevideoembed.metadata import testing
    >>> link = testing.Link()
    >>> link.url = 'http://blip.tv/file/111111'

    >>> import p4a.plonevideoembed.interfaces
    >>> p4a.plonevideoembed.interfaces.IVideoLinkEnhanced.providedBy(
    ...     link)
    False

Register a subscriber:

    >>> from zope import component
    >>> from p4a.plonevideoembed.metadata import interfaces, providers
    >>> component.getSiteManager().registerSubscriptionAdapter(
    ...     factory=lambda context, adapter: (('foo', 'bar'),),
    ...     required=[p4a.plonevideoembed.interfaces.IVideoLinkEnhanced,
    ...               providers.IBlipTvVideo],
    ...     provided=interfaces.IVideoURLExtractor)

Since the link is not activated as a video, the subscriber will not be
notified:

    >>> import zope.event
    >>> from zope.app.event import objectevent
    >>> zope.event.notify(objectevent.ObjectModifiedEvent(link))

    >>> import p4a.video.interfaces
    >>> video = p4a.video.interfaces.IVideo(link)
    >>> video.urls
    ()

Activate the link as a p4a.video.Video:

    >>> p4a.video.interfaces.IMediaActivator(
    ...     link).media_activated = True
    >>> p4a.plonevideoembed.interfaces.IVideoLinkEnhanced.providedBy(
    ...     link)
    True

Now notify IObjectModifiedEvent again to populate the urls attribute:

    >>> zope.event.notify(objectevent.ObjectModifiedEvent(link))

    >>> video.urls
    (('foo', 'bar'),)

Unrecognized providers
----------------------

Verify that everything works properly for URLs that aren't from
recognized providers.

    >>> bar_link = testing.Link()
    >>> bar_link.url = 'http://foo.com/bar.flv'
    >>> p4a.video.interfaces.IMediaActivator(
    ...     bar_link).media_activated = True

    >>> zope.event.notify(objectevent.ObjectModifiedEvent(bar_link))

    >>> video = p4a.video.interfaces.IVideo(bar_link)
    >>> video.urls
    ()

Other content
-------------

Content that does not store a link should be exempted from url
harvesting.

    >>> foo_file = testing.File()
    >>> p4a.video.interfaces.IMediaActivator(
    ...     foo_file).media_activated = True
    >>> zope.event.notify(objectevent.ObjectModifiedEvent(foo_file))
    >>> video = p4a.video.interfaces.IVideo(foo_file)
    >>> video.urls
    ()
