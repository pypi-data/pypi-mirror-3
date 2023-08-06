# -*- coding:utf-8 -*-
import unittest2 as unittest
import transaction
from collective.addthis.testing import ADDTHIS_INTEGRATION_TESTING,\
                                       ADDTHIS_FUNCTIONAL_TESTING
from collective.addthis.interfaces import IAddThisSettings,\
                                          IAddThisBrowserLayer
from plone.app.testing import logout, setRoles, TEST_USER_ID

from zope.component import getMultiAdapter, queryUtility
from zope.interface import directlyProvides
#from plone.testing.z2 import Browser
from plone.registry.interfaces import IRegistry
from plone.registry import Registry
from Products.CMFCore.utils import getToolByName


class IntegrationTest(unittest.TestCase):

    layer = ADDTHIS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.registry = Registry()
        self.registry.registerInterface(IAddThisSettings)
        directlyProvides(self.portal.REQUEST, IAddThisBrowserLayer)

    def test_registry_registered(self):
        registry = queryUtility(IRegistry)
        self.assertTrue(registry.forInterface(IAddThisSettings))

    def test_addthis_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name=u'addthis-settings')
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_controlpanel_view_is_protected(self):
        from AccessControl import Unauthorized
        logout()
        self.assertRaises(Unauthorized,
                          self.portal.restrictedTraverse,
                          '@@addthis-settings')

    def test_action_in_controlpanel(self):
        cp = getToolByName(self.portal, 'portal_controlpanel')
        actions = [a.getAction(self)['id'] for a in cp.listActions()]
        self.failUnless('addthis-settings' in actions)

    def test_registry_default_values(self):
        BASE = 'collective.addthis.interfaces.IAddThisSettings.%s'
        rec = self.registry.records
        self.assertTrue(rec[BASE % 'addthis_activated'].value)
        self.assertEqual(rec[BASE % 'addthis_account_name'].value, "")
        self.assertFalse(rec[BASE % 'addthis_load_asynchronously'].value)
        self.assertEqual(rec[BASE % 'addthis_url'].value,
            "http://www.addthis.com/bookmark.php?v=250")
        self.assertEqual(rec[BASE % 'addthis_script_url'].value,
            "http://s7.addthis.com/js/250/addthis_widget.js")
        self.assertEqual(rec[BASE % 'addthis_chicklets'].value, [])
        self.assertFalse(rec[BASE % 'addthis_data_track_clickback'].value)
        self.assertFalse(rec[BASE % 'addthis_data_track_addressbar'].value)



class FunctionalTest(unittest.TestCase):

    layer = ADDTHIS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.registry = Registry()
        self.registry.registerInterface(IAddThisSettings)
        directlyProvides(self.portal.REQUEST, IAddThisBrowserLayer)

    def test_registry_event_listener(self):
        pj = getToolByName(self.portal, 'portal_javascripts')
        BASE = 'collective.addthis.interfaces.IAddThisSettings.%s'
        rec = self.registry.records
        rec[BASE % 'addthis_load_asynchronously'].value = True
        transaction.commit()
        addthis = pj.getResource('++resource++collective.addthis/addthis.js')
        self.assertTrue(addthis.getEnabled())
        rec[BASE % 'addthis_load_asynchronously'].value = False
        transaction.commit()
        self.assertFalse(addthis.getEnabled())



def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
