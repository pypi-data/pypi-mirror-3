# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope import schema
from ngi.theme.simple import _

class IPrefForm(Interface):
        
    picture =  schema.Bytes(title=_(u"Logo File"), required=False)
    
    footer_text = schema.Text(title= _(u'Enter a footer text here'),
                          required=False)


