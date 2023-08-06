.. contents::

Why use this?
=============

Standardized sampledata makes it soo much easier to work on a project
(especially when working in teams).

This package eases the generation of sampledata for your plone project.


How to use it
=============

For developers working on a project there's a view listing and running
all available sampledata plugins:

http://localhost/plone/@@sampledata

.. image:: http://svn.plone.org/svn/collective/wm.sampledata/trunk/docs/screenshot.png
   :alt: Screenshot of the @@sampledata with enabled example plugin

By default the view does not list any plugins.
The screen above shows the example plugin activated via ``<include package="wm.sampledata.example" />``.


Writing and registering your custom sampledata plugin is very easy::

    class MyPlugin(object):
        implements(ISampleDataPlugin)

        title = u"My Plugin Content"
        description = u"Creates a portlet"

        def generate(self, context):
            portlet = StaticAssignment(u"Sample Portlet", "<p>some content</p>")
            addPortlet(context, 'plone.leftcolumn', portlet)

    myPlugin = MyPlugin()
    component.provideUtility(myPlugin,
                             ISampleDataPlugin
                             'my.plugin')

See `wm.sampledata.example`__
for a complete example of a custom plugin.

.. __: http://dev.plone.org/collective/browser/wm.sampledata/trunk/wm/sampledata/example

There is a growing set of utility methods in ``wm.sampledata.utils`` (eg for
handling portlets and files) which you can use in your plugins.


Installation
============


Simply add ``wm.sampledata`` to your buildout's instance eggs - a zcml slug is not needed
in plone versions that ship with z3c.autoinclude (Plone>=3.3)::

    [buildout]
    ...
    eggs =
        ...
        wm.sampledata



Why yet another package?
========================

There are several other packages for generating test/sampledata but none of them
fitted my usecase. (Which is providing a user interface for pluggable sampledata generators
so developers/skinners can use standardized data when developing on a project)

A while ago i `asked what other people do on plone.users`__

.. __: http://plone.293351.n2.nabble.com/Best-way-to-create-sampledata-for-tests-and-development-tp338487p338487.html


If you have any ideas for improvement or know another alternative to this package
please `drop me a mail`_

.. _`drop me a mail`: mailto:harald (at) webmeisterei dot com


z3c.sampledata
    Would do the same and much more (dependencies, groups, configuration ui for each plugin)

    for me it was too complex to get it running on my zope2 instance and it
    seems to be tailored for zope3 anyway.

    Basically it would be great to make wm.sampledata use z3c.sampledata
    and provide plone specific plugins for it.

    .. http://comments.gmane.org/gmane.comp.web.zope.plone.devel/17379

`ely.contentgenerator`_
    provides a xml syntax to create samplecontent,
    might be useful to use in custom plugins

    .. _`ely.contentgenerator`: http://ely.googlecode.com/svn/ely.contentgenerator


collective.contentgenerator
    looks like this is meant for creating (random) sampledata for stresstests




Ideas
=====

Integrate
* http://lorempixel.com/
* https://github.com/collective/collective.loremipsum/blob/master/README.rst

