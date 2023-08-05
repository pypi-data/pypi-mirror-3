'''
Created on 07.09.2011

@author: peterm
'''
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.contentmigration.migrator import BaseInlineMigrator
from Products.contentmigration.walker import CustomQueryWalker
from StringIO import StringIO
from plone.app.blob.migrations import migrate
from transaction import savepoint
from zope.component._api import getMultiAdapter


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


def migrate_to_blob_storage(portal_setup):
    out = StringIO()
    utool = getToolByName(portal_setup, 'portal_url')
    portal = utool.getPortalObject()

    print >> out, "migrate FileAttachments..."
    print >> out, migrateSimpleAttachment(portal, FileAttachmentMigrator)
    print >> out, "migrate ImageAttachments..."
    print >> out, migrateSimpleAttachment(portal, ImageAttachmentMigrator)
    return out.getvalue()


class SimpleAttachmentMigrationView(BrowserView):

    def migrate(self):
        migrate_to_blob_storage(self.context)
