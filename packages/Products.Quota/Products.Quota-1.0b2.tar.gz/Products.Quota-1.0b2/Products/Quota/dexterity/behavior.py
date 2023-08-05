from Products.Five import BrowserView
from Products.Quota import QuotaMessageFactory as _
from Products.Quota.browser.utils import set_quota, calculate_size
from Products.Quota.interfaces import IQuotaAware, IQuotaSettings, IQuotaSizer
from five import grok
from persistent.dict import PersistentDict
from plone.dexterity.interfaces import IDexterityContainer
from plone.directives import form
from z3c.form.interfaces import IAddForm, IEditForm
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.interface import alsoProvides, implements



class IQuotaProvider(form.Schema):
    """Behavior interface to enable next previous navigation per item.
    """

    form.fieldset('quota', label=_(u"Quota"),
                   fields=['size_limit', 'size_threshold', ])

    size_limit = schema.Int(title=_(u"Maximum size"),
                            description=_(u"Default maximum size of content "
                                          u"(MB) for quota aware containers"),
                            default= -1,
                            required=False)

    size_threshold = schema.Int(title=_(u"Size threshold"),
                                description=_(u"This value (MB) is added to "
                                              u"the previous value to make up "
                                              u"a hard maximum size"),
                                default=0,
                                required=False)

    form.omitted('size_limit')
    form.omitted('size_threshold')

    form.no_omit(IEditForm, 'size_limit')
    form.no_omit(IEditForm, 'size_threshold')
    form.no_omit(IAddForm, 'size_limit')
    form.no_omit(IAddForm, 'size_threshold')

    form.write_permission(size_limit='cmf.ManagePortal')
    form.write_permission(size_threshold='cmf.ManagePortal')

alsoProvides(IQuotaProvider, form.IFormFieldProvider)


class QuotaProviderAdapter(grok.Adapter):
    grok.implements(IDexterityContainer)
    grok.context(IQuotaAware)


class QuotaProvider(object):
    adapts(IDexterityContainer)
    implements(IQuotaProvider)

    def __init__(self, context):
        self.context = context

        ann = IAnnotations(self.context)
        if not ann.has_key('quota'):
            ann['quota'] = PersistentDict()
            ann['quota']['max_size'] = -1
            ann['quota']['threshold'] = 0
            ann['quota']['total'] = 0
            ann['quota']['size'] = 0

    def _get_limit(self):
        ann = IAnnotations(self.context)
        return ann['quota']['max_size'] / (1024 * 1024)

    def _set_limit(self, value):
        ann = IAnnotations(self.context)
        ann['quota']['max_size'] = int(value) * 1024 * 1024

    def _get_threshold(self):
        ann = IAnnotations(self.context)
        return ann['quota']['threshold'] / (1024 * 1024)

    def _set_threshold(self, value):
        ann = IAnnotations(self.context)
        ann['quota']['threshold'] = int(value) * 1024 * 1024

    size_limit = property(_get_limit, _set_limit)
    size_threshold = property(_get_threshold, _set_threshold)
