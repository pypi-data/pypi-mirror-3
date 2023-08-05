# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

"""Parser grammer for EazyText text"""

# Gotcha : None
# Notes  :
#   1. Endmarker is appender to the wiki text to facilitate the wiki parsing.
# Todo   : None

import logging, re, sys, copy
from   os.path  import splitext, dirname
from   hashlib  import sha1
from   copy     import deepcopy

import ply.yacc

import eazytext.macro
import eazytext.extension
import eazytext.ttags
from   eazytext.lexer        import ETLexer
from   eazytext.ast          import *

log = logging.getLogger( __name__ )
rootdir = dirname( __file__ )
LEXTAB = 'lexetxtab'
YACCTAB = 'parseetxtab'

class ParseError( Exception ):
    pass

# Default Wiki page properties
class ETParser( object ):
    ENDMARKER = '<{<{}>}>'
    def __init__(   self,
                    etxconfig={},
                    outputdir=None,
                    # PLY-lexer options
                    lex_optimize=False,
                    lextab=LEXTAB,
                    lex_debug=False,
                    # PLY-parser options
                    yacc_optimize=False,
                    yacctab=YACCTAB,
                    yacc_debug=False,
                    debug=None
                ):
        self.debug = lex_debug or yacc_debug or debug
        self._etxconfig = etxconfig

        # Build Lexer
        self.etlex = ETLexer( error_func=self._lex_error_func )
        kwargs = {'optimize' : lex_optimize} if lex_optimize != None else {}
        kwargs.update( debug=lex_debug ) if lex_debug else None
        kwargs.update( lextab=lextab )
        self.etlex.build( **kwargs )
        self.tokens = self.etlex.tokens

        # Build Parser
        kwargs = {'optimize' : yacc_optimize} if yacc_optimize != None else {}
        kwargs.update( debug=yacc_debug    ) if yacc_debug else None
        kwargs.update( outputdir=outputdir ) if outputdir else None
        kwargs.update( tabmodule=yacctab )
        self.parser = ply.yacc.yacc( module=self, **kwargs )
        self.parser.etparser = self   # For AST nodes to access `this`

        self._initialize()

    def _initialize( self, etxfile=None, etxconfig={} ):
        self.etxfile = etxfile
        self.etxconfig = deepcopy( self._etxconfig )
        self.etxconfig.update( etxconfig )
        self.etlex.reset_lineno()
        self.ctx = Context()

    def _fetchskin( self, skinfile ):
        if skinfile == None :
            skincss = ''
        elif skinfile.endswith( '.css' ) :
            skincss = open( join(rootdir, 'skins', skinfile) ).read()
        else :
            skincss = skincss
        return skincss

    def _preprocess( self, text ) :
        """The text to be parsed is pre-parsed to remove and fix unwanted
        side effects in the parser.
        Return the preprossed text"""
        # Replace `a string ESCAPE characters`
        text = re.compile( r'\\+', re.MULTILINE | re.UNICODE ).sub(r'\\', text)
        text = text.rstrip( r'\\' )   # Remove trailing ESCAPE char
        # Replace `\ Escaped new lines`
        text = text.replace( '\\\n', '' )
        return text

    def parse( self, text, etxfile=None, etxconfig={}, debuglevel=0 ):
        """Parses eazytext-markup //text// and creates an AST tree. For every
        parsing invocation, the same lex, yacc, and objects will
        be used.

        : text ::
            A string containing the Wiki text
        : etxfile ::
            Name of the file being parsed (for meaningful error messages)
        : debuglevel ::
            Debug level to yacc
        """
        # Initialize
        self._initialize( etxfile=etxfile, etxconfig=etxconfig )
        self.text = text
        self.etlex.filename = etxfile
        self.hashtext = sha1( text ).hexdigest()

        self.skincss = self._fetchskin( self.etxconfig['skinfile'] 
                       ) if self.etxconfig['include_skin'] else ''

        # Pre-process the text, massage them for prasing.
        self.pptext = self._preprocess( text )

        # parse and get the Translation Unit
        debuglevel = self.debug or debuglevel
        self.pptext += '\n' + self.ENDMARKER
        self.tu = self.parser.parse(self.pptext, lexer=self.etlex, debug=debuglevel)
        return self.tu

    # ------------------------- Private functions -----------------------------

    def _lex_error_func( self, msg, line, column ):
        self._parse_error( msg, self._coord( line, column ))
    
    def _coord( self, lineno, column=None ):
        return Coord( file=self.etlex.filename, 
                      line=lineno,
                      column=column
               )
    
    def _parse_error(self, msg, coord):
        raise ParseError("%s: %s" % (coord, msg))

    def _printparse( self, p ) :
        print p[0], "  : ",
        for i in range(1,len(p)) :
            print p[i],
        print

    # ---------- Precedence and associativity of operators --------------------

    precedence = (
        ( 'left', 'PREC_LINK', 'PREC_MACRO', 'PREC_HTML' ),
    )
    
    def _buildterms( self, p, terms ):
        rc = []
        for t in terms :
            if t == None :
                rc.append( None )
                continue
            elif isinstance(t, tuple) :
                cls, idx = t
                rc.append( cls(p.parser, p[idx]) )
            else :
                rc.append(t)
        return rc


    #---- Page

    def p_wikipage( self, p ):
        """wikipage         : paragraphs
                            | paragraphs ENDMARKER"""
        p[0] = WikiPage( p.parser, p[1] )

    def p_paragraphs_1( self, p ):
        """paragraphs       : paragraph_separator"""
        p[0] = Paragraphs( p.parser, None, None, p[1] )

    def p_paragraphs_2( self, p ):
        """paragraphs       : paragraph"""
        p[0] = Paragraphs( p.parser, None, p[1], None )

    def p_paragraphs_3( self, p ):
        """paragraphs       : paragraph paragraph_separator"""
        p[0] = Paragraphs( p.parser, None, p[1], p[2] )

    def p_paragraphs_4( self, p ):
        """paragraphs       : paragraphs paragraph paragraph_separator"""
        p[0] = Paragraphs( p.parser, p[1], p[2], p[3] )

    def p_paragraphs_5( self, p ):
        """paragraphs       : paragraphs paragraph"""
        p[0] = Paragraphs( p.parser, p[1], p[2], None )

    def p_paragraph_1( self, p ):
        """paragraph        : textlines"""
        p[0] = Paragraph( p.parser, p[1] )

    def p_paragraph_2( self, p ):
        """paragraph        : specialpara"""
        p[0] = p[1]

    def p_specialpara( self, p ):
        """specialpara      : nowikiblock
                            | heading
                            | horizontalrule
                            | btable
                            | table
                            | mixedlists
                            | definitions
                            | blockquotes"""
        p[0] = Paragraph( p.parser, p[1] )

    #---- Nowiki

    def p_nowiki_1( self, p ):
        """nowikiblock  : NOWIKI_OPEN NEWLINE nowikilines NOWIKI_CLOSE NEWLINE"""
        terms = [ (NOWIKI_OPEN,1), (NEWLINE,2), p[3], (NOWIKI_CLOSE,4), (NEWLINE,5) ]
        p[0] = NoWiki( p.parser, *self._buildterms( p, terms ) )

    def p_nowiki_2( self, p ):
        """nowikiblock  : NOWIKI_OPEN NEWLINE nowikilines ENDMARKER"""
        terms = [ (NOWIKI_OPEN,1), (NEWLINE,2), p[3], None, None ]
        p[0] = NoWiki( p.parser, *self._buildterms( p, terms ) )

    def p_nowikilines_1( self, p ):
        """nowikilines  : NEWLINE"""
        p[0] = NowikiLines( p.parser, None, None, NEWLINE(p.parser, p[1]) )

    def p_nowikilines_2( self, p ):
        """nowikilines  : NOWIKITEXT NEWLINE"""
        terms = [ None, (NOWIKITEXT,1), (NEWLINE,2) ]
        p[0] = NowikiLines( p.parser, *self._buildterms(p, terms) )

    def p_nowikilines_3( self, p ):
        """nowikilines  : nowikilines NEWLINE"""
        p[0] = NowikiLines( p.parser, p[1], None, NEWLINE(p.parser, p[2]) )

    def p_nowikilines_4( self, p ):
        """nowikilines  : nowikilines NOWIKITEXT NEWLINE"""
        terms = [ p[1], (NOWIKITEXT,2), (NEWLINE,3) ]
        p[0] = NowikiLines( p.parser, *self._buildterms(p, terms) )

    def p_nowikilines_5( self, p ):
        """nowikilines  : """
        p[0] = NowikiLines( p.parser, None, None, None )

    #---- Heading, horizontal and textlines

    def p_heading( self, p ):
        """heading      : HEADING text_contents NEWLINE
                        | HEADING NEWLINE"""
        terms = [ (HEADING,1), p[2], (NEWLINE,3) 
                ] if len(p) == 4 else [ (HEADING,1), None, (NEWLINE,2) ]
        p[0] = Heading( p.parser, *self._buildterms( p, terms ))

    def p_horizontalrule( self, p ):
        """horizontalrule : HORIZONTALRULE"""
        p[0] = HorizontalRule( p.parser, HORIZONTALRULE(p.parser, p[1]) )

    def p_textlines( self, p ):
        """textlines    : textline
                        | textlines textline"""
        args = [ p[1], p[2] ] if len(p)==3 else [ None, p[1] ]
        p[0] = TextLines( p.parser, *args )

    def p_textline( self, p ):
        """textline     : text_contents NEWLINE"""
        p[0] = TextLine( p.parser, p[1], NEWLINE(p.parser, p[2]) )

    #---- Bigtable rows

    def p_btable( self, p ):
        """btable       : btableblocks"""
        p[0] = BTable( p.parser, p[1] )

    def p_btableblocks( self, p ):
        """btableblocks : btableblock
                        | btableblocks btableblock"""
        args = [ p[1], p[2] ] if len(p) == 3 else [ None, p[1] ]
        p[0] = BigtableBlocks( p.parser, *args )

    def p_btableblock_1( self, p ):
        """btableblock  : BTABLE_START text_contents NEWLINE
                        | BTABLE_START NEWLINE"""
        terms = [ None, (BTABLE_START,1), p[2], (NEWLINE,3)
                ] if len(p) == 4 else [ None, (BTABLE_START,1), None, (NEWLINE,2) ]
        p[0] = BigtableBlock( p.parser, *self._buildterms( p, terms ) )

    def p_btableblock_2( self, p ):
        """btableblock  : btableblock text_contents NEWLINE"""
        p[0] = BigtableBlock( p.parser, p[1], None, p[2], NEWLINE(p.parser, p[3] ))

    #---- table

    def p_table( self, p ):
        """table        : table_rows"""
        p[0] = Table( p.parser, p[1] )

    def p_table_rows( self, p):
        """table_rows   : table_row
                        | table_rows table_row"""
        args = [ p[1], p[2] ] if len(p)==3 else [ None, p[1] ]
        p[0] = TableRows( p.parser, *args )

    def p_table_row( self, p ):
        """table_row    : table_cells NEWLINE"""
        p[0] = TableRow( p.parser, p[1], NEWLINE(p.parser, p[2]) )

    def p_table_cells( self, p ):
        """table_cells  : table_cell
                        | table_cells table_cell"""
        args = [ p[1], p[2] ] if len(p) == 3 else [ None, p[1] ]
        p[0] = TableCells( p.parser, *args )

    def p_table_cell( self, p ):
        """table_cell   : TABLE_CELLSTART
                        | TABLE_CELLSTART text_contents"""
        args = [ TABLE_CELLSTART(p.parser, p[1]), p[2]
               ] if len(p) == 3 else [ TABLE_CELLSTART(p.parser, p[1]), None ]
        p[0] = TableCell( p.parser, *args )

    #---- Lists

    def p_mixedlists_1( self, p ):
        """mixedlists   : orderedlists
                        | mixedlists unorderedlists"""
        args = [ p[1], p[2], None ] if len(p)==3 else [ None, p[1], None ]
        p[0] = MixedLists( p.parser, *args )

    def p_mixedlists_2( self, p ):
        """mixedlists   : unorderedlists
                        | mixedlists orderedlists"""
        args = [ p[1], None, p[2] ] if len(p)==3 else [ None, None, p[1] ]
        p[0] = MixedLists( p.parser, *args )

    def p_orderedlists( self, p ):
        """orderedlists : orderedlist
                        | orderedlists orderedlist"""
        args = [ p[1], p[2] ] if len(p)==3 else [ None, p[1] ]
        p[0] = Lists( p.parser, 'ol', *args )

    def p_unorderedlists( self, p ):
        """unorderedlists   : unorderedlist
                            | unorderedlists unorderedlist"""
        args = [ p[1], p[2] ] if len(p)==3 else [ None, p[1] ]
        p[0] = Lists( p.parser, 'ul', *args )

    def p_orderedlist( self, p ):
        """orderedlist  : orderedlistbegin
                        | orderedlist text_contents NEWLINE"""
        args = [ None, p[1], p[2], NEWLINE(p.parser, p[3]) 
               ] if len(p) == 4 else [ p[1], None, None, None ]
        p[0] = List( p.parser, 'ol', *args )

    def p_unorderedlist( self, p ):
        """unorderedlist    : unorderedlistbegin
                            | unorderedlist text_contents NEWLINE"""
        args = [ None, p[1], p[2], NEWLINE(p.parser, p[3]) 
               ] if len(p) == 4 else [ p[1], None, None, None ]
        p[0] = List( p.parser, 'ul', *args )

    def p_orderedlistbegin( self, p ):
        """orderedlistbegin : ORDLIST_START text_contents NEWLINE
                            | ORDLIST_START NEWLINE"""
        terms = [ (ORDLIST_START,1), p[2], (NEWLINE,3) 
                ] if len(p) == 4 else [ (ORDLIST_START,1), None, (NEWLINE,2) ]
        p[0] = ListBegin( p.parser, 'ol', *self._buildterms(p, terms) )

    def p_unorderedlistbegin( self, p ):
        """unorderedlistbegin   : UNORDLIST_START text_contents NEWLINE
                                | UNORDLIST_START NEWLINE"""
        terms = [ (UNORDLIST_START,1), p[2], (NEWLINE,3) 
                ] if len(p) == 4 else [ (UNORDLIST_START,1), None, (NEWLINE,2) ]
        p[0] = ListBegin( p.parser, 'ul', *self._buildterms(p, terms) )

    #---- Definition

    def p_definitions( self, p ):
        """definitions  : definition
                        | definitions definition"""
        args = [ p[1], p[2] ]if len(p) == 3 else [ None, p[1] ]
        p[0] = Definitions( p.parser, *args )

    def p_definition( self, p ):
        """definition   : definitionbegin
                        | definition text_contents NEWLINE"""
        args = [ None, p[1], p[2], NEWLINE(p.parser, p[3]) 
               ] if len(p) == 4 else [ p[1], None, None, None ]
        p[0] = Definition( p.parser, *args )

    def p_definitionbegin( self, p ):
        """definitionbegin  : DEFINITION_START text_contents NEWLINE
                            | DEFINITION_START NEWLINE"""
        terms = [ (DEFINITION_START,1), p[2], (NEWLINE,3)
                ] if len(p) == 4 else [ (DEFINITION_START,1), None, (NEWLINE,2) ]
        p[0] = DefinitionBegin( p.parser, *self._buildterms(p, terms) )

    #---- Blockquotes

    def p_blockquotes( self, p ):                       # BQuotes
        """blockquotes  : blockquote
                        | blockquotes blockquote"""
        args = [ p[1], p[2] ] if len(p) == 3 else [ None, p[1] ]
        p[0] = BlockQuotes( p.parser, *args )

    def p_blockquote( self, p ):                        # BQuote
        """blockquote   : BQUOTE_START text_contents NEWLINE
                        | BQUOTE_START NEWLINE"""
        terms = [ (BQUOTE_START,1), p[2], (NEWLINE,3)
                ] if len(p) == 4 else [ (BQUOTE_START,1), None, (NEWLINE,2) ]
        p[0] = BlockQuote( p.parser, *self._buildterms( p, terms ) )

    #---- Text contents

    def p_text_contents( self, p ) :                    # TextContents
        """text_contents    : basictext
                            | markuptext
                            | link
                            | macro
                            | html
                            | text_contents basictext
                            | text_contents markuptext
                            | text_contents link
                            | text_contents macro
                            | text_contents html"""
        args = [ p[1], p[2] ] if len(p)==3 else [ None, p[1] ]
        p[0] = TextContents( p.parser, *args )

    def p_link( self, p ):
        """link         : LINK %prec PREC_LINK"""
        p[0] = Link( p.parser, LINK(p.parser, p[1]) )

    #def p_nestedlink( self, p ):
    #    """nestedlink   : NESTEDLINK %prec PREC_LINK"""
    #    p[0] = NestedLink( p.parser, NESTEDLINK(p.parser, p[1]) )
    #    pass

    def p_macro( self, p ):
        """macro        : MACRO %prec PREC_MACRO"""
        p[0] = Macro( p.parser, MACRO(p.parser, p[1]) )

    def p_html( self, p ):
        """html         : HTML %prec PREC_HTML"""
        p[0] = Html( p.parser, HTML(p.parser, p[1]) )


    #---- Basic Text

    def p_basictext_0( self, p ):
        """basictext    : TEXT"""
        p[0] = BasicText( p.parser, TEXT(p.parser, p[1]) )

    def p_basictext_1( self, p ):
        """basictext    : ESCAPED_TEXT"""
        p[0] = BasicText( p.parser, TEXT(p.parser, p[1]) )

    def p_basictext_2( self, p ):
        """basictext    : SPECIALCHARS"""
        p[0] = BasicText( p.parser, SPECIALCHARS(p.parser, p[1]) )

    def p_basictext_3( self, p ):
        """basictext    : HTTP_URI"""
        p[0] = BasicText( p.parser, HTTP_URI(p.parser, p[1]) )

    def p_basictext_4( self, p ):
        """basictext    : HTTPS_URI"""
        p[0] = BasicText( p.parser, HTTPS_URI(p.parser, p[1]) )

    def p_basictext_5( self, p ):
        """basictext    : WWW_URI"""
        p[0] = BasicText( p.parser, WWW_URI(p.parser, p[1]) )

    def p_basictext_6( self, p ):
        """basictext    : LINEBREAK"""
        p[0] = BasicText( p.parser, LINEBREAK(p.parser, p[1]) )

    def p_markuptext_1( self, p ):
        """markuptext   : M_SPAN"""
        p[0] = MarkupText( p.parser, M_SPAN(p.parser, p[1]) )

    def p_markuptext_2( self, p ):
        """markuptext   : M_BOLD"""
        p[0] = MarkupText( p.parser, M_BOLD(p.parser, p[1]) )

    def p_markuptext_3( self, p ):
        """markuptext   : M_ITALIC"""
        p[0] = MarkupText( p.parser, M_ITALIC(p.parser, p[1]) )

    def p_markuptext_4( self, p ):
        """markuptext   : M_UNDERLINE"""
        p[0] = MarkupText( p.parser, M_UNDERLINE(p.parser, p[1]) )

    def p_markuptext_5( self, p ):
        """markuptext   : M_SUPERSCRIPT"""
        p[0] = MarkupText( p.parser, M_SUPERSCRIPT(p.parser, p[1]) )

    def p_markuptext_6( self, p ):
        """markuptext   : M_SUBSCRIPT"""
        p[0] = MarkupText( p.parser, M_SUBSCRIPT(p.parser, p[1]) )

    def p_markuptext_7( self, p ):
        """markuptext   : M_BOLDITALIC"""
        p[0] = MarkupText( p.parser, M_BOLDITALIC(p.parser, p[1]) )

    def p_markuptext_8( self, p ):
        """markuptext   : M_BOLDUNDERLINE"""
        p[0] = MarkupText( p.parser, M_BOLDUNDERLINE(p.parser, p[1]) )

    def p_markuptext_9( self, p ):
        """markuptext   : M_ITALICUNDERLINE"""
        p[0] = MarkupText( p.parser, M_ITALICUNDERLINE(p.parser, p[1]) )

    def p_markuptext_10( self, p ):
        """markuptext   : M_BOLDITALICUNDERLINE"""
        p[0] = MarkupText( p.parser, M_BOLDITALICUNDERLINE(p.parser, p[1]) )

    #---- sub-grammars

    def p_paragraph_seperator_1( self, p ) :
        """paragraph_separator  : NEWLINE"""
        p[0] = ParagraphSeparator( p.parser, None, NEWLINE(p.parser, p[1]) )

    def p_paragraph_seperator_2( self, p ) :
        """paragraph_separator  : paragraph_separator NEWLINE"""
        p[0] = ParagraphSeparator( p.parser, p[1], NEWLINE(p.parser, p[2]) )

    #def p_paragraph_seperator_3( self, p ) :
    #    """paragraph_separator  : """
    #    p[0] = ParagraphSeparator( p.parser, None, None )

    def p_error( self, p ):
        if p:
            column = self.etlex._find_tok_column( p )
            self._parse_error( 'before: %s ' % p.value,
                               self._coord(p.lineno, column) )
        else:
            self._parse_error( 'At end of input', '' )

class Coord( object ):
    """ Coordinates of a syntactic element. Consists of:
        - File name
        - Line number
        - (optional) column number, for the Lexer
    """
    def __init__( self, file, line, column=None ):
        self.file   = file
        self.line   = line
        self.column = column

    def __str__( self ):
        str = "%s:%s" % (self.file, self.line)
        if self.column :
            str += ":%s" % self.column
        return str


if __name__ == "__main__":
    import pprint, time
    
    text   = codecs.open( sys.argv[1], encoding='utf-8' 
             ).read() if len(sys.argv) > 1 else "hello" 
    parser = ETParser( lex_optimize=True, yacc_debug=True, yacc_optimize=False )
    t1     = time.time()
    # set debuglevel to 2 for debugging
    t = parser.parse( text, 'x.c', debuglevel=2 )
    t.show( showcoord=True )
    print time.time() - t1
