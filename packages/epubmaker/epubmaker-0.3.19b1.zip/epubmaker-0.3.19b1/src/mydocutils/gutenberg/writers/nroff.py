# -*- coding: utf-8 -*-
# $Id: manpage.py 6270 2010-03-18 22:32:09Z milde $
# Author: Engelbert Gruber <grubert@users.sourceforge.net>
# Copyright: This module is put into the public domain.
# Rewritten almost completely
# by Marcello Perathoner <marcello@perathoner.de>

"""

Nroff writer for reStructuredText. Tweaked for Project Gutenberg usage.

"""

__docformat__ = 'reStructuredText'

from epubmaker.mydocutils.writers import nroff
from epubmaker import Unitame

from epubmaker.lib.Logger import info, debug, warn, error

GUTENBERG_NROFF_PREAMBLE = r""".\" -*- mode: nroff -*- coding: {encoding} -*-
.\" This file produces Project Gutenberg plain text. Usage:
.\"   $ groff -t -K {device} -T {device} this_file > output.txt
.
.pl 100000       \" very tall page: disable pagebreaks
.ll 72m
.po 0
.ad l           \" text-align: left
.nh             \" hyphenation: off
.cflags 0 .?!   \" single sentence space
.cflags 0 -\[hy]\[em]   \" don't break on -
.
.de nop
..
.blm nop        \" do nothing on empty line
.
.nr [env_cnt] 0
.ev 0           \" start in a defined environment
.
.de push_env
.br
.nr last_env \\n[.ev]            \" save current environment name
.nr env_cnt +1   \" generate new environment name
.ev \\n[env_cnt]
.evc \\n[last_env]
..
.de pop_env
.br
.ev
.nr env_cnt -1
..
.
"""

GUTENBERG_NROFF_POSTAMBLE = r""".
.pl 0    \" ends very long page here
.\" End of File
"""

class Writer (nroff.Writer):
    """ A plaintext writer thru nroff. """

    supported = ('pg-nroff',)
    """Formats this writer supports."""

    def __init__ (self):
        nroff.Writer.__init__ (self)
        self.translator_class = Translator

    def translate (self):
        visitor = self.translator_class (self.document)
        del Unitame.unhandled_chars[:]
        self.document.walkabout (visitor)
        self.output = visitor.astext ()
        if Unitame.unhandled_chars:
            error ("unitame: unhandled chars: %s" % u", ".join (set (Unitame.unhandled_chars)))

    #def get_transforms (self):
    #    tfs = writers.Writer.get_transforms (self)
    #    return tfs + [parts.CharsetTransform]

        
        
class Translator (nroff.Translator):
    """ nroff translator """

    def __init__ (self, document):
        nroff.Translator.__init__ (self, document)

        self.attribution_formats['dash'] = (u'———— ' if self.encoding == 'utf-8' else '---- ', '')


    def preamble (self):
        """ Inserts nroff preamble. """
        return GUTENBERG_NROFF_PREAMBLE.format (
            encoding = self.encoding, device = self.device)


    def postamble (self):
        """ Inserts nroff postamble. """
        return GUTENBERG_NROFF_POSTAMBLE.format (
            encoding = self.encoding, device = self.device)


    def init_translate_maps (self):
        nroff.Translator.init_translate_maps (self)

        update = {
            0x0011: ur"\~",       # nbsp, see: Unitame.py
            0x0012: ur"\%",       # shy,  see: Unitame.py
            }

        self.translate_map.update (update)
        self.translate_map_literal.update (update)


    def register_classes (self):
        """ Register classes.
        
        Use the idiosyncratic PG convention of marking up italics etc.

        """

        #
        # This does not call the base class !!!
        #

        self.register_inline_class ('left',         '.ad l',  '')
        self.register_inline_class ('right',        '.ad r',  '')
        self.register_inline_class ('center',       '.ad c',  '')
                                                    
        self.register_inline_class ('byline',       '.ad c',  '')
                                                    
        self.register_inline_class ('italics',     r'_',    r'_')
        self.register_inline_class ('no-italics',  r'_',    r'_')

        self.register_inline_class ('bold',        r'*',    r'*')
        self.register_inline_class ('no-bold',     r'*',    r'*')

        self.register_inline_class ('monospaced',  r'',     r'')
        self.register_inline_class ('superscript', r'',     r'')
        self.register_inline_class ('subscript',   r'',     r'')

        self.register_inline_class ('small-caps',  r'_',    r'_')
        self.register_inline_class ('gesperrt',    r'_',    r'_')
        self.register_inline_class ('antiqua',     r'_',    r'_')
        self.register_inline_class ('larger',      r'',     r'')
        self.register_inline_class ('smaller',     r'',     r'')


    def visit_Text (self, node):
        text = node.astext ()

        # NOTE: there's an alternate approach in
        # transforms.parts.CharsetTransform

        if self.encoding != 'utf-8':
            # reduce the charset while keeping it a unicode string
            text = text.encode (self.encoding, 'unitame')
            text = text.decode (self.encoding)

        if self.in_literal:
            text = text.translate (self.translate_map_literal)
        else:
            text = text.translate (self.translate_map)

        self.text (text)


    def visit_inline (self, node):
        if 'toc-pageref' in node['classes']:
            maxlen = 3 # sensible default
            while node.parent:
                node = node.parent
                if 'pageno_maxlen' in node:
                    maxlen = node['pageno_maxlen']
                    break
            self.cmd (('linetabs 1',
                       r'ta (\n[.l]u - \n[.i]u - %dm) +%dmR' % (maxlen + 1, maxlen + 1),
                       r'lc .'))
            self.text (chr (1) + '\t')
        nroff.Translator.visit_inline (self, node)

    def visit_section_title (self, node):
        """ Implements PG-standard spacing before headers. """
        self.sp (max (2, 5 - self.section_level))

    def visit_figure (self, node):
        self.sp (1)
        self.push ()

    def depart_figure (self, node):
        self.pop ()
        self.sp (1)

    def visit_image (self, node):
        # ignore alt attribute except for dropcaps
        if 'dropcap' in node['classes']:
            self.text (node.attributes.get ('alt', ''))

    def visit_caption (self, node):
        nroff.Translator.visit_caption (self, node)
        self.cmd ('ad l')
        self.text ('[Illustration: ')

    def depart_caption (self, node):
        self.text (']')
        nroff.Translator.depart_caption (self, node)

    def visit_transition (self, node):
        self.sp ()
        self.cmd ('ce 1')
        self.text (u'————' if self.encoding == 'utf-8' else '----')
        self.sp ()

    def visit_page (self, node):
        if 'clearpage' in node['classes']:
            self.sp (4)
        elif 'cleardoublepage' in node['classes']:
            self.sp (4)
        else:
            nroff.Translator.visit_page (self, node)

