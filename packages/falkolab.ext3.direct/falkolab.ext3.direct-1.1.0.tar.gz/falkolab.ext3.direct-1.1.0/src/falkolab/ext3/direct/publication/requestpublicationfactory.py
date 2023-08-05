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
import zope.component
from zope.app.publication.interfaces import IRequestPublicationFactory
from zope.interface.declarations import implements
from falkolab.ext3.direct.publication.interfaces import IExtDirectRequestFactory
from falkolab.ext3.direct.publication.request import ExtDirectRequest
from falkolab.ext3.direct.publication.publication import ExtDirectPublication
"""
Created on 06.07.2009

@author: falko

$Id$
"""

class ExtDirectFactory(object):    
    implements(IRequestPublicationFactory)

    def canHandle(self, environment):
        return True

    def __call__(self):
        request_class = zope.component.queryUtility(
            IExtDirectRequestFactory, default=ExtDirectRequest)
        return request_class, ExtDirectPublication
