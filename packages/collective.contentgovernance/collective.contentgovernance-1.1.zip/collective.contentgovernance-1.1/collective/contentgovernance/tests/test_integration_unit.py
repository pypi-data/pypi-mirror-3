import unittest2 as unittest
from collective.contentgovernance.testing  import CG_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName


class TestResponsiblePerson(unittest.TestCase):

    layer = CG_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        self.folder = portal['test-folder']

    def test_responsiblepersonindex(self):
        """ check whether the 'responsibleperson' index has been added to the
            catalog """
        catalog = getToolByName(self.folder, 'portal_catalog')
        self.failUnless('responsibleperson' in catalog.indexes())

    def test_responsiblepersonfield_available(self):
        """ Test that we have managed to inject the responsibleperson field
            in objects"""

        self.folder.invokeFactory('Document', 'my-page')
        doc = getattr(self.folder, 'my-page')
        self.failUnless('responsibleperson' in doc.Schema())

    def test_responsiblepersonfield_stored(self):
        """ Test that we can update the resposible person field and that
            its value is getting stored """

        doc = self.folder.invokeFactory('Document', 'my-page',
                                        responsibleperson='foobar')
        doc = getattr(self.folder, 'my-page')
        field = doc.Schema().getField('responsibleperson')
        field.set(doc, 'foobar')
        self.assertEqual(field.get(doc), 'foobar')

    def test_ownership_changed(self):
        doc = self.folder.invokeFactory('Document', 'my-page',
                                        responsibleperson='foobar')
        doc = getattr(self.folder, 'my-page')
        self.assertEqual(['foobar'], doc.users_with_local_role('Owner'))

    def test_responsiblepersonfield_indexed_in_catalog(self):
        self.folder.invokeFactory('Document', 'my-page',
                                  responsibleperson='foobar')
        catalog = getToolByName(self.folder, 'portal_catalog')
        results = catalog.searchResults(responsibleperson='foobar')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, 'my-page')
