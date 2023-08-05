"""Base class for integration tests, based on ZopeTestCase and PloneTestCase.

Note that importing this module has various side-effects: it registers a set of
products with Zope, and it sets up a sandbox Plone site with the appropriate
products installed.
"""

from Testing import ZopeTestCase


# Let Zope know about the products we require above-and-beyond a basic
# Plone install (PloneTestCase takes care of these).
ZopeTestCase.installProduct('Products.Quota')

# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite

from zope.event import notify
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.component import getUtility
from Products.Quota.interfaces import IQuotaService, IQuotaSettings

# Set up a Plone site, and apply the quota extension profiles
# to make sure they are installed.
setupPloneSite(products=['Products.Quota'])

import os
from Globals import package_home
path = os.path.join(package_home(globals()), 'input', 'img.gif')
path2 = os.path.join(package_home(globals()), 'input', 'Barracuda.jpg')
fd = open(path, 'rb')
fd2 = open(path2, 'rb')
img = fd.read()
barracuda = fd2.read()
fd.close()
fd2.close()


class TestPloneQuota(PloneTestCase):
    """Base class for integration tests for the 'Products.Quota' product. This may
    provide specific set-up and tear-down operations, or provide convenience
    methods.
    """

    def afterSetUp(self):
        self.setRoles(['Manager'])
        props = self.portal.portal_properties
        qs = getUtility(IQuotaSettings)
        qs.size_limit = 1
        qs.enforce_quota = False
        f1 = self.portal.invokeFactory('Folder', 'f1')
        self.f1 = self.portal['f1']
        self.f1.reindexObject()
        d1 = self.f1.invokeFactory('Document', 'd1', title='doc 1', text='d')
        self.d1 = self.f1['d1']
        self.d1.reindexObject()
        qf1 = self.portal.invokeFactory('QuotaFolder', 'qf1')
        self.qf1 = self.portal['qf1']
        self.qf1.reindexObject()
        f2 = self.qf1.invokeFactory('Folder', 'f2')
        self.f2 = self.qf1['f2']
        self.f2.reindexObject()
        f3 = self.f2.invokeFactory('Folder', 'f3')
        self.f3 = self.f2['f3']
        self.f3.reindexObject()
        d2 = self.f3.invokeFactory('Document', 'd2', title='doc 2', text='d')
        self.d2 = self.f3['d2']
        self.d2.reindexObject()
        self.sizer = getUtility(IQuotaService)

    def tearDown(self):
        self.portal.manage_delObjects(ids=['qf1', 'f1'])

    def testInitialObjectWeight(self):
        size = self.sizer.get_size(self.d2)
        self.assertEquals(96, size)

    def testInitialTotalWeightNotQEnforcer(self):
        total = self.sizer.get_total(self.d2)
        self.assertEquals(0, total)

    def testInitialTotalWeight(self):
        total = self.sizer.get_total(self.qf1)
        self.assertEquals(359, total)

    def testEditOnce(self):
        self.d2.setTitle('docu 2')
        notify(ObjectModifiedEvent(self.d2))
        total = self.sizer.get_total(self.qf1)
        self.assertEquals(360, total)

    def testEditThrice(self):
        self.d2.setTitle('docu 2')
        notify(ObjectModifiedEvent(self.d2))
        self.d2.setTitle('document 2')
        notify(ObjectModifiedEvent(self.d2))
        self.d2.setTitle('doc 2')
        notify(ObjectModifiedEvent(self.d2))
        total = self.sizer.get_total(self.qf1)
        self.assertEquals(359, total)

    def testEditText(self):
        self.d2.setText('1234567890')
        notify(ObjectModifiedEvent(self.d2))
        total = self.sizer.get_total(self.qf1)
        self.assertEquals(368, total)
        size = self.sizer.get_size(self.d2)
        self.assertEquals(105, size)

    def testDeleteObject(self):
        self.f3.manage_delObjects(ids=['d2'])
        total = self.sizer.get_total(self.qf1)
        self.assertEquals(263, total)

    def testMoveObjectOutOfQF(self):
        # let me cut / move please
        self.f3.d2.cb_isMoveable = lambda: 1
        self.f1.manage_pasteObjects(self.f3.manage_cutObjects(ids=['d2']))
        total = self.sizer.get_total(self.qf1)
        self.assertEquals(263, total)

    def testMoveObjectWithinQF(self):
        # let me cut / move please
        self.f3.d2.cb_isMoveable = lambda: 1
        self.f2.manage_pasteObjects(self.f3.manage_cutObjects(ids=['d2']))
        total = self.sizer.get_total(self.qf1)
        self.assertEquals(359, total)
        self.f3.manage_pasteObjects(self.f2.manage_cutObjects(ids=['d2']))
        total = self.sizer.get_total(self.qf1)
        self.assertEquals(359, total)

    def testCopyObjectIntoQF(self):
        self.f3.manage_pasteObjects(self.f1.manage_copyObjects(ids=['d1']))
        total = self.sizer.get_total(self.qf1)
        self.assertEquals(455, total)

    def testCopyObjectWithinQF(self):
        self.f2.manage_pasteObjects(self.f3.manage_copyObjects(ids=['d2']))
        total = self.sizer.get_total(self.qf1)
        self.assertEquals(455, total)

    def testRenameObjectWithinQF(self):
        # let me cut / move please
        self.f3.d2.cb_isMoveable = lambda: 1
        self.f3.manage_renameObjects(['d2'], ['d3'])
        total = self.sizer.get_total(self.qf1)
        self.assertEquals(359, total)

    def testImage(self):
        # we are taking into account the weight of the original image
        # plus that of all its scales, that's why such a small image (481b)
        # increases the total weight so much
        self.f3.invokeFactory('Image', 'im1')
        self.f3.im1.setImage(img, content_type="image/gif")
        notify(ObjectModifiedEvent(self.f3.im1))
        total = self.sizer.get_total(self.qf1)
        self.assertEquals(13160, total)

    def testNewsItemWithImage(self):
        self.f3.invokeFactory('News Item', 'ni1')
        self.f3.ni1.setImage(img, content_type="image/gif")
        notify(ObjectModifiedEvent(self.f3.ni1))
        total = self.sizer.get_total(self.qf1)
        self.assertEquals(13160, total)

    def testPortalQuotaExceeded(self):
        qs = getUtility(IQuotaSettings)
        qs.size_limit = '0.1'
        self.f3.invokeFactory('Image', 'im1')
        self.f3.im1.setImage(barracuda, content_type='image/jpg')
        self.assertRaises("Redirect", notify, ObjectModifiedEvent(self.f3.im1))

    def testFolderQuotaExceeded(self):
        self.qf1.size_limit = '0.1'
        self.f3.invokeFactory('Image', 'im1')
        self.f3.im1.setImage(barracuda, content_type='image/jpg')
        self.assertRaises("Redirect", notify, ObjectModifiedEvent(self.f3.im1))

    def testDontEnforceGlobalQuota(self):
        qs = getUtility(IQuotaSettings)
        self.qf1.size_limit = '1'
        qs.size_limit = '0.1'
        qs.enforce_quota = False
        self.f3.invokeFactory('Image', 'im1')
        self.f3.im1.setImage(barracuda, content_type='image/jpg')
        notify(ObjectModifiedEvent(self.f3.im1))
        total = self.sizer.get_total(self.qf1)
        self.assertEquals(180453, total)
        

    def testEnforceGlobalQuota(self):
        qs = getUtility(IQuotaSettings)
        self.qf1.size_limit = '1'
        qs.size_limit = '0.1'
        qs.enforce_quota = True
        self.f3.invokeFactory('Image', 'im1')
        self.f3.im1.setImage(barracuda, content_type='image/jpg')
        self.assertRaises("Redirect", notify, ObjectModifiedEvent(self.f3.im1))


class TestNestedPloneQuota(PloneTestCase):

    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Folder', 'f1')
        self.f1 = self.portal['f1']
        self.f1.invokeFactory('QuotaFolder', 'qf2')
        self.f1.qf2.invokeFactory('Folder', 'f4')
        self.f1.qf2.f4.invokeFactory('QuotaFolder', 'qf3')
        self.f1.qf2.f4.qf3.invokeFactory('Folder', 'f5')
        self.f1.qf2.f4.qf3.f5.invokeFactory('Image', 'im1')
        self.f1.qf2.f4.qf3.f5.im1.setImage(barracuda, content_type='image/jpg')
        self.sizer = getUtility(IQuotaService)

    def tearDown(self):
        self.portal.manage_delObjects(ids=['f1'])


    def testNestedOuterQuotaExceeded(self):
        total = self.sizer.get_total(self.f1.qf2.f4.qf3)
        self.assertTrue(255, total)
        self.f1.qf2.size_limit = '0.1'
        self.assertRaises("Redirect",
                          notify,
                          ObjectModifiedEvent(self.f1.qf2.f4.qf3.f5.im1))

    def testNestedInnerQuotaExceeded(self):
        total = self.sizer.get_total(self.f1.qf2.f4.qf3)
        self.assertTrue(255, total)
        self.f1.qf2.f4.qf3.size_limit = '0.1'
        self.assertRaises("Redirect",
                          notify,
                          ObjectModifiedEvent(self.f1.qf2.f4.qf3.f5.im1))


class TestPloneQuotaSettings(PloneTestCase):
    """Base class for integration tests for the 'Products.Quota' product. This may
    provide specific set-up and tear-down operations, or provide convenience
    methods.
    """

    def afterSetUp(self):
        self.setRoles(['Manager'])
        props = self.portal.portal_properties
        qs = getUtility(IQuotaSettings)
        qs.size_limit = 1
        qs.enforce_quota = False
        qf1 = self.portal.invokeFactory('QuotaFolder', 'qf1')
        self.qf1 = self.portal['qf1']
        self.sizer = getUtility(IQuotaService)

    def tearDown(self):
        self.portal.manage_delObjects(ids=['qf1',])

    def testNoGlobalQuota(self):
        pass

    def testNoLocalQuota(self):
        pass

    def testHigherGlobalQuota(self):
        pass

    def testHigherLocalQuota(self):
        pass

    def testHigherLocalQuotaEnforceGlobal(self):
        pass




def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPloneQuota))
    suite.addTest(makeSuite(TestNestedPloneQuota))
    return suite
