# -*- coding: utf-8 -*-
#

from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.base import registerATCT
from Products.Quota.config import *
from Products.Quota.interfaces import IQuotaAware


class QuotaFolder(ATFolder):
    """
    """
    implements(IQuotaAware)

    portal_type = 'QuotaFolder'
    archetype_name = 'QuotaFolder'

registerATCT(QuotaFolder, PROJECTNAME)
