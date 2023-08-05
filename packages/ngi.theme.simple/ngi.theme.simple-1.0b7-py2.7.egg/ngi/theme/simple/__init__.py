# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('ngi.theme.simple')
logger.debug('Installing Product')
from Products.Archetypes import listTypes
from Products.Archetypes.ArchetypeTool import process_types
from Products.CMFCore import permissions as cmfpermissions
from Products.CMFCore import utils as cmfutils

from config import *

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("ngi.theme.simple")

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

