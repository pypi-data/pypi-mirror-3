from zope.publisher.interfaces import IPublishTraverse
from zope.interface import implements
from zope.component import adapts

from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces import IRequest
from zope.publisher.http import IHTTPRequest

from ZPublisher.BaseRequest import DefaultPublishTraverse
from zope.globalrequest import getRequest

import Acquisition
import traject

class Model(Acquisition.Implicit):
    def getPhysicalPath(self):
        obj = self.aq_base
        app = self.aq_parent.aq_base
        traject.locate(self.aq_parent, obj, None)
        stack = []
        current = obj
        while current is not app:
            stack.append(current.__name__)
            current = current.__parent__.aq_base
        stack.reverse()
        return tuple(list(self.aq_parent.getPhysicalPath()) + stack)

    def absolute_url(self, relative=0):
        if relative:
            return self.virtual_url_path()

        return getRequest().physicalPathToURL(self.getPhysicalPath())

    def virtual_url_path(self):
        return getRequest().physicalPathToVirtualPath(self.getPhysicalPath())


class DefaultModel(Model):
    def __init__(self, **kw):
        self.kw = kw

class Traverser(DefaultPublishTraverse):

    def fallback(self, request, name):
        return super(Traverser, self).publishTraverse(request, name)

    def publishTraverse(self, request, name):
        stack = self.request.path
        stack.append(name)
        self.request['TRAJECTORY_APP'] = self.context
        unconsumed, consumed, obj = traject.consume_stack(
            self.context, stack, DefaultModel)
        if obj is self.context:
            return self.fallback(request, name)
        self.request.path=unconsumed
        self.request._steps.extend(consumed)
        return obj.__of__(self.context)

