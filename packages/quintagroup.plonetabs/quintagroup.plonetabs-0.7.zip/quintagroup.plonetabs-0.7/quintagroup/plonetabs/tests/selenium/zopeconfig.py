from zope.interface import implements

from kss.demo import KSSSeleniumTestSuite, KSSSeleniumTestDirectory, \
    KSSSeleniumTestCase

from plone.app.kss.demo.zopeconfig import PloneSiteLayer, \
    LoggedInManagerLayer, LoggedInUserLayer, IResource


#
# XXX Important message to developers
#
# Dear Developer! Do _not_ use the setup you see below as an example
# for your own programs, or otherwise you will need to change
# it later. The test suite creation interface will change in
# the next kss.demo versions. The plugin class (PloneDemos) 
# will change in the next major KSS (and possibly Plone) version. 
# This configuration file will be kept up-to-date to these changes.
#
# It is safe, however, to fix existing tests or drop new
# tests in the directories set up below.
#

class PortalTabsLayer(LoggedInManagerLayer):
    setup = KSSSeleniumTestCase('install-tabs.html')
    teardown = KSSSeleniumTestCase('uninstall-tabs.html')

class PloneTabsSeleniumKssTests(object):
    implements(IResource)

    demos = ()

    selenium_tests = (
        KSSSeleniumTestSuite(
            tests = KSSSeleniumTestDirectory('selenium_tests/run_as_testmanager'),
            layer = PortalTabsLayer,
            component = 'quintagroup.plonetabs',
            application = 'quintagroup.plonetabs',
        ),
    )
