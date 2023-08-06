#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009, Mathieu PASQUET <mpa@makina-corpus.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the <ORGANIZATION> nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import os.path

from collective.z3cform.grok.tests.base import collective_z3cform_grok_FunctionalTestCase

#######################################################################################
# IMPORT/DEFINE VARIABLES OR MODULES THERE
# THEY WILL BE AVAILABLE AS GLOBALS INSIDE YOUR DOCTESTS
#######################################################################################
# example:
# from for import bar
# and in your doctests, you can do:
# >>> bar.something
from collective.z3cform.grok.tests.utils import *
from collective.z3cform.grok.tests.globals import *
#######################################################################################

# stolen from five.grok.tests.doctest
def doctestToPython(filenameInput, filenameOutput):
    assert os.path.exists(filenameInput)
    docFileR = open(filenameInput, 'r')
    newLines = []
    originalLines = []
    for line in docFileR.readlines():
        originalLines.append(line)
        if '<<<' in line:
            match = re.match(re.compile('(\s+<<<\s)(.*)'), line)
            if match:
                grokCodeFlag = True
                newLines.append("%s\n" % match.groups()[1])
        elif '...' in line and grokCodeFlag == True:
            match = re.match(re.compile('(\s+\.\.\.\s)(.*)'), line)
            if match:
                newLines.append("%s\n" % match.groups()[1])
        elif '<<<' not in line or '...' not in line: # handle comments
            grokCodeFlag = False
            newLines.append('#%s' % line)

    docFileR.close()

    # backup old one as it could be source, do not override it!
    index = 0
    if os.path.exists(filenameOutput):
        dontstop = True
        while dontstop:
            saved = '%s.sav.%s' % (filenameOutput, index)
            if os.path.exists(saved): 
                index += 1
                continue
            else:
                os.rename(filenameOutput, saved)
                dontstop = False
        
    docFileW = open(filenameOutput, 'w')
    for newLine in newLines:
        if newLine.strip() != '#':
            docFileW.write('%s' % newLine)
        else:
            docFileW.write('\n')
    docFileW.close()

class DocTestCase(collective_z3cform_grok_FunctionalTestCase):
    # if you use sparse files, just set the base module from where are the txt files
    # otherwise it will be the 'tests' module parent from your classfile
    tested_module = None

    def setUp_hook(self, *args, **kwargs):
        """Override if you want in subclasses."""
        collective_z3cform_grok_FunctionalTestCase.setUp(self)

    def tearDown_hook(self, *args, **kwargs):
        """Override if you want in subclasses."""
        collective_z3cform_grok_FunctionalTestCase.tearDown(self)

    def reDoctestTize(self, testFile=None):
        """Helper to regenerate doctests while doing some pdb on tests, for reloading on the fly."""
        if not testFile:
            testFile = self.globs['test'].filename
        testFileDirName, testFullFileName = os.path.split(testFile)
        testFileName, testFileExt = os.path.splitext(testFullFileName)
        pythonTestFile = os.path.join(testFileDirName, testFileName + '.py') 
        doctestToPython(testFile, pythonTestFile)
        # cleanup the file on exit
        def filescleanup(files, *args, **kwargs):
            [os.remove(f)
             for f in files
             if os.path.exists(f)] 
        zope.testing.cleanup.addCleanUp(
            filescleanup,
            ([pythonTestFile, pythonTestFile+"c"],)
        ) 
        module_dotted_name = self.tested_module
        if not self.tested_module:
            module_dotted_name =  '.'.join(self.globs['test'].globs["__name__"].split('.')[:-1])
        dotted_name = "%s.%s" % (
            module_dotted_name,
            os.path.split(pythonTestFile)[1].replace('.py', ''))
        fgrok(dotted_name) 
        return pythonTestFile

def collective_z3cform_grok_setUp(self):
    """Using self here give us our testcase + its globs, 
    when we use the test without the setUp function, we do not have yet globs.
    """
    pythonTestFile = self.reDoctestTize()
    zope.component.eventtesting.setUp()
    # the first inherited method will win the right to configure the plone site :)
    # good for subclassing
    self.setUp_hook(pythonTestFile)
    #XXX this should be done by the GrokDocFileSuite
    from zope.traversing.adapters import DefaultTraversable
    zope.component.provideAdapter(DefaultTraversable, [None])
    self.portal.getSiteManager().registerAdapter(DefaultTraversable, [None]) 
    
def collective_z3cform_grok_tearDown(self):
    self.tearDown_hook()
    zope.testing.cleanup.cleanUp() 
    



