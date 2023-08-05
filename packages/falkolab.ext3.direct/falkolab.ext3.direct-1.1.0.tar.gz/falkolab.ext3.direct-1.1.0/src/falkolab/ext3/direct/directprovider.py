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
from falkolab.ext3.direct.interfaces import IDirectProvider, IDirectConfig
from zope.interface.declarations import implements
from zope.publisher.publish import mapply
from zope.app.appsetup import appsetup
from falkolab.ext3.direct import buildErrorMessage
from zope.component._api import adapts
from zope.interface.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest

"""
Created on 15.08.2009

@author: falko

$Id$
"""

class DirectProvider(object):
    implements(IDirectProvider)
    adapts(Interface, IBrowserRequest)
    
    namespace = None
    type = None
    config = None
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self, directRequest):   
        directResponse = directRequest.response
        try:
            directResponse['result'] = self._processRequest(directRequest)
        except Exception as e:   
                ti=appsetup.getConfigContext()        
                if ti != None and ti.hasFeature('devmode'):                    
                                                                   
                    directResponse.update({
                        'type': 'exception',
                        'message': 'Application error',
                        'where': buildErrorMessage(),
                        'result': None})
                else:
                    raise e

    
    def callObject(self, args, ob, request):
        return mapply(ob, args, request)
    
    def _processRequest(self, directRequest):
        raise NotImplemented, 'Method must be implemented by subclasses.'
    
    def _getConfig(self):
        return IDirectConfig(self.context)()
    
    config = property(_getConfig)