from Products.CMFCore.utils import getToolByName
from Products.Quota.interfaces import IQuotaEnforcer
from Products.Quota.browser.utils import QuotaBrowserView, set_quota


class QuotaView(QuotaBrowserView):

    def quota(self):
        enforcer = IQuotaEnforcer(self.context)
        quota = enforcer.max_size()
        return int(quota) / (1024 * 1024)

    def threshold(self):
        enforcer = IQuotaEnforcer(self.context)
        threshold = enforcer.size_threshold()
        return int(threshold) / (1024 * 1024)

    def total(self):
        enforcer = IQuotaEnforcer(self.context)
        total = enforcer.get_total()
        return int(total) / (1024 * 1024)

    def can_edit(self):
        pm = getToolByName(self.context, 'portal_membership')
        return pm.checkPermission('Manage portal', self.context)


class QuotaEdit(QuotaBrowserView):

    def __call__(self):
        if self.request.get('submit', False):
            max_size = self.request.get('max_size', -1)
            threshold = self.request.get('threshold', 0)
            set_quota(self.context, max_size=int(max_size) * 1024 * 1024,
                                    threshold=int(threshold) * 1024 * 1024)
        redirect = '%s/@@quota' % self.context.absolute_url()
        return self.request.response.redirect(redirect)
