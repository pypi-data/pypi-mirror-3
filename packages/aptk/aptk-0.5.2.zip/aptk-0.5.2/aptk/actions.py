#
# Copyright 2012 by Kay-Uwe (Kiwi) Lorenz
# Published under New BSD License, see LICENSE.txt for details.
#
from .util import Undef

class ParseActions:
    def _list(self, lexems, filter=None):
        if filter:
            return [ l.ast for l in lexems if l.ast is not Undef and filter(l.ast) ]
        else:
            return [ l.ast for l in lexems if l.ast is not Undef ]

    def make_list(self, p, lex):
        return self._list(lex.lexems)

    def make_pair(self, name, method):
        return lambda p, lex: (name, getattr(self, method)(p, lex))

    def make_string(self, p, lex):
        return str(lex)

    def make_number(self, p, lex):
        try:
            return int(str(lex))
        except ValueError:
            return float(str(lex))

    def make_name(self, p, lex):
        return lex.name

    PARENS = { '<':'>', '(':')', '{':'}', '[':']' }
    def make_quoted(self, p, lex):
         ls = self._ast_list(lex.lexems)
         if ls:
             return ''.join(ls)

         s = str(lex)
 #         log.error("_smart_string(s): %s", s)

         start = s[0]
         if start in self.PARENS:
             end = self.PARENS[start]
             s = re.sub(r'\\\\|\\%s|\\%s'%(start, end), 
                     lambda m: m.group(0)[1], s[1:-1])
         else:
             s = re.sub(r'\\\\|\\'+end, lambda m: m.group(0)[1], s[1:-1])

 #        log.error("_smart_string(s): %s", s)

         return s

    def make_dict(self, p, lex):
        try:
            _l = self.ast_list(p, lex)
            return dict(_l)
        except Exception, e:
            pass

    def make_inherit(self, p, lex):
        result = self.ast_list(p, lex)
        if not result: return None
        return result[0]


