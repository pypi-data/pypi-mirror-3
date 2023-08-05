#
#   PROGRAM:     PowerConsole
#   MODULE:      release.py
#   DESCRIPTION: Release information about pwc
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
#  for the Firebird Open Source RDBMS project.
#  http://www.firebirdsql.org
#
#  Copyright (c) 2007 Pavel Cisar <pcisar@users.sourceforge.net>
#  and all contributors signed below.
#
#  All Rights Reserved.
#  Contributor(s): ______________________________________.

version = "0.7.5"

name = "PowerConsole"
description = "Advanced Command Console"
copyright = "2007-2009 by Pavel Cisar"
long_description = """
PowerConsole is enhanced python interpreter that can host user defined commands.
Uses pyparsing-based grammars for user commands to translate them into python calls,
so it has limited support for mixing them with Python code.

PowerConsole execution engine is designed as embeddable, extensible scripting environment
without strong ties to any particular user interface. This approach:

- allows developers to create interactive consoles or tools with various user interfaces (CLI,
  TUI, GUI, web or even plain automation) that best suits the particular purpose on top of common
  functional core engine that could be easily extended beyond original design (see next point).

- allows developers to create task or domain-specific commands (or even micro-languages) that
  integrate seamlessly into any application built around the PowerConsole engine (see above).

- allows users of these tools and extensions to switch between tools or load extensions according
  to their immediate needs, and combine power of domain-specific commands with versatility of pure
  Python code.

This distibution also contains ready-to-use CLI interpreter.
"""
author="Pavel Cisar"
author_email="pcisar@users.sourceforge.net"
url="http://www.ibphoenix.cz/pwc/index.html"
download_url="http://ibphoenix.cz/pwc/download/"
license="IDPL 1.0 <http://www.firebirdsql.org/index.php?op=doc&id=idpl>"
