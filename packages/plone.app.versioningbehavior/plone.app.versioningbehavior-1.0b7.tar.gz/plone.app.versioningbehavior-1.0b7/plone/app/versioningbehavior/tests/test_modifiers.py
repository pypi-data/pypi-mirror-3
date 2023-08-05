from Products.PloneTestCase import PloneTestCase
from plone.dexterity.fti import DexterityFTI
from plone.app.versioningbehavior.modifiers import CloneNamedFileBlobs
from unittest import TestSuite, makeSuite
from plone.namedfile.file import NamedBlobFile
from plone.namedfile import field
from plone.directives import form
from plone.dexterity.utils import createContentInContainer
from ZODB.interfaces import IBlob
from zope.interface import alsoProvides
from StringIO import StringIO
from zope.configuration import xmlconfig

PloneTestCase.setupPloneSite(
    extension_profiles=['plone.app.versioningbehavior:default'])


class IBlobFile(form.Schema):
        file = field.NamedBlobFile(title=u'File')
alsoProvides(IBlobFile, form.IFormFieldProvider)


class TestModifiers(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        # we need to have the Manager role to be able to add things
        # to the portal root
        self.setRoles(['Manager',])

    def testCloneNamedFileBlobsInSchema(self):
        file_fti = DexterityFTI(
            'BlobFile',
            model_source = """
            <model xmlns="http://namespaces.plone.org/supermodel/schema">
                <schema>
                    <field name="file" type="plone.namedfile.field.NamedBlobFile">
                        <title>File</title>
                        <required>True</required>
                    </field>
                </schema>
            </model>
        """)
        self.portal.portal_types._setObject('BlobFile', file_fti)

        file1 = createContentInContainer(self.portal, 'BlobFile')
        file1.file = NamedBlobFile('dummy test data', filename=u'test.txt')
        modifier = CloneNamedFileBlobs('modifier', 'Modifier')
        attrs_dict = modifier.getReferencedAttributes(file1)
        self.assertTrue(
            'plone.dexterity.schema.generated.plone_0_BlobFile.file'
            in attrs_dict)
        blob = attrs_dict.values()[0]
        self.assertTrue(IBlob.providedBy(blob))
        
        file2 = createContentInContainer(self.portal, 'BlobFile')
        file2.file = NamedBlobFile('dummy test data', filename=u'test.txt')
        modifier.reattachReferencedAttributes(file2, attrs_dict)
        self.assertTrue(file2.file._blob is blob)

    def testCloneNamedFileBlobsInBehavior(self):
        configuration = """\
        <configure
             package="plone.behavior"
             xmlns="http://namespaces.zope.org/zope"
             xmlns:plone="http://namespaces.plone.org/plone"
             i18n_domain="plone.behavior.tests">

             <include package="plone.behavior" file="meta.zcml" />

            <plone:behavior
                title="BlobFile behavior"
                description="A behavior"
                provides="plone.app.versioningbehavior.tests.test_modifiers.IBlobFile"
                factory="plone.behavior.AnnotationStorage"
                />
        </configure>
        """
        xmlconfig.xmlconfig(StringIO(configuration))

        file_fti = DexterityFTI(
            'BlobFile',
            behaviors = [IBlobFile.__identifier__])
        self.portal.portal_types._setObject('BlobFile', file_fti)

        file1 = createContentInContainer(self.portal, 'BlobFile')
        IBlobFile(file1).file = NamedBlobFile('dummy test data',
                                              filename=u'test.txt')
        modifier = CloneNamedFileBlobs('modifier', 'Modifier')
        attrs_dict = modifier.getReferencedAttributes(file1)
        self.assertTrue(
            'plone.app.versioningbehavior.tests.test_modifiers.IBlobFile.file'
            in attrs_dict)
        blob = attrs_dict.values()[0]
        self.assertTrue(IBlob.providedBy(blob))

        file2 = createContentInContainer(self.portal, 'BlobFile')
        IBlobFile(file2).file = NamedBlobFile('dummy test data',
                                              filename=u'test.txt')
        modifier.reattachReferencedAttributes(file2, attrs_dict)
        self.assertTrue(IBlobFile(file2).file._blob is blob)

    def testCloneNamedFileBlobsOnCloneModifiers(self):
        file_fti = DexterityFTI(
            'BlobFile',
            model_source = """
            <model xmlns="http://namespaces.plone.org/supermodel/schema">
                <schema>
                    <field name="file" type="plone.namedfile.field.NamedBlobFile">
                        <title>File</title>
                        <required>True</required>
                    </field>
                </schema>
            </model>
        """)
        self.portal.portal_types._setObject('BlobFile', file_fti)

        file1 = createContentInContainer(self.portal, 'BlobFile')
        file1.file = NamedBlobFile('dummy test data', filename=u'test.txt')
        modifier = CloneNamedFileBlobs('modifier', 'Modifier')
        pers_id, pers_load, empty1, empty2 = modifier.getOnCloneModifiers(file1)
        self.assertTrue(pers_id(file1.file._blob))
        self.assertTrue(pers_load(file1.file._blob) is None)
        self.assertTrue(empty1 == [])
        self.assertTrue(empty2 == [])

    def testCloneNamedFileBlobsWithNoFile(self):
        file_fti = DexterityFTI(
            'BlobFile',
            model_source = """
            <model xmlns="http://namespaces.plone.org/supermodel/schema">
                <schema>
                    <field name="file" type="plone.namedfile.field.NamedBlobFile">
                        <title>File</title>
                        <required>True</required>
                    </field>
                </schema>
            </model>
        """)
        self.portal.portal_types._setObject('BlobFile', file_fti)
        file1 = createContentInContainer(self.portal, 'BlobFile')
        modifier = CloneNamedFileBlobs('modifier', 'Modifier')
        attrs_dict = modifier.getReferencedAttributes(file1)
        self.assertTrue(attrs_dict=={})
        pers_id, pers_load, empty1, empty2 = modifier.getOnCloneModifiers(file1)
        self.assertTrue(pers_id(None) is None)
        self.assertTrue(pers_load(None) is None)
        self.assertTrue(empty1 == [])
        self.assertTrue(empty2 == [])

        # Previous version without file but working copy has a file.
        self.portal.portal_repository.save(file1)
        file1.file = NamedBlobFile('dummy test data', filename=u'test.txt')
        attrs_dict = modifier.getReferencedAttributes(file1)
        self.assertTrue(
            'plone.dexterity.schema.generated.plone_0_BlobFile.file'
            in attrs_dict)
        blob = attrs_dict.values()[0]
        self.assertTrue(IBlob.providedBy(blob))
        pers_id, pers_load, empty1, empty2 = modifier.getOnCloneModifiers(file1)
        self.assertTrue(pers_id(file1.file._blob))
        self.assertTrue(pers_load(file1.file._blob) is None)
        self.assertTrue(empty1 == [])
        self.assertTrue(empty2 == [])


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestModifiers))
    return suite
