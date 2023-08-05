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
from zope.component.globalregistry import provideAdapter
from falkolab.ext3.direct.testing import AlbumList, Contact 
from zope.app.folder.interfaces import IFolder
from zope.interface.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest

"""
Created on 22.06.2009

@author: falko

$Id$
"""

import re
from zope.testing import renormalizing
from zope.app.testing import  setup

def setUp(test):
    setup.setUpTestAsModule(test, 'falkolab.ext3.direct.README')    
    
def tearDown(test):    
    provideAdapter(None, (IFolder, IBrowserRequest), provides=Interface, name=u'albumlist')
    provideAdapter(None, (IFolder, IBrowserRequest), provides=Interface, name=u'Contact') 
        
checker = renormalizing.RENormalizing([
    (re.compile(r"HTTP/1\.([01]) (\d\d\d) .*"), r"HTTP/1.\1 \2 <MESSAGE>"),
    ])
