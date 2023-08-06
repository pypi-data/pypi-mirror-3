.. contents:: Table of Contents
   :depth: 2

Package Repository Site 
****************************************

Overview
--------

This package installs a Plone Software Center in a clean Plone Site.

The main idea is to provide an easy and fast way to create a package repository, 
like PyPi or plone.org/downloads, to be used by a company to release its 
packages.

.. warning:: This is an early alpha intended to be used internally only.

Requirements
------------

    - Plone >=4.0.x (http://plone.org/products/plone)
    
Installation
------------
    
To enable this product,on a buildout based installation:

    1. Edit your buildout.cfg and add ``sc.psc.policy``
       to the list of eggs to install ::

        [buildout]
        ...
        eggs = 
            sc.psc.policy

    
After updating the configuration you need to run the ''bin/buildout'',
which will take care of updating your system.

Go to the 'Site Setup' page in the Plone interface and click on the
'Add/Remove Products' link.

Choose the product (check its checkbox) and click the 'Install' button.

Uninstall -- This can be done from the same management screen, but only
if you installed it from the quick installer.

Note: You may have to empty your browser cache and save your resource registries
in order to see the effects of the product installation.

Sponsoring
----------

Development of this product was sponsored by `TV1 
<http://www.tv1.com.br/>`_ and by `Serpro <http://www.serpro.gov.br/>`_.


Credits
-------

    * Simples Consultoria (products at simplesconsultoria dot com dot br) - 
      Implementation
    
