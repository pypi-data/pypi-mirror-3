===========
aws.pdfbook
===========

Description
===========

``aws.pdfbook`` is a component for Plone 3 or Plone 4 that enables to download
content rendered to PDF. It provides support for default content types. Third
party content type authors and integrators may add support to their personal
content types through dedicated Zope 3 named views.

When downloading a Folder or a Topic/Collection, all subcontents is included in
the PDF document but not recursively.

.. warning::

   `htmldoc <http://www.htmldoc.org/>`_ requires ISO latin 9 encoded HTML. As a
   consequence, this component is suitable only to site in western european
   languages. We cannot support Hebrew, Arabic, (...) as long as htmldoc does not
   support UTF-8.


Requirements
============

The following softwares should be installed:

* Tested with Plone 3.x, Plone 4.0, Plone 4.1.
* htmldoc (required)
* recode (optional)

Installation
============

Instance wide
-------------

In your ``buildout.cfg`` file::

  [buildout]
  ...
  eggs =
    ...
    aws.pdfbook

We assume that:

* The site charset is ``utf-8``
* The server buffer for downloading has 40000 bytes.

Otherwise you can change these default values in your ``zope.conf`` or in
``buildout.cfg`` like this::

  [instance]
  recipe = plone.recipe.zope2instance
  ...
  zope-conf-additional =
    ...
    <product-config aws.pdfbook>
    # Your site charset (default: utf-8)
    site-charset utf-8
    # The download buffer bytes size (default: 40000)
    download-buffer-size 40000
    </product-config>
    ...

.. note::

   Increasing the buffer size may speed up download but at the expense of a
   bigger memory footprint.

Plone site
----------

In your Plone site go to the 'Site Setup' page and click on the 'Add/Remove
Products' link.

Choose ``aws.pdfbok`` (check its checkbox) and click the 'Install' button.

The go **as soon as possible** to the **PDF Book** configuration panel and
configure according to your system settings and your layout preferences.

More particularly, you may change default ``pdfbook`` options. See the `pdfbook
documentation <http://www.htmldoc.org/documentation.php/toc.html>`_ for the
various available options.

Other setups
------------

It is strongly recommanded to use linking with UID in your visual editor
preferences. Otherwise images may not display in topics prints.

Developers
==========

Customizing default templates in ZMI
------------------------------------

Open your Plone site in ZMI, then the ``portal_view_customization`` object.

Click on a link **printlayout** that suits the interface of the content items
you want to customize.

Change the template as you prefer...

Add a template for your content types
-------------------------------------

Assuming you have a personal content type that implements the
``myproduct.interfaces.IMyContentType`` interface, You must add a view like this
one::

  <browser:page
     name="printlayout"
     for="myproduct.interfaces.IMyContentType"
     layer="aws.pdfbook.interfaces.IAWSPDFBookLayer"
     permission="zope.Public"
     template="templates/mycontenttype.pt"
     />

Keep the following attributes as above:

* ``name="printlayout"``
* ``layer="aws.pdfbook.interfaces.IAWSPDFBookLayer"``
* ``permission="zope.Public"``

Examples for standard content types are provided in the
``browser/transformers.zcml`` configuration and associated files.

Otherwise ``aws.pdfbook`` provides a default template that may or may not fit
with paper layout.

.. important::

   Your personal template:

   * must provide a "body" macro that renders the body of your content.
   * the title of your content must be in an ``<h1>`` element.
   * must be careful with HTML limitations of htmldoc.

If the default layout for personal or third party content types is somehow
awful, you may blacklist such content types in the configuration panel.

Contributors
============

The subversion repository for this component is
https://svn.plone.org/svn/collective/aws.pdfbook .

The development kit comes with a ``buildout.cfg`` for the latest Plone stable
version.

Please don't forget to file your changes in the ``docs/HISTORY.txt`` file.

Support
=======

Please use the tracker at http://plone.org/products/aws.pdfbook/issues

Credits
=======


* Original version for Plone 2.x by `John Doe <john.doe@dev.null>`_
* Plone 3.x support by `Gilles Lenfant <mailto:gilles.lenfant@amterway.fr>`_ for
  `Alter Way Solutions <http://www.alterway.fr>`_
* Sponsored by `Materis <http://www.materis.com/>`_

.. image:: http://www.materis.com/template/imgs_fr/logo.gif
   :align: center
