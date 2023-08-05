from Acquisition import aq_parent, aq_inner
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.Quota.interfaces import IQuotaSizer
from Products.Quota.interfaces import IQuotaRecurse

try:
    from Products.ATContentTypes.interfaces.interfaces import IATContentType
except ImportError:
    # older versions of ATContentTypes
    from Products.ATContentTypes.interface.interfaces import IATContentType


def objectMovedHandler(ob, event):
    """
    handler for IObjectMovedEvent
    """

    if (IATContentType.providedBy(ob) and ob.isTemporary()) or \
        IPloneSiteRoot.providedBy(ob):
        return

    sizer = IQuotaSizer(ob)
    increment = sizer.get_increment()
    size = sizer.get_size()
    old_size = size - increment

    # for moves and deletes
    if event.oldParent is not None and \
             not IPloneSiteRoot.providedBy(event.oldParent):
        try:
            recurser = IQuotaRecurse(event.oldParent)
        except TypeError:  # on site creation and deletion
            pass
        else:
            recurser.recurse_quota(-old_size)

    # for moves and creations
    if event.newParent is not None and \
             not IPloneSiteRoot.providedBy(event.newParent):
        try:
            recurser = IQuotaRecurse(event.newParent)
        except TypeError:  # on site creation and deletion
            pass
        else:
            recurser.recurse_quota(size)


def objectModifiedHandler(ob, event):
    """
    handler for IObjectModifiedEvent
    """
    if (IATContentType.providedBy(ob) and ob.isTemporary()) or \
        IPloneSiteRoot.providedBy(ob):
        return

    try:
        parent = aq_parent(aq_inner(ob))
    except AttributeError:
        return
    if not IPloneSiteRoot.providedBy(parent):
        sizer = IQuotaSizer(ob)
        increment = sizer.get_increment()
        while True:
            try:
                recurser = IQuotaRecurse(parent)
                break
            except TypeError:
                parent = aq_parent(aq_inner(parent))
                if IPloneSiteRoot.providedBy(parent):
                    return
        recurser.recurse_quota(increment)
