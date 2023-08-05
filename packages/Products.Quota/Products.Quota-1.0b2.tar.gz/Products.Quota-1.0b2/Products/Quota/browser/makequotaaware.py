from zope.interface import directlyProvides
from zope.interface.declarations import noLongerProvides
from Products.Archetypes.interfaces import IBaseFolder
from Products.Quota.browser.utils import QuotaBrowserView, set_quota
from Products.Quota.interfaces import IQuotaAware


class MakeQuotaAware(QuotaBrowserView):
    def __call__(self):
        """
        """
        assert(IBaseFolder.providedBy(self.context))
        directlyProvides(self.context, IQuotaAware)
        set_quota(self.context)
        redirect = '%s/@@quota' % self.context.absolute_url()
        return self.request.response.redirect(redirect)


class RmQuotaAwareness(QuotaBrowserView):
    def __call__(self):
        """
        """
        assert(IBaseFolder.providedBy(self.context))
        noLongerProvides(self.context, IQuotaAware)
        redirect = self.context.absolute_url()
        return self.request.response.redirect(redirect)


class CheckQuotaAwareness(QuotaBrowserView):
    def is_quota_aware(self):
        return IQuotaAware.providedBy(self.context)
