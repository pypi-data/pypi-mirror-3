#!/usr/bin/env python
#  -*- mode: python; indent-tabs-mode: nil; -*- coding: utf-8 -*-

"""

gutenberg.py

Copyright 2012 by Marcello Perathoner

Distributable under the GNU General Public License Version 3 or newer.

Transforms for the Project Gutenberg flavor.

"""

import datetime

from docutils import nodes
import docutils.transforms
import docutils.transforms.parts

from epubmaker.lib.Logger import error, info, debug, warn
from epubmaker.lib.DublinCore import DublinCore

# pylint: disable=W0142

class GutenbergParams (docutils.transforms.Transform):
    """ Replaces substitution defs with parameters from metadata. """

    default_priority = 219
    """ Before the Substitutions transform. """

    def apply(self):
        doc = self.document
        meta = doc.meta_block
        defs = doc.substitution_defs

        def getone (name, default = None):
            """ Get first value. """
            if name in meta:
                return meta[name][0]
            return default
                
        def getmany (name, default = []):
            """ Get list of all values. """
            return meta.get (name, default)

        title = getone ('PG.Title') or getone ('DC.Title', 'No Title')
        title = title.partition ('\n')[0] 

        language = getmany ('DC.Language', ['en'])
        language = map (lambda x: DublinCore.language_map.get (
            x, 'Unknown').title (), language)
        language = DublinCore.strunk (language)

        copyrighted = getone ('PG.Rights').lower () == 'copyrighted'

        # tweak sub defs
        for name, subdef in defs.items ():
            children = []

            if name == 'upcase-title':
                children = [ nodes.inline ('', title.upper ()) ]

            elif name == 'pg-produced-by':
                producers = getmany ('PG.Producer')
                if producers:
                    children = [ nodes.inline ('', u'Produced by %s.' % 
                                               DublinCore.strunk (producers)) ]
            elif name == 'pg-credits':
                children = [ nodes.inline ('', getone ('PG.Credits', '')) ]

            elif name == 'bibrec-url':
                url = 'http://www.gutenberg.org/ebooks/%s' % getone ('PG.Id', '999999')
                children = [ nodes.reference ('', '', nodes.inline ('', url), refuri = url) ]

            elif name == 'pg-copyrighted-header':
                if copyrighted:
                    continue
                # else delete children

            elif name == 'pg-copyrighted-footer':
                if copyrighted:
                    continue

            elif name == 'pg-machine-header':

                s = u'Title: %s\n\n' % getone ('DC.Title', 'No Title')
                s += u'Author: %s\n\n' % DublinCore.strunk (getmany ('DC.Creator', ['Unknown']))

                date = getone ('PG.Released')
                try:
                    date = datetime.datetime.strptime (date, '%Y-%m-%d')
                    date = datetime.datetime.strftime (date, '%B %d, %Y') 
                except ValueError:
                    date = 'unknown date'
                s += u'Release Date: %s [EBook #%s]\n' % (date, getone ('PG.Id', '999999'))

                for item in getmany ('PG.Reposted', []):
                    try:
                        date, comment = item.split (None, 1)
                    except ValueError:
                        date = item
                        comment = None
                    try:
                        date = datetime.datetime.strptime (date, '%Y-%m-%d')
                        date = datetime.datetime.strftime (date, '%B %d, %Y')
                    except ValueError:
                        date = 'unknown date'

                    s += u'Reposted: %s' % date
                    if comment:
                        s += u' [%s]' % comment
                    s += '\n'
                    
                s += u'\nLanguage: %s\n\n' % language
                s += u'Character set encoding: %s' % doc.settings.encoding.upper ()

                children = [ nodes.inline ('', nodes.Text (s)) ]

            subdef.children = children 


