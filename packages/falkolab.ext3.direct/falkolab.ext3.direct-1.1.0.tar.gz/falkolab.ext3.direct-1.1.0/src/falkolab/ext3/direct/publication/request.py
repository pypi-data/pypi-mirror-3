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
from zope.interface.declarations import implements
from falkolab.ext3.direct.publication.interfaces import IExtDirectRequest
from falkolab.ext3.direct.publication.response import ExtDirectResponse
from zope.publisher.browser import BrowserRequest, ZopeFieldStorage, FileUpload,\
    get_converter, CONVERTED, RECORD, DEFAULT, REC, SEQUENCE, Record, RECORDS
from falkolab.ext3.direct.directrequest import DirectRequest
from types import StringType
from falkolab.ext3.direct.jsonsupport import jsonDecode
import types
"""
Created on 06.07.2009

@author: falko

$Id$
"""
_get_or_head = 'GET', 'HEAD'
class ExtDirectRequest(BrowserRequest):
    implements(IExtDirectRequest)    
    
    def __init__(self, body_instream, environ, response=None):
        self.directRequests = []
        super(ExtDirectRequest, self).__init__(body_instream, environ, response)
    
    def _createResponse(self):
        """Create a specific ExtDirect response object."""
        return ExtDirectResponse()

    def processInputs(self):
        'See IPublisherRequest'            
        # Parse the request       
        if self.method not in _get_or_head:
            # Process self.form if not a GET request.
            fp = self._body_instream
        else:
            fp = None

        # If 'QUERY_STRING' is not present in self._environ
        # FieldStorage will try to get it from sys.argv[1]
        # which is not what we need.
        if 'QUERY_STRING' not in self._environ:
            self._environ['QUERY_STRING'] = ''
            
        # The Python 2.6 cgi module mixes the query string and POST values
        # together.  We do not want this.
        env = self._environ
        if self.method == 'POST' and self._environ['QUERY_STRING']:
            env = env.copy()
            del env['QUERY_STRING']

        fs = ZopeFieldStorage(fp=fp, environ=self._environ,
                              keep_blank_values=1)
        
        fslist = getattr(fs, 'list', None)
        file = getattr(fs, 'file', None)
        
        if fslist is not None:
            self.__meth = None
            self.__tuple_items = {}
            self.__defaults = {}

            # process all entries in the field storage (form)
            for item in fslist:
                self.__processItem(item)

            if self.__defaults:
                self.__insertDefaults()

            if self.__tuple_items:
                self.__convertToTuples()

            if self.__meth:
                self.setPathSuffix((self.__meth,))
                
            if self.form.get('extAction'):                
                req = DirectRequest({'action': self.form['extAction'],
                             'method': self.form['extMethod'],
                             'tid': self.form['extTID'], 
                             'type': self.form['extType'],   
                             'isUpload': bool(self.form['extUpload']),
                             'data': self.form        
                            })  
                
                self.directRequests.append(req)
#            else:
#                raise ValueError('Can''t find parameters for Ext.Direct form post.')
            
        elif file is not None:            
            rawPost = file.read()
            rawRequest = jsonDecode(rawPost)
            
            if type(rawRequest) == types.ListType:
                for reqAttrs in rawRequest:
                    self.directRequests.append(DirectRequest(reqAttrs))
            elif type(rawRequest) == types.DictType:
                self.directRequests.append(DirectRequest(rawRequest))
            else:
                raise TypeError('Ext.Direct request must be list or dict type.')           
        else:
            raise ValueError('Can''t process inputs')
        
    def __processItem(self, item):
        """Process item in the field storage."""

        # Check whether this field is a file upload object
        # Note: A field exists for files, even if no filename was
        # passed in and no data was uploaded. Therefore we can only
        # tell by the empty filename that no upload was made.
        key = item.name
        if (hasattr(item, 'file') and hasattr(item, 'filename')
            and hasattr(item,'headers')):
            if (item.file and
                (item.filename is not None and item.filename != ''
                 # RFC 1867 says that all fields get a content-type.
                 # or 'content-type' in map(lower, item.headers.keys())
                 )):
                item = FileUpload(item)
            else:
                item = item.value

        flags = 0
        converter = None

        # Loop through the different types and set
        # the appropriate flags
        # Syntax: var_name:type_name

        # We'll search from the back to the front.
        # We'll do the search in two steps.  First, we'll
        # do a string search, and then we'll check it with
        # a re search.

        while key:
            pos = key.rfind(":")
            if pos < 0:
                break
            match = self._typeFormat.match(key, pos + 1)
            if match is None:
                break

            key, type_name = key[:pos], key[pos + 1:]

            # find the right type converter
            c = get_converter(type_name, None)

            if c is not None:
                converter = c
                flags |= CONVERTED
            elif type_name == 'list':
                flags |= SEQUENCE
            elif type_name == 'tuple':
                self.__tuple_items[key] = 1
                flags |= SEQUENCE
            elif (type_name == 'method' or type_name == 'action'):
                if key:
                    self.__meth = key
                else:
                    self.__meth = item
            elif (type_name == 'default_method'
                    or type_name == 'default_action') and not self.__meth:
                if key:
                    self.__meth = key
                else:
                    self.__meth = item
            elif type_name == 'default':
                flags |= DEFAULT
            elif type_name == 'record':
                flags |= RECORD
            elif type_name == 'records':
                flags |= RECORDS
            elif type_name == 'ignore_empty' and not item:
                # skip over empty fields
                return

        # Make it unicode if not None
        if key is not None:
            key = self._decode(key)

        if type(item) == StringType:
            item = self._decode(item)

        if flags:
            self.__setItemWithType(key, item, flags, converter)
        else:
            self.__setItemWithoutType(key, item)

    def __setItemWithoutType(self, key, item):
        """Set item value without explicit type."""
        form = self.form
        if key not in form:
            form[key] = item
        else:
            found = form[key]
            if isinstance(found, list):
                found.append(item)
            else:
                form[key] = [found, item]

    def __setItemWithType(self, key, item, flags, converter):
        """Set item value with explicit type."""
        #Split the key and its attribute
        if flags & REC:
            key, attr = self.__splitKey(key)

        # defer conversion
        if flags & CONVERTED:
            try:
                item = converter(item)
            except:
                if item or flags & DEFAULT or key not in self.__defaults:
                    raise
                item = self.__defaults[key]
                if flags & RECORD:
                    item = getattr(item, attr)
                elif flags & RECORDS:
                    item = getattr(item[-1], attr)

        # Determine which dictionary to use
        if flags & DEFAULT:
            form = self.__defaults
        else:
            form = self.form

        # Insert in dictionary
        if key not in form:
            if flags & SEQUENCE:
                item = [item]
            if flags & RECORD:
                r = form[key] = Record()
                setattr(r, attr, item)
            elif flags & RECORDS:
                r = Record()
                setattr(r, attr, item)
                form[key] = [r]
            else:
                form[key] = item
        else:
            r = form[key]
            if flags & RECORD:
                if not flags & SEQUENCE:
                    setattr(r, attr, item)
                else:
                    if not hasattr(r, attr):
                        setattr(r, attr, [item])
                    else:
                        getattr(r, attr).append(item)
            elif flags & RECORDS:
                last = r[-1]
                if not hasattr(last, attr):
                    if flags & SEQUENCE:
                        item = [item]
                    setattr(last, attr, item)
                else:
                    if flags & SEQUENCE:
                        getattr(last, attr).append(item)
                    else:
                        new = Record()
                        setattr(new, attr, item)
                        r.append(new)
            else:
                if isinstance(r, list):
                    r.append(item)
                else:
                    form[key] = [r, item]

    def __splitKey(self, key):
        """Split the key and its attribute."""
        i = key.rfind(".")
        if i >= 0:
            return key[:i], key[i + 1:]
        return key, ""

    def __convertToTuples(self):
        """Convert form values to tuples."""
        form = self.form

        for key in self.__tuple_items:
            if key in form:
                form[key] = tuple(form[key])
            else:
                k, attr = self.__splitKey(key)

                # remove any type_names in the attr
                i = attr.find(":")
                if i >= 0:
                    attr = attr[:i]

                if k in form:
                    item = form[k]
                    if isinstance(item, Record):
                        if hasattr(item, attr):
                            setattr(item, attr, tuple(getattr(item, attr)))
                    else:
                        for v in item:
                            if hasattr(v, attr):
                                setattr(v, attr, tuple(getattr(v, attr)))

    def __insertDefaults(self):
        """Insert defaults into form dictionary."""
        form = self.form

        for keys, values in self.__defaults.iteritems():
            if not keys in form:
                form[keys] = values
            else:
                item = form[keys]
                if isinstance(values, Record):
                    for k, v in values.items():
                        if not hasattr(item, k):
                            setattr(item, k, v)
                elif isinstance(values, list):
                    for val in values:
                        if isinstance(val, Record):
                            for k, v in val.items():
                                for r in item:
                                    if not hasattr(r, k):
                                        setattr(r, k, v)
                        elif not val in item:
                            item.append(val)
