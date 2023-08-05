'''
Created on 22.06.2009

@author: falko
'''
from falkolab.ext3.direct.interfaces import IDirectProvider
from falkolab.ext3.direct import ROUTER_VIEW_NAME
from falkolab.ext3.direct.jsonsupport import encode, setNoCacheHeaders
import re
import urllib
from zope.publisher.browser import BrowserPage
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.app.component.hooks import getSite
import zope.component

jsid = re.compile(r'^[a-zA-Z_\$][a-zA-Z0-9_\$]*$')
repl = re.compile(r'[^a-zA-Z0-9_\$\.]+')

_type_alias = {'remoting':'rpc'}

def checkIdentifier(id):
    m = jsid.match(id)
    return m and True or False   
     

class DirectAPIView(BrowserPage):    
    addProvider = False
    namespace=None
    type=None
    
    
    def getProvider(self, type):
        if _type_alias.has_key(type):
            type = _type_alias[type]
        return zope.component.queryMultiAdapter((self.context, self.request), 
                                                        IDirectProvider, type)
        
    def __call__(self):
        response = self.request.response         
        ns = self.getNamespace()
        provider = self.getProvider(self.type)
        
            
        api = {'url': "%s/@@%s" %(absoluteURL(self.context , self.request), 
                                         ROUTER_VIEW_NAME),
               'type': self.type,
               'actions': provider.config,
               'namespace': ns
               }
        varName = '%s.REMOTING_API' %ns
        result = '%s=%s;' %(varName, encode(api, self.context))
        
        if self.addProvider or self.request.get("add_provider")!=None:
            result+='\nExt.Direct.addProvider(%s);' %varName
            
        if ns!='Ext.app':
            result='Ext.namespace(\'%s\');\n%s' %(ns,result)
            
        response.setHeader('Content-Type', 'text/javascript')
        setNoCacheHeaders(response)      
             
        return unicode(result)
    
        
    def getNamespace(self):
        ns=u''

        if(self.namespace):
            ns=self.namespace     
            if ns != u'.'.join(filter(checkIdentifier, ns.split('.'))):
                raise ValueError('Namespace is not valid: %s' % ns)
        else:
            siteUrl = absoluteURL(getSite(), self.request)             
            objurl = absoluteURL(self.context, self.request) 
            url = urllib.unquote(objurl.replace(siteUrl,'')).strip('/').replace('/','.')
            ns =repl.sub('_',url)
        
        if not ns:
            ns=u'Ext.app'
        
        return ns