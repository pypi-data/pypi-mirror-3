import os
from Acquisition import aq_base
from App.class_init import InitializeClass
from itertools import izip
from plone.dexterity.utils import iterSchemata, resolveDottedName
from plone.namedfile.interfaces import INamedBlobFileField
from plone.namedfile.interfaces import INamedBlobImageField
from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.interfaces.IArchivist import ArchivistRetrieveError
from Products.CMFEditions.interfaces.IModifier import IAttributeModifier
from Products.CMFEditions.interfaces.IModifier import ICloneModifier
from Products.CMFEditions.Modifiers import ConditionalTalesModifier
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from ZODB.blob import Blob
from zope.interface import implements
from zope.schema import getFields


manage_CloneNamedFileBlobsAddForm =  \
    PageTemplateFile('www/CloneNamedFileBlobs.pt',
                   globals(),
                   __name__='manage_CloneNamedFileBlobs')


def manage_addCloneNamedFileBlobs(self, id, title=None, REQUEST=None):
    """Add a clone namedfile blobs modifier.
    """
    modifier = CloneNamedFileBlobs(id, title)
    self._setObject(id, modifier)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')


class CloneNamedFileBlobs:
    """Modifier to save an un-cloned reference to the blob to avoid it being
    packed away.
    """

    implements(IAttributeModifier, ICloneModifier)

    def __init__(self, id_, title):
        self.id = str(id_)
        self.title = str(title)

    def getReferencedAttributes(self, obj):
        file_data = {}
        # Try to get last revision, only store a new blob if the
        # contents differ from the prior one, otherwise store a
        # reference to the prior one.
        # The implementation is mostly based on CMFEditions's CloneBlobs
        # modifier.
        repo = getToolByName(obj, 'portal_repository')
        try:
            prior_rev = repo.retrieve(obj)
        except ArchivistRetrieveError:
            prior_rev = None

        for schemata in iterSchemata(obj):
            for name, field in getFields(schemata).items():
                if (INamedBlobFileField.providedBy(field) or
                    INamedBlobImageField.providedBy(field)):
                    field_value = field.get(field.interface(obj))
                    if field_value is None:
                        continue
                    blob_file = field_value.open()
                    save_new = True
                    dotted_name = '.'.join([schemata.__identifier__, name])

                    if prior_rev is not None:
                        prior_obj = prior_rev.object
                        prior_blob = field.get(field.interface(prior_obj))
                        prior_file = prior_blob.open()

                        # Check for file size differences
                        if (os.fstat(prior_file.fileno()).st_size ==
                            os.fstat(blob_file.fileno()).st_size):
                            # Files are the same size, compare line by line
                            for line, prior_line in izip(blob_file,
                                                         prior_file):
                                if line != prior_line:
                                    break
                            else:
                                # The files are the same, save a reference
                                # to the prior versions blob on this version
                                file_data[dotted_name] = prior_blob._blob
                                save_new = False

                    if save_new:
                        new_blob = file_data[dotted_name] = Blob()
                        new_blob_file = new_blob.open('w')
                        try:
                            blob_file.seek(0)
                            new_blob_file.writelines(blob_file)
                        finally:
                            blob_file.close()
                            new_blob_file.close()

        return file_data

    def reattachReferencedAttributes(self, obj, attrs_dict):
        obj = aq_base(obj)
        for name, blob in attrs_dict.iteritems():
            iface = resolveDottedName('.'.join(name.split('.')[:-1]))
            fname = name.split('.')[-1]
            field = iface.get(fname)
            field.get(iface(obj))._blob = blob

    def getOnCloneModifiers(self, obj):
        """Removes references to blobs.
        """
        blob_refs = {}
        for schemata in iterSchemata(obj):
            for name, field in getFields(schemata).items():
                if (INamedBlobFileField.providedBy(field) or
                    INamedBlobImageField.providedBy(field)):
                    field_value = field.get(field.interface(obj))
                    if field_value is not None:
                        blob_refs[id(aq_base(field_value._blob))] = True

        def persistent_id(obj):
            return blob_refs.get(id(obj), None)

        def persistent_load(obj):
            return None

        return persistent_id, persistent_load, [], []

InitializeClass(CloneNamedFileBlobs)


modifiers = (
    {
        'id': 'CloneNamedFileBlobs',
        'title': "Store blobs by reference on content",
        'enabled': True,
        'condition': "python:True",
        'wrapper': ConditionalTalesModifier,
        'modifier': CloneNamedFileBlobs,
        'form': manage_CloneNamedFileBlobsAddForm,
        'factory': manage_addCloneNamedFileBlobs,
        'icon': 'www/modifier.gif',
    },
)
