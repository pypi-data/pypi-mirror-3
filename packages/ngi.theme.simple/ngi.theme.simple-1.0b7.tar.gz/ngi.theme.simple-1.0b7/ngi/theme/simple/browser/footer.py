# encoding: utf-8

'''
Created on 2010/10/18

@author: nagai
'''

__author__ = """Takashi NAGAI <ngi644@gmail.com>"""
__docformat__ = 'plaintext'

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import FooterViewlet as PloneFooterViewlet
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from ngi.theme.simple.config import *
from ngi.theme.simple import _


class FooterViewlet(PloneFooterViewlet):
    """
    Footer Viewlet.
    """
    
    template = ViewPageTemplateFile('footer.pt')
    
    def getInstalledName(self):
        qi = self.context.portal_url.getPortalObject().portal_quickinstaller
        return ( x['id'] for x in qi.listInstalledProducts())
    
    def update(self):
        super(FooterViewlet, self).update()
        if PROJECTNAME in self.getInstalledName():
            self.index = self.template
        
    def getFooterData(self):
        """
        Get Footer data
        """
        registry = getUtility(IRegistry)
        if 'ngi.theme.simple.footer' in registry:
            return registry['ngi.theme.simple.footer']
        else:
            return _(u'footer_meeseage', default=u'Input footer here.')
        