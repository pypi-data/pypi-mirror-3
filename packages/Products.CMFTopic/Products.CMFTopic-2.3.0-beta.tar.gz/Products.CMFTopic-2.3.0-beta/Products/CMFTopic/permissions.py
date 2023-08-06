##############################################################################
#
# Copyright (c) 2001 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Permissions used throughout CMFTopic.
"""

from AccessControl import ModuleSecurityInfo
from AccessControl.Permission import addPermission

security = ModuleSecurityInfo('Products.CMFTopic.permissions')

security.declarePublic('AddTopics')
AddTopics = 'Add portal topics'
addPermission(AddTopics, ('Manager',))

security.declarePublic('ChangeTopics')
ChangeTopics = 'Change portal topics'
addPermission(ChangeTopics, ('Manager', 'Owner',))

security.declarePublic('AccessContentsInformation')
from Products.CMFCore.permissions import AccessContentsInformation

security.declarePublic('ListFolderContents')
from Products.CMFCore.permissions import ListFolderContents

security.declarePublic('View')
from Products.CMFCore.permissions import View
