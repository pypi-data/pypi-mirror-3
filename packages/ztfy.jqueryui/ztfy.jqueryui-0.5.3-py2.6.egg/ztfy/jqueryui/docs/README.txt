=====================
ztfy.jqueryui package
=====================

.. contents::

What is ztfy.jqueryui ?
=======================

ztfy.jqueryui is a set of javascript resources (and their dependencies) allowing any application to easily
use a set of JQuery plug-ins ; when possible, all CSS and JavaScript resources are already minified
via Yahoo 'yuicompressor' tool.

Most of these plug-ins are used by default ZTFY skins.

Currently available plug-ins include :
 - the JQuery engine
 - jquery-alerts
 - jquery-datetime
 - jquery-fancybox
 - jquery-form
 - jquery-jsonrpc
 - jquery-jtip
 - jquery-tools
 - jquery-treetable
 - jquery-ui


How to use ztfy.jqueryui ?
==========================

All JQuery resources are just defined via zc.resourcelibrary package directive in ZCML files.

Using a given plug-in is as simple as using the following syntax in any HTML view: ::

    >>> from zc import resourcelibrary
    >>> resourcelibrary.need('ztfy.jquery.form')

Given that, all plug-in dependencies will automatically be included into resulting HTML page.
