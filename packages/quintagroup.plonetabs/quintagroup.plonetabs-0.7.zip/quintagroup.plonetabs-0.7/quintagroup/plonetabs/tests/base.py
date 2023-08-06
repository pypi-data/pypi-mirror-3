try:
    from zope.annotation.interfaces import IAnnotations
except ImportError:
    from zope.app.annotation.interfaces import IAnnotations

from plone.browserlayer.layer import mark_layer

from  Testing import ZopeTestCase as ztc
from  Products.Five import zcml
from  Products.Five import fiveconfigure
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IAction, IActionCategory
from Products.CMFCore.ActionInformation import Action, ActionCategory
from  Products.PloneTestCase import PloneTestCase as ptc
from  Products.PloneTestCase.layer import onsetup

from quintagroup.plonetabs.tests.data import PORTAL_ACTIONS, PORTAL_CONTENT

#ztc.installProduct('Zope2Product')

@onsetup
def setup_package():
    import quintagroup.plonetabs
    zcml.load_config('configure.zcml', quintagroup.plonetabs)
    #ztc.installPackage('some.other.package')
    ztc.installPackage('quintagroup.plonetabs')

setup_package()
ptc.setupPloneSite(products=['quintagroup.plonetabs'])

_marker = object()

class PloneTabsTestCase(ptc.PloneTestCase):
    """Common test base class"""
    
    def afterSetUp(self):
        # due to some reason plone.browserlayer is not marking REQUEST
        # with installed products layer interfaces
        # so I'm doing it manually here 
        class DummyEvent(object):
            def __init__(self, request):
                self.request = request
        mark_layer(self.portal, DummyEvent(self.portal.REQUEST))
    
    def purgeCache(self, request):
        annotations = IAnnotations(request)
        cache = annotations.get('plone.memoize', _marker)
        if cache is not _marker:
            del annotations['plone.memoize']
    
    def purgeActions(self):
        for obj in self.tool.objectValues():
            self.tool._delObject(obj.id)
            #if IAction.providedBy(obj):
                #self.tool._delObject(obj.id)
            #elif IActionCategory.providedBy(obj):
                #obj.manage_delObjects(ids=obj.objectIds())
    
    def setupActions(self, parent, kids=PORTAL_ACTIONS):
        ids = parent.objectIds()
        for id, child in kids:
            if child['type'] == 'action' and id not in ids:
                parent._setObject(id, Action(id, **child))
                continue
            if child['type'] == 'category':
                if id not in ids:
                    parent._setObject(id, ActionCategory(id))
                if child.get('children', {}):
                    self.setupActions(getattr(parent, id), child['children'])
    
    def purgeContent(self):
        ids = [obj.id for obj in self.portal.listFolderContents()]
        self.portal.manage_delObjects(ids=ids)
    
    def setupContent(self, parent, kids=PORTAL_CONTENT):
        ids = parent.objectIds()
        for id, child in kids:
            if id not in ids:
                self._createType(parent, child['type'], id, **child)
            if child.get('children', {}) and id in ids:
                self.setupContent(getattr(parent, id), child['children'])
    
    def _createType(self, container, portal_type, id, **kwargs):
        """Helper method to create content objects"""
        ttool = getToolByName(container, 'portal_types')
        portal_catalog =  getToolByName(container, 'portal_catalog')
    
        fti = ttool.getTypeInfo(portal_type)
        fti.constructInstance(container, id, **kwargs)
        obj = getattr(container.aq_inner.aq_explicit, id)
    
        # publish and reindex
        #self._publish_item(portal, obj)
        portal_catalog.indexObject(obj)
        return obj
