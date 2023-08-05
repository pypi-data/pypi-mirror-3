'''
Created on 22.06.2009

@author: falko
'''
import zope.interface
from zope import schema
import zope.security.zcml
from zope.configuration.fields import GlobalObject, Tokens, GlobalInterface,\
    PythonIdentifier

class IViewDirective(zope.interface.Interface):
    """View Directive for Ext.Direct methods."""   

    for_ = GlobalObject(
        title=u"Published Object Type",
        description=u"""The types of objects to be published via Ext.Direct

        This can be expressed with either a class or an interface
        """,
        required=True,
        )
    
    class_ = GlobalObject(
        title=u"Class",
        description=u"A class that provides attributes used by the view.",
        required=True
        )
    
    name = schema.TextLine(
        title=u"The name of the view.",
        description=u"""""",
        required=False,
        )

    interface = Tokens(
        title=u"Interface to be published.",
        required=False,
        value_type=GlobalInterface()
        )

    methods = Tokens(
        title=u"Methods (or attributes) to be published",
        required=False,
        value_type=PythonIdentifier()
        )


    permission = zope.security.zcml.Permission(
        title=u"Permission",
        description=u"""The permission needed to use the view.""",
        required=False)


class IAPIDirective(zope.interface.Interface):    
    """API Directive for Ext.Direct api bindings."""
    
    for_ = GlobalObject(
        title=u"The interface or class this api is for.",
        required=False
        )
    
    name = schema.TextLine(
        title=u"The name of the api view.",
        description=u"""""",
        required=False,
        )
    
    namespace = schema.TextLine(
        title=u"The namespace of the view.",
        description=u"""If a name is given, then Ext.Direct Server-side Stack use
        this namespace to avoid conflicts in views for different contexts while 
        generate api configuration script.
        """,
        required=False,
        )
    
    type = schema.TextLine(
        title=u"The type of used Ext.Direct adapter.",
        description=u"""""",
        required=False,        
        )