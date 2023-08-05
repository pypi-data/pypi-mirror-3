from zope.component import getUtility
from zope.formlib import form
from plone.app.controlpanel.form import ControlPanelForm
from Products.Quota.interfaces import IQuotaSettings
from Products.Quota import QuotaMessageFactory as _



def quota_settings(context):
    return getUtility(IQuotaSettings)


class QuotaSettingsControlPanel(ControlPanelForm):

    form_fields = form.FormFields(IQuotaSettings)

    form_name = _(u"Quota Settings")
    label = _(u"Quota Settings")
    description = _(u"Please enter the appropriate global quota settings")
