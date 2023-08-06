# -*- coding: utf-8 -*-
# Copyright: This module is put into the public domain.
# Author: Marcello Perathoner <webmaster@gutenberg.org>

"""

Mydocutils writer package.

"""

__docformat__ = 'reStructuredText'

import collections
import operator

from docutils import nodes, writers
import roman


class Writer (writers.Writer):
    """ A base class for writers. """

    output = None
    """Final translated form of `document`."""

    config_section_dependencies = ('writers', )

    def translate (self):
        visitor = self.translator_class (self.document)
        self.document.walkabout (visitor)
        self.output = visitor.astext ()

        
class TablePass1 (nodes.SparseNodeVisitor):

    """
    Makes a first pass over table to get row and col count.
    """
    
    def __init__ (self, document):
        nodes.SparseNodeVisitor.__init__ (self, document)
        
        self.row = -1     # 0-based
        self.column = 0   # 0-based
        self.cells = 0
        self.colspecs = None

    def visit_table (self, table):
        """ Called on each table. """
        self.colspecs = table.traverse (nodes.colspec)
        width = sum (map (operator.itemgetter ('colwidth'), self.colspecs))
        for colspec in self.colspecs:
            colspec['relative_width'] = float (colspec['colwidth']) / width
            
    def depart_table (self, table):
        table['rows'] = self.rows ()
        table['columns'] = self.cols ()

    def visit_row (self, dummy_node):
        """ Called on each table row. """
        self.row += 1
        self.column = 0
        for colspec in self.colspecs:
            colspec['spanned'] = max (0, colspec.get ('spanned', 0) - 1)
        
    def visit_entry (self, node):
        """ Called on each table cell. """

        morerows = node.get ('morerows', 0)
        morecols = node.get ('morecols', 0)

        self.cells += (morecols + 1) * (morerows + 1)

        # skip columns that are row-spanned by preceding entries
        while True:
            colspec = self.colspecs [self.column]
            if colspec.get ('spanned', 0) > 0:
                placeholder = nodes.entry ()
                placeholder['column'] = self.column
                placeholder.colspecs = self.colspecs[self.column:self.column + 1]
                placeholder['vspan'] = True
                node.replace_self ([placeholder, node])
                self.column += 1
            else:
                break

        # mark columns we row-span
        if morerows:
            for colspec in self.colspecs [self.column : self.column + 1 + morecols]:
                colspec['spanned'] = morerows + 1

        node['row'] = self.row
        node['column'] = self.column
        
        node.colspecs = self.colspecs[self.column:self.column + morecols + 1]

        self.column += 1 + morecols
        
        raise nodes.SkipNode

    def rows (self):
        """ Return the no. of columns. """
        return self.row + 1

    def cols (self):
        """ Return the no. of columns. """
        return self.cells / self.rows ()


class ListEnumerator:
    """ Enumerate according to type. """

    def __init__ (self, node, encoding):
        self.type  = node.get ('enumtype') or node.get ('bullet') or '*'
        self.start = node['start'] if 'start' in node else 1
        self.prefix = node.get ('prefix', '')
        self.suffix = node.get ('suffix', '')
        self.encoding = encoding

        self.indent = len (self.prefix + self.suffix) + 1
        if self.type == 'arabic':
            # indentation depends on end value
            self.indent += len (str (self.start + len (node.children)))
        elif self.type.endswith ('alpha'):
            self.indent += 1
        elif self.type.endswith ('roman'):
            self.indent += 5 # FIXME: calculate real length
        else:
            self.indent += 1 # none, bullets, etc.

    def get_next (self):
        """ Get next enumerator. """
        if self.type == 'none':
            res = ''
        elif self.type == '*':
            res = u'•' if self.encoding == 'utf-8' else '-'
        elif self.type == '-':
            res = u'-'
        elif self.type == '+':
            res = u'+'
        elif self.type == 'arabic':
            res = "%d" % self.start
        elif self.type == 'loweralpha':
            res = "%c" % (self.start + ord ('a') - 1)
        elif self.type == 'upperalpha':
            res = "%c" % (self.start + ord ('A') - 1)
        elif self.type == 'upperroman':
            res = roman.toRoman (self.start).upper ()
        elif self.type == 'lowerroman':
            res = roman.toRoman (self.start).lower ()
        else:
            res = "%d" % self.start

        self.start += 1

        return self.prefix + res + self.suffix

    def get_width (self):
        """ Get indent width for this list. """
        return self.indent


class Translator (nodes.NodeVisitor):
    """ A base translator """

    admonitions = """
    attention caution danger error hint important note tip warning
    """.split ()

    docinfo_elements = """
    address author contact copyright date organization revision status
    version
    """.split ()

    # see http://docutils.sourceforge.net/docs/ref/doctree.html#simple-body-elements

    simple_body_elements = tuple ((getattr (nodes, n) for n in """
    comment doctest_block image literal_block math_block paragraph 
    pending raw rubric substitution_definition target
    """.split ()))

    simple_body_subelements = tuple ((getattr (nodes, n) for n in """
    attribution caption classifier colspec field_name 
    label line option_argument option_string term
    """.split ()))

    mixed_contents_elements = simple_body_elements + simple_body_subelements

    # all classes you register with register_inline must be inheritable

    block_inherits = set ()

    inline_inherits = set ()

    def __init__ (self, document):
        nodes.NodeVisitor.__init__ (self, document)
        self.settings = document.settings
        
        self.body = []
        self.context = self.body # start with context == body
        self.docinfo = collections.defaultdict (list)
        self.list_enumerator_stack = []
        self.section_level = 0
        self.vspace = 0 # pending space (need this for collapsing)
        self.src_vspace = 0 # pending space for source pretty printing

        self.field_name = None
        self.compacting = 0 # > 0 if we are inside a compacting list
        
        self.inline_classes_prefixes = [] # order in which to apply classes
        self.inline_classes_suffixes = [] # reverse of above
        self.block_classes_prefixes = []  # order in which to apply classes
        self.block_classes_suffixes = []  # reverse of above
        
        self.environments = [] # holds pushed environments
        self.in_literal = 0    # are we inside one or more literal blocks?

        self.register_classes ()
        
        for name in self.docinfo_elements:
            setattr (self, 'visit_' + name,
                     lambda node: self.visit_field_body (node, name))
            setattr (self, 'depart_' + name, self.depart_field_body)
            
        for adm in self.admonitions:
            setattr (self, 'visit_' + adm,
                     lambda node: self.visit_admonition (node, adm))
            setattr (self, 'depart_' + adm, self.depart_admonition)
            
        self.attribution_formats = {'dash':         (u'—— ', ''),
                                    'parentheses':  ('(', ')'),
                                    'parens':       ('(', ')'),
                                    'none':         ('',  '')}


    def register_classes (self):
        pass


    def inherit_classes (self, node):
        """ Inherit some classes from parent. """

        parent = node.parent

        classes = set (node['classes'])
        classes_on_parent = set (parent['classes'])

        if isinstance (node, nodes.Inline):
            classes |= (self.inline_inherits & classes_on_parent)
        else:
            classes |= (self.block_inherits & classes_on_parent)

        #print 'classes: ', classes

        classes -= set ([c[3:] for c in classes if c.startswith ('no-')])

        #print classes

        node['classes'] = list (classes)


    def dispatch_visit (self, node):
        """
        Call self."``visit_`` + node class name" with `node` as
        parameter.  If the ``visit_...`` method does not exist, call
        self.unknown_visit.

        There are 3 hooks for every visit:
        
        pre_visit_block
        visit_<classname>
        visit_block or visit_Inline
        visit_mixed_contents_element

        """

        if node.parent and not isinstance (node, nodes.Text):
            self.inherit_classes (node)

        node.is_block = not isinstance (node, (nodes.Text, nodes.Inline))
        node.is_simple = isinstance (node, self.mixed_contents_elements)
        node.is_inline = isinstance (node, nodes.Inline)

        if node.is_block:
            self.pre_visit_block (node)

        node_name = node.__class__.__name__
        method = getattr (self, 'visit_' + node_name, self.unknown_visit)
        self.document.reporter.debug (
            'docutils.nodes.NodeVisitor.dispatch_visit calling %s for %s'
            % (method.__name__, node_name))
        res = method (node)

        if node.is_block:
            self.visit_block (node)
            if node.is_simple:
                self.visit_mixed_contents_element (node)
        elif node.is_inline:
            self.visit_Inline (node)

        return res

    def dispatch_departure (self, node):
        """
        Call self."``depart_`` + node class name" with `node` as
        parameter.  If the ``depart_...`` method does not exist, call
        self.unknown_departure.
        """

        if node.is_block:
            if node.is_simple:
                self.depart_mixed_contents_element (node)
            self.depart_block (node)
        elif node.is_inline:
            self.depart_Inline (node)

        node_name = node.__class__.__name__
        method = getattr (self, 'depart_' + node_name, self.unknown_departure)
        self.document.reporter.debug (
            'docutils.nodes.NodeVisitor.dispatch_departure calling %s for %s'
            % (method.__name__, node_name))
        res = method (node)

        if node.is_block:
            self.post_depart_block (node)

        return res

    def unknown_visit (self, node):
        pass

    def unknown_departure (self, node):
        pass

    def pre_visit_block (self, node):
        """ The very first hook called on a block. """
        pass

    def post_depart_block (self, node):
        """ The very last hook called on a block. """
        pass

    def visit_block (self, node):
        """ Called on a block after visit_<classname>. """
        pass

    def depart_block (self, node):
        """ Called on a block before depart_<classname>. """
        pass

    def visit_mixed_contents_element (self, node):
        """ Called on a simple body element after visit_block. 
        
        Because simple body elements have a mixed content and contain
        inline elements, this is a good place to output inline stylings
        that are set on the block.

        """
        pass

    def depart_mixed_contents_element (self, node):
        """ Called at the end of a block, after visiting the inline elements. """
        pass

    def visit_Inline (self, node):
        """ Called on an inline after visit_<classname>. """
        pass

    def depart_Inline (self, node):
        """ Called on an inline before depart_<classname>. """
        pass

    def register_inline_class (self, class_, prefix, suffix):
        """ Register inline class. 

        Inline classes get honored immediately inside `simple body
        elements´ and `inline´ elements. These elements have a mixed
        content model and may contain inline elements and Text.

        """

        self.inline_classes_prefixes.append ( (class_, prefix) )
        self.inline_classes_suffixes.insert (0, (class_, suffix))

    def register_block_class (self, class_, prefix, suffix):
        """ Register block class. 

        Block classes get honored immediately inside a block.

        """
        self.block_classes_prefixes.append ( (class_, prefix) )
        self.block_classes_suffixes.insert (0, (class_, suffix))

    def prefix_for_block (self, classes):
        return self.prefix_for_classes (classes, self.block_classes_prefixes)

    def suffix_for_block (self, classes):
        return self.prefix_for_classes (classes, self.block_classes_suffixes)

    def prefix_for_inline (self, classes):
        return self.prefix_for_classes (classes, self.inline_classes_prefixes)

    def suffix_for_inline (self, classes):
        return self.prefix_for_classes (classes, self.inline_classes_suffixes)

    def prefix_for_classes (self, classes, array):
        """ Helper for inline handlers. """
        if isinstance (classes, basestring):
            classes = classes.split ()

        res = []
        for s in array:
            if s[0] in classes:
                res.append (s[1])
        return res
    
    def set_class_on_child (self, node, class_, index = 0):
        """
        Set class `class_` on the visible child no. index of `node`.
        Do nothing if node has fewer children than `index`.
        """
        children = [n for n in node if not isinstance (n, nodes.Invisible)]
        try:
            child = children[index]
        except IndexError:
            return
        child['classes'].append (class_)

    def set_first_last (self, node):
        """ Set class 'first' on first child, 'last' on last child. """
        self.set_class_on_child (node, 'first', 0)
        self.set_class_on_child (node, 'last', -1)
 	
    def astext (self):
        """ Return the final formatted document as a string. """
        return self.preamble () + ''.join (self.context) + self.postamble ()

    def comment (self, text):
        """ Output a comment. """
        pass
    
    def text (self, text):
        """ Output text. """
        pass

    def sp (self, n = 1):
        """ Add vertical spacing. Delay output for collapsing. """
        if n == 0:
            self.vspace = 1999
        else:
            self.vspace = max (n, self.vspace)

    def src_sp (self, n = 1):
        """ Add vertical spacing to the source. """
        if n == 0:
            self.src_vspace = 1999
        else:
            self.src_vspace = max (n, self.src_vspace)

    def output_sp (self):
        pass
    
    def output_src_sp (self):
        pass
    
    def push (self):
        """ Push environment. """
        pass
       
    def pop (self):
        """ Pop environment. """
        pass
        
    def br_if_line_longer_than (self, length):
        """ Go one line up if the last line was shorter than length.

        Use this to compact lists etc. """
        pass
        
    def indent (self, by = 2):
        """ Indent text. """
        pass

    def rindent (self, by = 2):
        """ Indent text on the right side. """
        pass

    def preamble (self):
        return ''

    def postamble (self):
        return ''

    def visit_title (self, node):
        if isinstance (node.parent, nodes.section):
            self.visit_section_title (node)
        elif isinstance (node.parent, nodes.topic):
            self.visit_topic_title (node)
        elif isinstance (node.parent, nodes.table):
            self.visit_table_caption (node)
        elif isinstance (node.parent, nodes.document):
            self.visit_document_title (node)
        elif isinstance (node.parent, nodes.sidebar):
            pass
        elif isinstance (node.parent, nodes.admonition):
            pass
        else:
            assert ("Can't happen.")

    def depart_title (self, node):
        if isinstance (node.parent, nodes.section):
            self.depart_section_title (node)
        elif isinstance (node.parent, nodes.topic):
            self.depart_topic_title (node)
        elif isinstance (node.parent, nodes.table):
            self.depart_table_caption (node)
        elif isinstance (node.parent, nodes.document):
            self.depart_document_title (node)

    def visit_subtitle (self, node):
        if isinstance (node.parent, nodes.document):
            self.visit_document_subtitle (node)
        else:
            self.visit_section_subtitle (node)
        
    def depart_subtitle (self, node):
        if isinstance (node.parent, nodes.document):
            self.depart_document_subtitle (node)
        else:
            self.depart_section_subtitle (node)
        
