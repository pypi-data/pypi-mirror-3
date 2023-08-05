#
#   PROGRAM:     Power Console
#   MODULE:      stdcmd.py
#   DESCRIPTION: Standard built-in commands
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
#  Copyright (c) 2006 Pavel Cisar <pcisar@users.sourceforge.net>
#  and all contributors signed below.
#
#  All Rights Reserved.
#  Contributor(s): ______________________________________.

import pkg_resources
import pyparsing as pp
from pwc.base import *
from inspect import getdoc, currentframe
import os.path
import sys
import types
import base
import operator

class ShowExtender(Command):
    """Base class for all PowerConsole SHOW command extenders."""
    
    def __init__(self,controller):
        self.controller = controller
        self._name = self.__class__.__name__.lower()
        self.writeErr = controller.writeErr
        self.write = controller.write
        self.name_node = self._makeNameNode(pp.Empty())
        
    def _getContextLocals(self,depth=0):
        """Return locals from specified frame.
        
        'depth' is number of frames up in stack; 0 means one frame above caller.
        """
        return sys._getframe(depth+3).f_locals
    def _makeNameNode(self,node):
        """Helper functions that sets the specified PyParsing grammar node as
        extender identification node.
        """
        return node.setName(self._name).setResultsName('extender').setParseAction(pp.replaceWith(self._name))

class cmdShow(Command):
    """Show information about topic, object or sequence of objects.

    Uses UI_TEXT and UI_OBJECT display interfaces with context 'show'.
    
    Syntax::
    
        SHOW <topic> | <expression>

    :topic: topic name.
    :expression: object or iterable containing objects to list.
    
    Special topics are installed via extender classes derived from
    :class:`pwc.stdcmd.ShowExtender` class (which is specialized Command class).
    """

    def __init__(self,controller):
        super(cmdShow,self).__init__(controller)
        self.extenders = {}
        self.display = controller.ui_provider.getDisplay('show',
                        [base.UI_TEXT,base.UI_OBJECT])
        # Grammar
        self.keyShow = self._makeNameNode(pp.CaselessKeyword('show'))
        # SHOW <extension-grammars> | <expression>
        ext_full_grammar = []
        ext_check_grammar = []
        for extender in itertools.chain(*(p.show_extensions() for p 
                                          in self.controller.packages 
                                          if hasattr(p,'show_extensions'))):

            try:
                ext = extender(controller)
                self.extenders[ext.getName()] = ext
                ext_full_grammar.append(ext._getGrammar())
                ext_check_grammar.append(pp.Optional(ext._getCmdKeyword()))
            except:
                ## ToDo: Handle exceptions in extender call
                raise
        ext_full_grammar.append(self.EXPR.setResultsName('expr'))
        self.cmdShow = self.keyShow + pp.MatchFirst(ext_full_grammar)
        self.cmdShow.setParseAction(self._compile)
        self.keyShow = self.keyShow + pp.Or(ext_check_grammar)

    def _getGrammar(self):
        return self.cmdShow
    def _getCmdKeyword(self):
        return self.keyShow
    def getHelp(self):
        """Shows information about item or object.
        
        Syntax:: SHOW <item> | <expression>

        :item: item name.
        :expression: object or string to show.
        
        Available special items:
        """
        help = [getdoc(self.getHelp)]
        for extender in self.extenders.values():
            doc = getattr(extender, 'getHelp',None)
            if not doc:
                doc = getattr(extender.execute, '__doc__',None)
            if doc:
                help.append(doc)
        return '\n'.join(help)

    def __displayExpr(self,expr):
        if isinstance(expr,types.StringTypes):
            self.display.writeLine(expr)
        else:
            self.display.writeObject(expr)
        
    def execute(self,**kwargs):

        if 'extender' in kwargs:
            ext = self.extenders[kwargs['extender']]
            del kwargs['extender']
            expr = ext.execute(**kwargs)
            if expr:
                self.__displayExpr(expr)
        elif 'expr' in kwargs:
            expr = kwargs['expr']
            self.__displayExpr(expr)

class cmdList(Command):
    """List information extracted from object or sequence of objects.

    Uses UI_OBJECTLIST and UI_TABLE display interface with context 'list'.
    
    Syntax::
    
        LIST [<attribute>[,<attribute>] IN] <expression>

    :attribute:  attribute name.
    :expression: object or iterable containing objects to list.

    Uses tabular output when attributes are specified, otherwise uses
    object output.
    """

    def __init__(self,controller):
        super(cmdList,self).__init__(controller)
        self.display = controller.ui_provider.getDisplay('list',[base.UI_LIST,base.UI_TABLE])
        # Grammar
        self.keyList = self._makeNameNode(pp.CaselessKeyword('list'))
        keyAttr = pp.delimitedList(self.IDENT,combine=True).setResultsName('attr') + \
                pp.CaselessKeyword('in')
        # LIST [<attribute>,<attribute> IN] <expression>
        self.cmdList = self.keyList + pp.Optional(keyAttr) + self.EXPR.setResultsName('expr')
        self.cmdList.setParseAction(self._compile)

    def _getGrammar(self):
        return self.cmdList
    def _getCmdKeyword(self):
        return self.keyList

    def execute(self,expr,attr=None):
        """List information about object or sequence of objects.
        
        Syntax::
        
           LIST [<attribute>[,<attribute>] IN] <expression>

        :attribute:  attribute name.
        :expression: object or iterable containing objects to list.
        
        Uses tabular output when attributes are specified, otherwise uses
        object output.
        """
        
        if not isiterable(expr):
            expr = [expr]
        if attr:
            if ',' in attr:
                attr = attr.split(',')
                items = map(operator.attrgetter(*attr),expr)
            else:
                attr = [attr]
                items = [(i,) for i in map(operator.attrgetter(*attr),expr)]
            desc = []
            for i in xrange(len(attr)):
                biggest = max((str(item[i]) for item in items),key=len)
                desc.append((attr[i],len(biggest)))
            self.display.writeTable(desc,items)
        else:
            self.display.writeObjectList(expr)


class cmdRun(Command):
    """Run script as if commands had been entered at the console.
    
    Syntax:: 

        RUN <expression> 
        
    :expression: has to be a script filename or iterable containing lines 
                     to execute.
    """

    def __init__(self,controller):
        super(cmdRun,self).__init__(controller)
        # Grammar
        self.keyRun = self._makeNameNode(pp.CaselessKeyword('run'))
        # RUN [arg]
        self.cmdRun = self.keyRun + self.EXPR.setResultsName('expr')
        self.cmdRun.setParseAction(self._compile)

    def _getGrammar(self):
        return self.cmdRun
    def _getCmdKeyword(self):
        return self.keyRun

    def execute(self,expr):
        """Execute sequence of commands as if they were typed into the shell.
        
        Syntax:: RUN <expression> 
        
        :expression: has to be a script filename or iterable containing lines 
                     to execute.
        """

        buffer = []
        lineno = 0
        script = expr

        isFile = os.path.exists(script)
        if isFile:
            source = script
            commands = file(script,"rU")
        else:
            source = str(type(script))
            try:
                commands = eval(script,self._getUserNamespace(),
                    self._getContextLocals())
            except Exception, e:
                raise pcError(str(e))
            if not isiterable(commands):
                raise pcError('File name or iterable object expected.')

        try:
            for command in commands:
                if not isinstance(command,types.StringTypes):
                    raise pcError('String expected, but %s found.' % \
                        str(type(command)))
                buffer.append(command.rstrip())
                more = self.controller.runsource("\n".join(buffer), source,
                    line_offset=lineno)
                lineno += 1
                if not more:
                    buffer = []
        finally:
            if isFile:
                commands.close()


class cmdHelp(Command):
    """Show list of help topics or help text for requested topic.

    Uses UI_TEXT display with context 'help'.

    Syntax:: 
    
        HELP [<argument>]

    Without argument, it will list all internal commands that have help 
    text and all registered special help topics. With argument, it will try 
    to show help for topic or object specified by argument.

    """

    ruler = '='
    doc_leader = """To get help about specific topic, PowerConsole command
or Python object/function/expression, type help <topic>.
"""
    doc_header = "Simple PowerConsole commands:"
    misc_header = "Miscellaneous help topics:"
    nohelp = "*** No help on %s"
    
    def __init__(self,controller):
        super(cmdHelp,self).__init__(controller)
        import __builtin__
        self._help = __builtin__.help
        __builtin__.help = self.execute
        self.display = controller.ui_provider.getDisplay('help')
        # Find and instantiate help topics
        self.help_providers = []
        help_providers = [helpBuiltin,helpPython]
        help_providers.extend(itertools.chain(*(p.help_providers() for p 
                                          in self.controller.packages 
                                          if hasattr(p,'help_providers'))))
        for provider in help_providers:
            try:
                obj = provider(self._help)
            except:
                ## ToDo: Handle exceptions in provider initialization
                raise
            else:
                self.help_providers.append(obj)
        # Grammar
        self.keyHelp = self._makeNameNode(pp.CaselessKeyword('help'))
        # HELP [arg]
        self.cmdHelp = self.keyHelp + pp.Optional(self.ARG.setResultsName('arg'))
        self.cmdHelp.setParseAction(self._compile)

    def __findProvider(self, topic):
        for provider in self.help_providers:
            if provider.canHandle(topic): 
                return provider
        return None
    def __showHelp(self,help):
        if callable(help):
            help = help()
        if help:
            self.display.writeLine(help)
    def __printTopics(self, header, cmds, cmdlen, maxcol):
        if cmds:
            self.display.writeLine("%s" % str(header))
            if self.ruler:
                self.display.writeLine("%s" % str(self.ruler * len(header)))
            for line in columnize(cmds, maxcol-1):
                self.display.writeLine(line)
            self.display.writeLine()

    def _getGrammar(self):
        return self.cmdHelp
    def _getCmdKeyword(self):
        return self.keyHelp

    def execute(self,arg=''):
        """Show list of help topics or help text for requested topic.
        
        Without argument, it will list all internal commands that have help 
        text and all registered special help topics. With argument, it will try 
        to show help for topic or object specified by argument.

        Syntax:: HELP [<argument>]
        """

        if arg:
            if self.controller.commands.has_key(arg) and (
                hasattr(self.controller.commands[arg], 'getHelp') or 
                getdoc(getattr(self.controller.commands[arg], 'execute'))):
                # Help for PowerConsole command
                cmd = self.controller.commands[arg]
                try:
                    self.__showHelp(getattr(cmd, 'getHelp'))
                except AttributeError:
                    # There is not separate help provider function
                    # we'll look for docstring in 'execute' method
                    doc = getdoc(getattr(cmd, 'execute'))
                    if doc:
                        self.__showHelp(str(doc))
                    else:
                        self.__showHelp("%s" % str(self.nohelp % arg))
            else:
                # It's not a PowerConsole command or it doesn' directly
                # provide documentation, we'll look for help provider
                provider = self.__findProvider(arg)
                if provider:
                    self.__showHelp(provider.getHelp(arg))
                else:
                    # No provider found, we'll show help for Python object/topic
                    try:
                        self._help(eval(arg,self._getUserNamespace(),self._getContextLocals()))
                    except Exception:
                        self.__showHelp("%s" % str(self.nohelp % arg))
        else:
            # Show list of documented internal commands and help topics
            cmds_doc = []
            for cmd in self.controller.commands.values():
                if hasattr(cmd, 'getHelp') or getdoc(getattr(cmd, 'execute')):
                    cmds_doc.append(cmd.getName())
            helptopics = []
            for provider in self.help_providers:
                helptopics.extend(provider.getTopics())
            cmds_doc.sort()
            helptopics.sort()
            self.display.writeLine("%s" % str(self.doc_leader))
            self.__printTopics(self.doc_header, cmds_doc, 15,80)
            self.__printTopics(self.misc_header, helptopics, 15,80)
    
class helpBuiltin(HelpProvider):
    """Help Provider for built-in commands and other general topics"""

    help_terminator = """PowerConsole supports two types of commands:

    1. Commands terminated with special text sequence - `terminator` (for example SQL
       commands has to be terminated by ";").
    2. Commands without terminator sequence.

Standard terminator is ";". When you would need to change the command terminator
to other sequence of characters, use the SET TERM command.

Syntax:: SET TERM <new-terminator> <current-terminator>

:new-terminator: Continuous sequence of non-whitespace characters.

Note:: SET TERM is also terminated command, so you have to end it with current
       terminator sequence.
    """

class helpPython(HelpProvider):
    """Help Provider that provides access to standard Python help system."""

    def canHandle(self,topic):
        """Return True if 'topic' starts with 'python'."""

        return topic.startswith('python')

    def getTopics(self):
        """Return list of topics handled by provider."""

        return ['python']

    def getHelp(self, topic):
        """Return python help for 'topic'."""

        topic = topic[6:].strip()
        if topic != '':
            self._help(topic)
        else:
            self._help()

