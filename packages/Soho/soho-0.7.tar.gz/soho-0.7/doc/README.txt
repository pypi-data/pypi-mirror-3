.. -*- coding: utf-8 -*-

Soho
====

Soho lets you build a web site from a set of `reStructuredText`_
source files (the content) and a template file (the layout).

.. _reStructuredText: http://docutils.sourceforge.net/rst.html


Why do I need this
------------------

Soho comes from a simple need that I have: I need to easily build
static (or mostly static) web sites. There are lots of ways this can
be done, but I want:

- to use a template: I want the content to be separated from the
  appearance. I also want to have an homogeneous site, with an unique
  layout. I use and like TAL (a.k.a. ZPT, Zope Page Template) a lot,
  so this seems to be a good choice. To me, at least. ;)

- to avoid writing HTML. reStructuredText is great. It lets you easily
  write any text in a readable fashion and can be processed to produce
  files in HTML, LaTeX and other formats. Moreover, this format is
  used to document a lot of Python code (Python itself but also Python
  programs and libraries). I hence use it for my own code, and can
  therefore re-use the documentation to produce a web site, without
  changing anything;

- a static web site that can be served by a standard web server
  (Apache, Lighttpd, Nginx, etc.) or even without any web server.


Typical scenario
----------------

In a nutshell, here is the process:

1. I write the content of my website as reStructuredText files in
   multiple folders and sub-folders if needed.

2. I write a template in TAL.

3. I run Soho, with specific options if needed. For example, I can set
   a list of filters that will be run on each file before or after the
   reStructuredText->HTML conversion.

4. I configure Apache or any other web server to serve my HTML files
   or write them on a CD-ROM, or send them to my low-price hosting
   provider.

.. note::

  If you do not know reStructuredText or TAL, do not run away. Well,
  not yet. ;) Take a look at the `tutorial`_ first. You might see that
  it is quite easy to grasp and that you do not need to master all
  their inner mysteries to build a simple web site, hopefully.

  If you do not like TAL and/or reStructuredText, it should be quite
  easy to hack Soho so that it uses another template engine and/or
  another format for its source files. I am not currently interested
  in developing a generic solution: this is left as an exercise to the
  reader.

  .. _tutorial: tutorial.txt


Examples
--------

An example is worth tons of explanation. Take a look at these:

- `Noherring.com code warehouse`_ (this very site);

- `Bosnie-Herzégovine et Croatie : notes de voyage`_ (trip notes, in
  French).

.. _Noherring.com code warehouse: http://code.noherring.com
.. _Bosnie-Herzégovine et Croatie \: notes de voyage: http://bihhr.noherring.com


Requirements
------------

You need the following programs and libraries to run Soho:

- `Python`_ 2.4 or higher;

- `Docutils`_ 0.5 or higher. Prior versions might work, too;

- `zope.pagetemplate`_ 3.4 or higher. Prior versions might work, too.

.. _Python: http://python.org

.. _Docutils: http://docutils.sourceforge.net

.. _zope.pagetemplate: http://pypi.python.org/pypi/zope.pagetemplate


See also
--------

If Soho does not fit your need, you may want to try out `rest2web`_ or
`Sphinx`_.

.. _rest2web: http://www.voidspace.org.uk/python/rest2web
.. _Sphinx: http://sphinx.pocoo.org


Installation
------------

If you have ``easy_install``, then the following should do the trick::

    $ easy_install soho

For further details, see the `Installation`_ chapter.

.. _Installation: install.txt


Subversion repository
---------------------

Soho source code lives in a Subversion repository. To checkout the
trunk::

    $ svn co https://svn.noherring.com/code/soho/trunk

You can also `browse the sources`_ with the same URL.

.. _`browse the sources`: https://svn.noherring.com/code/soho/trunk


Credits
-------

Soho has been written by Damien Baty. The very first version was based
on `grok2html`_, a small utility that was used to generate the first
version of the web site of `Grok`_.

.. _grok2html: http://svn.zope.org/grok/trunk/doc/grok2html.py
.. _Grok: http://grok.zope.org


License
-------

Soho is copyright 2008 by Damien Baty.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see the `section about licenses`_ of
the `GNU web site`_.

.. _section about licenses: http://www.gnu.org/licenses
.. _GNU web site: http://www.gnu.org
