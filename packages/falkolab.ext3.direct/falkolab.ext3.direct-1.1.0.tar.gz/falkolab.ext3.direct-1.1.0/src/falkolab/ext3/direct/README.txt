=================================================
Zope3 Ext.Direct - Server-side Stack for ExtJS 3.
=================================================

How do I use it ?
-----------------  
  
Let's register api and views:

  >>> from zope.configuration import xmlconfig
  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns="http://namespaces.zope.org/zope"
  ...     xmlns:extdirect="http://namespaces.zope.org/extdirect"
  ...     >
  ...   <include package="falkolab.ext3.direct" file="meta.zcml" />
  ...
  ...   <extdirect:api
  ...       for="zope.app.folder.interfaces.IFolder"
  ...       namespace = "my.app"       
  ...       />   
  ...
  ...   <extdirect:view
  ...       for="zope.app.folder.interfaces.IFolder"
  ...       class="falkolab.ext3.direct.testing.AlbumList"
  ...       permission="zope.ManageContent"
  ...       name="albumlist"
  ...       />
  ...
  ...   <extdirect:view
  ...       for="zope.app.folder.interfaces.IFolder"
  ...       class="falkolab.ext3.direct.testing.Contact"
  ...       permission="zope.ManageContent"
  ...       />  
  ... </configure>
  ... """)
  
Direct API:
  
  >>> print http(r"""
  ... GET /@@directapi HTTP/1.1
  ... Authorization: Basic bWdyOm1ncnB3
  ... """)
  HTTP/1.1 200 Ok
  Cache-Control: no-cache
  Content-Length: ...
  Content-Type: text/javascript;charset=utf-8
  Expires: ...
  Pragma: no-cache
  <BLANKLINE>
  Ext.namespace('my.app');
  my.app.REMOTING_API={"url": "http://localhost/@@directrouter", "namespace": "my.app", "type": "remoting", "actions": {"Contact": [{"name": "getInfo", "len": 1}], "albumlist": [{"formHandler": true, "name": "add", "len": 0}, {"name": "getAll", "len": 0}]}};

Auto add provider : 

  >>> print http(r"""
  ... GET /@@directapi?add_provider HTTP/1.1
  ... Authorization: Basic bWdyOm1ncnB3
  ... """)
  HTTP/1.1 200 Ok
  Cache-Control: no-cache
  Content-Length: ...
  Content-Type: text/javascript;charset=utf-8
  Expires: ...
  Pragma: no-cache
  <BLANKLINE>
  Ext.namespace('my.app');
  my.app.REMOTING_API={"url": "http://localhost/@@directrouter", "namespace": "my.app", "type": "remoting", "actions": {"Contact": [{"name": "getInfo", "len": 1}], "albumlist": [{"formHandler": true, "name": "add", "len": 0}, {"name": "getAll", "len": 0}]}};
  Ext.Direct.addProvider(my.app.REMOTING_API);
  
And Direct Request hanling (for addition see ROUTER.TXT): 

  >>> print http(r"""
  ... POST /@@directrouter HTTP/1.1
  ... Authorization: Basic bWdyOm1ncnB3
  ... Content-Length: 71
  ... Content-Type: application/json; charset=UTF-8
  ... Referer: http://localhost/
  ... 
  ... {"action":"albumlist","method":"getAll","data":[],"type":"rpc","tid":1}""")  
  HTTP/1.1 200 Ok
  Content-Length: 89
  Content-Type: text/javascript
  <BLANKLINE>
  {"action": "albumlist", "tid": 1, "type": "rpc", "method": "getAll", "result": [1, 2, 3]}
  
