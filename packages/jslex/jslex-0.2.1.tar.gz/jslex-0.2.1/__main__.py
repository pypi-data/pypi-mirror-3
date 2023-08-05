"""A main program for jslex."""

import sys
from jslex import JsLexer

def show_js_tokens(jstext, ws=False):
    line = 1
    lexer = JsLexer()
    for name, tok in lexer.lex(jstext):
        print_it = True
        if name == 'ws' and not ws:
            print_it = False
        if print_it:
            print "%4d %s: %r" % (line, name, tok)
        line += tok.count("\n")

if __name__ == '__main__':
    show_js_tokens(open(sys.argv[1]).read())
