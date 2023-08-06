#
# Copyright 2012 by Kay-Uwe (Kiwi) Lorenz
# Published under New BSD License, see LICENSE.txt for details.
#


from aptk import compile, generate_testsuite, GrammarType
from types import ModuleType
from unittest import TestSuite
import os, sys

def doctests(filename, suite, test_patterns):
    with open(filename, 'rb') as f:
        grammars = compile(f, type='sphinx', filename=filename)
        for n,g in grammars.items():
            generate_testsuite(g, suite, test_patterns)

def load_tests(loader, tests, pattern):
    root = os.path.join(os.path.dirname(__file__), '..')
    files = [ os.path.join(root, 'README.txt') ]

    suite = TestSuite()

    from __main__ import test_patterns

    #if hasattr(loader, 'test_patterns'):
        #test_patterns = loader.test_patterns
    #else:
        #test_patterns = None

    sys.path.insert(0, os.path.join(root, 'examples'))
    # python examples
    for d, ds, fs in os.walk(os.path.join(root, 'examples')):
        for f in fs:
            if not f.endswith('.py'): continue
            module = f[:-3]
            exec "import %s"%module in globals()

            m = globals()[module]

            for g in dir(m):
                g = getattr(m, g)
                if isinstance(g, GrammarType):
                    generate_testsuite(g, suite, test_patterns)

    # rst examples    
    for d, ds, fs in os.walk(os.path.join(root, 'docs')):
        for f in fs:
            if not f.endswith('.rst'): continue
            doctests(os.path.join(d, f), suite, test_patterns)

    # other files
    for f in files:
        doctests(f, suite, test_patterns)

    return suite

if __name__ == '__main__':
    from unittest import main
    main()
