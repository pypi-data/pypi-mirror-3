How to use zc.datetimewidget with Zope2
=======================================

1. Add gocept.datetimewidget egg to your instance
-------------------------------------------------

This should automatically install the following dependencies:

 - zc.datetimewidget, zc.i18n and zc.resourcelibrary


2. Make sure the correct set of zcml gets loaded.
-------------------------------------------------

If you use a custom site.zcml, Include the following IN THIS ORDER::

    <!-- Enable zc.datetimewidget to load its zcml.
         Do not include zc.resourcelibrarys configure.zcml, as this 
         will not work in z2. --> 
    <include package="zc.resourcelibrary" file="meta.zcml" />
    <!-- Contains a copy of the resource directory of zc.datetimewidget
         registered as a browser:resourceDirectory.
         Also contains a viewlet manager with viewlets providing html
         snippets for including the javascripts in your templates (see below). -->
    <include package="gocept.datetimewidget" />
    <include package="zc.datetimewidget" />
    <!-- Replace the formlib datetimewidget with the zc one. -->
    <includeOverrides package="zc.datetimewidget" />
    <!-- Overwrite the zc.resourcelibrary resourcedirectory
         of zc.datetimewidget with a browser:resourceDirectory. -->
    <includeOverrides package="gocept.datetimewidget" />

If you use the zcml parameter of plone.recipe.zope2instance you can just set::

    zcml = zc.resourcelibrary-meta
           gocept.datetimewidget
           zc.datetimewidget
           zc.datetimewidget-overrides
           gocept.datetimewidget-overrides

3. Add javascript resources to your templates.
----------------------------------------------

Place a line like this in a template where your forms will be displayed::

    <tal:jsviewlets replace="structure provider:zc.datetimewidget.resources" />

Or make sure the following resources are loaded
(i.e. using plone portal_javascript/portal_css)::

    /++resource++zc.datetimewidget/calendar-system.css
    /++resource++zc.datetimewidget/calendar.js
    /++resource++zc.datetimewidget/datetimewidget.js
    /++resource++zc.datetimewidget/languages/calendar-en.js
    /++resource++zc.datetimewidget/calendar-setup.js

Or use Fanstatic_::

    import gocept.datetimewidget.resource
    gocept.datetimewidget.resource.datetimewidget.need()

.. _Fanstatic: http://www.fanstatic.org/
