#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Martín Gaitán <gaitan@gmail.com>
# based on Bruno Renie's work <bruno@renie.fr>
# 
# Contributors: timtam, 


"""
HTML5 Slideshow Writer
"""

__docformat__ = 'reStructuredText'


import os
import re
import sys
import shutil
import docutils
from docutils import frontend, nodes, utils, languages
from docutils.writers import html4css1
from docutils.parsers.rst import directives
from docutils._compat import b
import inspect


from . import __version__, url
import rst_directive




class Writer(html4css1.Writer):
    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = HTML5Translator

class HTML5Translator(html4css1.HTMLTranslator):
    doctype = '<!DOCTYPE html>\n'
    head_prefix_template = '<html lang="%s">\n'
    content_type = '<meta charset="%s">\n'
    stylesheet_link = '<link rel="stylesheet" href="ui/styles.css" />\n'\
                      '<link rel="stylesheet" href="ui/pygments_style.css" />\n'\
                      '<link rel="stylesheet" href="ui/user.css" />\n'
    nav = """\n
    <header>
    <nav>
        <ul>
            <li><button id="prev-btn" title="Previous slide">Previous Slide</button></li>
            <li><span id="slide-number"></span>/<span id="slide-total"></span></li>
            <li><button id="next-btn" title="Next Slide">Next Slide</button></li>
        </ul>
    </nav>
    </header>\n"""
    js = """\n
        <script src="ui/jquery-1.4.2.min.js"></script>
        <script src="ui/htmlSlides.js"></script>
        """
    generator = '<meta name="generator" content="rst2slides %s" />'


    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)
        self.settings = settings = document.settings
        lcode = settings.language_code
        arglen=len(inspect.getargspec(languages.get_language)[0])
        if arglen == 2:
            self.language = languages.get_language(lcode,self.document.reporter)
        else:
            self.language = languages.get_language(lcode)
        self.meta = [self.content_type % settings.output_encoding,
                     self.generator % __version__]
        self.head_prefix = []
        self.html_prolog = []
        #if settings.xml_declaration:
        #    self.head_prefix.append(self.xml_declaration
        #                            % settings.output_encoding)
            # encoding not interpolated:
            #self.html_prolog.append(self.xml_declaration)
        self.head_prefix.extend([self.doctype,
                                 self.head_prefix_template % lcode])
        self.html_prolog.append(self.doctype)
        self.head = self.meta[:]
        # stylesheets
        styles = utils.get_stylesheet_list(settings)
        if settings.stylesheet_path and not(settings.embed_stylesheet):
            styles = [utils.relative_path(settings._destination, sheet)
                      for sheet in styles]
        self.stylesheet = [self.stylesheet_link,]
        self.body_prefix = ['</head>\n<body>%s\n' % self.nav]
        # document title, subtitle display
        self.body_pre_docinfo = []
        # author, date, etc.
        self.docinfo = []
        self.body = []
        self.fragment = []
        self.body_suffix = ['%s</body>\n</html>\n' % self.js]
        self.section_level = 0
        self.initial_header_level = int(settings.initial_header_level)
        # A heterogenous stack used in conjunction with the tree traversal.
        # Make sure that the pops correspond to the pushes:
        self.context = []
        self.topic_classes = []
        self.colspecs = []
        self.compact_p = 1
        self.compact_simple = None
        self.compact_field_list = None
        self.in_docinfo = None
        self.in_sidebar = None
        self.title = []
        self.subtitle = []
        self.header = []
        self.footer = []
        self.html_head = [self.content_type] # charset not interpolated
        self.html_title = []
        self.html_subtitle = []
        self.html_body = []
        self.in_document_title = 0
        self.in_mailto = 0
        self.author_in_authors = None
        self.quit_next = False
    
    def visit_document(self, node):
        self.head.append('<title>%s</title>\n'
                         % node.get('title', '') )

    def depart_document(self, node):
        self.fragment.extend(self.body)
        self.body_prefix.append("<div id='deck'>\n")
        self.body_suffix.insert(0, '</div>\n')
        self.html_head.extend(self.head[1:])
        self.html_body.extend(self.body_prefix[1:] + self.body_pre_docinfo
                              + self.docinfo + self.body
                              + self.body_suffix[:-1])
        self.copy_files()

    def visit_section(self, node):
        if self.quit_next:
            self.body.append('</section>\n')
            self.quit_next = False
        self.section_level += 1
        if self.section_level == 1:
            self.body.append('<section>\n')

    def depart_section(self, node):
        self.section_level -= 1
        if self.section_level == 0:
            self.body.append('  </section>\n\n')

    def visit_title(self, node):
        if self.section_level == 0:
            self.body.append('<section>\n')
            self.quit_next = True
        if self.section_level in (0, 1):
            self.body.append('<hgroup>\n')
            self.body.append('    <h1>\n')
        else:
            self.body.append('    <h%s>\n' % self.section_level)

    def depart_title(self, node):
        if self.section_level in (0, 1):
            self.body.append('    </h1>\n')
            self.body.append('</hgroup>\n')
        else:
            self.body.append('    </h%s>\n' % self.section_level)

    def visit_header(self, node):
        self.context.append(len(self.body))

    def depart_header(self, node):
        start = self.context.pop()
        footer = [self.starttag(node, 'header')]
        footer.append('<h1>\n')
        footer.extend(self.body[start:])
        footer.append('</h1>\n')
        footer.append('</header>\n')
        self.footer.extend(footer)
        self.body_suffix[:0] = footer

    def visit_footer(self, node):
        self.context.append(len(self.body))

    def depart_footer(self, node):
        start = self.context.pop()
        footer = [self.starttag(node, 'footer')]
        footer.append('<p>\n')
        elements = self.body[start:]
        for i, part in enumerate(elements):
            if ' | ' in part:
                flag = True
                break
        else:
            flag = False
        if flag:
            elements = elements[:i] + [part.split(' | ')[0], '<address>', 
                       part.split(' | ')[1]] + elements[i+1:] + ['</address>'] 
        footer.extend(elements)
            
        #import ipdb; ipdb.set_trace()

        footer.append('</p>\n')
        footer.append('</footer>\n')
        self.footer.extend(footer)
        self.body_suffix[:0] = footer


    def copy_files(self):
        """
        Locate & copy js and css.
        """

        orig_path = os.path.join(os.path.dirname(__file__), 'data', 'ui')
        orig_path = os.path.abspath(orig_path)
        dest_path = os.path.join(os.getcwd(), 'ui')

        try:
            shutil.copytree(orig_path, dest_path)
        except OSError:
            print './ui exists. Not copied.'
            
