# -*- coding: utf-8 -*-

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

"""Provides the :ref:`mkbootstrap` command.

.. _virtualenv: http://pypi.python.org/pypi/virtualenv

.. |doc/MKBOOTSTRAP.txt| replace:: :ref:`mkbootstrap`
.. |optparse.OptionGroup| replace:: :mod:`optparse`\ *.OptionGroup*
.. |optparse.Values| replace:: :mod:`optparse`\ *.Values*

"""

# Remember: This code should work under at least Python 2.4, if not earlier
#           versions, as that is what virtualenv itself supports.


#---Imports--------------------------------------------------------------------

#---  Standard library imports
import optparse
import os
from os import path

#---  Third-party imports
import pkg_resources
import virtualenv

#---  Project imports


#---Globals--------------------------------------------------------------------

__ALL__ = [b'main']

#: Program description displayed in :option:`mkbootstrap --help`.
_DESCRIPTION = """\
Generate an enhanced virtualenv bootstrap script.
"""

#: Program epilogue displayed in :option:`mkbootstrap --help`.
_EPILOGUE = """\
Report bugs to:
http://bitbucket.org/everyapp/bootstrap/issues

everyapp.bootstap home page:
http://pypi.python.org/pypi/everyapp.bootstrap

Documentation:
http://packages.python.org/everyapp.bootstrap
"""

#: Program version template displayed in :option:`mkbootstrap --help`.
#:
#: In the template ``%%prog`` will be replaced with the program name as it used
#: on the command-line.  The first ``%s`` is replaced with the distribution
#: name and the second ``%s`` is replaced with the program's version.
#: This is in line with GNU recommendations.
#:
_VERSION_TEMPLATE = """\
%%prog (%s) %s
Copyright (C) 2010-2012 Krys Lawrence
Licence GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
"""

#: :option:`mkbootstrap -v` option help.
#:
#: This is a replacement of the built-in help text to include proper
#: capitalization and punctuation.
#:
_VERSION_HELP = "Show program's version number and exit."

#: :option:`mkbootstrap --help` option help.
#:
#: This is a replacement of the built-in help text to include proper
#: capitalization and punctuation.
#:
_HELP_HELP = 'Show this help message and exit.'

#: :option:`mkbootstrap -s` option help.
_SCRIPT_NAME_HELP = """\
The name of the bootstrap python script to generate.  (Default: %default)
"""

#: :option:`mkbootstrap -c` option help.
_CONFIG_NAME_HELP = """\
The name of the bootstrap configuration file to generate.  (Default: Same as
script name but with a .cfg extension.)
"""

#: :option:`mkbootstrap -e` option help.
_ETC_HELP = """\
Put the generated configuration file in an etc sub-directory instead of in the
current directory.
"""

#: :option:`mkbootstrap -n` option help.
_NO_CUSTOMIZATION_HELP = """\
Only generate a plain vanilla virtualenv bootstrap script without any
customizations or configuration file.
"""

#: :option:`mkbootstrap -S` option help.
_CUSTOMIZE_SCRIPT_HELP = """\
Use your own virtualenv customization code instead of that provided by this
program.  (The $DEFAULT_CONFIG_FILE_NAME$ token in your script will be replaced
with the name of the config file.
"""

#: :option:`mkbootstrap -C` option help.
_DEFAULT_CONFIG_HELP = """\
Use your own default configuration file instead of the one provided by this
program.  Note: A new configuration file will not be generated if an existing
one is found in the current directory or in an etc sub-directory.
"""


#---Functions------------------------------------------------------------------

def main(args=None, program_name=None):
    """Main program for the :ref:`mkbootstrap` command.

    This function will generate the virtualenv_ bootstrap script in the current
    directory, and optionally a default configuration file as well.

    :parameter args: The command-line arguments to use.  If it is :obj:`None`,
      then ``sys.args[1:]`` will be used.
    :type args: :obj:`tuple` of :obj:`str`, or :obj:`None`
    :parameter program_name: The name of the program as it appears on the
      command-line.  If it is :obj:`None`, then ``sys.argv[0]`` is used.
    :type program_name: :obj:`str`, or :obj:`None`

    .. SEEALSO::

       |doc/MKBOOTSTRAP.txt| for details on the accepted command-line
       arguments.

    """
    parser = _build_parser(program_name)
    options = _parse_options(parser, args)
    _create_bootstrap_script(options)
    _create_bootstrap_config(options)


def _build_parser(program_name=None):
    """Return the command-line parser.

    :parameter program_name: The name of the program as it appears on the
      command-line.  If it is :obj:`None`, then ``sys.argv[0]`` is used.
    :type program_name: :obj:`str`, or :obj:`None`
    :rtype: :class:`optparse.OptionParser`

    .. SEEALSO::

       |doc/MKBOOTSTRAP.txt| for details on the supported command-line options.

    """
    project_name = 'everyapp.bootstrap'
    version = pkg_resources.get_distribution(project_name).version
    parser = optparse.OptionParser(
      prog=program_name,
      description=_DESCRIPTION,
      epilog=_EPILOGUE,
      version=_VERSION_TEMPLATE % (project_name, version),
    )
    parser.add_option_group(_build_advanced_options_group(parser))
    # Fix up the provided option help messages to include proper capitalization
    # and punctuation.
    parser.get_option('--version').help = _VERSION_HELP
    parser.get_option('--help').help = _HELP_HELP
    parser.add_option('-s', '--script-name',
      metavar='FILE_NAME',
      default='bootstrap.py',
      help=_SCRIPT_NAME_HELP,
    )
    parser.add_option('-c', '--config-name',
      metavar='FILE_NAME',
      help=_CONFIG_NAME_HELP,
    )
    parser.add_option('-e', '--etc',
      action='store_true',
      help=_ETC_HELP,
    )
    parser.add_option('-n', '--no-customization',
      action='store_true',
      help=_NO_CUSTOMIZATION_HELP,
    )
    return parser


def _build_advanced_options_group(parser):
    """Return the Advanced Options group for the command-line parser.

    :parameter optparse.OptionParser parser: The command-line parser to which
      the group belongs.
    :rtype: |optparse.OptionGroup|

    .. SEEALSO::

       |doc/MKBOOTSTRAP.txt| for details on the advanced command-line options.

    """
    group = optparse.OptionGroup(parser, 'Advanced Options')
    group.add_option('-S', '--customize-script',
      metavar='FILE_NAME',
      help=_CUSTOMIZE_SCRIPT_HELP,
    )
    group.add_option('-C', '--default-config',
      metavar='FILE_NAME',
      help=_DEFAULT_CONFIG_HELP,
    )
    return group


def _parse_options(parser, args=None):
    """Parse the command-line arguments.

    :parameter optparse.OptionParser parser: The command-line parser to use.
    :parameter args: The command-line arguments to use.  If it is :obj:`None`,
    then ``sys.args[1:]`` will be used.
    :type args: :obj:`tuple` of :obj:`str`, or :obj:`None`
    :returns: The parsed option values.
    :rtype: optparse.Values

    .. NOTE::

       Positional command-line arguments are not supported.

    .. SEEALSO::

       :func:`_build_parser` for details about creating the parser.

    """
    options, _ = parser.parse_args(args)
    if not options.config_name:
        options.config_name = path.splitext(options.script_name)[0] + '.cfg'
    return options


def _create_bootstrap_script(options):
    """Generate the virtualenv_ bootstrap script in the current directory.

    :parameter options: The options values used to configure the program.
    :type options: |optparse.Values|

    .. SEEALSO::

       :func:`_parse_options` for details about creating the configuration
       option values.

    """
    if options.no_customization:
        customize_source = ''
    else:
        customize_source = _get_customize_source(options)
    bootstrap_source = virtualenv.create_bootstrap_script(customize_source)
    script_file = open(options.script_name, 'wb')
    try:
        script_file.write(bootstrap_source)
    finally:
        script_file.close()


def _get_customize_source(options):
    """Return the customization source code.

    If a customization script file has been specified in the options, thne it
    is read in and returned.  Otherwise, the default customization script
    provided by this package is returned.

    Also, if the script contains the token ``$DEFAULT_CONFIG_FILE_NAME$``, it
    is replaced with the path of the bootstrap configuration file as specified
    in the given options.

    :parameter options: The options values used to configure the program.
    :type options: |optparse.Values|

    .. SEEALSO::

       :func:`_parse_options` for details about creating the configuration
       option values.

    """
    file_name = options.customize_script
    if file_name:
        source_file = open(file_name, 'rb')
        try:
            source = source_file.read()
        finally:
            source_file.close()
    else:
        source = pkg_resources.resource_string(__name__, 'customize.py')
    source = source.replace('$DEFAULT_CONFIG_FILE_NAME$', options.config_name)
    return source


def _create_bootstrap_config(options):
    """Generate the configuration file to be used by the bootstrap script.

    If the given options indicate not to generate a configuration file, no file
    will be generated.  Otherwise, a configuration file will either be
    generated in the current directory or in an :file:`etc` sub-directory of
    the current directory, depending on the given options.  The :file:`etc`
    sub-directory will automatically be created if necessary.

    Also, if a configuration file already exists in either of the above two
    locations, it will not be overwritten and a new configuration file will not
    be generated.

    :parameter options: The options values used to configure the program.
    :type options: |optparse.Values|

    .. SEEALSO::

       :func:`_parse_options` for details about creating the configuration
       option values.

    """
    file_name = options.config_name
    etc_dir = 'etc'
    etc_file_name = path.join(etc_dir, file_name)
    default_config = options.default_config
    if options.no_customization:
        return
    if path.exists(file_name) or path.exists(etc_file_name):
        return
    if default_config:
        source = open(default_config, 'rb').read()
    else:
        source = pkg_resources.resource_string(__name__, 'bootstrap.cfg')
        source = source.split('=== BEGIN BOOTSTRAP.CFG ===')[-1].lstrip()
    if options.etc:
        if not path.exists(etc_dir):
            os.makedirs(etc_dir)
        file_name = etc_file_name
    config_file = open(file_name, 'wb')
    try:
        config_file.write(source)
    finally:
        config_file.close()


#---Classes--------------------------------------------------------------------


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
