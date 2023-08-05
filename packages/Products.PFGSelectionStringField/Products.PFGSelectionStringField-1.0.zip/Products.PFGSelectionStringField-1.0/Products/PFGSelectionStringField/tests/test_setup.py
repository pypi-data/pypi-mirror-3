from Products.CMFCore.utils import getToolByName
from Products.PFGSelectionStringField.tests.base import IntegrationTestCase


class TestSetup(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

        self.catalog = getToolByName(self.portal, 'portal_catalog')
        self.types = getToolByName(self.portal, 'portal_types')
        self.wftool = getToolByName(self.portal, 'portal_workflow')
        self.content_types = [
            'PFGSelectionStringField',
        ]
        self.installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.skins = getToolByName(self.portal, 'portal_skins')
        self.properties = getToolByName(self.portal, 'portal_properties')
        self.site_properties = getattr(self.properties, 'site_properties')
        self.navtree_properties = getattr(self.properties, 'navtree_properties')

    def test_is_pfg_installed(self):
        self.failUnless(self.installer.isProductInstalled('PloneFormGen'))

    def test_is_pfg_selection_string_field_installed(self):
        self.failUnless(self.installer.isProductInstalled('PFGSelectionStringField'))

    def test_invokeFactory(self):
        from plone.app.testing import TEST_USER_ID
        from plone.app.testing import setRoles
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        import transaction
        transaction.commit()
        self.portal.invokeFactory(
            'FormFolder',
            'formfolder',
            title='Form Folder',
        )
        folder = self.portal.formfolder
        folder.invokeFactory(
            'PFGSelectionStringField',
            'field',
            title='Selection String Field',
        )

    def testSkinLayersInstalled(self):
        self.failUnless('PFGSelectionStringField' in self.skins.objectIds())

    ## Content Types
    def test_contents_installed(self):
        for type in self.content_types:
            self.failUnless(type in self.types.objectIds())

    def test_PFGSelectionStringField_content_type(self):
        item = self.types.getTypeInfo('PFGSelectionStringField')
        self.assertEquals('Selection String Field', item.title)
        self.assertEquals('Selection String Field', item.description)
        self.assertEquals('PFGSelectionStringField', item.content_meta_type)
        self.assertEquals('addPFGSelectionStringField', item.factory)
        self.assertEquals('fg_base_view_p3', item.immediate_view)
        self.assertEquals(False, item.global_allow)
        self.assertEquals(False, item.filter_content_types)
        self.assertEquals((), item.allowed_content_types)
        self.assertEquals('fg_base_view_p3', item.default_view)
        self.assertEquals(('fg_base_view_p3',), item.view_methods)
        aliases = {'edit': 'atct_edit', 'sharing': '@@sharing', '(Default)': '(dynamic view)', 'view': '(selected layout)'}
        self.assertEquals(aliases, item.getMethodAliases())
        self.assertEquals(
            [
                ('View', 'view', 'string:${object_url}/view', True, (u'View',)),
                ('Edit', 'edit', 'string:${object_url}/edit', True, (u'Modify portal content',))
            ],
            [
                (action.title, action.id, action.getActionExpression(), action.visible, action.permissions) for action in item.listActions()
            ]
        )

    ## site_properties
    def test_not_searchable(self):
        self.failUnless('PFGSelectionStringField' in self.site_properties.getProperty('types_not_searched'))

    def test_use_folder_tabs(self):
        self.failUnless('PFGSelectionStringField' not in self.site_properties.getProperty('use_folder_tabs'))

    def test_typesLinkToFolderContentsInFC(self):
        self.failUnless('PFGSelectionStringField' not in self.site_properties.getProperty('typesLinkToFolderContentsInFC'))

    ## navtree_properties
    def test_not_in_navtree(self):
        self.failUnless('PFGSelectionStringField' in self.navtree_properties.getProperty('metaTypesNotToList'))

    # Workflow
    def test_workflow(self):
        self.assertEquals((), self.wftool.getChainForPortalType('PFGSelectionStringField'))
