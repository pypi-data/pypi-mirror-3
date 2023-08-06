"""
    Functional tests - collects all *.txt files
"""

import os
import glob
from zope.testing import doctest
import unittest
from Globals import package_home
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from base import FunctionalTestCase

GLOBALS = globals()


UNITTESTS = []

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_ONLY_FIRST_FAILURE)


class TestExtended(FunctionalTestCase):
    """ Tests the extentions profile for better performance.  """
    
    def afterSetUp(self):
        """ Load the extension profile """
        self.addProfile('betahaus.emaillogin:exdended')
        
    
def list_doctests():
    home = package_home(GLOBALS)
    return [filename for filename in
            glob.glob(os.path.sep.join([home, '*.txt']))
            if os.path.basename(filename) not in UNITTESTS]

def test_suite():
    filenames = list_doctests()

    test_suites = []
    for testclass in [FunctionalTestCase, TestExtended]:
        test_suites.extend(
                           [Suite(os.path.basename(filename),
                                  optionflags=OPTIONFLAGS,
                                  package='betahaus.emaillogin.tests',
                                  test_class=testclass)
                                  for filename in filenames])

    return unittest.TestSuite(test_suites)

