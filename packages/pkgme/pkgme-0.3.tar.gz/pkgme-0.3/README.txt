=====
pkgme
=====

The ``pkgme`` program is a framework for generating Debian packaging artifacts
from information gleaned from inspecting the code.  The framework takes care
of the common tasks, and knows about packaging in general.  It is extensible
so that programming language-specific conventions and rules can be supported.


Project information
===================

``pkgme`` development is `hosted on Launchpad`_.  Please see the project page
for downloads, bug reports, and accessing the latest code (available in the
Bazaar_ version control system).  You can also subscribe to the `pkgme mailing
list`_ for discussions on using and extending ``pkgme``.  The archives_ are
also available on-line.


.. _`hosted on Launchpad`: http://launchpad.net/pkgme
.. _Bazaar: http://bazaar.canonical.com
.. _`pkgme mailing list`: https://launchpad.net/~pkgme-devs
.. _archives: https://lists.launchpad.net/pkgme-devs/


Dependencies
============

In addition to the various Python modules documented in ``setup.py``,
``pkgme`` depends on ``devscripts`` and ``debhelper``.


Developers
==========

Right now, the best way to hack on ``pkgme`` is in a virtualenv_.  This allows
you to hack on ``pkgme`` in a clean environment, without touching or changing
your system Python.  You will need access to the internet in order to install
``pkgme`` into your virtualenv.  On Debian/Ubuntu, make sure you have the
`python-virtualenv` package installed, then do the following::

    % virtualenv /arbitrary/path
    % source /arbitrary/path/bin/activate
    % python setup.py develop
    <hack>

If you want to override the default location of the backends, set the
environment variable ``$PKGME_BACKEND_PATHS``.  This is a colon-separated list
of directories, for example:

    % export PKGME_BACKEND_PATHS=/pkgme/foo-backends:/pkgme/bar-backends
    % cd my-about-to-be-packaged-code
    % pkgme

When you're done, just run the ``deactivate`` command and blow away
`/arbitrary/path`.


Testing
-------

While in your virtualenv, you can run the full test suite like so::

    % python setup.py test


Building the documentation
--------------------------

If you have the Sphinx toolchain installed (on Debian/Ubuntu, the
python-sphinx package), you can build the documentation like so::

    % make html

You'll need to be in your virtualenv, and you should have installed ``pkgme``
in that virtualenv before trying to build the documentation.


.. _virtualenv: http://virtualenv.openplans.org/


Table of Contents
=================

.. toctree::
    :glob:

    *
..
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


