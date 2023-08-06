# $Id$
# Authors: Chris Liechti <cliechti@gmx.net>;
#          David Goodger <goodger@python.org>
# Copyright: This module has been placed in the public domain.

"""
HTML5 Slideshow Writer.
"""

__docformat__ = 'reStructuredText'


import sys
import os
import re
import shutil

import docutils
from docutils import frontend, nodes, utils
from docutils.writers import html4css1
from docutils.parsers.rst import directives
from docutils._compat import b


themes_dir_path = utils.relative_path(
    os.path.join(os.getcwd(), 'dummy'),
    os.path.join(os.path.dirname(__file__), 'themes'))


def find_theme(name):
    # Where else to look for a theme?
    # Check working dir?  Destination dir?  Config dir?  Plugins dir?
    path = os.path.join(themes_dir_path, name)
    if not os.path.isdir(path):
        raise docutils.ApplicationError(
            'Theme directory not found: %r (path: %r)' % (name, path))
    return path


class Writer(html4css1.Writer):

    settings_spec = html4css1.Writer.settings_spec + (
        'S5 Slideshow Specific Options',
        'For the S5/HTML writer, the --no-toc-backlinks option '
        '(defined in General Docutils Options above) is the default, '
        'and should not be changed.',
        (('Specify an installed HTML5 theme by name.  Overrides --theme-url.  '
          'The default theme name is "default".  The theme files will be '
          'copied into a "ui/<theme>" directory, in the same directory as the '
          'destination file (output HTML).  Note that existing theme files '
          'will not be overwritten (unless --overwrite-theme-files is used).',
          ['--theme'],
          {'default': 'default', 'metavar': '<name>',
           'overrides': 'theme_url'}),
         ('Specify an HTML5 slideshow theme URL.  The destination file (output HTML) will '
          'link to this theme; nothing will be copied.  Overrides --theme.',
          ['--theme-url'],
          {'metavar': '<URL>', 'overrides': 'theme'}),
         ('Specify an HTML5 slideshow theme path.  ',
          ['--theme-dir'],
          {'action': 'store',}),
         ('Allow existing theme files in the ``ui/<theme>`` directory to be '
          'overwritten.  The default is not to overwrite theme files.',
          ['--overwrite-theme-files'],
          {'action': 'store_true', 'validator': frontend.validate_boolean}),
         ('Keep existing theme files in the ``ui/<theme>`` directory; do not '
          'overwrite any.  This is the default.',
          ['--keep-theme-files'],
          {'dest': 'overwrite_theme_files', 'action': 'store_false'}),
         ('Set the initial view mode to "slideshow" [default] or "outline".',
          ['--view-mode'],
          {'choices': ['slideshow', 'outline'], 'default': 'slideshow',
           'metavar': '<mode>'}),
         ('Enable the current slide indicator ("1 / 15").  '
          'The default is to disable it.',
          ['--current-slide'],
          {'action': 'store_true', 'validator': frontend.validate_boolean}),
         ))

    settings_default_overrides = {'toc_backlinks': 0}

    config_section = 'html5_slide writer'
    config_section_dependencies = ('writers', 'html4css1 writer')

    def __init__(self):

        self.settings_default_overrides.update(
            {
                'initial_header_level': 3,
                'xml_declaration': False,
             },
        )

        html4css1.Writer.__init__(self)
        self.translator_class = HTML5SlideTranslator


class HTML5SlideTranslator(html4css1.HTMLTranslator):

    doctype = '<!DOCTYPE html>\n\n'

    head_prefix_template = '<html>'

    s5_stylesheet_template = """\
<meta charset='utf-8'>
<link rel='stylesheet' href='%(path)s/theme.css' />

<!-- style sheet links -->
<script>
var PERMANENT_URL_PREFIX = '%(path)s/';
</script>
<script src="%(path)s/slides.js" type="text/javascript"></script>

"""

    layout_template=""

    default_theme = 'default'
    """Name of the default theme."""

    base_theme_file = '__base__'
    """Name of the file containing the name of the base theme."""

    direct_theme_files = (
        'styles.css',
        'theme.css',
    )
    """Names of theme files directly linked to in the output HTML"""

    indirect_theme_files = (
        'prettify.js',
        'slides.js',
        'images',
    )
    """Names of files used indirectly; imported or used by files in
    `direct_theme_files`."""

    required_theme_files = indirect_theme_files + direct_theme_files
    """Names of mandatory theme files."""

    def __init__(self, *args):
        html4css1.HTMLTranslator.__init__(self, *args)

        #insert S5-specific stylesheet and script stuff:
        self.theme_file_path = None
        self.setup_theme()
        view_mode = self.document.settings.view_mode
        self.stylesheet.append(self.s5_stylesheet_template
                               % {'path': self.theme_file_path}
                               )

        self.s5_footer = []
        self.s5_header = []
        self.section_count = 0
        self.theme_files_copied = None

    def setup_theme(self):
        if self.document.settings.theme:
            self.copy_theme()
        elif self.document.settings.theme_url:
            self.theme_file_path = self.document.settings.theme_url
        else:
            raise docutils.ApplicationError(
                'No theme specified for S5/HTML writer.')

    def copy_theme(self):
        """
        Locate & copy theme files.

        A theme may be explicitly based on another theme via a '__base__'
        file.  The default base theme is 'default'.  Files are accumulated
        from the specified theme, any base themes, and 'default'.
        """
        settings = self.document.settings
        if settings.theme_dir:
            path = os.path.join(os.getcwd(), settings.theme_dir)
            settings.theme = [p for p in
                              settings.theme_dir.split(os.path.sep)
                              if p][-1]
        else:
            path = find_theme(settings.theme)
        theme_paths = [path]
        self.theme_files_copied = {}
        required_files_copied = {}
        # This is a link (URL) in HTML, so we use "/", not os.sep:
        self.theme_file_path = '%s/%s' % ('ui', settings.theme)
        if settings._destination:
            dest = os.path.join(
                os.path.dirname(settings._destination), 'ui', settings.theme)
            if not os.path.isdir(dest):
                os.makedirs(dest)
        else:
            # no destination, so we can't copy the theme
            return
        default = False
        while path:
            for f in os.listdir(path):  # copy all files from each theme
                if f == self.base_theme_file:
                    continue            # ... except the "__base__" file
                if ( self.copy_file(f, path, dest)
                     and f in self.required_theme_files):
                    required_files_copied[f] = 1
            if default:
                break                   # "default" theme has no base theme
            # Find the "__base__" file in theme directory:
            base_theme_file = os.path.join(path, self.base_theme_file)
            # If it exists, read it and record the theme path:
            if os.path.isfile(base_theme_file):
                lines = open(base_theme_file).readlines()
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        path = find_theme(line)
                        if path in theme_paths: # check for duplicates (cycles)
                            path = None         # if found, use default base
                        else:
                            theme_paths.append(path)
                        break
                else:                   # no theme name found
                    path = None         # use default base
            else:                       # no base theme file found
                path = None             # use default base
            if not path:
                path = find_theme(self.default_theme)
                theme_paths.append(path)
                default = True
        if len(required_files_copied) != len(self.required_theme_files):
            # Some required files weren't found & couldn't be copied.
            required = list(self.required_theme_files)
            for f in required_files_copied.keys():
                required.remove(f)
            raise docutils.ApplicationError(
                'Theme files not found: %s'
                % ', '.join(['%r' % f for f in required]))

    files_to_skip_pattern = re.compile(r'~$|\.bak$|#$|\.cvsignore$')

    def copy_file(self, name, source_dir, dest_dir):
        """
        Copy file `name` from `source_dir` to `dest_dir`.
        Return 1 if the file exists in either `source_dir` or `dest_dir`.
        """
        source = os.path.join(source_dir, name)
        dest = os.path.join(dest_dir, name)

        if dest in self.theme_files_copied:
            return 1
        else:
            self.theme_files_copied[dest] = 1

        if self.files_to_skip_pattern.search(source):
            return None
        settings = self.document.settings
        if os.path.exists(dest) and not settings.overwrite_theme_files:
            settings.record_dependencies.add(dest)
        else:
            if os.path.isfile(source):
                src_file = open(source, 'rb')
                src_data = src_file.read()
                src_file.close()
                dest_file = open(dest, 'wb')
                dest_dir = dest_dir.replace(os.sep, '/')
                dest_file.write(src_data.replace(
                    b('ui/default'),
                    dest_dir[dest_dir.rfind('ui/'):].encode(
                    sys.getfilesystemencoding())))
                dest_file.close()
                settings.record_dependencies.add(source)
            elif os.path.isdir(source):
                if os.path.exists(dest):
                    shutil.rmtree(dest)
                shutil.copytree(source, dest)

            return 1

        if os.path.exists(dest):
            return 1

    def depart_document(self, node):
        self.head_prefix.extend([self.doctype,
                                 self.head_prefix_template %
                                 {'lang': self.settings.language_code}])
        self.html_prolog.append(self.doctype)
        self.meta.insert(0, self.content_type % self.settings.output_encoding)
        self.head.insert(0, self.content_type % self.settings.output_encoding)

        header = ''.join(self.s5_header)
        footer = ''.join(self.s5_footer)
        title = ''.join(self.html_title).replace('<h1 class="title">', '<h1>')
        layout = self.layout_template % {'header': header,
                                         'title': title,
                                         'footer': footer}
        self.fragment.extend(self.body)
        self.body_prefix.extend(layout)
        self.body_prefix.append("<section class='slides layout-regular template-%s'>\n" %
                                self.document.settings.theme)
        self.body_prefix.append(
            self.starttag({'classes': ['slide level-0']}, 'article'))
        if not self.section_count:
            self.body.append('</div>\n')
        self.body_suffix.insert(0, '</section>\n')
        # skip content-type meta tag with interpolated charset value:
        self.html_head.extend(self.head[1:])
        self.html_body.extend(self.body_prefix[1:] + self.body_pre_docinfo
                              + self.docinfo + self.body
                              + self.body_suffix[:-1])

    def depart_footer(self, node):
        start = self.context.pop()
        self.s5_footer.append('<h2>')
        self.s5_footer.extend(self.body[start:])
        self.s5_footer.append('</h2>')
        del self.body[start:]

    def depart_header(self, node):
        start = self.context.pop()
        header = ['<div id="header">\n']
        header.extend(self.body[start:])
        header.append('\n</div>\n')
        del self.body[start:]
        self.s5_header.extend(header)

    def visit_section(self, node):

        if not self.section_count:
            self.body.append('\n</article>\n')
        self.section_count += 1
        self.section_level += 1

        if self.section_level > 2:
            # dummy for matching div's
            self.body.append(
                self.starttag(
                    node, 'div', CLASS='section level-%s' % self.section_level)
            )
        else:
            if self.section_level == 2 and not getattr(node.parent, 'closed', False):
                # close the previous slide
                node.parent.closed = True
                self.body.append('\n</article>\n')

            node.closed = False
            self.body.append(
                self.starttag(
                    node, 'article', CLASS='slide level-%s' % self.section_level))

    def depart_section(self, node):
        self.section_level -= 1
        if not getattr(node, 'closed', False):
            self.body.append('</article>\n')

    def visit_subtitle(self, node):
        if isinstance(node.parent, nodes.section):
            level = self.section_level + self.initial_header_level - 1
            if level == 1:
                level = 2
            tag = 'h%s' % level
            self.body.append(self.starttag(node, tag, ''))
            self.context.append('</%s>\n' % tag)
        else:
            html4css1.HTMLTranslator.visit_subtitle(self, node)

    def visit_title(self, node):
        html4css1.HTMLTranslator.visit_title(self, node)

    def visit_table(self, node):
        classes = ' '.join(['docutils', self.settings.table_style]).strip()
        self.body.append(
            self.starttag(node, 'table', CLASS=classes))
