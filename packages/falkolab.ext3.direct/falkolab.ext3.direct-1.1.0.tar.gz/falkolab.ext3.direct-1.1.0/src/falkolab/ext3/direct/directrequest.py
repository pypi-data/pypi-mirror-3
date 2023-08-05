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
'''
Created on 06.07.2009

@author: falko
'''

_common_names = ['type', 'action', 'method', 'tid']

class DirectRequestBase(dict):
    
    names = []
    dict = None
    
    def __init__(self, dict=None):              
        if dict != None:
            self.update(dict)               
          
    def __getattribute__(self, name):   
        if name in dict.__getattribute__(self, 'names'):
            return dict.__getitem__(self, name)        
        
        return dict.__getattribute__(self, name)
    
    def __setattr__(self, name, value):        
        if name in self.names:
            self.__setitem__(name, value)
        else:
            dict.__setattr__(self, name, value)
                  
            
class DirectRequest(DirectRequestBase):    
    names =  _common_names + ['isUpload', 'data']
    response = None
    
    def __init__(self, dict=None):
        super(DirectRequest, self).__init__(dict)
        self.response = DirectResponse()
        if dict:
            for name in _common_names:   
                if name in self:         
                    self.response[name] = self[name]
         
        
      
class DirectResponse(DirectRequestBase):
    names = _common_names + ['result', 'message', 'where']