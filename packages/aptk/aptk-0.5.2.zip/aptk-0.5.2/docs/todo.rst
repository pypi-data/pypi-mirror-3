TODO
====

.. highlight:: aptk

.. grammar off
   
   The following is a scratchpad, so no grammar here.

- Add implicit rules for "whitespace" in rules, usually to parse 
  whitespace::

      <ws>  ::= \s+

      :sigspace <ws>  # set sigspace rule to <ws>

      :+sigspace      # turn on significant space for next rules
      <foo> ::= "a" "b"

      :-sigspace      # turn off sigspace for next rules
      <bar> ::= "a" "b"

      <glork> ::= :s "a" "b" # turn on sigspace for this rule

  Then::

      foo   ~ "a   b"
      glork ~ "a  b"
      bar   ~ "ab"
      bar   !~ "a  b"

- Implement Grammar tests directly in grammar::

     foo   ~ "a   b"      # rule foo matches string "a   b"

     foo   ~ "a   b"  ->  <LEX(foo):'a   b'>  # rule foo matches string 
                                              # "a   b" and produces 
                                              # MatchObject lexed "foo"

     <foo> ~ "a   b"  -> <...>
     {foo} ~ "..."    ->     # token test

     <expression> ~ "a + b * c" 
                  -> (foo "a   b")<...>

  * -> means check parse tree
  * -A-> means check str of ast of A
  * ~ (or ~~) means tokenwise (split on ws) compare
  * =~ means equality

  ::

     # ini-file matches the following text and produces tree
     ini-file ~ 
        | ; this is a comment
        |
        | [section]
        | foo = bar
        |
        | bla = 1234
        | abcdabcdef...ef=x
        -> [
            section[ 
              section-name(section), 
              options[ <MOB:[
              <LEX(section):[
                <LEX(section-name):'section'>, 
                <LEX(options):[
                  <LEX(option):[<LEX(key):'foo'>, <LEX(value):'bar'>]>, 
                  <LEX(option):[<LEX(key):'bla'>, <LEX(value):'1234'>]>, 
                 <LEX(option):[<LEX(key):'abcdabcdef...ef'>, <LEX(value):'x'>
           ]>]>]>]>

      # ini-file matches following text and produces AST
      ini-file ~~

        | ; this is a comment
        |
        | [section]
        | foo = bar
        |
        | bla = 1234
        | abcdabcdef...ef=x

        -SomeParseActions->

        | { 'section': {
        |     'foo': 'bar', 
        |     'bla': '1234',
        |     'abcdabcdef...ef': 'x'
        |   }
        | }

- Implement operation precedence parser. It is not yet clear how to define it,
  but it will be something like this:

  =============== ==========================================
   precedence op   meaning
  =============== ==========================================
      a > b        operator a binds looser than operator b
      a < b        operator a binds tighter than operator b
      a = b        operator a binds like operator b
  =============== ==========================================

  ========== ==================
   Syntax     meaning    
  ========== ==================
    E+E       infix +   
    xEx       circumfix xx
    (E)       circumfix ()
    E(E)      postcircumfix ()
    (E)E      precircumfix ()
    E++       postfix ++
    ++E       prefix ++
  ========== ==================

  We then can define an extended rule, which takes following parameters::

   expression := <EXPR{
         EXPRESSION E <.expression>
         EXPRESSION N <.number>

         [ [ left-assoc | right-assoc | L | R ] E+E [  > | < | = ] E*E ] ]*
         [ [ left-assoc | right-assoc | L | R ] E+N [ {>|<|=} E*E ] ]*

         }>

  http://en.wikipedia.org/wiki/Operator-precedence_parser

- create rule_producer from fully integrated sphinx grammars, with
  reST directives, e.g.:

  .. code-block:: rst

     .. grammar:: MyGrammar

     .. token:: a-token

        this token does this and that

     .. rule:: foo

        <bar> <.glork>

     .. rule:: bar

     ...

     

