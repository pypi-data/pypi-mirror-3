from zope.interface import implements

from OFS.Image import File
from Products.ATContentTypes.content.image import ATImage
from Products.Archetypes.public import registerType
from Products.Archetypes.utils import shasattr

from Products.SimpleAttachment.config import PROJECTNAME
from Products.SimpleAttachment.interfaces import IImageAttachment


class ImageAttachment(ATImage):
    """An image attachment"""

    implements(IImageAttachment)

    portal_type = meta_type = 'ImageAttachment'

    def index_html(self, REQUEST, RESPONSE):
        """ download the file inline or as an attachment """
        field = self.getPrimaryField()
        if isinstance(field.get(self), File):
            return field.get(self).index_html(REQUEST, RESPONSE)
        return field.index_html(self, REQUEST, RESPONSE)

    def getFilename(self, key=None):
        """Returns the filename from a field.
        """
        if key is None:
            return self.getId()
        else:
            field = self.getField(key) or getattr(self, key, None)
            if field and shasattr(field, 'getFilename'):
                return field.getFilename(self)

registerType(ImageAttachment, PROJECTNAME)
