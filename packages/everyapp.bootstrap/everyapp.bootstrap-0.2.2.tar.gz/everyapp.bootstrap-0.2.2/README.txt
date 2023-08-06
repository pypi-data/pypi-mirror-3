.. This file is part of everyapp.bootstrap.
.. Copyright (C) 2010-2012 Krys Lawrence
..
.. everyapp.bootstrap is free software: you can redistribute it and/or modify
.. it under the terms of the GNU General Public License as published by the
.. Free Software Foundation, either version 3 of the License, or (at your
.. option) any later version.
..
.. everyapp.bootstrap is distributed in the hope that it will be useful, but
.. WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
.. or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
.. more details.
..
.. You should have received a copy of the GNU General Public License along with
.. this program.  If not, see <http://www.gnu.org/licenses/>.

##################
everyapp.bootstrap
##################

.. contents::

.. about
.. _about:

About
=====

*everyapp.bootstrap* provides an enhanced and customizable virtualenv_
bootstrap script.  It aims to make it easy to bootstrap a virtual environment
for your project.

This project includes a tool to generate a bootstrap script that will
automatically create the virtual environment when run.  By placing the
bootstrap script in the root of your project's source tree and making it
available on a fresh checkout/clone from your version control repository, you
make it easy for anyone who wants to hack on your project (including yourself!)
to work in a consistent development environment.

Additionally, this enhanced bootstrap script can read a configuration file and
perform additional actions beyond just creating a bare-bones virtual
environment.

.. features
.. _features:

Features
========

* Easy creation of a virtualenv_ bootstrap script.
* Better defaults for virtualenv_, like using distribute_ instead of
  setuptools_ and always unzipping EGGs.
* Easy customization of the bootstrapping process.
* Automatic installation of additional distributions using pip_ and/or
  easy_install_.
* Easy customization of pip_ and easy_install_ behaviour during distribution
  installation.
* Automatic execution of additional commands after the bootstrapping is
  complete.
* Adherence to `Semantic Versioning <http://semver.org/spec/v1.0.0.html>`_ in
  order to be a well behaved dependency.

.. status
.. _status:

Status
======

This project is very young and the code should be considered *Alpha* quality.
It has been minimally tested on Linux and Windows, under Python_ 2.6 and 2.7,
but has not yet been seriously tested on any platform.

That said, it is largely just a wrapper and a few customizations on the
production-grade virtualenv_ project [#ve1]_, so it should be reasonably
stable.  It should also be mostly feature complete.

.. installation

Installation
============

The easiest way to install this distribution is::

  pip install everyapp.bootstrap

or::

  easy_install everyapp.bootstrap

For additional information on installing and upgrading, see the `installation
documentation`_. |(in doc/INSTALL.txt)|

Basic Usage
===========

In your project's root directory, run::

  mkbootstrap

This will generate a ``bootstrap.py`` script and a ``bootstrap.cfg``
configuration file.  Edit ``bootstrap.cfg`` as desired, then run::

  python bootstrap.py

This will create the virtual environment in the root directory for your
project.

For additional bootstrap script options and usage information see the `usage
documentation`_. |(in doc/USAGE.txt)|

.. documentation and support
.. _documentation_and_support:

Documentation and Support
=========================

**Home page:**
  http://pypi.python.org/pypi/everyapp.bootstrap
**Downloads:**
  http://pypi.python.org/pypi/everyapp.bootstrap#downloads
**Documentation:**
  |See doc/README.txt|, or online in the following formats:
  `HTML <http://packages.python.org/everyapp.bootstrap>`_,
  `EPUB
  <http://packages.python.org/everyapp.bootstrap/_static/everyapp.bootstrap.epub>`_,
  and `PDF
  <http://packages.python.org/everyapp.bootstrap/_static/everyapp.bootstrap.pdf>`_.
**Bug/issue tracker:**
  http://bitbucket.org/everyapp/bootstrap/issues
**Source code repository:**
  http://bitbucket.org/everyapp/bootstrap

.. contributing
.. _contributing:

Contributing
============

There is always room for improvement in this project and contributions are
certainly welcome.  The easiest way to contribute is simply to file a bug
report in the `issue tracker`_ whenever you find a problem or want to suggest
an improvement.

If you would like to participate in a more substantial way, check out the
`issue tracker`_, the `list of known bugs`_ |(in doc/BUGS.txt)| and the `To Do
list`_ |(in doc/TODO.txt)| to find out about the work that still needs to be
done.

.. NOTE::

   If you submit a bug report, patch or other code, you automatically agree to
   licence the contribution.  See the `licensing information`_  |(in
   doc/LICENCE.txt)| for details on contribution licensing.

See also the `developer documentation`_ |(in doc/HACKING.txt)| for more
information on developing/hacking on *everyapp.bootstrap*.

.. licence

Licence
=======

*everyapp.bootstrap* is licensed under the `GNU General Public License version
3`_ or later (GPLv3+).  This is free software: you are free to change and
redistribute it under certain conditions.  There is NO WARRANTY, to the extent
permitted by law.  For full licensing information, see the `licensing
information`_. |(in doc/LICENCE.txt)|

Credits
=======

*everyapp.bootstrap* was created by Krys Lawrence <everyapp at krys ca>.

See the `list of authors`_ |(in doc/AUTHORS.txt)| for the full list of
contributors to this project.

This project would not be what it is without the efforts of many people.
Acknowledgements for their efforts can be found in the `list of
acknowledgements`_. |(in doc/THANKS.txt)|

.. footnotes_start
.. rubric:: Footnotes

.. [#ve1] Strictly speaking, virtualenv_ classifies itself as Beta
   quality, but many consider it to be production-grade.

.. footnotes_end


.. If you are reading this file in text form, you can ignore everything below.
.. ----------------------------------------------------------------------------

.. |See doc/README.txt| replace:: In the source distribution

.. These are hacks get around the fact that PyPI does not properly render links
.. in substitutions.
.. |(in doc/INSTALL.txt)| replace:: \ \
.. |(in doc/USAGE.txt)| replace:: \ \
.. |(in doc/BUGS.txt)| replace:: \ \
.. |(in doc/TODO.txt)| replace:: \ \
.. |(in doc/LICENCE.txt)| replace:: \ \
.. |(in doc/HACKING.txt)| replace:: \ \
.. |(in doc/AUTHORS.txt)| replace:: \ \
.. |(in doc/THANKS.txt)| replace:: \ \

.. _installation documentation:
   http://packages.python.org/everyapp.bootstrap/install.html
.. _usage documentation:
   http://packages.python.org/everyapp.bootstrap/usage/
.. _list of known bugs:
   http://packages.python.org/everyapp.bootstrap/bugs.html
.. _To Do list:
   http://packages.python.org/everyapp.bootstrap/development/todo.html
.. _licensing information:
   http://packages.python.org/everyapp.bootstrap/licence.html
.. _developer documentation:
   http://packages.python.org/everyapp.bootstrap/development/
.. _list of authors:
   http://packages.python.org/everyapp.bootstrap/credits/authors.html
.. _list of acknowledgements:
   http://packages.python.org/everyapp.bootstrap/credits/thanks.html

.. footer_start

.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _distribute: http://pypi.python.org/pypi/distribute
.. _setuptools: http://pypi.python.org/pypi/setuptools
.. _pip: http://pypi.python.org/pypi/pip
.. _easy_install: http://packages.python.org/distribute/easy_install.html
.. _Python: http://python.org
.. _issue tracker: http://bitbucket.org/everyapp/bootstrap/issues
.. _GNU General Public License version 3: http://www.gnu.org/licenses/gpl.html
