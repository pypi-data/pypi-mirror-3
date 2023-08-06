##############################################################################
#
# Copyright (c) 2006-2012 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""grokcore.catalog interfaces
"""
from zope.interface import Interface, Attribute

class IIndexDefinition(Interface):
    """Define an index for grok.Indexes.
    """

    def setup(catalog, name, context):
        """Set up index called name in given catalog.

        Use name for index name and attribute to index. Set up
        index for interface or class context.
        """

class IBaseClasses(Interface):
    Indexes = Attribute("Base class for a catalog indexes component.")
