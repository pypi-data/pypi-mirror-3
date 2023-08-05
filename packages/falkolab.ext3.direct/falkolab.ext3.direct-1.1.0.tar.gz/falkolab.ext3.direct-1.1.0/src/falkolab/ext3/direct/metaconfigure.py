'''
Created on 22.06.2009

@author: falko
'''
from zope.interface import Interface
from zope.security.checker import CheckerPublic, Checker, defineChecker
from zope.component.interface import provideInterface
from zope.component.zcml import handler
from zope.publisher.interfaces.browser import IBrowserRequest,\
    IDefaultBrowserLayer
from zope.interface.declarations import classImplements
from falkolab.ext3.direct.interfaces import IExtDirectView

from falkolab.ext3.direct.router import DirectRouterView
from falkolab.ext3.direct.publication.interfaces import IExtDirectRequest
from falkolab.ext3.direct.api import DirectAPIView
from falkolab.ext3.direct import DEFAULT_API_VIEW_NAME, ROUTER_VIEW_NAME
from falkolab.ext3.direct.directview import ExtDirectView



def view(_context, for_, class_, name=None, interface=None, methods=None, 
         permission=None):#, namespace=None  ):
    
    interface = interface or []
    methods = methods or []

    # If there were special permission settings provided, then use them
    if permission == 'zope.Public':
        permission = CheckerPublic

    require = {}
    for attr_name in methods:
        require[attr_name] = permission

    if interface:
        for iface in interface:
            for field_name in iface:
                require[field_name] = permission
            _context.action(
                discriminator = None,
                callable = provideInterface,
                args = ('', for_)
                ) 
            
    if not name:
        name = class_.__name__   

    cdict = {}
    cdict['__name__'] = name

#    if class_ is None:
#        class_ = original_class = MethodPublisher
#    else:
#        original_class = class_
    new_class = type(class_.__name__, (class_, ExtDirectView), cdict)
        
    if hasattr(class_, '__implements__'):
            classImplements(new_class, IExtDirectView)
        
      
#        if namespace=='Ext.app':    
#            namespace = None
     
    defineChecker(new_class, Checker(require))   

    # Register the new view.
    _context.action(
            discriminator = ('view', for_, name, IBrowserRequest),
            callable = handler,
            args = ('registerAdapter',
                    new_class, (for_, IBrowserRequest), Interface, 
                    name, _context.info)
            )
        
    # Register the used interfaces with the site manager
    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )
        
def api(_context, for_, name=DEFAULT_API_VIEW_NAME, namespace=None, type='remoting'): 
    
    def directAPIViewProxy(context, request, namespace=namespace, 
                                         type=type, name=name):
        api = DirectAPIView(context, request)
        api.namespace=namespace
        api.type = type
        api.__name__=name
        return api
    
    _context.action(
        discriminator = ('directapi', for_, IBrowserRequest, name),
        callable = handler,
        args = ('registerAdapter',
                directAPIViewProxy, (for_, IDefaultBrowserLayer), Interface, 
                name, _context.info),
        )
    
    _context.action(
        discriminator = ('directrouter', for_, IExtDirectRequest),
        callable = handler,
        args = ('registerAdapter',
                DirectRouterView, (for_, IExtDirectRequest), Interface, 
                ROUTER_VIEW_NAME, _context.info),
        )