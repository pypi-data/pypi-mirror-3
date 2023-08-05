from persistent import Persistent
from zope.interface import implements
from Products.Quota.interfaces import IQuotaSettings

class QuotaSettings(Persistent):
    implements(IQuotaSettings)

    size_limit = -1

    size_threshold = 0

    enforce_quota = False