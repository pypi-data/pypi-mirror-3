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
import sys
"""
Created on 16.08.2009

@author: falko

$Id$
"""



class directMethod(object):
    
    def __init__(self, **kw):
        self.props = dict(kw)
        
    def __call__(self, func):        
        self.func = func
        frame = sys._getframe(1)
        f_locals = frame.f_locals
        dm = f_locals.setdefault('__directmethods__', dict())
        key = func.__name__
        dm[key] = self
        return func