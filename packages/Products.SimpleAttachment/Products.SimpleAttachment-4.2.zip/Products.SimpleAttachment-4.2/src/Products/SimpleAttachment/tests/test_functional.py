"""
    SimpleAttachment functional doctests.  This module collects all *.txt
    files in the tests directory and runs them.

    Based partly on test_functional.py from CMFPlone and the test tutorial:
    http://plone.org/documentation/tutorial/testing/doctests

"""
import os
import glob
import doctest
import unittest
from Globals import package_home
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

from Products.SimpleAttachment.tests import GLOBALS
from Products.SimpleAttachment.tests.base import FunctionalTestCase

OPTIONFLAGS = (
    doctest.ELLIPSIS |
    doctest.NORMALIZE_WHITESPACE
)


def list_doctests():
    home = package_home(GLOBALS)
    return [filename for filename in
          glob.glob(os.path.sep.join([home, '*.txt']))]


def test_suite():
    filenames = list_doctests()
    suites = [Suite(os.path.basename(filename),
               optionflags=OPTIONFLAGS,
               package='Products.SimpleAttachment.tests',
               test_class=FunctionalTestCase)
              for filename in filenames]
    return unittest.TestSuite(suites)
