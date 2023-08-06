import unittest
from plone.app.redirector.tests.base import RedirectorTestCase

from zope.component import getUtility, getMultiAdapter
from plone.app.redirector.interfaces import IRedirectionStorage


class TestRedirectorView(RedirectorTestCase):
    """Ensure that the redirector view behaves as expected.
    """

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Folder', 'testfolder')
        self.folder = self.portal.testfolder
        self.storage = getUtility(IRedirectionStorage)

    def view(self, context, actual_url, query_string=''):
        request = self.app.REQUEST
        request['ACTUAL_URL'] = actual_url
        request['QUERY_STRING'] = query_string
        return getMultiAdapter((context, request), name='plone_redirector_view')

    def test_attempt_redirect_with_known_url(self):
        fp = '/'.join(self.folder.getPhysicalPath())
        fu = self.folder.absolute_url()
        self.storage.add(fp + '/foo', fp + '/bar')
        view = self.view(self.portal, fu + '/foo')
        self.assertEquals(True, view.attempt_redirect())
        self.assertEquals(301, self.app.REQUEST.response.getStatus())
        self.assertEquals(fu + '/bar', self.app.REQUEST.response.getHeader('location'))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRedirectorView))
    return suite
