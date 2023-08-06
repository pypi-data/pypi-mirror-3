import os
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from kss.core.tests.ecmaview import EcmaView as base

def absolute_dir(path):
    here = os.path.split(globals()['__file__'])[0]
    return os.path.abspath(os.path.join(here, path))

class EcmaView(base):
    '''quintagroup.plonetabs js test view
    
    This allows the runner.html to be used on this view.

    This provides the tests run with the compiled kukit.js
    resource, in the same way as they would be run
    in production with kss.
    '''

    _testdir = absolute_dir('js')

    _runner = ViewPageTemplateFile('js/runner.html')
