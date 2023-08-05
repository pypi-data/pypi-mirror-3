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
from falkolab.ext3.direct import DEFAULT_API_VIEW_NAME
"""
Created on 03.07.2009

@author: falko

$Id$
"""
__docformat__ = 'restructuredtext'

import os
from zope.viewlet.viewlet import ViewletBase
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class PathViewletBase(object):
    """A simple viewlet for inserting references to relative path.

    This is an abstract class that is expected to be used as a base only.
    """
    _path = None

    def getURL(self):         
        return "%s/@@%s" % (absoluteURL(self.context, self.request) , self._path)

    def render(self, *args, **kw):
        return self.index(*args, **kw)


def ExtDirecApiViewlet(apiViewName=DEFAULT_API_VIEW_NAME, addProvider=False):
    """Create a viewlet that can simply insert a javascript link."""
    src = os.path.join(os.path.dirname(__file__), 'javascriptlink_viewlet.pt')
    path = '%s' %apiViewName
    if addProvider:
        path+='?add_provider'

    klass = type('ExtDirecApiViewlet',
                 (PathViewletBase, ViewletBase),
                  {'index': ViewPageTemplateFile(src),
                   '_path': path})

    return klass