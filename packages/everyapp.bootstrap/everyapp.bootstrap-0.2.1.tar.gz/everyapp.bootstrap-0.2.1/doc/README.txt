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

####################
Documentation README
####################

This directory contains the documentation for the *everyapp.bootstrap* project.

To get started quickly, see ``INSTALL.txt`` and ``USAGE.txt``.

Conventions and Structure
=========================

The documentation is designed to be read in different formats (plain text,
HTML, PDF, etc.) and be easily readable on multiple platforms (Linux, Windows,
etc.).  To achieve that, the following conventions and structure are used:

* All files in this directory ending in ``.txt`` are documentation meant to be
  read in plain text.  This way no special tools are necessary to read the base
  documentation and file name traditions can be preserved.
* All files in the  ``source`` directory ending in ``.rst`` are source files
  for Sphinx to generate the other formats.
* The ``.rst`` files include the text from the ``.txt`` files.
* The ``.txt`` files can include some basic reStructuredText formatting used by
  Sphinx, but it should be kept to a minimum subset (mostly substitutions,
  links and certain directives).
* All files are UTF-8 encoded and use Windows line endings (\r\n).
* The line endings, along with the use of the ``.txt`` extension is necessary
  to achieve the broadest cross-platform ease of use.
* Files that are in CamelCase are automatically generated during the creation
  of the source distribution and are not tracked by version control.

File Descriptions
=================

The following are the major documentation files and their purpose:

AUTHORS.txt
  List of the project's authors and copyright holders.
BUGS.txt
  List of known bugs.
ChangeLog.txt
  The full commit log of all changes.  Only available in source distributions.
COPYING.txt
  The full licence text.
FAQ.txt
  List of frequently asked questions.
HACKING.txt
  Information on how to develop/hack on the code.
INSTALL.txt
  Information on how to install the project.
LICENCE.txt
  Copyright and licensing information for all components of the project.
NEWS.txt
  List of important changes in each release that could affect users.  This is
  more readable than the full ``ChangeLog.txt`` or Mercurial log.
README.txt
  An overview of the project's documentation.  This file.
THANKS.txt
  Credits and acknowledgements to those that have contributed to or helped
  shape this project.
TODO.txt
  List of remaining work to complete.
USAGE.txt
  Information on how to use the project.

Additional useful documentation can be found in the following files:

bootstrap.cfg.txt
  Full details on the format and options used in bootstrap.cfg-like files.
bootstrap.py.txt
  Full details on the options and usage of bootstrap.py.
glossary.txt
  Glossary of technical or unusual terms used in this project.
mkbootstrap.txt
  Full details on the options and usage of mkbootstrap.
related_projects.txt
  List of other projects that attempt to solve the same or similar problems.

Generating the Full Documentation
=================================

While the plain text version of the documentation provides the most relevant
information for getting started, the full documentation is best experienced in
one of the generated formats.  See ``HACKING.txt`` for instructions on how to
generate the full documentation in all supported formats.  Alternatively, you
can view the full documentation in HTML format online at
http://packages.python.org/everyapp.bootstrap.
