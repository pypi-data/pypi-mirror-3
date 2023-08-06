dm.zdoc
=======

Tiny wrapper around ``pydoc`` to make it usable for Zope.

Note: Python versions below 2.6 lack good support for namespace
packages in ``pydoc``. While Zope itself does not use
namespace packages before version 2.12 (which uses Python 2.6),
important Zope applications (such as Plone) do use namespace packages.
In these cases, the documentation produced by ``pydoc`` (and
by extension ``zdoc``) is incomplete.


Usage
=====

``zdoc`` can either be used via the script ``dmzdoc``, via module import
or integrated in a running Zope instance.

In the first two cases it might be necessary to set
the Zope environment variables ``INSTANCE_HOME``
and ``SOFTWARE_HOME`` to tell ``zdoc`` where the Zope sources can be found.

Use via ``dmzdoc``
------------------

The script ``dmzdoc`` is installed when you have ``setuptools`` installed.

Otherwise, you must install it yourself. It has the following content::

   import dm.zdoc; dm.zdoc.cli()

``dmzdoc`` has the exact same options and parameters as ``pydoc``,
documented in pydoc_.

Use via module import
---------------------

The module ``dm.zdoc`` defines the same objects as ``pydoc``,
documented in pydoc_.



Integrated in a running Zope instance
-------------------------------------

For this use, you must install the module in your Zope installation
and activate its ``configure.zcml`` at Zope startup.
This will give the "Zope Root Folder" the view ``@@zdoc``
which presents the documentation in the same way as the ``pydoc`` http server.

ATTENTION: Exposing the documentation of a Zope instance in this way
provides sensible insights and could give hackers valuable clues for
attacks. Likely, you will install this only in development
instances with restricted access.


Version History
===============

 * 2.0 support for the "integrated in a runnging Zope instance" use case

 * 1.1 works around a bug in either ``zope.interface`` or ``inspect``.


.. _pydoc: http://docs.python.org/lib/module-pydoc.html
