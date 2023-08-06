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
""" Topic: Canned catalog queries

$Id: __init__.py 110421 2010-04-01 17:14:12Z tseaver $
"""

def initialize(context):

    from Products.CMFCore.utils import ContentInit

    import Topic
    from permissions import AddTopics


    # Make sure security is initialized
    import DateCriteria
    import ListCriterion
    import SimpleIntCriterion
    import SimpleStringCriterion
    import SortCriterion

    context.registerHelpTitle( 'CMF Topic Help' )
    context.registerHelp( directory='help' )

    # BBB: register oldstyle constructors
    ContentInit( 'CMF Topic Content'
               , content_types=()
               , permission=AddTopics
               , extra_constructors=(Topic.addTopic,)
               , visibility=None
               ).initialize( context )
