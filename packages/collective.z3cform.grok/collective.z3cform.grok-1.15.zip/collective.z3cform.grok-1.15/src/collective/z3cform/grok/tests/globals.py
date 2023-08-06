#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################################################
# ADD GLOBALS TO BE USED Inside your doctests there
##########################################################################################

import os
import re
from copy import deepcopy
from pprint import pprint  
cwd = os.path.dirname(__file__)
try:
    from Products.Five.testbrowser import Browser
    browser = Browser()
except:pass
try:import zope
except:pass
try:from zope.interface.verify import verifyObject
except:pass  
try:import collective
except:pass
try:from zope import interface, schema
except:pass
try:from zope.component import adapts, getMultiAdapter, getAdapter, getAdapters
except:pass 
try:import z3c
except:pass 
try:from five import grok
except:pass  
try:from five.grok.testing import grok as fgrok
except:pass   
try:from Products.statusmessages.interfaces import IStatusMessage
except:pass
try:from Acquisition import aq_inner, aq_parent, aq_self, aq_explicit
except:pass


