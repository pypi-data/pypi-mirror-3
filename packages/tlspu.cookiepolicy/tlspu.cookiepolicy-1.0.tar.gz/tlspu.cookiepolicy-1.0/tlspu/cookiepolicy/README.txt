===============================================
TLSPU Cookie Policy (tlspu.cookiepolicy)
===============================================

.. contents:: Table of Contents
   :depth: 2


Overview
--------

**TLSPU Cookie Policy** is a Plone package (add-on) providing simple a simple
solution to comply with the so called "European Cookie Law".

Requirements
------------

Tested with

    - Plone 4.1.x (http://plone.org/products/plone)

Should also work with

    - Plone 4.0.x (http://plone.org/products/plone)
    - Plone 3.3.x (http://plone.org/products/plone)

Screenshot
-----------

    .. image:: http://www.tlspu.com/consultancy/cookiepolicy-screenshot.png

Installation
------------

To enable this product, on a buildout based installation:

    1. Edit your buildout.cfg and add ``tlspu.cookiepolicy``
       to the list of eggs to install ::

        [buildout]
        ...
        eggs = 
            tlspu.cookiepolicy

.. note:: Since Plone 3.3 is not is necessary to explictly inform 
          plone.recipe.zope2instance recipe to install the ZCML slug

After updating the configuration you need to run the ''bin/buildout'',
which will take care of updating your system.

Using in a Plone Site
----------------------

Step 1: Activate it
^^^^^^^^^^^^^^^^^^^^

Go to the 'Site Setup' page in the Plone interface and click on the
'Add/Remove Products' link.

Choose the product **TLSPU Cookie Policy** (check checkbox at its left side)
and click the 'Activate' button.

Step 2: Configure it
^^^^^^^^^^^^^^^^^^^^^^

Go to the 'Site Setup' page in the Plone interface and click on the
'Cookie Policy' link -- under Add-on Configuration.

.. image:: http://www.tlspu.com/consultancy/cookiepolicy-controlpanel.png

There you can configure how **TLSPU Cookie Policy** will behave.

Uninstall
-------------

Go to the 'Site Setup' page in the Plone interface and click on the
'Add/Remove Products' link.

Choose the product **TLSPU Cookie Policy**, which should be under *Activated
add-ons*, (check checkbox at its left side) and click the 'Deactivate' button.

.. note:: You may have to empty your browser cache and save your resource 
          registries in order to see the effects of the product installation.

Contributing
--------------


Sponsoring
----------

Development of this product was sponsored by :
    
    * `Historica <http://www.historica.co.uk/>`_
    
Credits
-------
    
    * `Adrian Hungate <http://www.tlspu.com/contact-us>`_ - Idea and implementation.

