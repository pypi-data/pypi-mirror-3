import os, sys
from jslex import js_to_c_for_gettext

def jslex_prepare():
    try:
        filename = sys.argv[1]
    except IndexError:
        print "Usage: jslex_prepare <filename>"
        sys.exit(1)
    f = open(filename, 'r')
    src = f.read()
    f.close()
    src = js_to_c_for_gettext(src)
    filename, ext = os.path.splitext(filename)
    filename += '.jslex'
    f = open(filename, 'w')
    f.write(src)
    f.close()
    
