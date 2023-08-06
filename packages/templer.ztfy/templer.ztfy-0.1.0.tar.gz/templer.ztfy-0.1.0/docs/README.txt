.. contents::

Introduction
============

This package extends the functionality of the templer code generation system. It
builds upon the functionality of templer.core_.
This package provides basic support for creating ZTFY extension packages using
zc.buildout_.

.. _templer.core: http://pypi.python.org/pypi/templer.core
.. _zc.buildout: http://www.buildout.org/

Creating Packages
-----------------

As with the parent package, templer.core, creating packages using
ztfy.templer templates is accomplished by using the ``templer`` script. The
script is invoked thus::

    templer ztfy_package

This will create a basic buildout skeleton, containing the zc.buildout 
bootstrap.py file and a buildout.cfg file which may be edited to taste.

Generated 'src' directory contains all files needed to be able to register your new package
in any ZTFY.webapp environment, including locales base directories.

Included Templates
------------------

ztfy_package
    This creates a basic skeleton package for ZTFY.

Other Functions
---------------

The ``templer`` script provides a number of other functions, these are described
in full on the index page for templer.core_ at PyPI_

.. _templer.core: http://pypi.python.org/pypi/templer.core
.. _PyPI: http://pypi.python.org/pypi