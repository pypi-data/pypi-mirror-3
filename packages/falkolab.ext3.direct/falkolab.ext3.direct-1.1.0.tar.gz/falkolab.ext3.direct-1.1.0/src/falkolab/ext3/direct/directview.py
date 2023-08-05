'''
Created on 22.06.2009

@author: falko
'''

from zope.interface.declarations import implements
from falkolab.ext3.direct.interfaces import IExtDirectView
    
from zope.publisher.browser import BrowserView


class ExtDirectView(BrowserView):
    """A base Ext.Direct view that can be used as mix-in for Ext.Direct views.""" 
    implements(IExtDirectView)