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
from zope.app.publication.browser import BrowserPublication
"""
Created on 06.07.2009

@author: falko

$Id$
"""


# Don't need any special handling for ExtDirect
ExtDirectPublication = BrowserPublication

class ExtDirectPublicationFactory(object):

    def __init__(self, db):
        self.__pub = ExtDirectPublication(db)

    def __call__(self):
        return self.__pub
