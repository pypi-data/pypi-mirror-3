from logging import getLogger

from plone.app.blob.interfaces import IATBlobImage
from zope.interface import implements

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from OFS.Image import File
from Products.ATContentTypes.content.file import ATFile
from Products.Archetypes.public import registerType
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError

from Products.SimpleAttachment.config import PROJECTNAME
from Products.SimpleAttachment.interfaces import IFileAttachment

debug = getLogger(__name__).debug
schema = ATFile.schema.copy()


class FileAttachment(ATFile):
    """A file attachment"""

    implements(IFileAttachment)

    portal_type = meta_type = 'FileAttachment'
    schema = schema
    security = ClassSecurityInfo()

    security.declarePrivate('getIndexValue')
    def getIndexValue(self, mimetype='text/plain'):
        """Copy/paste from plone.app.blob
        """
        field = self.getPrimaryField()
        source = field.getContentType(self)
        transforms = getToolByName(self, 'portal_transforms')
        if transforms._findPath(source, mimetype) is None:
            return ''
        value = str(field.get(self))
        filename = field.getFilename(self)
        try:
            return str(transforms.convertTo(mimetype, value,
                mimetype=source, filename=filename))
        except (ConflictError, KeyboardInterrupt):
            raise
        except:
            getLogger(__name__).exception('exception while trying to convert '
               'blob contents to "text/plain" for %r', self)

    security.declareProtected('View', 'index_html')
    def index_html(self, REQUEST, RESPONSE):
        """ download the file inline or as an attachment """
        field = self.getPrimaryField()
        if isinstance(field.get(self), File):
            return field.get(self).index_html(REQUEST, RESPONSE)
        if IATBlobImage.providedBy(self):
            return field.index_html(self, REQUEST, RESPONSE)
        elif field.getContentType(self) in ATFile.inlineMimetypes:
            return field.index_html(self, REQUEST, RESPONSE)
        else:
            return field.download(self, REQUEST, RESPONSE)

    def getFilename(self, key=None):
        """Returns the filename from a field.
        """
        if key is None:
            raw = self.getPrimaryField().getRaw(self)
            filename = getattr(aq_base(raw), 'filename', None)
            if filename:
                return filename
            return self.getId()
        else:
            field = self.getField(key) or getattr(self, key, None)
            if field and shasattr(field, 'getFilename'):
                return field.getFilename(self)

registerType(FileAttachment, PROJECTNAME)
