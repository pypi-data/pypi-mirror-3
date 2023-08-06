.. py:module:: sphinxcontrib.scaladomain

==============================================================
:py:mod:`sphinxcontrib.scaladomain` --- Documenting Scala APIs
==============================================================

This Sphinx_ extension provides a domain for documenting Scala_ APIs.

.. _Scala: http://www.scala-lang.org/
.. _Sphinx: http://sphinx.pocoo.org/latest

Getting Started
===============

Installation
------------

This extension can be installed from the Python Package Index::

   pip install sphinxcontrib-scaladomain

Alternatively, you can clone the sphinx-contrib_ repository from BitBucket and
install the extension directly from the repository::

   hg clone http://bitbucket.org/birkenfeld/sphinx-contrib
   cd sphinx-contrib/scaladomain
   python setup.py install

.. _sphinx-contrib: http://bitbucket.org/birkenfeld/sphinx-contrib

Configuration
-------------

Add ``sphinxcontrib.scaladomain`` to the configuration value
:confval:`sphinx:extensions` in your :file:`conf.py` configuration file.

.. confval:: scaladomain_pkgindex_common_prefix

   A list of prefixes that are ignored for sorting the Scala Package Index
   (e.g., if this is set to ``['foo.']``, then ``foo.bar`` is shown under
   ``B``, not ``F``). This can be handy if you document a project that consists
   of a single parent package. Works only for the HTML builder currently.
   Default is ``[]``.

Domain Markup
=============

As most Sphinx domains, the Scala domain (name **scl**) provides a number of
*object description directives*, used to describe specific objects provided by
packages. Each directive requires one or more signatures to provide basic
information about what is being described, and the content should be in the
description. The basic version makes entries in the general index; if no index
entry is desired, you can give the directive option flag ``:noindex:``.

The Scala domain also provides roles that link back to these object
descriptions. Both directive and role names contain the domain name and the
directive name.

Describing Scala objects
------------------------

The Scala domain provides the following directives for package
declarations:

.. rst:directive:: .. scl:package:: name

   This directive marks the beginning of the description of a package. It does
   not create content.

   This directive will also cause an entry in the Global Package Index.

   The ``platform`` option, if present, is a comma-separated list of the
   platforms on which the module is available. (if it is available on all
   platforms, the option should be omitted). The keys are short identifiers;
   examples that are in use include "IRIX", "Mac", "Windows", and "Unix". It is
   important to use a key which has already been used when applicable.

   The ``synopsis`` option should consist of one sentence describing the
   package's purpose -- it is currently only used in the Global Package Index.

   The ``deprecated`` option can be given (with no value) to mark a package as
   deprecated; it will be designated as such in various locations then.

.. rst:directive:: .. scl:currentpackage:: name

   This directive tells Sphinx that the classes, objects etc. documented from
   here are in the given package (like :rst:dir:`scl:package`),  but it will
   not create index entries, an index in the Global Package Index, or a link
   target for :rst:role:`scl:pkg`. This is helpful in situations where
   documentation for things in a package is spread over multiple files or
   sections -- one location has the :rst:dir:`scl:package` directive, the
   others only :rst:dir:`scl:currentpackage`.

Scala Signatures
----------------

Cross-referencing Scala objects
-------------------------------

The following roles refer to objects in packages and are possibly hyperlinked
if a matching identifier is found:

.. rst:role:: scl:pkg

   Reference a package.

Contribution
============

Please contact the author or create an issue in the `issue tracker`_ of the
`sphinx-contrib`_ repository, if you have found any bugs or miss some
functionality. Patches are welcome!

.. _issue tracker: https://bitbucket.org/birkenfeld/sphinx-contrib/issues

==================
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

