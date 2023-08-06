##############################################################################
#
# Copyright (c) 2008 Kapil Thangavelu
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from zope import interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.viewlet.interfaces import IViewletManager

class IYUILayer( IBrowserRequest ):
    """
    zope3 skin for yui
    """
    
class IYUIJavascript( IViewletManager ):
    """
    zope3 viewlet manager for yui js
    """
    
class IYUICSS( IViewletManager ):
    """
    zope3 css manager for yui
    """