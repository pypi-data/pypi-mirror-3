"""Define default bindings for Soho.

$Id: bindings.py 54 2008-02-17 13:23:24Z damien.baty $
"""

import re

try:
    from pygments.lexers import get_all_lexers
    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False


PYGMENTS_LEXER = re.compile('.. sourcecode:: (.*:?)')

def getPygmentsLexers(context):
    """Find Pygments "sourcecode" directives in ``context`` and return
    lexers that are used.
    """
    return set(PYGMENTS_LEXER.findall(context.source))


def getAvailablePygmentsLexers(context):
    """Return available Pygments lexers."""
    if not HAS_PYGMENTS:
        return ()
    lexers = get_all_lexers()
    return reduce(lambda x, y: x + y, [i[1] for i in list(lexers)])
