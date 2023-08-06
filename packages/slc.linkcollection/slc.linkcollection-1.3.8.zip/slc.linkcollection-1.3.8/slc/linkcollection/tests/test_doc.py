import os
import unittest

from zope.testing import doctest
from zope.component import testing
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import PloneSite
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase.layer import onsetup
from Globals import package_home
from slc.linkcollection import GLOBALS


class LinkCollectionFunctionalTestCase(PloneTestCase.PloneTestCase):
    pass

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

PloneTestCase.setupPloneSite()

def test_suite():
    home = package_home(GLOBALS)
    print home + '/README.txt',
    return unittest.TestSuite([

        Suite(
           'README.txt',
           optionflags=OPTIONFLAGS,
           package='slc.linkcollection',
           test_class=LinkCollectionFunctionalTestCase
           ),

        ])
