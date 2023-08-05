# encoding: utf-8

'''
Created on 2010/09/24

@author: nagai
'''
from zope.component import adapts
from zope.formlib import form
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.interfaces import ISiteRoot
from plone.app.controlpanel.form import ControlPanelForm
from PIL import Image
from StringIO import StringIO
from ngi.theme.simple.interfaces import IPrefForm
from ngi.theme.simple import _

class PrefHeaderFooterFormAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IPrefForm)

    def __init__(self, context):
        super(PrefHeaderFooterFormAdapter, self).__init__(context)

    def get_picture(self):
        registry = getUtility(IRegistry)
        if 'ngi.theme.simple.logo' in registry:
            return registry['ngi.theme.simple.logo']
        else:
            return None
        
    def set_picture(self, value):
        registry = getUtility(IRegistry)
        if value:
            registry['ngi.theme.simple.logo'] = value
            try:
                imf = StringIO(value)
                im_size = Image.open(imf).size
            except IOError:
                im_size = (0, 0)
            finally:
                registry['ngi.theme.simple.logosize'] = im_size

    picture = property(get_picture,
                                  set_picture)


    def get_footer_text(self):
        registry = getUtility(IRegistry)
        if 'ngi.theme.simple.footer' in registry:
            return registry['ngi.theme.simple.footer']
        else:
            return _(u'Please input footer text.')

    def set_footer_text(self, value):
        registry = getUtility(IRegistry)
        registry['ngi.theme.simple.footer'] = value

    footer_text = property(get_footer_text,
                                  set_footer_text)


class PrefHeaderFooterForm(ControlPanelForm):
    """"""
    label = _("Simple theme settings")
    description = _("Logo & Footer settings for this site.")
    form_name = _("Logo & Footer settings")
    form_fields = form.FormFields(IPrefForm)
    
