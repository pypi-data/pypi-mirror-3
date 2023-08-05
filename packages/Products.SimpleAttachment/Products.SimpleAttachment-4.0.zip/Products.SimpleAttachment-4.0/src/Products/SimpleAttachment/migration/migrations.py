'''
Created on 07.09.2011

@author: peterm
'''
from Products.Five.browser import BrowserView
from StringIO import StringIO
from plone.app.blob.migrations import migrate
from zope.component._api import getMultiAdapter
from Products.contentmigration.migrator import BaseInlineMigrator
from Products.CMFCore.utils import getToolByName
from Products.contentmigration.walker import CustomQueryWalker
from transaction import savepoint


class FileAttachmentMigrator(BaseInlineMigrator):

    src_portal_type = 'FileAttachment'
    src_meta_type = 'FileAttachment'
    dst_portal_type = 'FileAttachment'
    dst_meta_type = 'FileAttachment'

    fields_map = {
        'file': None,
    }

    def migrate_data(self):
        oldfield = self.obj.getField('file')
        f = oldfield.get(self.obj)
        oldfield.getMutator(self.obj)(f)

    def last_migrate_reindex(self):
        self.obj.reindexObject()


class ImageAttachmentMigrator(BaseInlineMigrator):

    src_portal_type = 'ImageAttachment'
    src_meta_type = 'ImageAttachment'
    dst_portal_type = 'ImageAttachment'
    dst_meta_type = 'ImageAttachment'

    fields_map = {
        'image': None,
    }

    def migrate_data(self):
        oldfield = self.obj.getField('image')
        if hasattr(oldfield, 'removeScales'):
            # clean up old image scales
            oldfield.removeScales(self.obj)
        f = oldfield.get(self.obj)
        oldfield.getMutator(self.obj)(f)

    def last_migrate_reindex(self):
        self.obj.reindexObject()



def migrateSimpleAttachment(portal, migrator):
    walker = CustomQueryWalker(portal, migrator, full_transaction=True)
    savepoint(optimistic=True)
    walker.go()
    return walker.getOutput()


class SimpleAttachmentMigrationView(BrowserView):

    def migrate(self):
        out = StringIO()
        portal = getMultiAdapter((self.context, self.request),
                                  name="plone_portal_state").portal()

        print >> out, "migrated FileAttachments"
        print >> out, migrateSimpleAttachment(portal, FileAttachmentMigrator)
        print >> out, "migrated ImageAttachments"
        print >> out, migrateSimpleAttachment(portal, ImageAttachmentMigrator)
        return out.getvalue()
