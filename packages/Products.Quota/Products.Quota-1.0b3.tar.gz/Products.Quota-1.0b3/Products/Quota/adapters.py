import logging
from Acquisition import aq_inner, aq_parent, aq_base
from persistent.dict import PersistentDict
from zExceptions import Redirect
from zope.component import adapts, getUtility
from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces import IBaseFolder, IBaseObject
from plone.app.blob.interfaces import IATBlob
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.Quota import QuotaMessageFactory as _
from Products.Quota.interfaces import (IQuotaRecurse, IQuotaEnforcer,
                            IQuotaAware, IQuotaSizer, IQuotaSettings)


class BaseQuotaSizer(object):
    implements(IQuotaSizer)
    adapts(object)

    def __init__(self, context):
        self.context = context

    def _increment(self, new_size):
        try:
            ann = IAnnotations(self.context)
        except TypeError:
            return 0
        if not ann.has_key('quota'):
            ann['quota'] = PersistentDict()
        try:
            old_size = ann['quota']['size']
        except KeyError:
            old_size = 0
        ann['quota']['size'] = new_size
        return new_size - old_size

    def get_increment(self):
        size = 0
        for method_name in ('get_size', 'getSize', 'size'):
            method = getattr(aq_base(self.context), method_name, None)
            if method is not None:
                if callable(method):
                    size = method()
                else:
                    try:
                        size = int(method)
                    except ValueError:
                        pass
                break
        return self._increment(size)

    def get_size(self):
        try:
            ann = IAnnotations(self.context)
        except TypeError:
            return 0
        if ann.has_key('quota') and ann['quota'].has_key('size'):
            return ann['quota']['size']
        return self.get_increment()

class ATQuotaSizer(BaseQuotaSizer):
    implements(IQuotaSizer)
    adapts(IBaseObject)

    def __init__(self, context):
        self.context = context

    def get_increment(self):
        size = 0
        for f in self.context.schema.fields():
            try:
                size += f.get_size(self.context)
            except ValueError:
                # XXX This should be logged
                pass # Some content types have fields that are not expected
                     # to be called with the get_size method under certain
                     # circumstances, for example at construction time.
                     # While this is bad behaviour on the side of the content
                     # types, it is easier to generally ignore this case
                     # for robustness.
        if IATBlob.providedBy(self.context):
            f = self.context.getFile()
            size += f.get_size()
        return self._increment(size)


class QuotaRecurse(object):
    implements(IQuotaRecurse)
    adapts(IBaseFolder)

    def __init__(self, context):
        self.context = context

    def recurse_quota(self, increment):
        try:
            enforcer = IQuotaEnforcer(self.context)
        except TypeError:
            pass
        else:
            enforcer.enforce_quota(increment)
        parent = aq_parent(aq_inner(self.context))
        if IPloneSiteRoot.providedBy(parent):
            return
        while True:
            try:
                recurser = IQuotaRecurse(parent)
                break
            except TypeError:
                parent = aq_parent(aq_inner(parent))
                if IPloneSiteRoot.providedBy(parent):
                    return
        recurser.recurse_quota(increment)


class QuotaEnforcer(object):
    implements(IQuotaEnforcer)
    adapts(IQuotaAware)

    def __init__(self, context):
        self.context = context

    def max_size(self):
        ann = IAnnotations(self.context)
        quota = ann['quota']['max_size']
        qs = getUtility(IQuotaSettings)
        enforce = qs.enforce_quota
        gen_quota = int(qs.size_limit) * 1024 * 1024
        if quota > -1 and enforce:
            quota = min(quota, gen_quota)
        elif quota == -1:
            quota = gen_quota
        return quota

    def size_threshold(self):
        ann = IAnnotations(self.context)
        threshold = ann['quota']['threshold']
        qs = getUtility(IQuotaSettings)
        enforce = qs.enforce_quota
        gen_threshold = int(qs.size_threshold) * 1024 * 1024
        if threshold > 0 and enforce:
            threshold = min(threshold, gen_threshold)
        elif threshold == 0:
            threshold = gen_threshold
        return threshold

    def get_total(self, increment=0):
        ann = IAnnotations(self.context)
        ann['quota']['total'] += increment
        return int(ann['quota']['total'])

    def enforce_quota(self, increment):
        total = self.get_total(increment)
        max_size = self.max_size()
        threshold = self.size_threshold()
        hard_max = max_size + threshold
        if max_size > -1:
            putils = getToolByName(self.context, 'plone_utils')
            if total > hard_max:
                # first, clear previous status messages
                old = putils.showPortalMessages()
                putils.addPortalMessage(_(u'ERROR: QUOTA EXCEEDED'))
                raise Redirect, '%s/@@quota?increment=%d' % \
                                   (self.context.absolute_url(),
                                   int(increment))
            elif total > max_size:
                # first, clear previous status messages
                old = putils.showPortalMessages()
                putils.addPortalMessage(_(u'WARNING: SOFT QUOTA EXCEEDED'))


