.. contents:: **Table of contents**

Overview
========

After installing this product, you will be able to add a "Portlet Page".

This is like a standard Plone Page, but it also has a "*Manage portlets*" tab, from
which you may assign portlets into four slots. The portlets will be shown on the main
view of the content.

.. image:: http://keul.it/images/plone/collective.portletpage-1.1b1-01.png
   :alt: Managing content's portlets

Use of other content data like title, description and body text can be avoided, making the Portlet
Page simply a portlet container.

This product is great for providing to your Plone sites a tool for building the site *homepage*,
or the home for a site subsection.

.. image:: http://keul.it/images/plone/collective.portletpage-1.1b1-02.png
   :alt: Example of the user view

Similar product
---------------

Other Plone users like creating homepage using `Collage`__.

__ http://plone.org/products/collage

Installation
============

Add the ``collective.portletpage`` eggs in your buildout.cfg configuration file
(see also the `Plone buildout documentation`__)::

    [instance]
    ...
    eggs=
       ...
       collective.portletpage

__ http://plone.org/documentation/manual/developer-manual/managing-projects-with-buildout/packages-products-and-eggs

Support
=======

For reporting issues or ask for new features, please refer to the `product issue tracker`__

__ http://plone.org/products/collective.portletpage/issues/

Authors
=======

This product was mainly developed by *Martin Aspeli*, and other from the Plone community.

Credits
=======

This work was sponsored by:

* `Centrepoint`__ 
* `Guardia di Finanza`__; Guardia di Finanza support the `PloneGov initiative`__

__ http://centrepoint.org.uk
__ http://www.gdf.gov.it/
__ http://www.plonegov.it/

