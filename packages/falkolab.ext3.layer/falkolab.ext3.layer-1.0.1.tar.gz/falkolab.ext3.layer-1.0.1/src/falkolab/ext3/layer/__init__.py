##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE. 
#
##############################################################################
"""falkolab.ext3.layer

$Id$
"""
from zope.publisher.interfaces.browser import IBrowserRequest,\
    IDefaultBrowserLayer
from falkolab.ext3.layer.interfaces import IExtLayerCSS, IExtLayerJavaScript
import types

class IExtLayer(IDefaultBrowserLayer):
    """  extjs layer  """

#class IExtDebugLayer(IExtLayer):
#    """  extjs debug layer  """

class IExtStandaloneLayer(IExtLayer):
    """ ext-standalone layer """
    
class IExtStandaloneDebugLayer(IExtStandaloneLayer):
    """ ext-standalone debug layer """
    
    
class IExtJQueryLayer(IExtLayer):
    """ ext-jquery layer """
    
class IExtJQueryDebugLayer(IExtJQueryLayer):
    """ ext-jquery debug layer """
    
    
class IExtPrototypeLayer(IExtLayer):
    """ ext-prototype layer """
    
class IExtPrototypeDebugLayer(IExtPrototypeLayer):
    """ ext-prototype debug layer """
        
    
class IExtYUILayer(IExtLayer):
    """ ext-yui layer """
    
class IExtYUIDebugLayer(IExtYUILayer):
    """ ext-yui debug layer """
