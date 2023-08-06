import unittest

from zope.interface import Interface
from zope.interface.verify import verifyClass
from zope.component import getMultiAdapter, provideAdapter

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.ActionInformation import Action, ActionCategory

from quintagroup.plonetabs import messageFactory as _
from quintagroup.plonetabs.browser.interfaces import IPloneTabsControlPanel
from quintagroup.plonetabs.browser.plonetabs import PloneTabsControlPanel as ptp
from quintagroup.plonetabs.tests.base import PloneTabsTestCase
from quintagroup.plonetabs.tests.data import PORTAL_ACTIONS

class TestControlPanelHelperMethods(PloneTabsTestCase):
    """Test here configlet helper methods"""
    
    def afterSetUp(self):
        super(TestControlPanelHelperMethods, self).afterSetUp()
        self.loginAsPortalOwner()
        panel = getMultiAdapter((self.portal, self.portal.REQUEST),
            name='plonetabs-controlpanel')
        # we need this to apply zope2 security (got from zope2 traverse method)
        self.panel = panel.__of__(self.portal)
        self.tool = getToolByName(self.portal, 'portal_actions')
    
    def test_redirect(self):
        response = self.portal.REQUEST.RESPONSE
        method = self.panel.redirect
        portal_url =  getMultiAdapter((self.portal, self.portal.REQUEST),
                                      name=u"plone_portal_state").portal_url()
        url = '%s/@@plonetabs-controlpanel' % portal_url
        method()
        self.assertEquals(response.headers.get('location', ''), url,
            'Redirect method is not working properly.')
        
        # check query string and anchor hash
        method('http://quintagroup.com', 'q=test', 'hash_code')
        self.assertEquals(response.headers.get('location', ''),
            'http://quintagroup.com?q=test#hash_code',
            'Redirect method is not working properly.')
    
    def test_fixExpression(self):
        method = self.panel.fixExpression
        self.assertEquals(method('/slash'), 'string:${portal_url}/slash')
        self.assertEquals(method('https://test.com'), 'string:https://test.com')
        self.assertEquals(method('python:True'), 'python:True')
        self.assertEquals(method('hello'), 'string:${object_url}/hello')
    
    def test_copyAction(self):
        data = PORTAL_ACTIONS[0][1]['children'][0][1]
        action = Action('act1', **data)
        info = self.panel.copyAction(action)
        self.assertEquals(len(info.keys()), 6)
        self.assertEquals(info['description'], 'The most important place')
    
    def test_validateActionFields(self):
        method = self.panel.validateActionFields
        good_data = PORTAL_ACTIONS[0][1]['children'][0][1].copy()
        good_data['id'] = 'new_one'
        errors = method('new_category', good_data)
        self.assertEquals(errors, {},
            'There should be no errors for valid data.')
        
        bad_data = {'id':'',
                    'title': ' ',
                    'available_expr': 'bad_type:test',
                    'url_expr': 'bad_type:test'}
        
        # Revert PloneTestCase's optimization
        # because this breaks our test
        def __init__(self, text):
            self.text = text
            if text.strip():
                self._v_compiled = getEngine().compile(text)
        from Products.CMFCore.Expression import Expression
        optimized__init__ = Expression.__init__
        Expression.__init__ = __init__
        errors = method('new_category', bad_data)
        # rollback our patch
        Expression.__init__ = optimized__init__
        
        self.assertEquals(len(errors.keys()), 4,
            'validateActionFields method is not working properly.')
    
    def test_processErrors(self):
        method = self.panel.processErrors
        errors = {'error':'error message'}
        self.assertEquals(method(errors), errors,
            'processErrors method is not working properly.')
        self.assertEquals(method(errors, 'pre_', '_post'),
            {'pre_error_post': 'error message'},
            'processErrors method is not working properly.')
    
    def test_parseEditForm(self):
        method = self.panel.parseEditForm
        form = {'orig_id': 'id1',
                'category': 'cat1',
                'visible_id1': True,
                'id_id1': 'id_new',
                'title_id1': 'title1',
                'url_expr_id1': 'expr1',
                'available_expr_id1': 'expr2'}
        self.assertEquals(method(form),
            ('id1', 'cat1', {'id': 'id_new',
                             'title': 'title1',
                             'url_expr': 'expr1',
                             'available_expr': 'expr2',
                             'visible': True}),
            'parseEditForm method is not working properly.')
        
        del form['orig_id']
        self.failUnlessRaises(KeyError, method, form)
    
    def test_parseAddForm(self):
        method = self.panel.parseAddForm
        form = {'id': 'id1',
                'category': 'cat1',
                'visible': True,
                'title': 'title1',
                'url_expr': 'string:expr1',
                'available_expr': 'expr2'}
        self.assertEquals(method(form),
            ('id1', 'cat1', {'id': 'id1',
                             'visible': True,
                             'title': 'title1',
                             'url_expr': 'string:expr1',
                             'available_expr': 'expr2'}),
            'parseAddForm method is not working properly.')
        
        del form['id']
        self.failUnlessRaises(KeyError, method, form)
    
    def test_getActionCategory(self):
        method = self.panel.getActionCategory
        self.purgeActions()
        self.failUnlessRaises(KeyError, method, 'portal_tabs')
        
        self.setupActions(self.tool)
        self.assertEquals(method('portal_tabs').id, 'portal_tabs',
            'getActionCategory is not working properly.')
    
    def test_getOrCreateCategory(self):
        method = self.panel.getOrCreateCategory
        self.purgeActions()
        self.assertEquals(method('portal_tabs').id, 'portal_tabs',
            'getOrCreateCategory is not working properly.')
    
    def test_setSiteProperties(self):
        self.panel.setSiteProperties(title='Test Title')
        sp = getToolByName(self.portal, 'portal_properties').site_properties
        self.assertEquals(sp.getProperty('title'), 'Test Title',
            'setSiteProperties method is not working properly.')
    
    def test_renderViewlet(self):
        # register test viewlet and it's manager
        from zope.viewlet.interfaces import IViewlet, IViewletManager
        from zope.viewlet.viewlet import ViewletBase
        from zope.viewlet.manager import ViewletManagerBase
        from zope.publisher.interfaces.browser import IDefaultBrowserLayer
        from zope.publisher.interfaces.browser import IBrowserView
        class TestViewlet(ViewletBase):
            def __of__(self, obj):
                return self
            def render(self):
                return 'test viewlet'
        provideAdapter(
            TestViewlet,
            (Interface, IDefaultBrowserLayer, IBrowserView, IViewletManager),
            IViewlet,
            name=u'test_viewlet')
        provideAdapter(
            ViewletManagerBase,
            (Interface, IDefaultBrowserLayer, IBrowserView),
            IViewletManager,
            name=u'test_manager')
        
        self.assertEquals(
            self.panel.renderViewlet('test_manager', 'test_viewlet'),
            'test viewlet',
            'renderViewlet method is not workig properly')
    
    def test_addAction(self):
        self.purgeActions()
        self.panel.addAction('new_category', {'id':'id1', 'title':'Test'})
        self.failUnless('id1' in self.tool.new_category.objectIds(),
            'addAction method is not workig properly')
    
    def test_updateAction(self):
        method = self.panel.updateAction
        
        self.purgeActions()
        self.failUnlessRaises(KeyError, method, 'id1', 'cat1', {'id':'new'})
        
        self.setupActions(self.tool)
        # we need to commit transaction because
        # we are going to rename just added action now
        import transaction
        transaction.savepoint()
        method('home', 'portal_tabs', {'id':'new_home'})
        self.failUnless('new_home' in self.tool.portal_tabs.objectIds(),
            'updateAction method is not workig properly')
    
    def test_deleteAction(self):
        self.purgeActions()
        self.setupActions(self.tool)
        self.panel.deleteAction('home', 'portal_tabs')
        self.failIf('home' in self.tool.portal_tabs.objectIds(),
             'deleteAction method is not workig properly')
    
    def test_moveAction(self):
        self.purgeActions()
        self.setupActions(self.tool)
        pos = self.tool.portal_tabs.getObjectPosition
        self.assertEquals(pos('home'), 0,
            'moveAction method is not workig properly')
        self.panel.moveAction('home', 'portal_tabs', -1)
        self.assertEquals(pos('home'), 1,
             'moveAction method is not workig properly')


class TestControlPanelAPIMethods(PloneTabsTestCase):
    """Test here interface methods of control panel class"""
    
    def afterSetUp(self):
        super(TestControlPanelAPIMethods, self).afterSetUp()
        self.loginAsPortalOwner()
        panel = getMultiAdapter((self.portal, self.portal.REQUEST),
            name='plonetabs-controlpanel')
        # we need this to apply zope2 security (got from zope2 traverse method)
        self.panel = panel.__of__(self.portal)
        self.tool = getToolByName(self.portal, 'portal_actions')
    
    def test_interface(self):
        self.failUnless(IPloneTabsControlPanel.implementedBy(ptp),
            'PloneTabs control panel does not implement required interface.')
        self.failUnless(verifyClass(IPloneTabsControlPanel, ptp),
            'PloneTabs control panel does not implement required interface.')
    
    def test_getPageTitle(self):
        self.assertEquals(self.panel.getPageTitle(),
            _(u"Portal Tabs Configuration"),
            'getPageTitle method is broken')
        self.assertEquals(self.panel.getPageTitle(category='notexists'),
            _(u"Plone '${cat_name}' Configuration",
              mapping={'cat_name': 'notexists'}),
            'getPageTitle method is broken')
    
    def test_hasActions(self):
        method = self.panel.hasActions
        # purge any default portal actions
        self.purgeActions()
        self.failIf(method(),
            'There should be no portal_tab actions in portal')
        
        # setup our own actions
        self.setupActions(self.tool)
        self.failUnless(method(),
            'There should be portal_tab actions in portal')
    
    def test_getPortalActions(self):
        method = self.panel.getPortalActions
        # purge any default portal actions
        self.purgeActions()
        self.assertEquals(len(method()), 0,
            'There should be no actions in portal_tabs category.')
        
        # setup our own actions
        self.setupActions(self.tool)
        self.assertEquals(len(method()), 2,
            'There should be 2 actions in portal_tabs category.')
        
        # marginal arguments
        self.assertEquals(len(method('notexistent_category')), 0,
            'There should be no actions for not existed category.')
    
    def test_isGeneratedTabs(self):
        method = self.panel.isGeneratedTabs
        # prepare value
        sp = getToolByName(self.portal, 'portal_properties').site_properties
        sp.manage_changeProperties(disable_folder_sections=True)
        self.failIf(method(), 'But folder sections are disabled...')
    
    def test_isNotFoldersGenerated(self):
        method = self.panel.isNotFoldersGenerated
        # prepare value
        sp = getToolByName(self.portal, 'portal_properties').site_properties
        sp.manage_changeProperties(disable_nonfolderish_sections=True)
        self.failIf(method(), 'But non folderish sections are disabled...')
    
    def test_getActionsList(self):
        method = self.panel.getActionsList
        # purge any default portal actions
        self.purgeActions()
        self.failIf('class="editform"' in method(),
            'There should no be actions in actions list template.')
        self.setupActions(self.tool)
        self.failUnless('class="editform"' in method(),
            'There are no actions in actions list template.')
    
    def test_getAutoGenereatedSection(self):
        method = self.panel.getAutoGenereatedSection
        self.failIf('<form' in method('user'),
            'There should be no form in autogenerated tabs template '
            'for category other than portal_tabs.')
        self.failUnless('<form' in method('portal_tabs'),
            'There should be form in autogenerated tabs template '
            'for portal_tabs category.')
    
    def test_getGeneratedTabs(self):
        self.panel.getGeneratedTabs()
        # check expiration header set by generated tabs template
        self.assertEquals(
            self.portal.REQUEST.RESPONSE.headers.get('expires', ''),
            'Mon, 26 Jul 1996 05:00:00 GMT',
            'Expiration header is not set properly.')
    
    def test_getRootTabs(self):
        method = self.panel.getRootTabs
        # make sure we don't depend on external settings
        self.purgeContent()
        self.assertEquals(len(method()), 0,
            'There should be no root elements for navigation.')
        
        # now add some testing content
        self.setupContent(self.portal)
        self.assertEquals(len(method()), 2,
            'There should be 2 elements in portal root for navigation.')
        
        # now switch off autogeneration
        sp = getToolByName(self.portal, 'portal_properties').site_properties
        sp.manage_changeProperties(disable_folder_sections=True)
        self.assertEquals(len(method()), 0,
            'There should be no root elements for navigation when '
            'tabs autogeneration is switched off.')
    
    def test_getCategories(self):
        method = self.panel.getCategories
        # purge any default portal actions
        self.purgeActions()
        self.assertEquals(len(method()), 0,
            'There should be no categories in portal_actions tool.')
        
        # now setup actions
        self.setupActions(self.tool)
        self.assertEquals(method(), ['portal_tabs', 'new_category'],
            'There should be exactly 2 categories in portal_actions tool.')
    
    def test_portal_tabs(self):
        method = self.panel.portal_tabs
        self.purgeContent()
        self.purgeActions()
        self.assertEquals(len(method()), 0,
            'There should be no portal tabs.')
        
        # cleanup memoize cache
        # cause actions method of portal context state is caching it's
        # results in request and we have the same request for every call
        self.purgeCache(self.portal.REQUEST)
        
        # add actions
        self.setupActions(self.tool)
        self.assertEquals(len(method()), 2,
            'There should be 2 portal tabs.')
        
        # add content
        self.setupContent(self.portal)
        self.assertEquals(len(method()), 4,
            'There should be 4 portal tabs.')
    
    def test_selected_portal_tab(self):
        self.assertEquals(self.panel.selected_portal_tab(), 'index_html',
            'index_html is not selected tab while being on configlet.')

    def test_test(self):
        self.assertEquals(self.panel.test(True, 'true', 'false'), 'true',
            'Test function does not work properly.')


class TestControlPanelManageMethods(PloneTabsTestCase):
    """Test here management methods of control panel class"""
    
    def afterSetUp(self):
        super(TestControlPanelManageMethods, self).afterSetUp()
        self.loginAsPortalOwner()
        panel = getMultiAdapter((self.portal, self.portal.REQUEST),
            name='plonetabs-controlpanel')
        # we need this to apply zope2 security (got from zope2 traverse method)
        self.panel = panel.__of__(self.portal)
        self.tool = getToolByName(self.portal, 'portal_actions')
        
        # purge standard set of actions and set our own testing ones
        self.purgeActions()
        self.setupActions(self.tool)
    
    def test_manage_setAutogeneration(self):
        self.setupContent(self.portal)
        form = {'generated_tabs': '1',
                'nonfolderish_tabs': '0',
                'folder1': '0'}
        self.panel.manage_setAutogeneration(form, {})
        self.failUnless(self.portal.folder1.exclude_from_nav())
        sp = getToolByName(self.portal, 'portal_properties').site_properties
        self.failIf(sp.disable_folder_sections)
        self.failUnless(sp.disable_nonfolderish_sections)
    
    def test_manage_addAction(self):
        self.purgeActions()
        form = {'id': 'id1',
                'category': 'cat1',
                'visible': True,
                'title': 'title1',
                'url_expr': 'string:expr1',
                'available_expr': 'expr2'}
        postback = self.panel.manage_addAction(form, {})
        self.failUnless('id1' in self.tool.cat1.objectIds())
        self.failIf(postback,
            'There should be redirect after successfull adding.')
    
    def test_manage_editAction(self):
        method = self.panel.manage_editAction
        self.purgeActions()
        self.setupActions(self.tool)
        form = {'orig_id': 'home',
                'category': 'portal_tabs',
                'visible_home': True,
                'id_home': 'id_new',
                'title_home': 'title1',
                'url_expr_home': 'expr1',
                'available_expr_home': 'expr2'}
        import transaction
        transaction.savepoint()
        
        postback = method(form, {})
        self.failUnless('id_new' in self.tool.portal_tabs.objectIds())
        self.failIf(postback,
            'There should be redirect after successfull edition.')
        
        form['category'] = 'non_existent'
        self.failUnlessRaises(KeyError, method, form, {})
    
    def test_manage_deleteAction(self):
        self.purgeActions()
        self.setupActions(self.tool)
        form = {'orig_id': 'home',
                'category': 'portal_tabs',
                'visible_home': True,
                'id_home': 'id_new',
                'title_home': 'title1',
                'url_expr_home': 'expr1',
                'available_expr_home': 'expr2'}
        self.panel.manage_deleteAction(form, {})
        self.failIf('home' in self.tool.portal_tabs.objectIds())
    
    def test_manage_moveUpAction(self):
        self.purgeActions()
        self.setupActions(self.tool)
        form = {'orig_id': 'quintagroup',
                'category': 'portal_tabs',
                'visible_quintagroup': True,
                'id_quintagroup': 'quintagroup',
                'title_quintagroup': 'title1',
                'url_expr_quintagroup': 'expr1',
                'available_expr_quintagroup': 'expr2'}
        self.panel.manage_moveUpAction(form, {})
        self.assertEquals(
            self.tool.portal_tabs.getObjectPosition('quintagroup'), 0)
    
    def test_manage_moveDownAction(self):
        self.purgeActions()
        self.setupActions(self.tool)
        form = {'orig_id': 'home',
                'category': 'portal_tabs',
                'visible_home': True,
                'id_home': 'home',
                'title_home': 'title1',
                'url_expr_home': 'expr1',
                'available_expr_home': 'expr2'}
        self.panel.manage_moveDownAction(form, {})
        self.assertEquals(self.tool.portal_tabs.getObjectPosition('home'), 1)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestControlPanelHelperMethods))
    suite.addTest(unittest.makeSuite(TestControlPanelAPIMethods))
    suite.addTest(unittest.makeSuite(TestControlPanelManageMethods))
    
    # these tests are implemented as Selenium KSS Tests
    # using kss.demo package, and KSS plugins are tested by means of
    # ecmaunit.js
    #suite.addTest(unittest.makeSuite(TestControlPanelKSSMethods))
    return suite
