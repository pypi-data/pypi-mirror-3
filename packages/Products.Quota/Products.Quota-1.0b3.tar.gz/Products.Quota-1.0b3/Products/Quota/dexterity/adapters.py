from Products.Quota import adapters as at_adapters
from Products.Quota.interfaces import IQuotaSizer, IQuotaRecurse
from plone.dexterity.interfaces import IDexterityContent, IDexterityContainer
from plone.namedfile.editor import INamedBlobFileField
from zope.component import adapts
from zope.interface import implements
from zope.interface.interface import InterfaceClass
from zope.schema import getFieldsInOrder
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict


class DexterityQuotaSizer(at_adapters.BaseQuotaSizer):
    implements(IQuotaSizer)
    adapts(IDexterityContent)

    def _increment(self, new_size):
        ann = IAnnotations(self.context)
        if not ann.has_key('quota'):
            ann['quota'] = PersistentDict()
            ann['quota']['max_size'] = -1
            ann['quota']['threshold'] = 0
            ann['quota']['total'] = 0
            ann['quota']['size'] = 0

        old_size = ann['quota']['size']
        ann['quota']['size'] = new_size
        return new_size - old_size

    def get_increment(self):
        size = 0

        # XXX: I don't know exactly how to locate all schema fields
        # provided by dexterity content types as it is done in AT with 
        # context.schema. So i digged into z3c.form.field and copied some
        # knowhow :-)

        fields = []
        for arg in self.context.__provides__.interfaces():
            if isinstance(arg, InterfaceClass):
                for name, field in getFieldsInOrder(arg):
                    fields.append(field)
                    try:
                        #if INamedBlobFileField.providedBy(field):
                        size += field.query(self.context).size
                        #else:
                        #    size += field.get_size(self.context)

                    except (ValueError, AttributeError):
                        pass

        return self._increment(size)


class QuotaRecurse(at_adapters.QuotaRecurse):
    implements(IQuotaRecurse)
    adapts(IDexterityContainer)
