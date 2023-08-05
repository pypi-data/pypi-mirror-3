from zope.app.cache.caching import getCacheForObject, getLocationForCache
import inspect
import types
import zope.component
from zope.interface.interface import Interface
from zope.publisher.interfaces.http import IHTTPRequest
from zope.interface.declarations import providedBy, implements    
from falkolab.ext3.direct.interfaces import IExtDirectView, IDirectConfig


cacheKey = 'Ext.Direct config'

__docformat__ = "reStructuredText"

def getViews(ifaces):
    """Get all view registrations for methods"""
    gsm = zope.component.getGlobalSiteManager()
    for a in gsm.registeredAdapters():        
        if (len(a.required) > 0 and
            a.required[-1] is not None and
            a.required[-1].isOrExtends(IHTTPRequest)):              
            for required_iface in a.required[:-1]:
                if required_iface is not None:                    
                    for iface in ifaces:
                        if iface.isOrExtends(required_iface):
                            yield a
               
#def extdirectmethod(return_type, *parameters_types):
#    def wrapper(func):
#        # adding info on the function object
#        func.return_type = return_type
#        func.parameters_types = parameters_types
#        return ajaxmethod(func)
#    return wrapper 

class DirectConfig(object):
    implements(IDirectConfig)
    zope.component.adapts(Interface)
    
    def __init__(self, context):
        self.context = context 
        self.config=None
        
    def __call__(self, invalidate=False): 
#        try:
#            configKey = getPath(self.context)            
#        except:
#            intid = zope.component.queryUtility(IIntIds, context=self.context)
#            if intid!=None:
#                configKey = intid.queryId(self.context)      
        
        #if configKey!=None:       
       
        cache = getCacheForObject(self.context)
        location = getLocationForCache(self.context)       
        
        if cache and location:            
            _marker = object()
            if invalidate:                
                cache.invalidate(location)
            else:
                config = cache.query(location, {'directConfig': True}, default=_marker)
                if config is not _marker:                    
                    return config
        config = {} 
        for name, reg in self._getViews():                  
            config[name] = self._getMethidsConfig(reg.factory)  

        if cache and location:           
            cache.set(config, location, {'directConfig': True})
        
        return config
    
    def _getViews(self):                 
        interfaces = list(providedBy(self.context))                    
        adapter_registrations = self._getRegistrationAdapters(interfaces)
            
        if not adapter_registrations:
            adapter_registrations = self._getRegistrationAdapters([Interface])
            
        regs = {}
        for reg in adapter_registrations:
            if reg.name not in regs.keys():
                regs[reg.name] = reg       
            
        return regs.items()
    
    def _getRegistrationAdapters(self, interfaces):        
        registrations = list(getViews(interfaces))         
        return list(self._filterRegistrations(registrations))
    
    def _filterRegistrations(self, registrations):            
        for r in registrations:            
            if IExtDirectView.implementedBy(r.factory):
                yield r     
        
    def _getMethidsConfig(self, view):
        methods = []
        if hasattr(view, '__ajaxrequesthandlers__'):
            handlers = view.__ajaxrequesthandlers__
            for name in handlers:   
                handler = handlers.get(name)                       
                methods.append(self._getMethodSignature(handler.func))
        
        if hasattr(view, '__directmethods__'):            
            for dm in view.__directmethods__.values():
                methods.append(self._getDirectMethodConfig(dm))
         
        return methods
    
    def _getDirectMethodConfig(self, directMethod):
        config = self._getMethodSignature(directMethod.func)
        config.update(directMethod.props)
        return config
    
    def _getMethodSignature(self, func):
        if not isinstance(func, (types.FunctionType, types.MethodType)):
            raise TypeError("func must be a function or method")        
        
        config = {}
        config['name'] = func.__name__ 
        config['len'] = self._getFunctionArgumentSize(func)
        if hasattr(func, 'return_type') and hasattr(func, 'parameters_types'):
            pass
        
        return config
    
    def _getFunctionArgumentSize(self, func):
        args, varargs, varkw, defaults = inspect.getargspec(func)
        num_params = len(args) - 1
        if varargs is not None:
            num_params += len(varargs)
        if varkw is not None:
            num_params += len(varkw)

        return num_params