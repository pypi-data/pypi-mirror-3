from zope import schema
from zope.interface import Interface, implements
from Products.Quota import QuotaMessageFactory as _


class IQuotaSizer(Interface):
    """
    adapter that let us find out the size of the adapted object
    """

    def get_increment():
        """
        calculate the increment in size of the adapted object since
        the last call to adapter.get_increment() or adapter.get_size(),
        and annotate its new size
        """

    def get_size():
        """
        return the size of the adapted object
        """


class IQuotaRecurse(Interface):
    """
    adapter to propagate changes in size upwards in the containment
    hyerarchy so that they will reach any concerned quota aware container.
    """

    def recurse_quota(increment):
        """
        If we can be adapted to IQuotaAware, execute enforce_quota,
        else execute recurse_quota on parent.
        """


class IQuotaAware(Interface):
    """
    marker interface for classes that can be adapted to IQuotaEnforcer (can be made quota aware)
    """


class IQuotaEnforcer(Interface):
    """
    adapter that will enforce the necessary quota whenever an IQuotaRecurse
    adapter reaches an IQuotaAware container.
    """

    def max_size(ob):
        """Return maximum allowed size (quota)
        """

    def size_threshold(ob):
        """Return allowed size over quota
        """

    def get_total(increment):
        """
        return the size of the object plus the size of all it's contained
        objects (given there is an IQuotaSizer adapter for all of them
        """

    def enforce_quota(increment):
        """
        Check that total size + increment does not go over the allowed quota, and add increment to total.
        """


class IQuotaSettings(Interface):
    """Global quota settings
    """

    size_limit = schema.Int(title=_(u"Maximum size"),
                            description=_(u"Default maximum size of content "
                                          u"(MB) for quota aware containers"),
                            default=-1,
                            required=False)

    size_threshold = schema.Int(title=_(u"Size threshold"),
                                description=_(u"This value (MB) is added to "
                                              u"the previous value to make up "
                                              u"a hard maximum size"),
                                default=0,
                                required=False)

    enforce_quota = schema.Bool(title=_(u"Enforce quota"),
                                description=_(u"If checked, no quota aware "
                                              u"container will be allowed "
                                              u"to contain more than these "
                                              u"settings"),
                                default=False,
                                required=False)

class IQuotaLayer(Interface):
    """BrowserLayer for this add-on"""
