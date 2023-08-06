# -*- coding: utf-8 -*-

from zope.component import getMultiAdapter

from collective.analyticspanel.testing import ANALYTICS_PANEL_INTEGRATION_TESTING
from collective.analyticspanel.pair_fields import ErrorCodeValuePair, SitePathValuePair

from collective.analyticspanel.browser.viewlet import AnalyticsViewlet

from base import BaseTestCase

class TestViewlet(BaseTestCase):

    layer = ANALYTICS_PANEL_INTEGRATION_TESTING

    def test_viewlet_registered(self):
        portal = self.layer['portal']
        request = self.layer['request']
        self.markRequestWithLayer()
        request.set('ACTUAL_URL', 'http://nohost/plone')
        self.getSettings().general_code = u'SITE ANALYTICS'
        self.assertTrue('SITE ANALYTICS' in portal())

# Do not run this test until p.a.testing will not fix https://dev.plone.org/ticket/11673
#    def test_back_base_viewlet(self):
#        portal = self.layer['portal']
#        applyProfile(portal, 'collective.analyticspanel:uninstall')
#        self.assertTrue('SITE DEFAULT ANALYTICS' in portal())

    def test_not_found(self):
        portal = self.layer['portal']
        request = self.layer['request']
        request.set('ACTUAL_URL', 'http://nohost/plone')
        self.markRequestWithLayer()
        settings = self.getSettings()

        record = ErrorCodeValuePair()
        record.message = 'NotFound'
        record.message_snippet = u'You are in a NotFound page'

        settings.error_specific_code += (record,)
        request.set('error_type', 'NotFound')
        view = getMultiAdapter((portal, request), name=u"sharing")
        self.assertTrue('You are in a NotFound page' in view())

    def test_for_path(self):
        portal = self.layer['portal']
        portal.invokeFactory(type_name='Folder', id='news', title="News")
        request = self.layer['request']
        request.set('ACTUAL_URL', 'http://nohost/plone/news')
        self.markRequestWithLayer()
        settings = self.getSettings()

        record = SitePathValuePair()
        record.path = u'/news'
        record.path_snippet = u'You are in the News section'
        settings.path_specific_code += (record,)

        self.assertTrue('You are in the News section' in portal.news())
        request.set('ACTUAL_URL', 'http://nohost/plone')
        self.assertFalse('You are in the News section' in portal())

    def test_most_specific_path_used(self):
        portal = self.layer['portal']
        portal.invokeFactory(type_name='Folder', id='news', title="News")
        portal.news.invokeFactory(type_name='Folder', id='subnews', title="Subfolder inside news")

        request = self.layer['request']
        request.set('ACTUAL_URL', 'http://nohost/plone/news')
        self.markRequestWithLayer()
        settings = self.getSettings()

        record1 = SitePathValuePair()
        record1.path = u'/news'
        record1.path_snippet = u'You are in the News section'
        record2 = SitePathValuePair()
        record2.path = u'/news/subnews'
        record2.path_snippet = u'You are in the Subnews section'
        settings.path_specific_code += (record1, record2)

        request.set('ACTUAL_URL', 'http://nohost/plone/news')
        self.assertTrue('You are in the Subnews section' in portal.news.subnews())

    def test_hiding_code(self):
        portal = self.layer['portal']
        portal.invokeFactory(type_name='Folder', id='news', title="News")

        request = self.layer['request']
        request.set('ACTUAL_URL', 'http://nohost/plone/news')
        self.markRequestWithLayer()
        settings = self.getSettings()

        self.assertTrue('SITE DEFAULT ANALYTICS' in portal.news())

        record = SitePathValuePair()
        record.path = u'/news'
        record.path_snippet = u''
        settings.path_specific_code += (record,)

        self.assertFalse('SITE DEFAULT ANALYTICS' in portal.news())

class TestViewletPathCleanup(BaseTestCase):
    
    layer = ANALYTICS_PANEL_INTEGRATION_TESTING
    
    def getViewlet(self):
        portal = self.layer['portal']
        request = self.layer['request']        
        return AnalyticsViewlet(portal, request, None, None)

    def test_add_starting_slash(self):
        viewlet = self.getViewlet()
        self.assertEquals(viewlet.cleanup_path('plone/foo'), '/plone/foo')

    def test_add_starting_portalid(self):
        viewlet = self.getViewlet()
        self.assertEquals(viewlet.cleanup_path('/foo'), '/plone/foo')

    def test_add_starting_portalid_and_slash(self):
        viewlet = self.getViewlet()
        self.assertEquals(viewlet.cleanup_path('foo'), '/plone/foo')

    def test_remove_trailing_slash(self):
        viewlet = self.getViewlet()
        self.assertEquals(viewlet.cleanup_path('/foo/bar/'), '/plone/foo/bar')
