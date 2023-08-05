from zope import interface
import zope.annotation.interfaces
import p4a.videoembed.interfaces

class Link(object):
    interface.implements(
        zope.annotation.interfaces.IAttributeAnnotatable,
        p4a.videoembed.interfaces.ILinkProvider)

    def getLink(self):
        return self.url

class File(object):
    interface.implements(
        zope.annotation.interfaces.IAttributeAnnotatable)
