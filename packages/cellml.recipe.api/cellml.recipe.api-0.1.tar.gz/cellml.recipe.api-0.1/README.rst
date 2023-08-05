Overview
========

This is the recipe that will build the CellML API Python bindings with
all options enabled by default.  Currently, there are some limitations,
such as all dependencies required to build the CellML API must be
installed before this recipe can be used, and I don't think this will
work under Windows at the moment.


Supported options
=================

The recipe supports the following options:

api-version
    CellML API version to build.  Valid versions any versions that build
    via CMake and has Python bindings (>1.10), and must be present in
    the list of valid versions.

cmake-generator
    The generator to use.  Only the default option ``Unix Makefiles`` is
    supported, as this recipe is built on top of ``zc.recipe.cmmi`` 
    which will make use of ``make`` and ``make install``.

check-build
    Whether to check build time dependencies.  Default is off because it
    didn't detect GSL libraries even though it was installed for me.
    Same as passing ``-DCHECK_BUILD:BOOL=OFF`` to ``cmake``.

Other supported options:

    - enable-examples
    - enable-annotools
    - enable-ccgs
    - enable-celeds
    - enable-celeds-exporter
    - enable-cevas
    - enable-cis
    - enable-cuses
    - enable-gsl-integrators
    - enable-malaes
    - enable-python
    - enable-rdf
    - enable-spros
    - enable-srus
    - enable-telecems
    - enable-vacss

Please refer to the `CellML API Documentations`_ for what these options
do.

.. _CellML API Documentations: http://cellml-api.sourceforge.net/


Copyright/License information
=============================

This software is released under the MPL/GPL/LGPL licenses.

Please refer to the file ``COPYING.txt`` for detailed copyright
information, and ``docs`` directory for specific licenses that this
software is released under.
