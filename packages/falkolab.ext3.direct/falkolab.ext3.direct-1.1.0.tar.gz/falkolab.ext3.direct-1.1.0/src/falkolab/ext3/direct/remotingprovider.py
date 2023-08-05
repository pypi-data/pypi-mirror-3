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
from zope.interface.interface import Interface
from falkolab.ext3.direct.directprovider import DirectProvider
from zope.publisher.interfaces.browser import IBrowserRequest
from types import DictionaryType
"""
Created on 15.08.2009

@author: falko

$Id$
"""


class RemotingProvider(DirectProvider):     
    zope.component.adapts(Interface, IBrowserRequest) 
        
                
    type = 'rpc'
    
    def _processRequest(self, directRequest):
        actionName = directRequest.action  
        methodName = directRequest.method 
        
        callResult = None      
           
        action = self.config.get(actionName, None)
        if action == None:
            raise ValueError("Unable to find action '%s'" %actionName)        
                  
        m = None
        for method in action:            
            if method.get('name')==methodName: 
                m=True
                break
            
        if not m:
            raise ValueError("Unable to find method '%s' on action '%s'" %(methodName,actionName))
                
        view = zope.component.getMultiAdapter((self.context,self.request), 
                                                Interface, actionName)
        if view == None:
            raise ValueError("Unable to find view for action '%s'" % actionName)
        
        handler = None
        if hasattr(view, '__ajaxrequesthandlers__'):
            handler = view.__ajaxrequesthandlers__.get(methodName, None)         
        
        if handler==None and hasattr(view, '__directmethods__'): 
            handler = view.__directmethods__.get(methodName, None)         
                         
        args = directRequest.data or []
        if type(args) == DictionaryType:
            args = [view, args]
        else:
            args.insert(0,view)            
            
        callResult=self.callObject(args, handler.func, self.request)        
            
        return callResult