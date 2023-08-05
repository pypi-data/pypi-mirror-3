# -*- coding: utf-8 -*-
#
# Copyright (c) 2007 by Yaco Sistemas S.L.
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Enrique Pérez <eperez@yaco.es>"""
__docformat__ = 'plaintext'

import Products.CMFPlone.interfaces
from Products.GenericSetup import EXTENSION
from Products.GenericSetup import profile_registry
from Products.Quota import config
from Products.CMFCore.utils import ContentInit

try:
    from Products.LinguaPlone.public import process_types
    from Products.LinguaPlone.public import listTypes
except ImportError:
    from Products.Archetypes.public import process_types
    from Products.Archetypes.public import listTypes


def initialize(context):

    from Products.Quota.content import quotafolder

    listOfTypes = listTypes(config.PROJECTNAME)

    content_types, constructors, ftis = process_types(
        listOfTypes,
        config.PROJECTNAME)

    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (config.PROJECTNAME, atype.portal_type)
        ContentInit(
            kind,
            content_types      = (atype,),
            permission         = config.ADD_PERMISSION,
            extra_constructors = (constructor,),
            fti                = ftis,
            ).initialize(context)


from zope.i18nmessageid import MessageFactory
QuotaMessageFactory = MessageFactory('Products.Quota')
