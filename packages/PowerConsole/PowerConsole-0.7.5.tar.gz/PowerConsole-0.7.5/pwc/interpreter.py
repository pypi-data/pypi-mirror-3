#
#   PROGRAM:     Power Console
#   MODULE:      interpreter.py
#   DESCRIPTION: Command Interpreter
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
#  Based on code.py module from Standard Python Library
#
#  Copyright (c) 2007-2009 Pavel Cisar <pcisar@users.sourceforge.net>
#  and all contributors signed below.
#
#  All Rights Reserved.
#  Contributor(s): ______________________________________.

import pyparsing as pp
import sys
import traceback
from codeop import CommandCompiler
import pwc
import pwc.base as base
import __builtin__
import string
import base
import itertools

__all__ = ["Interpreter", "Console", "interact"]

#--- Constants

IDENTCHARS = string.ascii_letters + string.digits + '_'
SET_TERM_CMD = 'SET TERM'

#--- Exceptions

#--- Functions

#--- Classes

class Interpreter(object):
    """Interpreter based on :class:`code.InteractiveInterpreter` from Python Library.

    *Attributes:*
    
    :packages:      List of package interface objects.
    :ui_provider:   UserInterfaceProvider instance used by interpreter.
    :locals:        the dictionary in which code will be executed.
    :compile:       CommandCompiler instance.
    :linecont:      Line continuation marker.
    :terminator:    Default terminator string for terminated commands
    :commands:      Disctionary of installed commands, key is command name.
    :full_grammar:  Complete grammar for internal commands.
    :check_grammar: Grammar for internal commands used to check whether 
                    internal commands starts on given line.
    """

    terminator = ';'
    commands = {}
    debug = False
    
    def __init__(self,packages=[],locals=None,ui_provider=None,ui_factory=None):
        """Constructor.

        :packages: Optional list of extension packages; defaults to empty list.
        :locals: Optional dictionary in which the user code will be executed; 
                 it defaults to a newly created dictionary with key "__name__"
                 set to "__console__" and key "__doc__" set to None.
        
        :ui_provider: Optional UserInterfaceProvider; defaults to 
                      base.UserInterfaceProvider.
        :ui_factory: Optional User Interface Factory callable that creates UI
                     elements with required interface.
        """

        self.packages = packages
        
        if ui_provider is None:
            ui_provider = base.UserInterfaceProvider(packages,ui_factory)
        self.ui_provider = ui_provider
        
        # Displays for use in Interpreter
        self.__errout = self.ui_provider.getDisplay("main.stderr")
        self.__out = self.ui_provider.getDisplay("main")
        
        if locals is None:
            locals = {"__name__": "__console__", "__doc__": None,"shell":self,
                      "ui": ui_provider}
        self.locals = locals
        self.compile = CommandCompiler()
        self.linecont = '\\'

        # Install our own displayhook that uses ui_provider
        self.__displayhook = sys.displayhook
        sys.displayhook = self._displayhook
        self.__display = self.ui_provider.getDisplay("main.displayhook",base.UI_OBJECT)

        # Call Controller extenders
        for extender in itertools.chain(*(p.controller_extensions() for p 
                                          in self.packages 
                                          if hasattr(p,'controller_extensions'))):
            try:
                extender(self)
            except:
                ## ToDo: Handle exceptions in extender call
                raise

        # Find and instantiate commands
        commands = [pwc.stdcmd.cmdList,pwc.stdcmd.cmdHelp,pwc.stdcmd.cmdShow,
                    pwc.stdcmd.cmdRun]
        commands.extend(itertools.chain(*(p.commands() for p 
                                     in self.packages if hasattr(p,'commands'))))
        for command in commands:
            try:
                cmd = command(self)
                name = cmd.getName()
            except:
                ## ToDo: Handle exceptions in command initialization
                raise
            else:
                self.commands[name] = cmd
                __builtin__.__dict__['_%s_execute' % name] = cmd.execute

        # Build Grammars
        self._rebuildGrammar(base.GRAMMAR_FULL)
        self._rebuildGrammar(base.GRAMMAR_CHKCMD)

    def __buildGrammar(self,grammarType):
        """Returns pyparsing grammar assembled from grammars from all installed
        commands.
        
        Supported 'grammarType' values are defined in pwc.base.
        """

        grammar = None
        for cmd in self.commands.values():
            cmdGrammar = cmd.getGrammar(grammarType)
            if cmdGrammar == None: continue
            if grammar:
                grammar = grammar ^ cmdGrammar
            else:
                grammar = cmdGrammar
        return grammar.setResultsName('command')

    def __processCmd(self, line):
        """If 'line' is a command, it's converted into executable function call."""

        if not line:
            return ''
        else:
            i, n = 0, len(line)
            while i < n and line[i] in string.whitespace: i += 1
            indent, cmd = line[:i], line[i:].strip()

            call = self.full_grammar.parseString(cmd)
            if call is not None:
                if hasattr(call,'command'):
                    return indent + call.command
                else:
                    return indent + call[0]
            else:
                # It's not a valid command, return line as is
                return line

    def _rebuildGrammar(self,grammar_type):
        if grammar_type == base.GRAMMAR_FULL:
            self.full_grammar = self.__buildGrammar(base.GRAMMAR_FULL) + \
                pp.Optional(pp.pythonStyleComment) + pp.StringEnd()
        elif grammar_type == base.GRAMMAR_CHKCMD:
            self.check_grammar = self.__buildGrammar(base.GRAMMAR_CHKCMD)
    
    def _displayhook(self,item):
        if item is not None:
            self.__display.writeObject(item)

    def _precompile(self,source):
        """Look for any internal commands in 'source' and replace them with
        internal calls. Handles multiple commands, multi-line internal commands 
        and code blocks.
        """

        lines = source.split('\n')
        result = []
        multiline = None
        i, n = 0, len(lines)
        try:
            terminated = False
            while i < n:
                line = lines[i].rstrip()
                if multiline is None:
                    # SET TERM processing
                    pos = line.upper().find(SET_TERM_CMD)
                    if pos != -1:
                        if not line.endswith(self.terminator):
                            raise SyntaxError('Terminator expected', 
                                ('filename', i, len(line), line))
                        else:
                            terminator = line.lstrip()[len(SET_TERM_CMD):-len(self.terminator)].strip()
                            if terminator == '':
                                raise SyntaxError('New terminator expected', 
                                    ('filename', i, len(line), line))
                            else:
                                self.terminator = terminator
                            result.append(line.upper().replace(SET_TERM_CMD,'#'+SET_TERM_CMD))
                    elif self.isCmd(line):
                        # Only internal multiline commands are handled specially
                        # because we need to parse the whole command.
                        # Python multiline commands are handled by code compiler.
                        
                        # Commands could use terminator string or free-form
                        ret = self.check_grammar.parseString(line)
                        terminated = self.commands[ret.command].usesTerminator
                        if terminated:
                            # Uses terminator string (for example SQL command)
                            if (line[-len(self.terminator):] == self.terminator):
                                result.append(self.__processCmd(line[:-len(self.terminator)].rstrip()))
                            else:
                                multiline = [line]
                        else:
                            # Python-style command, may use line continuation string
                            if (line[-len(self.linecont):] == self.linecont):
                                multiline = [line[:-len(self.linecont)].rstrip()]
                            else:
                                result.append(self.__processCmd(line))
                    else:
                        # Python code
                        result.append(line)
                else:
                    # multiline, continuation
                    if terminated:
                        if (line[-len(self.terminator):] == self.terminator):
                            multiline.append(line[:-len(self.terminator)].rstrip())
                            result.append(self.__processCmd('\n'.join(multiline)))
                            multiline = None
                        else:
                            multiline.append(line)
                    else:
                        if (line[-len(self.linecont):] != self.linecont):
                            multiline.append(line)
                            result.append(self.__processCmd('\n'.join(multiline)))
                            multiline = None
                        else:
                            multiline.append(line[:-len(self.linecont)].rstrip())
                i = i + 1
        except pp.ParseBaseException, err:
            raise SyntaxError(err.msg, ('filename', err.lineno, err.col, err.line))
        if multiline is None:
            return '\n'.join(result)
        else:
            # None means that command is not finished and we want more
            return None

    def runsource(self, source, filename="<input>", symbol="single", line_offset=0):
        """Compile and run some source in the interpreter.

        Argument 'lineoffset' is number of lines processed before this source code.
        It's used to report correct line number for syntax errors when input is 
        read from file.

        Other arguments are as for compile_command().
        
        One several things can happen:

        1) The input is incorrect; compile_command() raised an
        exception (SyntaxError or OverflowError).  A syntax traceback
        will be printed by calling the showsyntaxerror() method.

        2) The input is incomplete, and more input is required;
        compile_command() returned None.  Nothing happens.

        3) The input is complete; compile_command() returned a code
        object.  The code is executed by calling self.runcode() (which
        also handles run-time exceptions, except for SystemExit).

        The return value is True in case 2, False in the other cases (unless
        an exception is raised).  The return value can be used to
        decide whether to use sys.ps1 or sys.ps2 to prompt the next
        line.
        """

        # First we'll process any internal commands in 'source'
        try:
            #print 'Cmd:',source
            source = self._precompile(source)
            if self.debug_calls:
                print 'Calling',source
        except (OverflowError, SyntaxError, ValueError):
            self.showsyntaxerror(filename,line_offset)
            return False
        if source is None:
            # Case 2
            return True
        # Now we have pure Python code in 'source'
        try:
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            # Case 1
            self.showsyntaxerror(filename,line_offset)
            return False
        if code is None:
            # Case 2
            return True
        # Case 3
        #print 'Exe:',source.replace('\n','\n...: ')
        self.runcode(code)
        return False

    def runcode(self, code):
        """Execute a code object.

        When an exception occurs, self.showtraceback() is called to
        display a traceback.  All exceptions are caught except
        SystemExit, which is reraised.

        A note about KeyboardInterrupt: this exception may occur
        elsewhere in this code, and may not always be caught.  The
        caller should be prepared to deal with it.
        """

        def softspace(file, newvalue):
            oldvalue = 0
            try:
                oldvalue = file.softspace
            except AttributeError:
                pass
            try:
                file.softspace = newvalue
            except (AttributeError, TypeError):
                # "attribute-less object" or "read-only attributes"
                pass
            return oldvalue
        try:
            exec code in self.locals
        except SystemExit:
            raise
        except base.pcError:
            self.showtraceback(internal=True)
        except:
            self.showtraceback()
        else:
            if softspace(sys.stdout, 0):
                print

    def showsyntaxerror(self, filename=None, line_offset=0):
        """Display the syntax error that just occurred.

        This doesn't display a stack trace because there isn't one.

        If a filename is given, it is stuffed in the exception instead
        of what was there before (because Python's parser always uses
        "<string>" when reading from a string).

        The output is written by self.writeErr(), below.
        """

        type, value, sys.last_traceback = sys.exc_info()
        sys.last_type = type
        sys.last_value = value
        if filename and type is SyntaxError:
            # Work hard to stuff the correct filename in the exception
            try:
                msg, (dummy_filename, lineno, offset, line) = value
            except:
                # Not the format we expect; leave it alone
                pass
            else:
                # Stuff in the right filename
                value = SyntaxError(msg, (filename, lineno+line_offset, offset, line))
                sys.last_value = value
        list = traceback.format_exception_only(type, value)
        map(self.writeErr, list)

    def showtraceback(self,internal=False):
        """Display the exception that just occurred.

        We remove the first stack item because it is our own code. 
        If 'internal' is True, remove also the last stack item (internal 
        command 'execute' method).

        The output is written by self.writeErr(), below.
        """

        try:
            type, value, tb = sys.exc_info()
            sys.last_type = type
            sys.last_value = value
            sys.last_traceback = tb
            tblist = traceback.extract_tb(tb)
            del tblist[:1]
            if internal:
                del tblist[len(tblist)-1:]
            list = traceback.format_list(tblist)
            if list:
                list.insert(0, "Traceback (most recent call last):\n")
            list[len(list):] = traceback.format_exception_only(type, value)
        finally:
            tblist = tb = None
        map(self.writeErr, list)

    def writeErr(self, data=''):
        """Write a string to error output.

        It writes to UI_TEXT Display (context main.stderr) provided by ui_provider.
        """
        self.__errout.write(data)

    def write(self, data=''):
        """Write a string to standard output.

        It writes to UI_TEXT Display (context main) provided by ui_provider.
        """

        self.__out.write(data)

    def isCmd(self, cmdstr):
        """Returns True if 'cmdstr' is internal command. However, it doesn't 
        check whether 'cmdstr' is *valid*, as it uses 'command checking' grammar
        that usually parses only beginning of the 'cmdstr' for command keywords.
        """

        try:
            ret = self.check_grammar.parseString(cmdstr)
        except pp.ParseException:
            return False
        else:
            return True


class Console(Interpreter):
    """Closely emulate the behavior of the interactive Python interpreter.

    This class builds on InteractiveInterpreter and adds prompting
    using the familiar sys.ps1 and sys.ps2, and input buffering.
    """

    def __init__(self, packages=[], locals=None, filename="<console>", 
                  ui_provider=None, ui_factory=None):
        """Constructor.

        The optional locals argument will be passed to the
        InteractiveInterpreter base class.

        The optional filename argument should specify the (file)name
        of the input stream; it will show up in tracebacks.

        The optional display_provider argument specifies the UserInterfaceProvider;
        it defaults to base.UserInterfaceProvider.
        """

        super(Console,self).__init__(packages,locals,ui_provider,ui_factory)
        self.filename = filename
        self.resetbuffer()

    def resetbuffer(self):
        """Reset the input buffer."""

        self.buffer = []

    def interact(self, banner=None):
        """Closely emulate the interactive Python console.

        The optional banner argument specify the banner to print
        before the first interaction; by default it prints a banner
        similar to the one printed by the real Python interpreter,
        followed by the current class name in parentheses (so as not
        to confuse this with the real interpreter -- since it's so
        close!).
        """

        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = ">>> "
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = "... "
        cprt = 'Type "help", "copyright", "credits" or "license" for more information.'
        if banner is None:
            self.write("Python %s on %s\n%s\n(%s)\n" %
                       (sys.version, sys.platform, cprt,
                        self.__class__.__name__))
        else:
            self.write("%s\n" % str(banner))
        more = 0
        while 1:
            try:
                if more:
                    prompt = sys.ps2
                else:
                    prompt = sys.ps1
                try:
                    line = self.ui_provider.raw_input(prompt)
                except EOFError:
                    self.write("\n")
                    break
                else:
                    more = self.push(line)
            except KeyboardInterrupt:
                self.write("\nKeyboardInterrupt\n")
                self.resetbuffer()
                more = 0

    def push(self, line):
        """Push a line to the interpreter.

        The line should not have a trailing newline; it may have
        internal newlines.  The line is appended to a buffer and the
        interpreter's runsource() method is called with the
        concatenated contents of the buffer as source.  If this
        indicates that the command was executed or invalid, the buffer
        is reset; otherwise, the command is incomplete, and the buffer
        is left as it was after the line was appended.  The return
        value is 1 if more input is required, 0 if the line was dealt
        with in some way (this is the same as runsource()).
        """

        self.buffer.append(line)
        source = "\n".join(self.buffer)
        more = self.runsource(source, self.filename)
        if not more:
            self.resetbuffer()
        return more


def interact(banner=None, readfunc=None, local=None):
    """Closely emulate the interactive Python interpreter.

    This is a backwards compatible interface to the InteractiveConsole
    class.  When readfunc is not specified, it attempts to import the
    readline module to enable GNU readline if it is available.

    Arguments (all optional, all default to None):

    :banner: passed to InteractiveConsole.interact()
    :readfunc: if not None, replaces InteractiveConsole.raw_input()
    :local: passed to InteractiveInterpreter.__init__()
    """

    console = Console(local)
    if readfunc is not None:
        console.raw_input = readfunc
    else:
        try:
            import readline
        except ImportError:
            pass
    console.interact(banner)

