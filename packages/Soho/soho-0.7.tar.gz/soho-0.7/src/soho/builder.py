"""Define ``Builder``, the main class of Soho, and other utility class
and methods.

$Id: builder.py 54 2008-02-17 13:23:24Z damien.baty $
"""

import os
import re
import logging
from imp import load_source
from shutil import copyfile

from docutils.writers.html4css1 import Writer
from docutils.core import publish_doctree, publish_parts
from zope.pagetemplate.pagetemplate import PageTemplate

from soho.config import *


META_REGEXP = re.compile('<meta content="(.*?)" name="(.*?)".*?>')


def registerPygmentsDirective():
    """Register Pygments ``sourcecode`` directive."""
    from docutils import nodes
    from docutils.parsers.rst import directives
    from pygments import highlight
    from pygments.util import ClassNotFound
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter

    pygments_formatter = HtmlFormatter()

    ## FIXME: give credits
    def pygments_directive(name, arguments, options, content, lineno,
                           content_offset, block_text, state, state_machine):
        try:
            lexer = get_lexer_by_name(arguments[0])
        except ClassNotFound:
            logging.info('No lexer could be found for Pygments '\
                         '"sourcecode" directive "%s" in this file.'\
                         'Default to "text".', arguments[0])
            lexer = get_lexer_by_name('text')
        parsed = highlight(u'\n'.join(content), lexer, pygments_formatter)
        return [nodes.raw('', parsed, format='html')]
    pygments_directive.arguments = (1, 0, 1)
    pygments_directive.content = 1
    directives.register_directive('sourcecode', pygments_directive)


class Builder(object):
    """``Builder``, the main class of Soho.

    This class lets you generate HTML files from reStructuredText
    source files, a Zope Page Template (ZPT) and a set of optional
    filters which may be run before or after the conversion to HTML.
    """

    def __init__(self, in_dir, out_dir, template,
                 bindings, filters,
                 do_nothing, force,
                 ignore_directories, ignore_files):
        """Initialize the builder.

        ``in_dir``
            input directory where reStructured Text files live.

        ``out_dir``
            ouput directory, where HTML files will be created.

        ``template``
            path to the Zope Page Template file.

        ``bindings``
            path to the user defined bindings (Python) module.

        ``filters``
            path to the user defined filters (Python) module.

        ``do_nothing``
            if set, nothing is created: no directory, no files and no
            wheelbarrows (the latter are evil, anyway: you should not
            create any of them unless you really know what you are
            doing).

        ``force``
            if set, force the generation of HTML files, even if they
            have already been generated and are up to date.

        ``ignore_directories``
            if this regexp matches the path of the directory, it will
            not be processed.

        ``ignore_files``
            if this regexp matches the basename of the file, it will
            not be processed.
        """
        self._in_dir = os.path.normpath(in_dir)
        self._out_dir = os.path.normpath(out_dir)
        self._layout = PageTemplate()
        self._layout.write(open(template).read())

        ## Register filters
        if filters is not None:
            module = load_source('user_defined_filters',
                                 filters)
            self._pre_filters = getattr(module, 'pre_filters', ())
            self._post_filters = getattr(module, 'post_filters', ())
        else:
            self._pre_filters = ()
            self._post_filters = ()

        ## Register bindings
        if bindings is not None:
            module = load_source('user_defined_bindings',
                                 bindings)
            self._bindings = getattr(module, 'bindings', ())
        else:
            self._bindings = ()

        ## Prepare a context-free page template to be used later in
        ## ``processFile()``.
        self._page = PageTemplate()
        self._page.write('<metal:block use-macro='\
                         '"context/layout/macros/master"/>')

        self._do_nothing = do_nothing
        self._force = force
        self._ignore_directories = ignore_directories
        self._ignore_files = ignore_files


    def build(self):
        """Build web site by recursively processing the input
        directory.
        """
        if self._do_nothing:
            logging.info('Dry run. No files will be harmed, '\
                         'I promise.')
        logging.info("Begin building web site.")

        for dirpath, dirnames, filenames in os.walk(self._in_dir):
            for filename in filenames:
                input = os.path.join(dirpath, filename)

                if self._ignore_directories.match(dirpath):
                    continue
                if self._ignore_files.match(filename):
                    continue

                is_a_source_file = self.isASourceFile(filename)

                ## FIXME: the following code could probably be
                ## simplified
                relative_path = dirpath[len(self._in_dir) + 1 : ]
                if relative_path:
                    relative_dir = os.path.join(self._out_dir,
                                                relative_path)
                else:
                    relative_dir = self._out_dir
                if is_a_source_file:
                    output_filename = filename[:filename.rfind('.') + 1] + 'html'
                else:
                    output_filename = filename
                output = os.path.join(relative_dir, output_filename)

                if not self._force and os.path.exists(output) and \
                        os.stat(input).st_mtime < os.stat(output).st_mtime:
                    logging.info('Ignoring "%s" because previously '\
                                 'generated file seems to be up to '\
                                 'date.', input)
                    continue

                if not os.path.exists(relative_dir):
                    logging.info('Creating new directory: "%s"',
                                 relative_dir)
                    if not self._do_nothing:
                        os.mkdir(relative_dir)

                if not is_a_source_file:
                    logging.info('Copying file "%s" to "%s".',
                                 input, output)
                    if not self._do_nothing:
                        copyfile(input, output)
                else:
                    if relative_path:
                        relative_path = '/' + relative_path
                    path = '/'.join((relative_path, output_filename))
                    self.processFile(input, output, path)

        logging.info("Web site has been built.")


    def processFile(self, input, output, path):
        """Process ``input`` and write to ``output``.

        ``path`` is the absolute web path of ``output``.
        """
        logging.info('Processing "%s" (writing in "%s").',
                     input, output)

        source = open(input).read()
        for filter in self._pre_filters:
            source = filter(source)
        body, meta = self.rest2html(source)

        context = Context(path, source, body, meta,
                          self._layout, self._bindings)

        content = self._page.pt_render(namespace={'context': context})

        for filter in self._post_filters:
            content = filter(content)

        if not self._do_nothing:
            out = open(output, 'w+')
            out.write(content.encode(ENCODING))
            out.close()


    def rest2html(self, text):
        """Convert ``text`` from reStructuredText to HTML and return
        generated (HTML) content and meta informations.
        """
        writer = Writer()
        parts = publish_parts(text,
                              writer=writer,
                              settings_overrides=DOCUTILS_SETTINGS)
        meta = {}
        for value, key in META_REGEXP.findall(parts['meta']):
            meta[key] = value

        meta['title'] = parts['title']
        return parts['body'], meta


    def isASourceFile(self, filename):
        """Tells whether or not ``filename`` is a source file.

        This function is here merely for compatibility issues with
        ``endswith()`` versions prior to Python 2.5.
        """
        for suffix in SOURCE_SUFFIXES:
            if filename.endswith(suffix):
                return True
        return False


class Context:
    """Create a "context" for the page template.

    The context "represents" the HTML page and has a few attributes
    which will be available from the page template: ``path``,
    ``content``, ``meta``, etc. Other bindings can be added by the
    user.
    """

    def __init__(self, path, source, content, meta, layout, bindings):
        """Initialize the context object.

        The following attributes are set:

        ``path``
          absolute path of the page (e.g. ``/foo/bar.html``).

        ``source``
          source of the page.

        ``content``
          HTML content of the page.

        ``meta``
          a mapping which should at least have a ``title`` key. Other
          keys are optional and actually depends on the reST source.

        ``layout``
          main page template

        ``bindings``
          other bindings, as a list of functions that takes the
          context object as their parameter.
        """
        self.path = path
        self.source = source
        self.content = content
        self.meta = meta
        self.layout = layout
        for binding in bindings:
            setattr(self.__class__, binding.__name__, binding)
