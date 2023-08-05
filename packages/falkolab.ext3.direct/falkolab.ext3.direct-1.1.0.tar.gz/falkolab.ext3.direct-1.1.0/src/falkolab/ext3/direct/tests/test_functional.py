##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE. 
#
##############################################################################
from falkolab.ext3.direct.ftests import setUp, tearDown, checker
from falkolab.ext3.direct.testing import ExtDirectFunctionalTestsLayer    
from zope.app.testing import functional
import unittest
from zope.component import provideUtility
"""
Created on 22.06.2009

@author: falko

$Id$
"""


def test_suite():
    suite = unittest.TestSuite()
         
    extdirect_doctest = functional.FunctionalDocFileSuite(
        '../README.txt', tearDown=tearDown, checker=checker)
    extdirect_doctest.layer = ExtDirectFunctionalTestsLayer
    suite.addTest(extdirect_doctest)
    
    extdirect_doctest = functional.FunctionalDocFileSuite(
        '../ROUTER.txt', tearDown=tearDown, checker=checker)
    extdirect_doctest.layer = ExtDirectFunctionalTestsLayer
    suite.addTest(extdirect_doctest)
    
    extdirect_doctest = functional.FunctionalDocFileSuite(
        '../CONFIG.txt', 
        globs={
              'provideUtility': provideUtility
              },
        tearDown=tearDown, checker=checker)
    extdirect_doctest.layer = ExtDirectFunctionalTestsLayer
    suite.addTest(extdirect_doctest) 
    
    return suite  

if __name__ == '__main__':    
    unittest.main(defaultTest='test_suite')