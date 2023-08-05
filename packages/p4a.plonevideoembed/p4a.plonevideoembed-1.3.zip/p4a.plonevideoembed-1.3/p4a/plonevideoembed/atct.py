from zope import interface
from zope import component
from Products.ATContentTypes.content import link
from p4a.videoembed import interfaces as embedifaces
from p4a.plonevideoembed import interfaces

class ATLinkLinkHolder(object):
    interface.implements(interfaces.ILinkHolder)
    component.adapts(link.ATLink)

    def __init__(self, context):
        self.context = context

    def _set_url(self, url):
        self.context.setRemoteUrl(url)
    def _get_url(self):
        # we're bypassing the accessor as it's currently
        # converting & in the url to %26 which is bad
        url = self.context.remoteUrl

        if isinstance(url, unicode):
            # registered embed adapters fail when looking up on unicode
            # because they've been registered against str
            url = url.encode('utf-8')

        return url
    url = property(_get_url, _set_url)

class ATLinkLinkProvider(object):
    interface.implements(embedifaces.ILinkProvider)
    component.adapts(link.ATLink)

    def __init__(self, context):
        self.context = context

    def getLink(self):
        holder = component.getAdapter(self.context, interfaces.ILinkHolder)
        return holder.url
