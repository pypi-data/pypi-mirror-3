from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from Products.Five import BrowserView
from Products.Quota.interfaces import IQuotaSizer


class QuotaBrowserView(BrowserView):
    def context():
        def get(self):
            return self._context[0]

        def set(self, context):
            self._context = [context]

        return property(get, set)
    context = context()


def set_quota(container, max_size=-1, threshold=0):
    ann = IAnnotations(container)
    if not ann.has_key('quota'):
        ann['quota'] = PersistentDict()
    ann['quota']['max_size'] = int(max_size)
    ann['quota']['threshold'] = int(threshold)
    if not ann['quota'].has_key('total'):
        ann['quota']['total'] = calculate_size(container)


def calculate_size(ob):
    try:
        sizer = IQuotaSizer(ob)
    except TypeError:
        return 0.0
    size = sizer.get_size()
    if ob.isPrincipiaFolderish:
        for child in ob.objectValues():
            size += calculate_size(child)
    return size
