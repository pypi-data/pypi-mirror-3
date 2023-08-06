import unittest

import transaction
from AccessControl.SecurityManagement import newSecurityManager, \
    noSecurityManager
from Testing import ZopeTestCase as ztc

from zope.component import getSiteManager

from plone.browserlayer.utils import registered_layers

from Products.CMFCore.utils import getToolByName
from  Products.PloneTestCase.layer import PloneSiteLayer

from quintagroup.plonetabs.tests.base import PloneTabsTestCase

class TestErase(PloneTabsTestCase):
    # we use here nested layer for not to make an impact on
    # the rest test cases, this test case check uninstall procedure
    # thus it has to uninstall package which will be required to
    # be installed for other test cases
    class layer(PloneSiteLayer):
        @classmethod
        def setUp(cls):
            app = ztc.app()
            portal = app.plone

            # elevate permissions
            user = portal.getWrappedOwner()
            newSecurityManager(None, user)

            tool = getToolByName(portal, 'portal_quickinstaller')
            product_name = 'quintagroup.plonetabs'
            if tool.isProductInstalled(product_name):
                tool.uninstallProducts([product_name,])

            # drop elevated perms
            noSecurityManager()

            transaction.commit()
            ztc.close(app)

    def afterSetUp(self):
        self.loginAsPortalOwner()
    
    def test_actionIcons(self):
        tool = getToolByName(self.portal, 'portal_actionicons')
        icon_ids = [i._action_id for i in tool.listActionIcons()]
        self.failIf('plonetabs' in icon_ids,
            'There should be no plonetabs action icon after uninstall.')
    
    def test_controlPanel(self):
        tool = getToolByName(self.portal, 'portal_controlpanel')
        action_ids = [a.id for a in tool.listActions()]
        self.failIf('plonetabs' in action_ids,
            'There should be no plonetabs configlet after after uninstall.')
    
    def test_cssRegistry(self):
        tool = getToolByName(self.portal, 'portal_css')
        css = tool.getResource('++resource++plonetabs.css')
        self.failUnless(css is None,
            'There should be no ++resource++plonetabs.css stylesheets after'
            ' uninstall.')
    
    def test_jsRegistry(self):
        tool = getToolByName(self.portal, 'portal_javascripts')
        
        effects = tool.getResource('++resource++pt_effects.js')
        self.failUnless(effects is None,
            'There should be no ++resource++pt_effects.js script after'
            ' uninstall.')
        
        dad = tool.getResource('++resource++sa_dragdrop.js')
        self.failUnless(dad is None,
            'There should be no ++resource++sa_dragdrop.js script after'
            ' uninstall.')

    def test_kssRegistry(self):
        tool = getToolByName(self.portal, 'portal_kss')
        kss = tool.getResource('++resource++plonetabs.kss')
        self.failUnless(kss is None,
            'There should be no ++resource++plonetabs.kss sheets after'
            ' uninstall.')
        kss = tool.getResource('++resource++plonetabsmode.kss')
        self.failUnless(kss is None,
            'There should be no ++resource++plonetabsmode.kss sheets after'
            ' uninstall.')
    
    def test_propertiesTool(self):
        tool = getToolByName(self.portal, 'portal_properties')
        self.failUnless(hasattr(tool, 'tabs_properties'),
            'There is no tabs_properties sheet in portal properties tool'
            ' after uninstall.')
        titles = tool.tabs_properties.getProperty('titles', None)
        self.assertEquals(titles,
            ('portal_tabs|Portal Tabs Configuration',
             'portal_footer|Portal Footer Configuration'),
            'titles plonetabs property was erased from portal_properties'
            ' after uninstall.'
        )
    
    def test_browserLayer(self):
        sm = getSiteManager(self.portal)
        layers = [o.__name__ for o in registered_layers()]
        self.failIf('IPloneTabsProductLayer' in layers,
            'There should be no quintagroup.plonetabs layer after uninstall.')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestErase))
    return suite
