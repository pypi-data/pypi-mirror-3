Zope3 UI Layer, resource and viewlets bundles for ExtJS v3 JavaScript library

Introduction
================================
Download ExtJS v3.x (http://extjs.com/products/extjs/download.php)
and put it in your operating system anywhere.
For example for me it is the following path: /usr/lib/ext-3
Within this folder must be located extracted ExtJS v3 framework distribution.

Anywhere in you project register resource directory has named as `ext-3`.
For example:
::
    
    <resourceDirectory 
        layer="falkolab.ext3.layer.IExtJSLayer" 
        name="ext-3" 
        directory="/usr/lib/ext-3" 
        />

This package will looking for the resourceDirectory named `ext-3`,
so it's important that you use the same `name` in the resourceDirectory statement.

How to use?
================================
This package provide two Viewlet Managers: IExtLayerCSS and IExtLayerJavaScript.
You may use it in you project skin template. For example like this:
::
    
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
                "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en"
        i18n:domain="mysite">
    <head>
        ...
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
        <meta http-equiv="cache-control" content="no-cache" />
        <meta http-equiv="pragma" content="no-cache" />
        <tal:block replace="structure provider:IExtLayerCSS" />
        <tal:block replace="structure provider:IExtLayerJavaScript" />
    </head>
    <body>
    ...
    </body>
    </html>

Or derive/implement your own managers for falkolab.ext3.layer.IExtLayerCSS 
and falkolab.ext3.layer.IExtLayerJavaScript interfaces.

NOTE: For necessary script including order, please use ordered manager:
zope.viewlet.manager.WeightOrderedViewletManager

This package contain several viewlet bunles for ExtJS. Use one of them according base 
library you use:

=================   ==================================================================
 ext-all.css        All ExtJS library CSS styles.
-----------------   ------------------------------------------------------------------                 
 ext-standalone     ExtJS library with own adapter (without any external dependences).
                    IExtStandaloneLayer and IExtStandaloneDebugLayer layers.
-----------------   ------------------------------------------------------------------                                         
 ext-jquery         ExtJS library with jQuery adapter (WARNING: read note below).
                    IExtJQueryLayer and IExtJQueryDebugLayer layers.                  
-----------------   ------------------------------------------------------------------                      
 ext-yui            ExtJS library with YUI adapter (WARNING: read note below). 
                    IExtYUILayer and IExtYUIDebugLayer layers. 
-----------------   ------------------------------------------------------------------                    
 ext-prototype      ExtJS library with Prototype adapter (WARNING: read note below).
                    IExtPrototypeLayer and  IExtPrototypeDebugLayer layers.
=================   ==================================================================
 
NOTE: For bundles which dependet on external library jQuery, YUI or Prototype 
you must manualy register corresponding resources in your project and place it to
your template before this package inclusions. 
Please see http://extjs.com/learn/Ext_Getting_Started#What_is_the_proper_include_order_for_my_JavaScript_files.3F
for details.
 
Skin layer system example:

::
    
    from z3c.layer.pagelet import IPageletBrowserLayer
    from zope.viewlet.interfaces import IViewletManager
    from zope.publisher.interfaces.browser import IBrowserRequest   
    from falkolab.ext3.layer import  IExtJQueryLayer, IExtJQueryDebugLayer
    from falkolab.ext3.layer.interfaces import IExtLayerCSS, IExtLayerJavaScript
    
    class myskin(IExtJQueryLayer):
        """ layer for skin base components """
    
    class IMySkin(myskin, IPageletBrowserLayer):
        """ IMySkin skin """
    
    class IMyDebugSkin(IExtJQueryDebugLayer, IMySkin):
        """ IMySkin debug skin """
        
    class ITitle(IViewletManager):
        """Title viewlet manager."""
    
    # This two interfaces for case when you use own Viewlet Managers
    # registration for combine site templete and falkolab.ext3.layer viewlets.
    class ICSS(IExtLayerCSS):
        """CSS viewlet manager."""
    
    class IJavaScript(IExtLayerJavaScript):
        """JavaScript viewlet manager."""
