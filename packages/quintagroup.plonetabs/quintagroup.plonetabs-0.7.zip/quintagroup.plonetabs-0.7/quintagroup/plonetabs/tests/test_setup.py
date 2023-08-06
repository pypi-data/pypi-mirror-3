import unittest

from zope.component import getSiteManager

from plone.browserlayer.utils import registered_layers

from Products.CMFCore.utils import getToolByName

from quintagroup.plonetabs.tests.base import PloneTabsTestCase

class TestSetup(PloneTabsTestCase):
    
    def afterSetUp(self):
        self.loginAsPortalOwner()
    
    def test_actionIcons(self):
        tool = getToolByName(self.portal, 'portal_actionicons')
        icon_ids = [i._action_id for i in tool.listActionIcons()]
        self.failUnless('plonetabs' in icon_ids,
            'There is no plonetabs action icon in actionicons tool.')
    
    def test_controlPanel(self):
        tool = getToolByName(self.portal, 'portal_controlpanel')
        action_ids = [a.id for a in tool.listActions()]
        self.failUnless('plonetabs' in action_ids,
            'There is no plonetabs action in control panel.')
    
    def test_cssRegistry(self):
        tool = getToolByName(self.portal, 'portal_css')
        css = tool.getResource('++resource++plonetabs.css')
        self.failIf(css is None,
            'There is no ++resource++plonetabs.css stylesheets registered.')
    
    def test_jsRegistry(self):
        tool = getToolByName(self.portal, 'portal_javascripts')
        
        prototype = tool.getResource('++resource++prototype.js')
        self.failIf(prototype is None,
            'There is no ++resource++prototype.js script registered.')
        self.failUnless(prototype._data['enabled'],
            '++resource++prototype.js script is disabled.')
        
        effects = tool.getResource('++resource++pt_effects.js')
        self.failIf(effects is None,
            'There is no ++resource++pt_effects.js script registered.')
        
        dad = tool.getResource('++resource++sa_dragdrop.js')
        self.failIf(dad is None,
            'There is no ++resource++sa_dragdrop.js script registered.')

    def test_kssRegistry(self):
        tool = getToolByName(self.portal, 'portal_kss')
        kss = tool.getResource('++resource++plonetabs.kss')
        self.failIf(kss is None,
            'There is no ++resource++plonetabs.kss sheets registered.')
        kss = tool.getResource('++resource++plonetabsmode.kss')
        self.failIf(kss is None,
            'There is no ++resource++plonetabsmode.kss sheets registered.')
    
    def test_propertiesTool(self):
        tool = getToolByName(self.portal, 'portal_properties')
        self.failUnless(hasattr(tool, 'tabs_properties'),
            'There is no tabs_properties sheet in portal properties tool.')
        titles = tool.tabs_properties.getProperty('titles', None)
        self.assertEquals(titles,
            ('portal_tabs|Portal Tabs Configuration',
             'portal_footer|Portal Footer Configuration'),
            'Site properties was not setup properly'
        )
    
    def test_browserLayerRegistered(self):
        sm = getSiteManager(self.portal)
        layers = [o.__name__ for o in registered_layers()]
        self.failUnless('IPloneTabsProductLayer' in layers,
            'There should be quintagroup.ploentabs browser layer registered.')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
