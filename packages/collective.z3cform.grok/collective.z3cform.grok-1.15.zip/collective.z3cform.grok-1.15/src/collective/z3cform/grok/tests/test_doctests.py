"""
Launching all doctests in a specific directory
"""
import unittest
import doctest
import os.path
from Globals import package_home
from Testing import ZopeTestCase as ztc
from Products.CMFCore.utils import getToolByName

from collective.z3cform.grok.tests.base import (
    collective_z3cform_grok_TestCase,
    collective_z3cform_grok_FunctionalTestCase
)

# try to import, but not fail as we can do without (for example in a thirdparty which adapt the testcase)
try: from collective.z3cform.grok.app_config import GLOBALS
except:pass
try: from collective.z3cform.grok.app_config import PRODUCT_DEPENDENCIES
except:pass
try: from collective.z3cform.grok.app_config import SKIN
except:pass
try:from collective.z3cform.grok.tests_tools import getWorkflows
except:pass 
try:from portal_properties import check_portal_properties
except:pass
try:from portal_mailhost import check_portal_mailhost 
except:pass

# utilities and basic variables/options
# if you have plone.reload out there add an helper to use in doctests while programming
# just use preload(module) in pdb :)
# it would be neccessary for you to precise each module to reload, this method is also not recursive.
# eg: (pdb) from foo import bar;preload(bar)
# see utils.py for details
from collective.z3cform.grok.tests.utils import *

#######################################################################################
# IMPORT/DEFINE VARIABLES OR MODULES THERE or inside ./user_globals.py (better)
# THEY WILL BE AVAILABLE AS GLOBALS INSIDE YOUR DOCTESTS
#######################################################################################
# example:
# from for import bar
# and in your doctests, you can do:
# >>> bar.something
from collective.z3cform.grok.tests.globals import *
try:from collective.z3cform.grok.tests.user_globals import *
except:pass
#######################################################################################


# default test case, to regenerate all the test infrastructure without loosing this test, 
# just copy/edit this class in user_testcase.py/DocTestCase
class DocTestCase(collective_z3cform_grok_FunctionalTestCase):
    """Base functional doctestcase
    Think that you have a reference to the tested file in self.testref
    """

    def afterSetUp(self):
        """."""
        collective_z3cform_grok_FunctionalTestCase.afterSetUp(self)
        # add some specific setUp stuff there
        # myfoovar = 1
        # def iamacleanup(myvar, *args, **kwargs):
        #      print "i clean nothing but i know that myvar == %s " % myvar              
        # zope.testing.cleanup.addCleanUp(iamacleanup, myfoovar)

    def tearDown(self):
        collective_z3cform_grok_FunctionalTestCase.tearDown(self)
        # add some specific tearDown stuff there.
        # zope.testing.cleanup.cleanUp()

def collective_z3cform_grok_setUp(test):pass
def collective_z3cform_grok_tearDown(test):pass 

#######################################################################################
#You can even launch doctests from others packages with the grok setup with embedding this test suite
#You can even add others globals in those tests.
#No need to copy and duplicate this file, it is useless.
#######################################################################################
#Example : This snippet will launch all txt doctests in the other package directory
# cat someother/package/src/package/tests/tests_docs.py
#from collective.z3cform.grok.tests.test_setup import test_doctests_suite as ts
#def test_suite():
#    globs = globals()
#    return ts(__file__, globs)


#######################################################################################
# try to use user specific test cases found in:
#    -  collective.z3cform.grok.tests.user_testcase
# Otherwise take the above default
# As we do not touch to this user_testcase.py with the initial generation, it permits to regenerate
# the test infractructure when this paster is updated and to get its new features without
# overring exsiting special stuff
#######################################################################################
try:from collective.z3cform.grok.tests.user_testcase import DocTestCase
except:pass
try:from collective.z3cform.grok.tests.user_testcase import collective_z3cform_grok_setUp
except:pass
try:from collective.z3cform.grok.tests.user_testcase import collective_z3cform_grok_tearDown 
except:pass

def test_doctests_suite(directory=None, globs=None, suite=None, testklass=None):
    if not testklass: testklass=DocTestCase
    if not directory:
        directory, _f = os.path.split(os.path.abspath(__file__))
    elif os.path.isfile(directory):
        directory = os.path.dirname(directory)
    files = [os.path.join(directory, f) 
             for f in os.listdir(directory)
             if f.endswith('.txt')]
    if not globs:
        globs={}
    g = globals()
    for key in g:
        globs.setdefault(key, g[key])
    directory = directory

    if not suite:
        suite = unittest.TestSuite()
    if files:
        options = doctest.REPORT_ONLY_FIRST_FAILURE |\
                  doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
        for test in files:
            ft = ztc.ZopeDocFileSuite(
                test,
                test_class=testklass,
                optionflags=options,
                globs=globs,
                setUp=collective_z3cform_grok_setUp,
                tearDown=collective_z3cform_grok_tearDown,
                module_relative = False,
            )
            suite.addTest(ft)
    return suite

def test_suite():
    """."""
    suite = unittest.TestSuite()
    return test_doctests_suite(suite=suite)

# vim:set ft=python:
