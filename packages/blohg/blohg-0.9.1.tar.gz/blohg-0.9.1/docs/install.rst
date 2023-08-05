Installing blohg
================

These are some of the ways to install blohg at your system. blohg is currently
tested on Linux_ and Windows_, but should works properly in any Operating
System capable to run Flask_ powered applications.

blohg is known to work on Python 2.6 and 2.7. 

blohg is available at the *Python Package Index* (PyPI_):

http://pypi.python.org/pypi/blohg

.. _Linux: http://kernel.org/
.. _Windows: http://windows.microsoft.com/
.. _Flask: http://flask.pocoo.org/
.. _PyPI: http://pypi.python.org/


Manually
--------

Download the latest tarball from PyPI_, extract it and run::

   # python setup.py install


Using ``pip``/``easy_install``
------------------------------

To install blohg using ``pip``, type::

    # pip install blohg

Or using ``easy_install``, type::

    # easy_install blohg


Gentoo Linux
------------

There's a Gentoo_ ebuild available at the ``gentoo-x86`` tree. Install it
using::

    # emerge -av www-apps/blohg

.. _Gentoo: http://www.gentoo.org/


Windows
-------

You can install blohg easily on Windows using ``pip``/``easy_install``, but
it will try to build the Mercurial C extensions by default, and will fail
if you don't have a compiler installed. You may install a compiler, or just
install the pure Python implementation of Mercurial before install blohg,
using something like this inside a directory with Mercurial sources extracted::

    # python setup.py --pure install

