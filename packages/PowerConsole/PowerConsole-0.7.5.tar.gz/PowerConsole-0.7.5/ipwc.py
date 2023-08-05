#!/usr/bin/python
#
#   PROGRAM:     PowerConsole
#   MODULE:      ipwc.py
#   DESCRIPTION: PowerConsole Main script - CLI console version
#
#  The contents of this file are subject to the Initial
#  Developer's Public License Version 1.0 (the "License");
#  you may not use this file except in compliance with the
#  License. You may obtain a copy of the License at
#  http://www.firebirdsql.org/index.php?op=doc&id=idpl
#
#  Software distributed under the License is distributed AS IS,
#  WITHOUT WARRANTY OF ANY KIND, either express or implied.
#  See the License for the specific language governing rights
#  and limitations under the License.
#
#  The Original Code was created by Pavel Cisar
#
#  Copyright (c) 2007-2009 Pavel Cisar <pcisar@users.sourceforge.net>
#  and all contributors signed below.
#
#  All Rights Reserved.
#  Contributor(s): ______________________________________.

"""ipwc is bare bone CLI version of PowerConsole."""

import pkg_resources
from pwc.interpreter import Console
from pwc.release import *
from optparse import OptionParser
import itertools

import sys


def main():
    """The main function for the CLI PowerConsole program."""

    def package_filter(package):
        if options.load_package:
            return package.name in options.load_package
        else:
            return package.name not in options.exclude_package

    # create list of installed packages
    packages = []
    for package in pkg_resources.iter_entry_points("powerconsole.package"):
        try:
            p = package.load()()
            packages.append(p)
        except:
            ## ToDo: Handle exceptions in command initialization
            raise

    # Process options
    parser = OptionParser(conflict_handler="resolve",
                          version='%s v%s' % (name,version))
    parser.add_option('-l','--load-package',action='append',
                      metavar='PACKAGE',help='Load only specified package')
    parser.add_option('-e','--exclude-package',action='append',
                      metavar='PACKAGE',help='Do not load specified package')
    parser.add_option('--debug-calls',action='store_true',
                      help='Print debug information about command calls')
    parser.add_option('--debug-grammar',action='store_true',
                      help='Print debug information about command parsing')
    parser.set_defaults(load_package=[],exclude_package=[],debug_calls=False,
                        debug_grammar=False)
    # Add extension options
    for package_config in (getattr(p,'add_options') for p 
                           in packages if hasattr(p,'add_options')):
        try:
            package_config(parser)
        except:
            ## ToDo: Handle exceptions in extender call
            raise
    (options,args) = parser.parse_args()
    parser.destroy()
    
    # Filter out unwanted packages
    packages = [pkg for pkg in packages if package_filter(pkg)]
    # Process extension options
    for package_config in (getattr(p,'process_options') for p 
                           in packages if hasattr(p,'process_options')):
        try:
            package_config(options,args)
        except:
            ## ToDo: Handle exceptions in extender call
            raise

    package_names = ['%s(%s)' % (pkg.name,pkg.version) for pkg in packages]
    if package_names:
        env = 'Installed packages: ' + ', '.join(package_names)
    else:
        env = 'No extensions installed'
    hdr = '%s v%s [CLI version]\nPython %s on %s\n\n%s\n\n%s\n'

    console = Console(packages)
    try:
        import readline
    except ImportError:
        pass
    console.debug_calls = options.debug_calls
    if options.debug_grammar:
        console.full_grammar.setDebug()

    console.interact(hdr % (name,version,sys.version,sys.platform,env,
              'Type "help" for more information.'))

if __name__ == '__main__':
    main()
