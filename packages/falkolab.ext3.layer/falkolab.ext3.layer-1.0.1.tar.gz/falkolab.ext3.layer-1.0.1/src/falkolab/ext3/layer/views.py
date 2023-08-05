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
"""
Created on 05.06.2009

@author: falko

$Id$
"""

from zope.viewlet import viewlet

ExtAllCSS = viewlet.CSSViewlet('ext-3/resources/css/ext-all.css')

#*************************************************
# ext-standalone bundle
ExtStandaloneBundleViewlet = viewlet.JavaScriptBundleViewlet((           
            'ext-3/adapter/ext/ext-base.js',
            'ext-3/ext-all.js'))

ExtStandaloneDebugBundleViewlet = viewlet.JavaScriptBundleViewlet((            
            'ext-3/adapter/ext/ext-base-debug.js',
            'ext-3/ext-all-debug.js'))

#*************************************************
# ext-jquery bundle
ExtJQueryBundleViewlet = viewlet.JavaScriptBundleViewlet((
            'ext-3/adapter/jquery/ext-jquery-adapter.js',
            'ext-3/ext-all.js'))

ExtJQueryDebugBundleViewlet = viewlet.JavaScriptBundleViewlet((
            'ext-3/adapter/jquery/ext-jquery-adapter-debug.js',
            'ext-3/ext-all-debug.js'))

#*************************************************
# ext-prototype bundle
ExtPrototypeBundleViewlet = viewlet.JavaScriptBundleViewlet((
            'ext-3/adapter/prototype/ext-prototype-adapter.js',
            'ext-3/ext-all.js'))

ExtPrototypeDebugBundleViewlet = viewlet.JavaScriptBundleViewlet((
            'ext-3/adapter/prototype/ext-prototype-adapter-debug.js',
            'ext-3/ext-all-debug.js'))

#*************************************************
# ext-yui
ExtYUIBundleViewlet = viewlet.JavaScriptBundleViewlet((       
            'ext-3/adapter/yui/ext-yui-adapter.js',
            'ext-3/ext-all.js'))

ExtYUIDebugBundleViewlet = viewlet.JavaScriptBundleViewlet((         
            'ext-3/adapter/yui/ext-yui-adapter-debug.js',
            'ext-3/ext-all-debug.js'))

