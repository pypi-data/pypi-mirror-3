from zope.publisher.interfaces.browser import IDefaultBrowserLayer
import sys, traceback
from traceback import format_exception

DEFAULT_API_VIEW_NAME = 'directapi'
ROUTER_VIEW_NAME = 'directrouter'

class IExtDirectLayer(IDefaultBrowserLayer):
    pass

class IExtDirectDebugLayer(IExtDirectLayer):
    pass

def buildErrorMessage(routine=None):
    if routine==None:
        routine = sys._getframe().f_back.f_code.co_name
    etype = sys.exc_info()[0]
    value = sys.exc_info()[1]
    tb = sys.exc_info()[2]
    
    return """Error in routine: %s\n\n%s""" %(routine,
                                ''.join(format_exception(etype, value, tb)))