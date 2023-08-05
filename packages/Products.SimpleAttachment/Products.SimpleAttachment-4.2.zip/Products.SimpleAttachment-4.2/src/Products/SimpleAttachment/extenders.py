from zope.component import adapts
from zope.interface import implements

from archetypes.schemaextender.interfaces import ISchemaExtender
from plone.app.blob.subtypes.file import ExtensionBlobField as FileField
from plone.app.blob.subtypes.image import ExtensionBlobField as ImageField

from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import FileWidget
from Products.Archetypes.atapi import ImageWidget
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes import ATCTMessageFactory as _
from Products.validation import V_REQUIRED

from Products.SimpleAttachment.interfaces import IFileAttachment
from Products.SimpleAttachment.interfaces import IImageAttachment


class FileBlobAttachment(object):
    adapts(IFileAttachment)
    implements(ISchemaExtender)

    fields = [
        FileField('file',
            required=True,
            primary=True,
            searchable=True,
            accessor='getFile',
            mutator='setFile',
            index_method='getIndexValue',
            languageIndependent=True,
            storage=AnnotationStorage(migrate=True),
            default_content_type='application/octet-stream',
            validators=(('isNonEmptyFile', V_REQUIRED),
                          ('checkFileMaxSize', V_REQUIRED)),
            widget=FileWidget(label=_(u'label_file', default=u'File'),
                                description=_(u''),
                                show_content_type=False,)),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


class ImageBlobAttachment(object):
    adapts(IImageAttachment)
    implements(ISchemaExtender)

    fields = [
        ImageField('image',
            required=True,
            primary=True,
            accessor='getImage',
            mutator='setImage',
            sizes=None,
            languageIndependent=True,
            storage=AnnotationStorage(migrate=True),
            swallowResizeExceptions=zconf.swallowImageResizeExceptions.enable,
            pil_quality=zconf.pil_config.quality,
            pil_resize_algo=zconf.pil_config.resize_algo,
            original_size=None,
            max_size=zconf.ATImage.max_image_dimension,
            default_content_type='image/png',
            allowable_content_types=('image/gif', 'image/jpeg', 'image/png'),
            validators=(('isNonEmptyFile', V_REQUIRED),
                          ('checkImageMaxSize', V_REQUIRED)),
            widget=ImageWidget(label=_(u'label_image', default=u'Image'),
                                 description=_(u''),
                                 show_content_type=False,)),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
