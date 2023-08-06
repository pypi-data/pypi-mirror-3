"""

Argpext: Hierarchical argument processing based on argparse.

http://www.cita.utoronto.ca/~shirokov/soft/argpext

Copyright (c) 2012 by Alexander V. Shirokov, Toronto. This
material may be distributed only subject to the terms and
conditions set forth in the Open Publication License, v1.0
or later (the latest version is presently available at
http://www.opencontent.org/openpub ).


"""

import sys as _sys
import argparse as _argparse
import os as _os
import copy as _copy
import abc as _abc
import inspect as _inspect
import warnings as _warnings
import textwrap as _textwrap



# command pushes the 
class comm_cls(metaclass=_abc.ABCMeta):

    COMMAND_PROC = '_feed_func'

    @_abc.abstractmethod
    def HELP(self): pass

    @_abc.abstractmethod
    def HOOK(self): pass

    @_abc.abstractmethod
    def __call__(self,args): pass



# node pushes the rest of the command line args them to a
# separate function.
class node_cls(metaclass=_abc.ABCMeta):

    NODE_FUNC = '_node_func'

    @_abc.abstractmethod
    def HELP(self): pass

    def __call__(self,args):
        A = parser_cls( args,description=self.HELP )
        for args in self.SUBS: A.add_any( *args )
        A.finish ()


class parser_cls(object):

    def __init__(self,arguments,description):

        def sys_prog(arguments):
            S = _sys.argv
            S[0] = _os.path.basename(S[0])
            S = S[0:len(S)-len(arguments)]
            S = ' '.join(S)
            return S

        if not isinstance(arguments,list): raise TypeError
        self._parser = _argparse.ArgumentParser( prog = sys_prog(arguments) )
        self._parser.description = description
        self._subparser = self._parser.add_subparsers(help='Description')
        self._arguments = arguments
        self._items = {}
        self._procs = {}

    # Add node
    def _add_node(self,name,node):

        if not issubclass(node,node_cls): raise TypeError

        self._items[name] = node


        parser = self._subparser.add_parser(name,help=getattr(node,'HELP',None) )
        parser.description = getattr(node,'description',None)

        self._procs[name] = node()
        parser.set_defaults( ** { node.NODE_FUNC : node() } )


    # Add a command
    def _add_comm(self,name,command):

        if not issubclass(command,comm_cls): raise TypeError

        self._items[name] = command

        def command_process(namespace):
            # The input should be the output of command function.
            if not isinstance(namespace,_argparse.Namespace):raise TypeError

            # Find K: the content of the namespace in the argument.
            K = vars( namespace )
            del K[command.COMMAND_PROC]

            return command.HOOK( **K )


        help = getattr( command(),'HELP','')

        parser = self._subparser.add_parser(name, help = help )

        parser.set_defaults( ** { command.COMMAND_PROC : command_process } )
        self._procs[name] = command_process

        parser.description = help

        # Invoke predefined function call operator with parser as an argument.
        # TODO: Isnt this a duplication? of work in finish?
        command()( parser ) # Populate parser with commands options

    def add_any(self,name,something):
        if issubclass(something,comm_cls):
            return self._add_comm(name,something)
        elif issubclass(something,node_cls):
            return self._add_node(name,something)
        else:
            raise TypeError

    def finish(self):

        try:
            word = self._arguments[0]
            item = self._items[word]
        except:
            self._parser.parse_args( self._arguments )

        if issubclass(item,comm_cls):
            X = self._parser.parse_args( self._arguments )
            getattr(X,comm_cls.COMMAND_PROC)( X )
        elif issubclass(item,node_cls):
            L    = self._arguments[1:]
            X = self._parser.parse_args( [word] )
            getattr(X,node_cls.NODE_FUNC) ( L )
        else:
            raise TypeError




# Auxiliary routines

def collect(**arguments):
    class collect_cls(object):
        def __init__(self): pass
        def update(self,arguments):
            self.__dict__.update(arguments)
    C = collect_cls()
    C.update(arguments)
    return C


class keyval(object):

    def __init__(self,rules=(),restrictive=False,valuetype=str):
        if not isinstance(rules,(tuple,list)): raise TypeError
        self._rules = rules
        if not isinstance(restrictive,bool): raise TypeError
        self._restrictive = restrictive
        self._valuetype = valuetype

    def __str__(self): 
        keys = ', '.join([ k[0] for k in self._rules])
        if self._restrictive == True:
            return 'Restricted keys: %s' % ( keys )
        else:
            return 'Special keys: %s' % ( keys )


    def __call__(self,value):
        D = dict(self._rules)
        if value in D or self._restrictive == True:
            return D[value]
        else:
            return self._valuetype(value)
