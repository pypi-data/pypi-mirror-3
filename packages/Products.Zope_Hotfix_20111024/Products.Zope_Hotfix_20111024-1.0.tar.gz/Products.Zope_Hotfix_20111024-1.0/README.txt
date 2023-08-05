'Products.Zope_Hotfix_20111024' README
======================================

Overview
--------

This hotfix addresses a serious vulnerability in the Zope2 application
server.  Affected versions of Zope2 include:

- 2.12.x <= 2.12.20

- 2.13.x <= 2.13.6

Older releases (2.11.x, 2.10.x, etc.) are not vulnerable.

The Zope2 security response team recommends that all users of these 
releases upgrade to an unaffected release (2.12.21 or 2.13.11) as soon as
they become available.

Until that upgrade is feasible, deploying this hotfix also mitigates the
vulnerability.


Installing the Hotfix:  Via 'easy_install'
-------------------------------------------

If the Python which runs your Zope instance has 'setuptools' installed (or
is a 'virtualenv'), you can install the hotfix directly from PyPI::

  $ /prefix/bin/easy_install Products.Zope_Hotfix_20111024

and then restart the Zope instance, e.g.:

  $ /path/to/instance/bin/zopectl restart


Installing the Hotfix:  Via 'zc.buildout'
-----------------------------------------

If your Zope instance is managed via 'zc.buildout', you can install
the hotfix directly from PyPI.  Edit the 'buildout.cfg' file, adding
"Products.Zope_Hotfix_20111024" to the "eggs" section of the instance.
E.g.::

  [instance]
  recipe = plone.recipe.zope2instance
  #...
  eggs =
    ${buildout:eggs}
    Products.Zope_Hotfix_20111024

Next, re-run the buildout::

  $ /path/to/buildout/bin/buildout

and then restart the Zope instance, e.g.:

  $ /path/to/buildout/bin/instance restart


Installing the Hotfix:  Manual Installation
-------------------------------------------

You may also install this hotfix by unpacking the tarball and adding a
'products' key to the 'etc/zope.conf' of your instance.   E.g.::

  products /path/to/Products.Zope_Hotfix_20111024/Products


Verifying the Installation
--------------------------

After restarting the Zope instance, check the 'Control_Panel/Products'
folder in the Zope Management Interface, e.g.:

  http://localhost:8080/Control_Panel/Products/manage_main

You should see the 'Zope_Hotfix_20111024' product folder there.
