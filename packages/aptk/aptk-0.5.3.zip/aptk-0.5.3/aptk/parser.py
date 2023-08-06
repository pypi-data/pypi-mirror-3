#
# Copyright 2012 by Kay-Uwe (Kiwi) Lorenz
# Published under New BSD License, see LICENSE.txt for details.
#


# PARSER
# ========

from .actions import ParseActions
from .match_object import Lexem, MatchObject
from .util import Undef

__all__ = ['Parser']

class ParseException(Exception):
    pass

class Parser:
    '''This combines an abstract grammar and parse-actions to a parser
    which produces an abstract syntax tree.

    If no actions given, defaults to ParseActions object.
    '''

    def __init__(self, grammar, actions = None):
        if not actions: actions = ParseActions()

        if isinstance(actions, basestring):
            actions = grammar._PARSE_ACTIONS_[actions]
 
        self.actions = actions
        self.grammar = grammar

    def parse(self, s, rule=None):
        if rule is None: rule = self.grammar._START_RULE_
        
        #try:
        if 1:
            mob = getattr(self.grammar, rule)(self, s, 0)

            if not isinstance(mob, MatchObject):
                try:
                    mob = mob.next() # is an iterator, we need the first
                                     # valid match from
                except StopIteration:
                    return None

            return self.lex(mob, rule)

        else:
        #except:
            import sys
            try:
                #import rpdb2 ; rpdb2.setbreak()
                etype, evalue, tb = sys.exc_info()
                sys.stderr.write("%s\n" % str(evalue))
                rules_called = []
                while tb:
                    frame = tb.tb_frame
                    if '*RULE*' in frame.f_locals:
                        rules_called.append(frame.f_locals['*RULE*'])
                    #elif 'self' in frame.f_locals:
                        #rules_called.append(repr(frame.f_locals['self']))
                    tb = tb.tb_next
    
                rules_called = [x for x in reversed(rules_called)]
                import traceback
                raise ParseException(
                    ''.join(traceback.format_exception(etype, evalue, tb))
                    +"\n"+"\n".join(rules_called)+"\n")
            finally:
                etype = evalue = tb = None
            

    def action(self, name, lexem):
        if lexem.ast is not Undef:
            return

        if hasattr(self.actions, name):
            lexem.ast = getattr(self.actions, name)(self, lexem)
        else:
            if isinstance(self.actions, basestring):
               import rpdb2 ; rpdb2.setbreak()
            a = self.grammar._ACTIONS_.get(name)
            if isinstance(a, tuple):
                lexem.ast = (a[0], getattr(self.actions, a[1])(self, lexem))
            elif a:
                lexem.ast = getattr(self.actions, a)(self, lexem)
       
    def __call__(self, s, rule=None):
        mob = self.parse(s, rule=rule)
        if mob.ast is not None:
            return mob.ast
        return mob

    def lex(self, mob, name):
        lexem = Lexem(mob, name)
        self.action(name, lexem)
        return lexem

