# -*- coding: utf-8 -*-
#******************************************************************************
# Begin everyapp.bootstrap virtualenv bootstrap customization code.

#---Header---------------------------------------------------------------------

# This file is part of everyapp.bootstrap.
# Copyright (C) 2010-2012 Krys Lawrence
#
# everyapp.bootstrap is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# everyapp.bootstrap is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
# **Licensing clarification**
#
# When this customization code is included in virtualenv's generated bootstrap
# script, the above copyright and licensing information applies to the script
# as a whole since it is considered a derived work.  Since virtualenv itself is
# licensed under the MIT licence, the combined work is GPL compatible and the
# GPL takes precedence.  For details the virtualenv project and it's licence
# see: http://pypi.python.org/pypi/virtualenv.

"""Customization code for virtualenv_ bootstrap scripts.

This code is only useful when included in a virtualenv_ bootstrap script.  It
uses virtualenv_'s supported hooks to enhance and modify the script's
behaviour.

.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _pip: http://pypi.python.org/pypi/pip
.. _easy_install: http://packages.python.org/distribute/easy_install.html
.. _distribute: http://pypi.python.org/pypi/distribute

.. |doc/BOOTSTRAP.PY.txt| replace:: :ref:`bootstrap.py`
.. |doc/BOOTSTRAP.CFG.txt| replace:: :ref:`bootstrap.cfg`
.. |optparse.Values| replace:: :mod:`optparse`\ *.Values*

"""

# Remember: This code should work under at least Python 2.4, if not earlier
#           versions, as that is what virtualenv itself supports.


#---Imports--------------------------------------------------------------------

#---  Standard library imports
# Note: Some functions are implicitly provided by imports in the generated
#       virtualenv bootstrap script (e.g. sys, os, os.path.join, logger, and
#       call_process).
from os.path import exists

#---  Third-party imports

#---  Project imports


#---Globals--------------------------------------------------------------------

#: File name (or path) for the default configuration file.
#:
#: .. NOTE::
#:
#:    During script generation, the original customization source has a
#:   ``DEFAULT_CONFIG_FILE_NAME`` token (with surrounding ``$`` characters)
#:   which is replaced with the relative path to the bootstrap configuration
#:   file when it is included in the bootstrap script.
#
# Meta-Note: The above note is written in such a way as to make sense both in
#            the original source module as well as in the generated bootstrap
#            script. :)
#:
_DEFAULT_CONFIG_FILE_NAME = '$DEFAULT_CONFIG_FILE_NAME$'

#: Mapping of supported installer names to their handler functions.
# This is populated during module initialization.
_supported_installers = {}

#: Mapping of configuration file sections and their lines of text.
#:
#: The lines are interpreted differently depending on the section.  This is why
#: :mod:`ConfigParser` is not used.
#:
# This is stored globally because it is read before command-line arguments are
# fully processed and there is no way to pass on this data to subsequent
# virtualenv hook functions.
_config = {}


#---Functions------------------------------------------------------------------

def extend_parser(parser):
    """virtualenv_ hook to extend the command-line parser.

    This is also where the configuration file is read and overridden default
    option values are set.

    :parameter optparse.OptionParser parser: The command-line parser to use.

    .. SEEALSO::

       |doc/BOOTSTRAP.PY.txt| for the full list of command-line options,
       including the new and modified ones.

    .. SEEALSO::

       |doc/BOOTSTRAP.CFG.txt| for details on the configuration file and
       overriding default option values.

    """
    parser.set_usage('%prog [OPTIONS] [CONFIG_FILE]')
    parser.remove_option('--no-site-packages')
    parser.remove_option('--distribute')
    parser.add_option(
      '--setuptools',
      dest='use_setuptools',
      action='store_true',
      help='Use setuptools instead of distribute.')
    parser.remove_option('--unzip-setuptools')
    parser.add_option(
      '--zip-setuptools',
      dest='zip_setuptools',
      action='store_true',
      help='Do not unzip setuptools (or distribute) when installing it.')
    parser.add_option(
      '--pip-install-options',
      dest='pip_install_options',
      metavar='OPTIONS',
      action='store',
      help='Additional command line options for "pip install". (Default is '
        '"".)')
    parser.add_option(
      '--easy_install-options',
      dest='easy_install_options',
      metavar='OPTIONS',
      action='store',
      help='Additional command line options for "easy_install". (Default is '
        '"-Z".)')
    parser.set_defaults(
      pip_install_options='',
      easy_install_options='-Z')
    _load_bootstrap_config()
    if 'options' in _config:
        parser.set_defaults(**_config['options'])


def _load_bootstrap_config():
    """Find and load the bootstrap configuration file.

    This function either reads in the manually specified configuration file, or
    looks for the default configuration file in the current directory or in the
    :file:`etc` sub-directory of the current directory.

    """
    global _config
    file_paths, is_manually_specified = _get_config_file_paths()
    for file_path in file_paths:
        if exists(file_path):
            # Cannot use logger, not initialized yet.
            print 'Found %s' % file_path
            try:
                file_ = open(file_path)
                _config = _parse_bootstrap_config(file_)
            finally:
                file_.close()
            break
    else:
        if is_manually_specified:
            print >> sys.stderr, ('WARNING: Config file %s not found.' %
              file_paths[0])


def _get_config_file_paths():
    """Return paths in which to search for the bootstrap configuration file.

    This function first looks on the command-line for a manually specified
    configuration file.  If one is given, then that is returned as the only
    file path in which to search.  Otherwise, the returned file paths are the
    default configuration file name in the current directory and in the
    :file:`etc` sub-directory of the current directory.

    :returns: The file paths in which to search and whether or not the path was
      specified manually.
    :rtype: iterable of `tuple`\s of (`str`, `bool`)

    """
    file_name = _DEFAULT_CONFIG_FILE_NAME
    file_paths = [file_name, join('etc', file_name)]
    is_manually_specified = False
    for arg in sys.argv[1:]:
        if arg.startswith('-'):
            continue
        is_manually_specified = True
        file_paths = [arg]
        break
    return file_paths, is_manually_specified


def _parse_bootstrap_config(file_):
    """Parse bootstrap configuration from the given open file.

    The configuration file should consist of section headers in the form of
    :samp:`[{section_name}]`, followed by lines of text in the appropriate
    format for the section.

    For example the ``[easy_install]`` section would contain distributions,
    with optional version specifiers, to install with :program:`easy_install`.

    There is no special line processing except for the ``[options]`` section,
    which expects lines in the form of :samp:`{option_name} = {value}` with any
    amount of space around the equal sign.  This section is automatically
    parsed into a sub-dictionary instead of a list.

    Also all blank lines and lines starting with a ``#`` (i.e. comments) are
    ignored.

    :returns: A configuration dictionary with section names as keys and text
      lines as values (except for the ``options`` key, see above.)
    :rtype: `dict` of {`str`: iterable of `str`}

    """
    config = {}
    current_section = None
    for line in file_:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1]
            config.setdefault(current_section, [])
            continue
        if current_section == 'options':
            option, value = line.split('=', 1)
            option = option.strip()
            value = value.strip()
            line = (option, value)
        if current_section is None:
            print >> sys.stderr, ('A section header is required before the '
              'first non-blank, non-comment, line in the config file.')
            sys.exit(200)
        config[current_section].append(line)
    if 'options' in config:
        config['options'] = dict(config['options'])
    return config


def adjust_options(options, args):
    """virtualenv_ hook to adjust the parsed command-line options and args.

    This function just sets the home directory to the current directory and
    maps some of the new command-line options to their original counterparts.

    :parameter options: The parsed command-line options.
    :type options: |optparse.Values|
    :parameter tuple args: Any positional arguments from the command-line.

    .. SEEALSO::

       |doc/BOOTSTRAP.PY.txt| for the full list of command-line options,
       including the new and modified ones.

    """
    home_dir = '.'
    args[:] = [home_dir]
    options.use_distribute = not options.use_setuptools
    options.unzip_setuptools = not options.zip_setuptools


def after_install(options, home_dir):
    """virtualenv_ hook for post-bootstrap customization.

    This function is responsible for all the steps that take place after the
    virtual environment has been created.  Specifically, this function installs
    all the distributions and runs all the commands specified in the
    configuration file.

    :parameter options: The parsed command-line options.
    :type options: |optparse.Values|
    :parameter str home_dir: The home directory of the virtual environment.
      (This is always set to ``'.'``).

    .. SEEALSO::

       |doc/BOOTSTRAP.CFG.txt| for details on how to specify what distributions
       to install and what commands to run.

    """
    _install_requirements(options)
    _run_commands(options)


def _install_requirements(options):
    """Install all additional requirements specified in the configuration file.

    This function iterates over all the configuration sections that match a
    supported distribution installer (e.g. pip_ and easy_install_) and installs
    all the distributions listed in those sections with the appropriate
    installer.

    :parameter options: The parsed command-line options.
    :type options: |optparse.Values|

    .. SEEALSO::

       :func:`_pip_install` and :func:`_easy_install` for the specific details
       on how those two installers are invoked.

    """
    for section_name, section_data in _config.items():
        if section_name in _supported_installers and section_data:
            _print_distributions(section_name, section_data)
            installer = _supported_installers[section_name]
            installer(section_data, options)


def _print_distributions(installer_name, distribution_specs):
    """Notify the user that the given distributions will be installed.

    :parameter str installer_name: The name of the installer program that will
      be used to install the distributions (e.g. ``pip`` or ``easy_install``).
    :parameter distribution_specs: The distribution specifiers of the
      distributions to be installed (e.g. ``['pep8 (>=0.5,<0.6)']``).
    :type distribution_specs: iterable of `str`

    """
    logger.notify('Using %s to install the following distributions:' %
      installer_name)
    logger.indent += 2
    for distribution_spec in distribution_specs:
        logger.notify(distribution_spec)
    logger.indent -= 2


def _pip_install(distribution_specs, options):
    """Install distributions using pip_.

    Default options for :program:`pip install` can be overridden in the
    configuration file and those can be additionally overridden via
    command-line argument.

    :parameter distribution_specs: The distribution specifiers of the
       distributions to be installed (e.g. ``['pep8 (>=0.5,<0.6)']``).
    :type distribution_specs: iterable of `str`
    :parameter options: The parsed command-line options.
    :type options: |optparse.Values|

    .. SEEALSO::

       |doc/BOOTSTRAP.PY.txt| for details on how to override the default
       :program:`pip install` options from the command-line.

    .. SEEALSO::

       |doc/BOOTSTRAP.CFG.txt| for details on how to override the default
       :program:`pip install` options from the configuration file.

    .. SEEALSO::

       :func:`_convert_pep314_versions` for details on distribution specifier
       formats.

    """
    installer_opts = 'install ' + options.pip_install_options
    distribution_specs = _convert_pep314_versions(distribution_specs)
    _install_distribution('pip', installer_opts, distribution_specs)


def _easy_install(distribution_specs, options):
    """Install distributions using easy_install_.

    Default options for :program:`easy_install` can be overridden in the
    configuration file and those can be additionally overridden via
    command-line argument.

    :parameter distribution_specs: The distribution specifiers of the
       distributions to be installed (e.g. ``['pep8 (>=0.5,<0.6)']``).
    :type distribution_specs: iterable of `str`
    :parameter options: The parsed command-line options.
    :type options: |optparse.Values|

    .. SEEALSO::

       |doc/BOOTSTRAP.PY.txt| for details on how to override the default
       :program:`easy_install` options from the command-line.

    .. SEEALSO::

       |doc/BOOTSTRAP.CFG.txt| for details on how to override the default
       :program:`easy_install` options from the configuration file.

    .. SEEALSO::

       :func:`_convert_pep314_versions` for details on distribution specifier
       formats.

    """
    distribution_specs = _convert_pep314_versions(distribution_specs)
    _install_distribution('easy_install', options.easy_install_options,
      distribution_specs)


def _convert_pep314_versions(distribution_specs):
    """Convert :pep:`314` distribution specifiers to distribute_/pip_ format.

    :pep:`314` and :pep:`345` both dictate that distribution requirement
    specifications should include version indicators in parentheses (``()``).
    E.g.::

      everyapp.bootstrap (>=0.1,<0.2)

    :program:`easy_install` and :program:`pip`, however do not support
    parentheses.  This function removes them and any separating space.  E.g.::

      everyapp.bootstrap>=0.1,<0.2

    If any distribution specifier is in the second form already, it is left
    unchanged, as are distribution names without specified versions.

    :parameter distribution_specs: The distribution specifiers to convert.
    :type distribution_specs: iterable of `str`
    :returns: A new iterable of converted distribution specifiers.
    :rtype: iterable of `str`

    """
    converted_specs = []
    for distribution_spec in distribution_specs:
        if '(' in distribution_spec and ')' in distribution_spec:
            for character in ' ()':
                distribution_spec = distribution_spec.replace(character, '')
        converted_specs.append(distribution_spec)
    return converted_specs


def _install_distribution(installer_cmd, installer_opts, distribution_specs):
    """Install distributions using the given installer.

    The installer program must be in the virtual environment's :file:`bin` or
    :file:`Scripts` directory.

    :parameter str installer_cmd: The installer program to run (e.g. ``pip``).
    :parameter str installer_opts: Any additional command-line options to pass
      to the installer.
    :parameter distribution_specs: The distribution specifiers of the
       distributions to be installed.
    :type distribution_specs: iterable of `str`

    """
    bin_dir = _get_bin_dir()
    # Distribution specifiers should not need to be quoted, even if they
    # contain > or < because call_subprocess does not run the commands through
    # a shell.  In fact quoting specifiers breaks the code under Linux.  This
    # needs to be verified on Windows, however.
    full_install_cmd = (
      [join(bin_dir, installer_cmd)] +
      installer_opts.split() +
      distribution_specs)
    call_subprocess(full_install_cmd)


def _get_bin_dir(trailing_slash=False):
    """Return the platform-specific name for the :file:`bin` directory.

    On POSIX systems it is :file:`bin` and on Windows systems it is
    :file:`Scripts`.

    :parameter bool trailing_slash: If `True`, a platform-specific trailing
      slash will be append to the returned directory name.
    :rtype: `str`

    """
    if sys.platform == 'win32':
        bin_dir = 'Scripts'
    else:
        bin_dir = 'bin'
    if trailing_slash:
        return bin_dir + os.sep
    return bin_dir


def _run_commands(options):
    """Run all additional commands specified in the configuration file.

    Commands can use the token ``$bin$`` to represent the platform-specific
    :file:`bin` directory, including a trailing slash.

    :parameter options: The parsed command-line options.
    :type options: |optparse.Values|

    .. NOTE::

       The commands are run in a sub-process but are not run through a shell
       (e.g. :command:`bash`).  This means shell features are not available.

    """
    if 'commands' not in _config or not _config['commands']:
        return
    logger.notify('Running post-bootstrap commands...')
    bin_dir = _get_bin_dir(trailing_slash=True)
    for command in _config['commands']:
        call_subprocess(command.replace('$bin$', bin_dir).split())


#---Classes--------------------------------------------------------------------


#---Module initialization------------------------------------------------------

_supported_installers['pip'] = _pip_install
_supported_installers['easy_install'] = _easy_install


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------

# End of everyapp.bootstrap customization code.
#******************************************************************************
