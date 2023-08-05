from Products.PFGSelectionStringField.tests.base import FUNCTIONAL_TESTING
from Testing import ZopeTestCase as ztc
from hexagonit.testing.browser import Browser
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.testing import layered
from zope.testing import renormalizing

import doctest
import manuel.codeblock
import manuel.doctest
import manuel.testing
import re
import transaction
import unittest2 as unittest


FLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS | doctest.REPORT_NDIFF | doctest.REPORT_ONLY_FIRST_FAILURE

CHECKER = renormalizing.RENormalizing([
    # Normalize the generated UUID values to always compare equal.
    (re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'), '<UUID>'),
])


def setUp(self):
    layer = self.globs['layer']
    self.globs.update({
        'portal': layer['portal'],
        'portal_url': layer['portal'].absolute_url(),
        'browser': Browser(layer['app']),
    })
    ztc.utils.setupCoreSessions(layer['app'])
    portal = self.globs['portal']
    browser = self.globs['browser']
    portal_url = self.globs['portal_url']
    browser.setBaseUrl(portal_url)

    browser.handleErrors = True
    portal.error_log._ignored_exceptions = ()

    setRoles(portal, TEST_USER_ID, ['Manager'])

    from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
    basic = 'Basic {0}:{1}'.format(TEST_USER_NAME, TEST_USER_PASSWORD)
    browser.setHeader('Authorization', basic)

    # Create Form Folder
    portal.invokeFactory(
        'FormFolder',
        'form',
        title="Form Folder",
    )
    form = portal.form
    form_url = form.absolute_url()
    self.globs.update(
        {
            'form': form,
            'form_url': form_url,
        }
    )
    for key in form.keys():
        del form[key]
    form.thanksPage = ''
    form.reindexObject()

    transaction.commit()


def DocFileSuite(testfile, flags=FLAGS, setUp=setUp, layer=FUNCTIONAL_TESTING):
    """Returns a test suite configured with a test layer.

    :param testfile: Path to a doctest file.
    :type testfile: str

    :param flags: Doctest test flags.
    :type flags: int

    :param setUp: Test set up function.
    :type setUp: callable

    :param layer: Test layer
    :type layer: object

    :rtype: `manuel.testing.TestSuite`
    """
    m = manuel.doctest.Manuel(optionflags=flags, checker=CHECKER)
    m += manuel.codeblock.Manuel()

    return layered(
        manuel.testing.TestSuite(m, testfile, setUp=setUp, globs=dict(layer=layer)),
        layer=layer)


def test_suite():
    return unittest.TestSuite([
        DocFileSuite('functional/content_types_functional.txt'),
        ])
