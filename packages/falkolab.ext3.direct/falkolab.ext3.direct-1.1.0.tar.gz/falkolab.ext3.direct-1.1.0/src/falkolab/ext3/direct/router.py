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
from falkolab.ext3.direct.interfaces import IDirectProvider
from zope.cachedescriptors.method import cachedIn
from zope.component.interfaces import ComponentLookupError
from zope.publisher.browser import BrowserPage
import zope.component
from falkolab.ext3.direct.jsonsupport import encode
"""
Created on 22.06.2009

@author: falko

$Id$
"""


class DirectRouterView(BrowserPage):
        
    @cachedIn('_providers')
    def getProvider(self, type):
        return zope.component.queryMultiAdapter((self.context, self.request), 
                                                        IDirectProvider, type)

    def __call__(self):        
        directRresponses = []            
        for directRequest in self.request.directRequests:            
            provider = self.getProvider(directRequest.type)
            if provider==None:
                raise ComponentLookupError("Can't find provider '%s'" %directRequest.type)
            provider(directRequest)            
            directRresponses.append(directRequest.response)
                                 
        response = self.request.response
        response.setHeader('Content-Type', 'text/javascript')
        #setNoCacheHeaders(response) 
        
        if len(directRresponses) > 1:
            return encode(directRresponses)
        else:
            response = directRresponses[0];
            if hasattr(response, 'isUpload') and response.isUpload:
                return "<html><body><textarea>%s</textarea></body></html>" \
                        % encode(response).replace('&quot;', '\\&quot;')                
            else:
                return encode(response);        