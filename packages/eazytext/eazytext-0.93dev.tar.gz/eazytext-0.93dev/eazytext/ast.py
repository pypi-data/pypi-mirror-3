# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

"""Module containing Node definition for all non-teminals and translator
functions for translating the text to HTML.

The AST tree is constructed according to the grammar. From the root
non-terminal use the children() method on every node to walk through the tree,
the only exceptions are,
  * `nowikilines` and `nowikicontent` rules are not available, in the AST
    tree.
  * `basictext`, though is a non-terminal with many alternative terminals,
  * does not differentiate it.

To walk throug the AST,
  * parse() the text, which returns the root non-terminal
  * Use children() method on every non-terminal node.
  * Use _terms and _nonterms attribute to get lists of terminals and
    non-terminals for every node.
"""

# -*- coding: utf-8 -*-

# Gotcha : None
# Notes  : None
# Todo   : None

import sys, re, copy
from   os.path          import basename, abspath, dirname, join, isdir, isfile

from   eazytext.style   import stylemarkup
from   eazytext.lib     import escape_htmlchars, obfuscatemail
from   eazytext.lexer   import ETLexer

templtdir = join( dirname(__file__), 'templates' )

class ASTError( Exception ):
    pass

class Context( object ):
    def __init__( self, htmlindent='' ):
        self.htmlindent = htmlindent

# ------------------- AST Nodes (Terminal and Non-Terminal) -------------------

class Node( object ):

    def __init__( self, parser ):
        self.parser = parser
        self.parent = None
        self.ctx    = parser.etparser.ctx

    def children( self ):
        """Tuple of childrens in the same order as parsed by the grammar rule.
        """
        return tuple()

    def validate( self ):
        """Validate this node and all the children nodes. Expected to be called
        before processing the nodes."""
        pass

    def headpass1( self, igen ):
        """Pre-processing phase 1, useful to implement multi-pass compilers"""
        [ x.headpass1( igen ) for x in self.children() ]

    def headpass2( self, igen ):
        """Pre-processing phase 2, useful to implement multi-pass compilers"""
        [ x.headpass2( igen ) for x in self.children() ]

    def generate( self, igen, *args, **kwargs ):
        """Code generation phase. The result must be an executable python
        script"""
        [ x.generate( igen, *args, **kwargs ) for x in self.children() ]

    def tailpass( self, igen ):
        """Post-processing phase 1, useful to implement multi-pass compilers"""
        [ x.tailpass( igen ) for x in self.children() ]

    def dump( self, c ):
        """Simply dump the contents of this node and its children node and
        return the same."""
        return ''.join([ x.dump(c) for x in self.children() ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ):
        """ Pretty print the Node and all its attributes and children
        (recursively) to a buffer.
            
        buf:   
            Open IO buffer into which the Node is printed.
        
        offset: 
            Initial offset (amount of leading spaces) 
        
        attrnames:
            True if you want to see the attribute names in name=value pairs.
            False to only see the values.
        
        showcoord:
            Do you want the coordinates of each Node to be displayed.
        """

    #---- Helper methods

    def stackcompute( self, igen, compute, astext=True ):
        """Push a new buf, execute the compute function, pop the buffer and
        append that to the parent buffer."""
        igen.pushbuf()
        compute()
        igen.popcompute( astext=astext )
        return None

    def getroot( self ):
        """Get root node traversing backwards from this `self` node."""
        node = self
        parent = node.parent
        while parent : node, parent = parent, parent.parent
        return node

    def bubbleup( self, attrname, value ):
        """Bubble up value `value` to the root node and save that as its
        attribute `attrname`"""
        rootnode = self.getroot()
        setattr( rootnode, attrname, value )

    def bubbleupaccum( self, attrname, value, to=None ):
        """Same as bubbleup(), but instead of assigning the `value` to
        `attrname`, it is appended to the list."""
        rootnode = self.getroot()
        l = getattr( rootnode, attrname, [] )
        l.append( value )
        setattr( rootnode, attrname, l )

    def filter( self, handler ):
        nodes  = list( self.children() )
        result = []
        while nodes :
            node = nodes.pop(0)
            result.append( node ) if handler( node ) else None
            nodes = list( node.children() ) + nodes
        return result

    def flatterminals( self ):
        nodes = list( self.children() )
        result = []
        while nodes :
            node = nodes.pop(0)
            result.append(node) if isinstance(node, Terminal) else None
            nodes = list( node.children() ) + nodes
        return result

    @classmethod
    def setparent( cls, parnode, childnodes ):
        [ setattr( n, 'parent', parnode ) for n in childnodes ]


class Terminal( Node ) :
    """Abstract base class for EazyText AST terminal nodes."""

    def __init__( self, parser, terminal=u'', **kwargs ):
        Node.__init__( self, parser )
        self.terminal = terminal
        [ setattr( self, k, v ) for k,v in kwargs.items() ]

    def __repr__( self ):
        return unicode( self.terminal )

    def __str__( self ):
        return unicode( self.terminal )

    def generate( self, igen, *args, **kwargs ):
        """Dump the content."""
        igen.puttext( self.dump(None) )

    def dump( self, c ):
        """Simply dump the contents of this node and its children node and
        return the same."""
        return self.terminal

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ):
        """ Pretty print the Node and all its attributes and children
        (recursively) to a buffer.
            
        buf:   
            Open IO buffer into which the Node is printed.
        
        offset: 
            Initial offset (amount of leading spaces) 
        
        attrnames:
            True if you want to see the attribute names in name=value pairs.
            False to only see the values.
        
        showcoord:
            Do you want the coordinates of each Node to be displayed.
        """
        lead = ' ' * offset
        buf.write(lead + '<%s>: %r' % (self.__class__.__name__, self.terminal))
        buf.write('\n')


class NonTerminal( Node ):      # Non-terminal
    """Abstract base class for EazyText AST non-terminalnodes."""

    def __init__( self, *args, **kwargs ) :
        parser = args[0]
        Node.__init__( self, parser )
        self._terms, self._nonterms = tuple(), tuple()

    def flatten( self, attrnode, attrs ):
        """Instead of recursing through left-recursive grammar, flatten them
        into sequential list for looping on them later."""
        node, rclist = self, []

        if isinstance(attrs, basestring) :
            fn = lambda n : [ getattr(n, attrs) ]
        elif isinstance(attrs, (list,tuple)) :
            fn = lambda n : [ getattr(n, attr) for attr in attrs ]
        else :
            fn = attrs

        while node :
            rclist.extend( filter( None, list(fn(node))) )
            node = getattr(node, attrnode)
        rclist.reverse()
        return rclist



# ------------------- Non-terminal classes ------------------------

class WikiPage( NonTerminal ):
    """class to handle `wikipage` grammar."""
    tmpl_inclskin  = '<style type="text/css"> %s </style>'
    tmpl_article_o = '<article class="%s">'
    tmpl_article_c = '</article>'
    tmpl_html_o    = '<html><body>'
    tmpl_html_c    = '</body></html>'
    def __init__( self, parser, paragraphs ) :
        # Initialize the context
        NonTerminal.__init__( self, parser, paragraphs )
        self._nonterms = (self.paragraphs,) = (paragraphs,)

    def children( self ) :
        return self._nonterms

    def children( self ):
        return self._nonterms

    def headpass1( self, igen ):
        etparser       = self.parser.etparser
        etxconfig      = etparser.etxconfig
        ashtml, nested = etxconfig['ashtml'], etxconfig['nested']

        igen.initialize()
        # Generate the body function only.
        igen.cr()
        # Body function signature
        line = "def body( *args, **kwargs ) :"
        igen.putstatement( line )
        igen.codeindent( up='  ' )
        igen.pushbuf()

        # Wrapper Template
        (not nested and ashtml) and igen.puttext( self.tmpl_html_o )
        igen.puttext( self.tmpl_article_o % ['etpage', 'etblk'][nested] )

        NonTerminal.headpass1( self, igen )

    def headpass2( self, igen ):
        etparser  = self.parser.etparser
        etxconfig = etparser.etxconfig
        nested    = etxconfig['nested']

        # Use css skin
        if not nested and etxconfig['include_skin'] :
            igen.puttext( self.tmpl_inclskin % etparser.skincss )
        NonTerminal.headpass2( self, igen )

    def generate( self, igen, *args, **kwargs ):
        self.etxhash = kwargs.pop( 'etxhash', '' )
        self.etxfile = self.parser.etparser.etxfile
        # Generate paragraphs
        self.paragraphs.generate( igen, *args, **kwargs )

    def tailpass( self, igen ):
        etparser     = self.parser.etparser
        etxconfig    = etparser.etxconfig
        ashtml, nested = etxconfig['ashtml'], etxconfig['nested']

        igen.cr()
        NonTerminal.tailpass( self, igen )

        # Wrapper close
        igen.puttext( self.tmpl_article_c )
        (not nested and ashtml) and igen.puttext( self.tmpl_html_c )
        # finish body function
        igen.flushtext()
        igen.popreturn( astext=True )
        igen.codeindent( down='  ' )
        # Footer
        igen.comment( "---- Footer" )
        igen.footer( self.etxhash, self.etxfile )
        igen.finish()

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ):
        lead = ' ' * offset
        buf.write( lead + '-->wikipage: ' )
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+5, attrnames, showcoord) for x in self.children() ]


class Paragraphs( NonTerminal ) :
    """class to handle `paragraphs` grammar."""
    def __init__( self, parser, paras, para, ps ):
        NonTerminal.__init__( self, parser, paras, para, ps )
        self._nonterms = \
            (self.paragraphs, self.paragraph, self.paragraph_separator) = \
                paras, para, ps
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def headpass1( self, igen ):
        [ x.headpass1( igen ) for x in self.flatten() ]

    def headpass2( self, igen ):
        [ x.headpass2( igen ) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        [ x.generate( igen ) for x in self.flatten() ]

    def tailpass( self, igen ):
        [ x.tailpass( igen ) for x in self.flatten() ]

    def dump( self, c ):
        return ''.join([ x.dump(c) for x in self.flatten() ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        [ x.show(buf, offset, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        # Getch the attribute in reverse, so that when NonTerminal.flatten()
        # does a merged reverse it will in the correct order.
        return NonTerminal.flatten(
            self, 'paragraphs', ('paragraph_separator', 'paragraph')
        )


class Paragraph( NonTerminal ) :
    """class to handle `paragraph` grammar."""
    def __init__( self, parser, nonterm ) :
        NonTerminal.__init__( self, parser, nonterm )
        self._nonterms = (self.nonterm,) = (nonterm,)
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write(lead + 'paragraph: ')
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


#---- Nowiki

class NoWiki( NonTerminal ) :
    """class to handle `nowikiblock` grammar."""
    def __init__( self, parser, nwopen, nl1, nwlines, nwclose, nl2 ):
        NonTerminal.__init__( self, parser, nwopen, nl1, nwlines, nwclose, nl2 )
        self._terms = \
            self.NOWIKI_OPEN, self.NEWLINE1, self.NOWIKI_CLOSE, self.NEWLINE2 = \
                nwopen, nl1, nwclose, nl2
        self._terms = filter( None, self._terms )
        self._nonterms = (self.nwlines,) = (nwlines,)
        self.text = self.NEWLINE1.dump(None) + \
                    self.nwlines.dump(None) # Don't change the attribute name !!
        self.text = self.text[1:]           # Skip the first new line
        # Fetch the plugin
        try :
            headline = self.NOWIKI_OPEN.dump(None).strip()[3:].strip()
            try    : self.nowikiname, xparams = headline.split(' ', 1)
            except : self.nowikiname, xparams = headline, ''
            nowikiname = self.nowikiname.strip()
            extplugins = parser.etparser.etxconfig.get( 'extplugins', {} )
            factory = extplugins.get( nowikiname, None )
            self.extplugin = factory and factory( xparams.strip() )
            self.extplugin and self.extplugin.onparse(self)
        except :
            if parser.etparser.debug : raise
            self.extplugin = None
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        x = ( self.NOWIKI_OPEN, self.NEWLINE1, self.nwlines, self.NOWIKI_CLOSE,
              self.NEWLINE2 )
        return filter( None, x )

    def headpass1( self, igen ):
        self.extplugin and self.extplugin.headpass1( self, igen )

    def headpass2( self, igen ):
        self.extplugin and self.extplugin.headpass2( self, igen )

    def generate( self, igen, *args, **kwargs ):
        if self.extplugin :
            self.extplugin.generate( self, igen, *args, **kwargs )
        else :
            igen.puttext( escape_htmlchars( self.text ))

    def tailpass( self, igen ):
        self.extplugin and self.extplugin.tailpass( self, igen )
    
    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'ext: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


class NowikiLines( NonTerminal ):
    """class to handle `nowikilines` grammar."""
    def __init__( self, parser, nwlines, nowikitext, newline ) :
        NonTerminal.__init__( self, parser, nwlines, nowikitext, newline )
        self._terms = (self.NOWIKITEXT, self.NEWLINE) = nowikitext, newline
        self._nonterms = (self.nwlines,) = (nwlines,)
        self._terms = filter( None, self._terms )
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return filter( None, (self.nwlines, self.NOWIKITEXT, self.NEWLINE) )

    def headpass1( self, igen ):
        raise Exception( 'Execution does not come to nowikilines' )

    def headpass2( self, igen ):
        raise Exception( 'Execution does not come to nowikilines' )

    def generate( self, igen, *args, **kwargs ):
        raise Exception( 'Execution does not come to nowikilines' )

    def tailpass( self, igen ):
        raise Exception( 'Execution does not come to nowikilines' )

    def dump( self, c ):
        return ''.join([ x.dump(c) for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write(lead + 'nowikilines: ')
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        return NonTerminal.flatten( self, 'nwlines', ('NEWLINE', 'NOWIKITEXT') )


#---- Heading

class Heading( NonTerminal ) :
    """class to handle `heading` grammar."""
    tmpl_o  = '<h%s class="etsec" style="%s">'
    tmpl_c  = '</h%s>\n'
    tmpl_a  = '<a id="%s"></a>'
    tmpl_ah = '<a class="etseclink" href="#%s" title="Link to this section">&#9875;</a>'

    def __init__( self, parser, heading, text_contents, newline ):
        NonTerminal.__init__( self, parser, heading, text_contents, newline )
        self._terms = self.HEADING, self.NEWLINE = heading, newline
        self._nonterms = (self.text_contents,) = (text_contents,)
        self._nonterms = filter( None, self._nonterms )
        self.headtext = self.text_contents and self.text_contents.dump(None) or ''
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return filter( None, (self.HEADING, self.text_contents, self.NEWLINE) )

    def headpass1( self, igen ):
        self.ctx.markupstack = []
        NonTerminal.headpass1( self, igen )

    def generate( self, igen, *args, **kwargs ):
        level, style = self.HEADING.level, stylemarkup( self.HEADING.style )
        igen.puttext( self.tmpl_o % (level, style) )
        if self.text_contents :
            self.text_contents.generate( igen, *args, **kwargs )
            igen.puttext( self.tmpl_a % self.headtext )
            igen.puttext( self.tmpl_ah % self.headtext )
        self.NEWLINE.generate( igen, *args, **kwargs )
        igen.puttext( self.tmpl_c % level )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'heading: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]

    level = property( lambda self : self.HEADING.level )


#---- Horizontal rule

class HorizontalRule( NonTerminal ) :
    """class to handle `horizontalrule` grammar."""
    tmpl = '<hr class="ethorz"/>\n'
    def __init__( self, parser, term ) :
        NonTerminal.__init__( self, parser )
        self._terms = (self.TERMINAL,) = (term,)
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._terms

    def generate( self, igen, *args, **kwargs ):
        igen.puttext( self.tmpl )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'horizontalrule:' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


#---- Textlines

class TextLines( NonTerminal ) :
    """class to handle `textlines` grammar."""
    tmpl_o = '<p class="ettext">\n'
    tmpl_c = '</p>\n'

    def __init__( self, parser, textlines, textline ):
        NonTerminal.__init__( self, parser, textlines, textline )
        self._nonterms = self.textlines, self.textline = textlines, textline
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return filter( None, (self.textlines, self.textline) )

    def headpass1( self, igen ):
        self.ctx.markupstack = []
        [ x.headpass1( igen ) for x in self.flatten() ]

    def headpass2( self, igen ):
        [ x.headpass2( igen ) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        igen.puttext( self.tmpl_o )
        [ x.generate( igen, *args, **kwargs ) for x in self.flatten() ]
        igen.puttext( self.tmpl_c )

    def tailpass( self, igen ):
        [ x.tailpass( igen ) for x in self.flatten() ]

    def dump( self, c ):
        return ''.join([ x.dump(c) for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'textlines: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        return NonTerminal.flatten( self, 'textlines', 'textline' )


class TextLine( NonTerminal ) :
    """class to handle `textline` grammar."""
    def __init__( self, parser, text_contents, newline ):
        NonTerminal.__init__( self, parser, text_contents, newline )
        self._nonterms = (self.text_contents,) = (text_contents,)
        self._terms = (self.NEWLINE,) = (newline,)
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return (self.text_contents, self.NEWLINE)

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'textline: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


#---- Big Table

class BTable( NonTerminal ) :
    """class to handle `btable` grammar."""
    def __init__( self, parser, btableblocks ):
        NonTerminal.__init__( self, parser, btableblocks )
        self._nonterms = (self.btableblocks,) = (btableblocks,)
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'btable: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        # Show children
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


class BigtableBlocks( NonTerminal ) :
    """class to handle `btableblocks` grammar."""
    tmpl = {
      ETLexer.btopen  : ('<table class="etbtbl" style="%s">\n', None),
      ETLexer.btclose : ('</table>\n', None),
      ETLexer.btrow   : ('<tr class="etbtbl" style="%s">\n', '</tr>\n'),
      ETLexer.bthead  : ('<th class="etbtbl" style="%s">', '</th>\n'),
      ETLexer.btcell  : ('<td class="etbtbl" style="%s">', '</td>\n'),
    }
    def __init__( self, parser, btableblocks, btableblock ):
        NonTerminal.__init__( self, parser, btableblocks, btableblock )
        self._nonterms = self.btableblocks, self.btableblock = \
                btableblocks, btableblock
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def headpass1( self, igen ):
        [ x.headpass1( igen ) for x in self.flatten() ]

    def headpass2( self, igen ):
        [ x.headpass2( igen ) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        for bt in self.flatten() :
            style = stylemarkup( bt.style )
            tmpl_o, tmpl_c = self.tmpl.get( bt.btmark[2], (None, None) )
            opentag = tmpl_o if bt.btmark[2] == ETLexer.btclose else tmpl_o%style
            tmpl_o and igen.puttext( opentag )
            bt.generate( igen, *args, **kwargs )
            tmpl_c and igen.puttext( tmpl_c )

    def tailpass( self, igen ):
        [ x.tailpass( igen ) for x in self.flatten() ]

    def dump( self, c ):
        return ''.join([ x.dump(c) for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'btableblocks: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        # Show children
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        return NonTerminal.flatten( self, 'btableblocks', 'btableblock' )



class BigtableBlock( NonTerminal ) :
    """class to handle `bigtableblock` grammar."""
    def __init__( self, parser, btblock, btstart, text_contents, newline ):
        NonTerminal.__init__(
                self, parser, btblock, btstart, text_contents, newline )
        self._terms = self.BTABLE_START, self.NEWLINE = btstart, newline
        self._nonterms = self.bigtableblock, self.text_contents = \
                btblock, text_contents
        self._terms = filter( None, self._terms )
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return filter(None, (self.BTABLE_START, self.text_contents, self.NEWLINE))

    def headpass1( self, igen ):
        self.ctx.markupstack = []
        [ x.headpass1( igen ) for x in self.flatten() ]

    def headpass2( self, igen ):
        [ x.headpass2( igen ) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        [ x.generate( igen, *args, **kwargs ) for x in self.flatten() ]

    def tailpass( self, igen ):
        [ x.tailpass( igen ) for x in self.flatten() ]

    def dump( self, c ):
        return ''.join([ x.dump(c) for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'bigtableblock: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        # Show children
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]

    def flatten( self ):
        return NonTerminal.flatten(
            self, 'bigtableblock', ('NEWLINE', 'text_contents')
        )

    btmark = property( lambda self : (self.BTABLE_START or self.bigtableblock).btmark )
    style = property( lambda self : (self.BTABLE_START or self.bigtableblock).style )


#---- Table

class Table( NonTerminal ) :
    """class to handle `table_rows` grammar."""
    tmpl_o = '<table class="ettbl">\n'
    tmpl_c = '</table>\n'
    def __init__( self, parser, table_rows ):
        NonTerminal.__init__( self, parser, table_rows )
        self._nonterms = (self.table_rows,) = (table_rows,)
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def generate( self, igen, *args, **kwargs ):
        igen.puttext( self.tmpl_o )
        NonTerminal.generate( self, igen, *args, **kwargs )
        igen.puttext( self.tmpl_c )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'table: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        # Show children
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


class TableRows( NonTerminal ) :
    """class to handle `table_rows` grammar."""
    def __init__( self, parser, table_rows, table_row ):
        NonTerminal.__init__( self, parser, table_rows, table_row )
        self._nonterms = self.table_rows, self.table_row = table_rows, table_row
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def headpass1( self, igen ):
        [ x.headpass1( igen ) for x in self.flatten() ]
        maxcolumns = max([ x.columns for x in self.flatten() ])
        [ setattr(x, 'maxcolumns', maxcolumns) for x in self.flatten() ]

    def headpass2( self, igen ):
        [ x.headpass2( igen ) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        [ x.generate( igen, *args, **kwargs ) for x in self.flatten() ]

    def tailpass( self, igen ):
        [ x.tailpass( igen ) for x in self.flatten() ]

    def dump( self, c ):
        return ''.join([ x.dump(c) for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'table_rows: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        # Show children
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        return NonTerminal.flatten( self, 'table_rows', 'table_row' )


class TableRow( NonTerminal ) :
    """class to handle `table_row` grammar."""
    tmpl_o = '<tr class="ettbl">\n'
    tmpl_c = '</tr>\n'
    tmpl_emptyrow = '<td colspan="%s"></td>\n'
    def __init__( self, parser, table_cells, newline ):
        NonTerminal.__init__( self, parser, table_cells, newline )
        self._nonterms = (self.table_cells,) = (table_cells,)
        self._terms = (self.NEWLINE,) = (newline,)
        self.columns, self.emptyrow = None, None
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return (self.table_cells, self.NEWLINE)

    def headpass1( self, igen ):
        self.columns = len( self.table_cells.flatten() )
        NonTerminal.headpass1( self, igen )

    def headpass2( self, igen ):
        cell, colspan = None, 0
        for t in self.table_cells.flatten() :
            if t.colspan == 0 :
                colspan += 1
            elif colspan :
                t.colspan, cell, colspan = (t.colspan+colspan), t, 0
            elif t.colspan :
                cell = t
        n = self.maxcolumns - self.columns
        if cell and (colspan or n) :
            cell.colspan += colspan + n
        elif colspan or n :
            self.emptyrow = colspan + n
        NonTerminal.headpass2( self, igen )

    def generate( self, igen, *args, **kwargs ):
        igen.puttext( self.tmpl_o )
        NonTerminal.generate( self, igen, *args, **kwargs )
        if self.emptyrow :
            igen.puttext( self.tmpl_emptyrow % self.emptyrow )
        igen.puttext( self.tmpl_c )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'table_row: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        # Show children
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


class TableCells( NonTerminal ) :
    """class to handle `table_cells` grammar."""
    def __init__( self, parser, table_cells, table_cell ) :
        NonTerminal.__init__( self, parser, table_cells, table_cell )
        self._nonterms = self.table_cells, self.table_cell = table_cells, table_cell
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def headpass1( self, igen ):
        [ x.headpass1( igen ) for x in self.flatten() ]

    def headpass2( self, igen ):
        [ x.headpass2( igen ) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        [ x.generate( igen, *args, **kwargs ) for x in self.flatten() ]

    def tailpass( self, igen ):
        [ x.tailpass( igen ) for x in self.flatten() ]

    def dump( self, c ):
        return ''.join([ x.dump(c) for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'table_cells: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        return NonTerminal.flatten( self, 'table_cells', 'table_cell' )


class TableCell( NonTerminal ) :
    """class to handle `table_cell` grammar."""
    RIGHTALIGN = '$'
    tmpl_o = { 'h' : '<th class="ettbl" colspan="%s" style="%s">',
               'd' : '<td class="ettbl" colspan="%s" style="%s">' }
    tmpl_c = { 'h' : '</th>\n', 'd' : '</td>\n' }

    def __init__( self, parser, cellstart, text_contents ) :
        NonTerminal.__init__( self, parser, cellstart, text_contents )
        self._terms = (self.TABLE_CELLSTART,) = (cellstart,)
        self._nonterms = (self.text_contents,) = (text_contents,)
        self._nonterms = filter( None, self._nonterms )
        self.colspan   = 1 if self.text_contents else 0
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return filter( None, (self.TABLE_CELLSTART, self.text_contents) )

    def headpass1( self, igen ):
        self.ctx.markupstack = []
        NonTerminal.headpass1( self, igen )

    def generate( self, igen, *args, **kwargs ):
        if self.colspan > 0 :
            typ   = 'h' if self.TABLE_CELLSTART.ishead else 'd'
            cont  = self.text_contents.dump(None)
            style = stylemarkup( self.TABLE_CELLSTART.style )
            if cont[-1] == self.RIGHTALIGN :
                style += '; text-align : right'
                flatnodes = self.flatterminals()
                if flatnodes[-1].dump(None) == self.RIGHTALIGN :
                    flatnodes[-1].terminal = ''
                else :
                    raise Exception( 'Unexpected !!' )
            igen.puttext( self.tmpl_o[typ] % (self.colspan, style) )
            self.text_contents.generate( igen, *args, **kwargs )
            igen.puttext( self.tmpl_c[typ] )
        elif self.text_contents :
            raise Exception( 'Table cell is not empty !' )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'table_cell: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


#---- Lists

class MixedLists( NonTerminal ) :
    """class to handle `mixedlists` grammar."""
    def __init__( self, parser, mixedlists, ulists, olists ) :
        NonTerminal.__init__( self, parser, mixedlists, ulists, olists )
        self._nonterms = self.mixedlists, self.ulists, self.olists = \
                mixedlists, ulists, olists
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def headpass1( self, igen ):
        [ x.headpass1( igen ) for x in self.flatten() ]

    def headpass2( self, igen ):
        [ x.headpass2( igen ) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        self.ctx.lmarks = [ (0, None, None) ]
        [ x.generate( igen, *args, **kwargs ) for x in self.flatten() ]
        # Flush out all the closing tags for ordered and unordered list.
        for level, type_, closetag in self.ctx.lmarks :
            if type_ == None : continue
            igen.puttext( closetag )

    def tailpass( self, igen ):
        [ x.tailpass( igen ) for x in self.flatten() ]

    def dump( self, c ):
        return ''.join([ x.dump(c) for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'mixedlists: ' )
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        return NonTerminal.flatten( self, 'mixedlists', ('ulists', 'olists') )


class Lists( NonTerminal ) :
    """class to handle `unorderedlists` or `unorderedlists` grammar."""
    tmpl_o = { 'ul' : '<ul class="et">', 'ol' : '<ol class="et">' }
    tmpl_c = { 'ul' : '</ul>', 'ol' : '</ol>' }
    def __init__( self, parser, type_, lists, list_ ) :
        NonTerminal.__init__( self, parser, lists, list_ )
        self.type = type_
        self._nonterms = self.lists, self.list = lists, list_
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def headpass1( self, igen ):
        [ x.headpass1( igen ) for x in self.flatten() ]

    def headpass2( self, igen ):
        [ x.headpass2( igen ) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        for l in self.flatten() :
            level, type_, closetag = self.ctx.lmarks[-1]
            if l.level > level :
                for x in range(l.level-level) :
                    igen.puttext( self.tmpl_o[l.type] )
                    self.ctx.lmarks.append( (level+x+1, l.type, self.tmpl_c[l.type]) )
            elif l.level < level :
                for x in range(level-l.level) :
                    level, type_, closetag = self.ctx.lmarks.pop(-1)
                    igen.puttext( closetag )
            l.generate( igen, *args, **kwargs )

    def tailpass( self, igen ):
        [ x.tailpass( igen ) for x in self.flatten() ]

    def dump( self, c ):
        return ''.join([ x.dump(c) for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'lists: ' )
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        return NonTerminal.flatten( self, 'lists', 'list' )


class List( NonTerminal ) :
    """class to handle `orderedlist` or `unorderedlist` grammar."""
    tmpl_o = '<li class="et" style="%s">'
    tmpl_c = '</li>'
    def __init__( self, parser, type_, lbegin, list_, text_contents, newline ):
        NonTerminal.__init__( self, parser, lbegin, list_, text_contents, newline )
        self._nonterms = \
            self.listbegin, self.list, self.text_contents, self.NEWLINE = \
                lbegin, list_, text_contents, newline
        self.type, self.NEWLINE = type_, newline
        self._terms = (self.NEWLINE,)
        self._nonterms = filter( None, self._nonterms )
        self._terms = filter( None, self._terms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        x = (self.listbegin, self.list, self.text_contents, self.NEWLINE)
        return filter( None, x )

    def headpass1( self, igen ):
        self.ctx.markupstack = []
        NonTerminal.headpass1( self, igen )

    def generate( self, igen, *args, **kwargs ):
        NonTerminal.generate( self, igen, *args, **kwargs )
        igen.puttext( self.tmpl_c ) if isinstance(self.parent, Lists) else None

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'list: ' )
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]

    level = property( lambda self : (self.listbegin or self.list).level )


class ListBegin( NonTerminal ) :
    """class to handle `unorderedlistbegin` or `unorderedlistbegin` grammar."""
    def __init__( self, parser, type_, lstart, text_contents, newline ) :
        NonTerminal.__init__( self, parser, type_, lstart, text_contents, newline )
        self.type, self.NEWLINE = type_, newline
        self.UNORDLIST_START, self.ORDLIST_START = \
            (lstart, None) if self.type == 'ul' else (None, lstart)
        self._terms = self.UNORDLIST_START, self.ORDLIST_START, self.NEWLINE
        self._nonterms = (self.text_contents,) = (text_contents,)
        self._terms = filter( None, self._terms )
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        x = ( self.UNORDLIST_START, self.ORDLIST_START, self.text_contents, self.NEWLINE )
        return filter( None, x )

    def generate( self, igen, *args, **kwargs ):
        LIST = self.UNORDLIST_START or self.ORDLIST_START
        igen.puttext( self.parent.tmpl_o % stylemarkup( LIST.style ))
        self.text_contents and self.text_contents.generate( igen, *args, **kwargs )
        self.NEWLINE.generate( igen, *args, **kwargs )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'listbegin: ' )
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]

    level = property(
        lambda self : (self.UNORDLIST_START or self.ORDLIST_START).level
    )


#---- Definitions

class Definitions( NonTerminal ) :
    """class to handle `definitionlists` grammar."""
    tmpl_o = '<dl class="et">\n'
    tmpl_c = '</dl>\n'
    def __init__( self, parser, defns=None, defn=None ) :
        NonTerminal.__init__( self, parser, defns, defn )
        self._nonterms = self.definitions, self.definition = defns, defn
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def headpass1( self, igen ):
        [ x.headpass1( igen ) for x in self.flatten() ]

    def headpass2( self, igen ):
        [ x.headpass2( igen ) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        igen.puttext( self.tmpl_o )
        [ x.generate( igen, *args, **kwargs ) for x in self.flatten() ]
        igen.puttext( self.tmpl_c )

    def tailpass( self, igen ):
        [ x.tailpass( igen ) for x in self.flatten() ]

    def dump( self, c ):
        return ''.join([ x.dump(c) for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'definitions: ' )
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        return NonTerminal.flatten( self, 'definitions', 'definition' )


class Definition( NonTerminal ) :
    """class to handle `definitionlist` grammar."""
    tmpl_dt = '<dt class="et"><b>%s</b></dt>\n'
    tmpl_dd_o = '<dd class="et">\n'
    tmpl_dd_c = '</dd>\n'
    def __init__( self, parser, defbegin, definition, text_contents, newline ):
        NonTerminal.__init__(
                self, parser, defbegin, definition, text_contents, newline )
        self._terms = (self.NEWLINE,) = (newline,)
        self._nonterms = (self.defbegin, self.definition, self.text_contents) =\
                defbegin, definition, text_contents
        self._terms = filter( None, self._terms )
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ):
        x = ( self.defbegin, self.definition, self.text_contents, self.NEWLINE )
        return filter( None, x )

    def headpass1( self, igen ):
        self.ctx.markupstack = []
        NonTerminal.headpass1( self, igen )

    def generate( self, igen, *args, **kwargs ):
        NonTerminal.generate( self, igen, *args, **kwargs )
        igen.puttext( self.tmpl_dd_c ) if isinstance(self.parent, Definitions) else None

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'definition: ' )
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


class DefinitionBegin( NonTerminal ) :
    """class to handle `definitionbegin` grammar."""
    def __init__( self, parser, defstart, text_contents, newline ) :
        NonTerminal.__init__( self, parser, defstart, text_contents, newline )
        self._terms = self.DEFINITION_START, self.NEWLINE = defstart, newline
        self._nonterms = (self.text_contents,) = (text_contents,)
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        x = (self.DEFINITION_START, self.text_contents, self.NEWLINE )
        return filter( None, x )

    def generate( self, igen, *args, **kwargs ):
        defterm = escape_htmlchars( self.DEFINITION_START.defterm )
        igen.puttext( self.parent.tmpl_dt % defterm )
        igen.puttext( self.parent.tmpl_dd_o )
        if self.text_contents :
            self.text_contents.generate( igen, *args, **kwargs )
        self.NEWLINE.generate( igen, *args, **kwargs )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'definitionbegin: ' )
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


#---- Blockquotes

class BlockQuotes( NonTerminal ) :
    """class to handle `blockquotes` grammar."""
    tmpl_o = '<blockquote class="et %s">\n'
    tmpl_c = '</blockquote>\n'
    def __init__( self, parser, bquotes=None, bquote=None ) :
        NonTerminal.__init__( self, parser, bquotes, bquote )
        self._nonterms = self.blockquotes, self.blockquote = bquotes, bquote
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ):
        return self._nonterms

    def headpass1( self, igen ):
        level = 0
        for bquote in self.flatten() :
            if bquote.level != level :
                self.ctx.markupstack, level = [], bquote.level
            bquote.headpass1( igen )

    def headpass2( self, igen ):
        [ x.headpass2(igen) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        self.ctx.bqmarks = ['']
        [ bquote.generate( igen, *args, **kwargs ) for bquote in self.flatten() ]
        [ igen.puttext( self.tmpl_c ) for x in self.ctx.bqmarks[-1] ]

    def tailpass( self, igen ):
        [ x.tailpass(igen) for x in self.flatten() ]

    def dump( self, c ):
        return ''.join([ x.dump(c) for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'bquotes: ' )
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        return NonTerminal.flatten( self, 'blockquotes', 'blockquote' )


class BlockQuote( NonTerminal ) :
    """class to handle `blockquote` grammar."""
    def __init__( self, parser, bqstart, text_contents, newline ) :
        NonTerminal.__init__( self, parser, bqstart, text_contents, newline )
        self._terms = self.BQUOTE_START, self.NEWLINE = bqstart, newline
        self._nonterms = (self.text_contents,) = (text_contents,)
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ):
        x = (self.BQUOTE_START, self.text_contents, self.NEWLINE)
        return filter( None, x )

    def generate( self, igen, *args, **kwargs ):
        bqmark = self.BQUOTE_START.bqmark
        if bqmark > self.ctx.bqmarks[-1] :
            cls = 'firstlevel' if self.ctx.bqmarks[-1] == '' else 'innerlevel'
            for x in bqmark.replace( self.ctx.bqmarks[-1], '', 1 ) :
                igen.puttext( self.parent.tmpl_o % cls )
                cls = 'innerlevel'
            self.ctx.bqmarks.append( bqmark )
        elif bqmark < self.ctx.bqmarks[-1] :
            for x in self.ctx.bqmarks[-1].replace( bqmark, '', 1 ) :
                igen.puttext( self.parent.tmpl_c )
            self.ctx.bqmarks.pop( -1 )
            self.ctx.bqmarks.append( bqmark )
        if self.text_contents :
            self.text_contents.generate( igen, *args, **kwargs )
        self.NEWLINE.generate( igen, *args, **kwargs )
        igen.puttext( '<br/>' )

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'bquote: ' )
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]

    level  = property( lambda self : self.BQUOTE_START.level )


#---- Textcontents

class TextContents( NonTerminal ) :
    """class to handle `text_contents` grammar."""
    def __init__( self, parser, text_contents, text_content=None ) :
        NonTerminal.__init__( self, parser, text_contents, text_content )
        self._nonterms = (self.text_contents, self.text_content) = \
                text_contents, text_content
        self._nonterms = filter( None, self._nonterms )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._nonterms

    def headpass1( self, igen ):
        [ x.headpass1(igen) for x in self.flatten() ]

    def headpass2( self, igen ):
        [ x.headpass2(igen) for x in self.flatten() ]

    def generate( self, igen, *args, **kwargs ):
        [ x.generate( igen, *args, **kwargs ) for x in self.flatten() ]

    def tailpass( self, igen ):
        [ x.tailpass(igen) for x in self.flatten() ]

    def dump( self, c ):
        return ''.join([ x.dump(c) for x in self.flatten() ])

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        [ x.show(buf, offset, attrnames, showcoord) for x in self.flatten() ]

    def flatten( self ):
        return NonTerminal.flatten( self, 'text_contents', 'text_content' )


class Link( NonTerminal ) :
    """class to handle `link` grammer.
    There are special links, 
        * - Open in new window,
        # - Create an anchor
        + - Image
    """
    prefixes     = '*#+><'
    l_template   = '<a class="etlink" target="%s" href="%s">%s</a>'
    a_template   = '<a id="%s" class="etlink anchor" name="%s">%s</a>'
    img_template = '<img class="et" src="%s" alt="%s" style="%s"/>'

    def __init__( self, parser, link ) :
        NonTerminal.__init__( self, parser, link )
        self._terms = (self.LINK,) = (link,)
        self.obfuscatemail = self.parser.etparser.etxconfig['obfuscatemail']
        self.html = self._parse( self.LINK.dump(None)[2:-2].lstrip() )
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def _parse( self, _link ):
        prefix1, prefix2 = _link[:1], _link[1:2]
        _link = _link.lstrip( self.prefixes )
        try :
            href, text  = _link.split('|', 1)
        except :
            href, text = _link, _link
        href = escape_htmlchars( href.strip(' \t') )
        text = escape_htmlchars( text.strip(' \t') )

        if prefix1 == '*' :                         # Link - Open in new window
            html = self.l_template % ( '_blank', href, text )
        elif prefix1 == '#' :                       # Link - Anchor 
            html = self.a_template % ( href, href, text )
        elif prefix1 == '+' and prefix2 == '>' :    # Link - Image (right)
            html = self.img_template % ( href, text, 'float: right;' )
        elif prefix1 == '+' and prefix2 == '<' :    # Link - Image (left)
            html = self.img_template % ( href, text, 'float: left;' )
        elif prefix1 == '+' :                       # Link - Image
            html = self.img_template % ( href, text, '' )
        elif href[:6] == "mailto:" and self.obfuscatemail : # Link - E-mail
            if href == text :
                href = text = "mailto:" + obfuscatemail(href[7:])
            else :
                href = "mailto:" + obfuscatemail(href[7:])
            html = self.l_template % ( '', href, text )
        else :
            html = self.l_template % ( '', href, text )

        return html

    def children( self ) :
        return self._terms

    def generate( self, igen, *args, **kwargs ):
        igen.puttext( self.html )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'link: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


class Macro( NonTerminal ) :
    """class to handle `macro` grammer."""
    def __init__( self, parser, macro ) :
        NonTerminal.__init__( self, parser, macro )
        self._terms = (self.MACRO,) = (macro,)
        self.macrotext = self.MACRO.dump(None)
        # Fetch the plugin
        try :
            _macro = self.macrotext[2:-2].lstrip()
            try    : macroname, argstr = _macro.split('(', 1)
            except : macroname, argstr = _macro, ''
            macroname = macroname.strip()
            argstr = argstr.rstrip(' \r)')
            macroplugins = parser.etparser.etxconfig.get( 'macroplugins', {} )
            factory = macroplugins.get( macroname, None )
            self.macroplugin = factory and factory( argstr.strip() )
            self.macroplugin and self.macroplugin.onparse( self )
        except :
            if parser.etparser.debug : raise
            self.macroplugin = None
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ):
        return self._terms

    def headpass1( self, igen ):
        self.macroplugin and self.macroplugin.headpass1( self, igen )

    def headpass2( self, igen ):
        self.macroplugin and self.macroplugin.headpass2( self, igen )

    def generate( self, igen, *args, **kwargs ):
        if self.macroplugin :
            self.macroplugin.generate( self, igen, *args, **kwargs )
        else :
            igen.puttext( escape_htmlchars( self.macrotext ))

    def tailpass( self, igen ):
        self.macroplugin and self.macroplugin.tailpass( self, igen )
    
    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'macro: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


class Html( NonTerminal ) :
    """class to handle `html` grammer."""
    def __init__( self, parser, html ) :
        NonTerminal.__init__( self, parser, html )
        self._terms = (self.HTML,) = (html,)
        self.htmltext = html.dump(None)
        # Fetch the plugin
        try :
            lines = self.htmltext[2:-2].lstrip().splitlines()
            parts, lines = lines[0].split(' ', 1), lines[1:]
            self.tagname = parts.pop(0).strip() if parts else ''
            self.text = '\n'.join( parts + lines )
            ttplugins = parser.etparser.etxconfig.get( 'ttplugins', {} )
            ttplugin = ttplugins.get( self.tagname.lower(), None )
            self.ttplugin = ttplugin() if callable(ttplugin) else ttplugin
            self.ttplugin and self.ttplugin.onparse(self)
        except :
            if parser.etparser.debug : raise
            self.ttplugin = None
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ):
        return self._terms

    def headpass1( self, igen ):
        self.ttplugin and self.ttplugin.headpass1( self, igen )

    def headpass2( self, igen ):
        self.ttplugin and self.ttplugin.headpass2( self, igen )

    def generate( self, igen, *args, **kwargs ):
        if self.ttplugin :
            self.ttplugin.generate( self, igen, *args, **kwargs )
        else :
            if self.parser.etparser.etxconfig['stripscript'] :
                text = re.sub( '<[ \t]*script[^>]*?>', '', self.htmltext[2:-2] )
            else :
                text = self.htmltext[2:-2]
            igen.puttext( text )

    def tailpass( self, igen ):
        self.ttplugin and self.ttplugin.tailpass( self, igen )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write( lead + 'html: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


class BasicText( NonTerminal ) :
    """class to handle `basictext` grammar."""
    def __init__( self, parser, term ) :
        NonTerminal.__init__( self, parser, term )
        self._terms = (self.TERMINAL,) = (term,)
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._terms

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write(lead + 'basictext: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


class MarkupText( NonTerminal ) :
    """class to handle `markuptext` grammar."""
    def __init__( self, parser, term ) :
        NonTerminal.__init__( self, parser, term )
        self._terms = (self.TERMINAL,) = (term,)
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return self._terms

    def headpass1( self, igen ):
        TERM = self.TERMINAL
        OPEN = self.ctx.markupstack and self.ctx.markupstack[-1].TERMINAL
        if OPEN and (OPEN.markup == TERM.markup) :
            OPEN.html, TERM.html = \
                    OPEN.tmpl_o % stylemarkup(OPEN.style), TERM.tmpl_c
            self.ctx.markupstack.pop(-1)
        else :
            self.ctx.markupstack.append( self )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        lead = ' ' * offset
        buf.write(lead + 'markuptext: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        [ x.show(buf, offset+2, attrnames, showcoord) for x in self.children() ]


class ParagraphSeparator( NonTerminal ) :
    """class to handle `paragraph_separator` grammar."""

    def __init__( self, parser, ps, newline ) :
        NonTerminal.__init__( self, parser, ps, newline )
        self.NEWLINE = self.paragraph_separator = None
        self._terms = (self.NEWLINE,) = (newline,)
        self._nonterms = (self.paragraph_separator,) = (ps,)
        # Set parent attribute for children, should be last statement !!
        self.setparent( self, self.children() )

    def children( self ) :
        return filter( None, (self._nonterms+self._terms) )

    def show(self, buf=sys.stdout, offset=0, attrnames=False, showcoord=False):
        pass



#-------------------------- AST Terminals -------------------------

class BASICTEXT( object ):
    def generate( self, igen, *args, **kwargs ):
        igen.puttext( self.html )

class MARKUPTEXT( object ):
    html, spatt = '', re.compile( ETLexer.style )
    def generate( self, igen, *args, **kwargs ):
        igen.puttext( self.html or self.terminal )
    def _style( self ):
        rc = self.spatt.findall( self.terminal )
        return rc[0][1:-1] if rc else ''
    style  = property( lambda self : self._style() )

#---- Text
class NEWLINE( Terminal ): pass
class LINEBREAK( Terminal ):
    tmpl   = '<br/>'
    html   = property( lambda self : self.tmpl )
class ESCAPED_TEXT( Terminal ):
    html   = property( lambda self : escape_htmlchars( self.terminal ))
class TEXT( BASICTEXT, Terminal ):
    html   = property( lambda self : escape_htmlchars( self.terminal ))
class SPECIALCHARS( BASICTEXT, Terminal ):
    html   = property( lambda self : escape_htmlchars( self.terminal ))
class HTTP_URI( BASICTEXT, Terminal ):
    tmpl   = '<a class="ethttpuri" href="%s">%s</a>'
    html   = property( lambda self : self.tmpl % (self.terminal, self.terminal) )
class HTTPS_URI( BASICTEXT, Terminal ):
    tmpl   = '<a class="ethttpsuri" href="%s">%s</a>'
    html   = property( lambda self : self.tmpl % (self.terminal, self.terminal) )
class WWW_URI( BASICTEXT, Terminal ):
    tmpl   = '<a class="etwwwuri" href="%s">%s</a>'
    html   = property( lambda self : self.tmpl % (self.terminal, self.terminal) )

#---- Text markup
class M_SPAN( MARKUPTEXT, Terminal ):
    markup = 'span'
    tmpl_o = '<span class="etmark" style="%s">'
    tmpl_c = '</span>'

class M_BOLD( MARKUPTEXT, Terminal ):
    markup = 'bold'
    tmpl_o = '<strong class="etmark" style="%s">'
    tmpl_c = '</strong>'

class M_ITALIC( MARKUPTEXT, Terminal ):
    markup = 'italic'
    tmpl_o = '<em class="etmark" style="%s">'
    tmpl_c = '</em>'

class M_UNDERLINE( MARKUPTEXT, Terminal ):
    markup = 'underline'
    tmpl_o = '<u class="etmark" style="%s">'
    tmpl_c = '</u>'

class M_SUPERSCRIPT( MARKUPTEXT, Terminal ):
    markup = 'superscript'
    tmpl_o = '<sup class="etmark" style="%s">'
    tmpl_c = '</sup>'

class M_SUBSCRIPT( MARKUPTEXT, Terminal ):
    markup = 'subscript'
    tmpl_o = '<sub class="etmark" style="%s">'
    tmpl_c = '</sub>'

class M_BOLDITALIC( MARKUPTEXT, Terminal ):
    markup = 'bolditalic'
    tmpl_o = '<strong class="etmark"><em style="%s">'
    tmpl_c = '</em></strong>'

class M_BOLDUNDERLINE( MARKUPTEXT, Terminal ):
    markup = 'boldunderline'
    tmpl_o = '<strong class="etmark"><u style="%s">'
    tmpl_c = '</u></strong>'

class M_ITALICUNDERLINE( MARKUPTEXT, Terminal ):
    markup = 'italicunderline'
    tmpl_o = '<em class="etmark"><u style="%s">'
    tmpl_c = '</u></em>'

class M_BOLDITALICUNDERLINE( MARKUPTEXT, Terminal ):
    markup = 'bolditalicunderline'
    tmpl_o = '<strong class="etmark"><em><u style="%s">'
    tmpl_c = '</u></em></strong>'

#---- Inline text blocks
class LINK( Terminal ): pass
class NESTEDLINK( Terminal ): pass
class MACRO( Terminal ): pass
class HTML( Terminal ): pass

#---- Text Blocks
class HORIZONTALRULE( Terminal ): pass
class HEADING( Terminal ):
    hpatt1 = re.compile( r'={1,6}' ) 
    hpatt2 = re.compile( r'[hH][123456]' )
    spatt  = re.compile( ETLexer.style )
    def _level( self ):
        x = self.hpatt1.findall( self.terminal.strip() )
        y = x or self.hpatt2.findall( self.terminal.strip() )
        try    : level = len(x[0]) if x else int(y[0][1])
        except : level = 6
        return level
    def _style( self ):
        rc = self.spatt.findall( self.terminal.strip() )
        return rc[0][1:-1] if rc else ''
    level  = property( lambda self : self._level() )
    style  = property( lambda self : self._style() )

class ORDLIST_START( Terminal ):
    spatt = re.compile( ETLexer.style )
    def _style( self ):
        rc = self.spatt.findall( self.terminal.strip() )
        return rc[0][1:-1] if rc else ''
    lmark = property( lambda self : self.spatt.sub( '', self.terminal.strip() ).strip() )
    level = property( lambda self : len(self.lmark) )
    style = property( lambda self : self._style() )

class UNORDLIST_START( Terminal ):
    spatt = re.compile( ETLexer.style )
    def _style( self ):
        rc = self.spatt.findall( self.terminal.strip() )
        return rc[0][1:-1] if rc else ''
    lmark = property( lambda self : self.spatt.sub('', self.terminal.strip()).strip() )
    level = property( lambda self : len(self.lmark) )
    style = property( lambda self : self._style() )

class DEFINITION_START( Terminal ):
    defterm = property( lambda self : self.terminal.strip()[1:-2] )

class BQUOTE_START( Terminal ) :
    bqmark = property( lambda self : self.terminal.strip() )
    level  = property( lambda self : len(self.bqmark) )

class BTABLE_START( Terminal ):
    spatt = re.compile( ETLexer.style )
    def _style( self ):
        rc = self.spatt.findall( self.terminal.strip() )
        return rc[0][1:-1] if rc else ''
    btmark = property( lambda self : self.terminal.lstrip()[:3] )
    style  = property( lambda self : self._style() )

class TABLE_CELLSTART( Terminal ):
    spatt = re.compile( ETLexer.style )
    def _style( self ):
        rc = self.spatt.findall( self.terminal.strip() )
        return rc[0][1:-1] if rc else ''
    ishead = property( lambda self : '=' in self.terminal.strip()[:2] )
    style  = property( lambda self : self._style() )

class NOWIKI_OPEN( Terminal ): pass
class NOWIKITEXT( Terminal ): pass
class NOWIKI_CLOSE( Terminal ): pass
#---- Endmarker
class ENDMARKER( Terminal ): pass
