Introduction
============

This Zope hotfix fixes `CVE 2010-1104`_.

.. _`CVE 2010-1104`: http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=2010-1104

This hotfix has been tested with Zope instances using Zope 2.8.x - 2.11.x.
Users of Zope 2.12 and greater should instead update to the latest
corresponding minor revision, which already includes this fix.

.. WARNING:: Zope < 2.12 is no longer officially supported, and may have
             other unpatched vulnerabilities. You are encouraged to upgrade to
             a supported Zope 2.


Installation
============

Download the tarball from the PyPI page:

 http://pypi.python.org/pypi/Products.Zope_Hotfix_CVE_2010_1104

Unpack the tarball and add a 'products' key to the 'etc/zope.conf' of
your instance.  E.g.::

  products /path/to/Products.Zope_Hotfix_CVE_2010_1104/Products

and restart.  Alternatively, you may copy or symlink the 'Products'
directory into the 'Products' subdirectory of your Zope instance.  E.g.::

  $ cp -r /path/to/Products.Zope_Hotfix_CVE_2010_1104/Products \
    /path/to/instance/Products/


Verifying the Installation
--------------------------

After restarting the Zope instance, check the
'Control_Panel/Products' folder in the Zope Management Interface,
e.g.:

  http://localhost:8080/Control_Panel/Products/manage_main

You should see the 'Zope_Hotfix_CVE_2010_1104' product folder there.


Changelog
=========

1.0 (2012-01-18)
----------------

- Initial release
