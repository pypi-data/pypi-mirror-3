from plone.i18n.normalizer.interfaces import IUserPreferredFileNameNormalizer
from zope.publisher.browser import BrowserView


class FilenameNormalizer(BrowserView):

    def __call__(self, filename):
        return IUserPreferredFileNameNormalizer(self.request).normalize(filename)
