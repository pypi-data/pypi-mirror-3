# encoding: utf-8

'''
Created on 2010/10/18

@author: nagai
'''

__author__ = """Takashi NAGAI <ngi644@gmail.com>"""
__docformat__ = 'plaintext'

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import LogoViewlet as PloneLogoViewlet
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from ngi.theme.simple.config import PROJECTNAME
from ngi.theme.simple import _


class LogoViewlet(PloneLogoViewlet):
    """
    Logo Viewlet.
    """
    template = ViewPageTemplateFile('logo.pt')
    
    def getInstalledName(self):
        qi = self.context.portal_url.getPortalObject().portal_quickinstaller
        return ( x['id'] for x in qi.listInstalledProducts())
    
    def update(self):
        super(LogoViewlet, self).update()
        if PROJECTNAME in self.getInstalledName():
            self.index = self.template
    
    def getLogoSize(self):
        """
        get logo size(width/height) from registry
        """       
        registry = getUtility(IRegistry)
        if 'ngi.theme.simple.logosize' in registry:
            p_size = registry['ngi.theme.simple.logosize']
            if not p_size:
                p_size = (0, 0)        
        else:
            p_size = (0, 0)
        ti = ('width', 'height')
        return dict(zip(ti,p_size))

class LogoData(BrowserView):
    """
    render logo from registry
    """
    def __call__(self):
        registry = getUtility(IRegistry)
        if 'ngi.theme.simple.logo' in registry:
            return registry['ngi.theme.simple.logo']        
        else:
            return None
        