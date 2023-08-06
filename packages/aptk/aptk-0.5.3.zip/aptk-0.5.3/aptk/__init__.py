#
# Copyright 2012 by Kay-Uwe (Kiwi) Lorenz
# Published under New BSD License, see LICENSE.txt for details.
#

"""Write documented grammars.


"""

from .grammar import BaseGrammar, Grammar, compile, GrammarType
from .grammar_compiler import GrammarCompiler, GrammarError
from .grammar_tester import generate_testsuite, test
from .actions import *
from .parser  import *
from .__version__ import __version__

def parse(s, grammar, actions=None, rule=None):
    '''parse `s` with given grammar and apply actions to produced lexems.'''
    P = Parser(grammar, actions)
    mob = P.parse(s, rule=rule)
    return mob

def ast(s, grammar=None, actions=None, rule=None):
    '''return ast of s if has one, else, parse s using grammar and actions and return it then'''

    if isinstance(s, MatchObject):
        return s.ast
    return parse(s, grammar, actions=actions, rule=rule).ast

__all__ = [ 'Grammar', 'ParseActions', 'parse', 'ast' ]
