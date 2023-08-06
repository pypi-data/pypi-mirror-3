.. _usage:

Usage instructions
******************

Using versiontools is very easy. Just follow those steps to do it.

Declare package version
^^^^^^^^^^^^^^^^^^^^^^^

Put this code your package's ``__init__.py`` or in your main module::

    __version__ = (1, 2, 3, 'final', 0)  # replace with your project version

.. note:
    There is some rationale for each component of the tuple. This has been
    standardized in :pep:`386`. Make sure you understand what each field
    represents. There are a few constraints, such as having serial (the last
    component) greater than zero if the release is 'alpha', 'beta' or
    'candidate'.

Copy versiontools_support.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You will need to keep a copy of ``versiontools_support.py`` file in your
source tree. This file will be needed by your users that don't have
versiontools to still be able to run setup.py to install your package.

Update MANIFEST.in
^^^^^^^^^^^^^^^^^^
You will need to update (or create) ``MANIFEST.in`` to ensure that each
source distribution you make with ``setup.py sdist`` will ship a copy of the
support file. All that you have to do is to append this line to your
``MANIFEST.in``::

    include versiontools_support.py

Patch setup.py
^^^^^^^^^^^^^^
Edit your ``setup.py`` to have code that looks like this::

    import versiontools_support

    setup(
        version = ":versiontools:your_package",
    )

The trick here is to use a magic value for version keyword. The format of that
magic value is::

    ":versiontools:" - a magic string that versiontools matches
    your_package     - name of your package or module to import
    ":"              - colon separating package from identifier (optional)
    identifier       - Object to import from your_package. (optional)
                       Can be omitted if equal to __version__.

This will make versiontools use :meth:`versiontools.format_version()` on
whatever `your_package.__version__` contains. Since your `__version__` is a
tuple as described above you'll get a correctly formatted version
identifier.

This code will ensure that:

#. Your package will use version tools
#. Your package will correctly install via pip

Developing with versiontools
============================

While you are working on the next version of your project you should
make sure that ``releaselevel`` is set to ``"dev"``. This will (if you
have proper vcs integration in place) allow you to get the most benefit.

Releases
========

Each time you make a release (with setup.py sdist or any bdist commands) make
sure to change the ``releaselevel`` to something other than ``"dev"``. You can
use the following strings:

* ``"alpha"``
* ``"beta"``
* ``"candidate"``
* ``"final"``
