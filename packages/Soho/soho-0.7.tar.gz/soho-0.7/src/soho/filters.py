"""Define default filters for Soho.

$Id: filters.py 54 2008-02-17 13:23:24Z damien.baty $
"""

import re


def dummy(content):
    """Return ``content`` unchanged."""
    return content


## FIXME: add euro sign (\u20ac), too.
FR_NBSP_BEFORE = re.compile(' ([\?!:;])')

def applyFrenchTypographyRules(content):
    """Fix ``content`` by applying French typography rules.

    FIXME: this is probably not complete
    """
    ## Add non-breaking space before specific characters
    content = FR_NBSP_BEFORE.sub('&nbsp;\g<1>', content)

    ## Add non-breaking spaces inside "guillemets"
    content = content.replace(u'\xab ', u'\xab&nbsp;')
    content = content.replace(u' \xbb', u'&nbsp;\xbb')

    return content


def useHTMLentity(content):
    """Replace some characters with their equivalent HTML entity."""
    content = content.replace('...', '&hellip;')
    return content


XHTML_SHORT_TAGS = re.compile('(<.*?) ?/>')

def replaceXHTMLShortTags(text):
    """Replace XHTML short tags by an HTML-compatible tag."""
    return XHTML_SHORT_TAGS.sub('\g<1>>', text)


LINKS_TO_RST_FILES = re.compile('(\.\. _.*?:.*?\.)(txt|rst)\n',
                                re.DOTALL)

def changeLinksFromTxtToHTML(text):
    """Process reST links so that links to reStructuredText files
    (``*.{rst, txt}``) are converted to links to ``*.html`` files.
    """
    return LINKS_TO_RST_FILES.sub('\g<1>html\n', text)
