#! /usr/bin/env python
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-


"""Lexing rules for EazyText text"""

# Gotcha :
# Notes  :
# Todo   :

import re, sys, logging, codecs

import ply.lex
from   ply.lex    import TOKEN, LexToken

log = logging.getLogger( __name__ )

class ETLexer( object ) :
    """A lexer for the EazyText markup.
        build() To build   
        input() Set the input text
        token() To get new tokens.
    The public attribute filename can be set to an initial filaneme, but the
    lexer will update it upon #line directives."""

    ## -------------- Internal auxiliary methods ---------------------

    def _error( self, msg, token ):
        print "Error in file %r ..." % self.filename
        loct = self._make_tok_location( token )
        self.error_func and self.error_func(self, msg, loct[0], loct[1])
        self.lexer.skip( 1 )
        log.error( "%s %s" % (msg, token) )
    
    def _find_tok_column( self, token ):
        i = token.lexpos
        while i > 0:
            if self.lexer.lexdata[i] == '\n': break
            i -= 1
        return (token.lexpos - i) + 1
    
    def _make_tok_location( self, token ):
        return ( token.lineno, self._find_tok_column(token) )

    def _incrlineno( self, token ) :
        newlines = len( token.value.split('\n') ) - 1
        if newlines > 0 : token.lexer.lineno += newlines

    def _lextoken( self, type_, value ) :
        tok = LexToken()
        tok.type = type_
        tok.value = value
        tok.lineno = self.lexer.lineno
        tok.lexpos = self.lexer.lexpos
        return tok
    
    def _onescaped( self, token ):
        if len(token.value) == 1 :
            # If escaping the newline then increment the lexposition, but count
            # the lin-number
            self._incrlineno( token )
            token.lexer.lexpos += 1
            return None
        else :
            return self._lextoken( 'ESCAPED_TEXT', token.value[1] )


    ## --------------- Interface methods ------------------------------

    def __init__( self, error_func=None, conf={} ):
        """ Create a new Lexer.
        error_func :
            An error function. Will be called with an error message, line
            and column as arguments, in case of an error during lexing.
        """
        self.error_func = error_func
        self.filename = ''
        self.conf = conf

    def build( self, **kwargs ) :
        """ Builds the lexer from the specification. Must be called after the
        lexer object is created. 
            
        This method exists separately, because the PLY manual warns against
        calling lex.lex inside __init__"""
        self.lexer = ply.lex.lex(
                        module=self,
                        reflags=re.MULTILINE | re.UNICODE,
                        **kwargs
                     )

    def reset_lineno( self ) :
        """ Resets the internal line number counter of the lexer."""
        self.lexer.lineno = 1

    def input( self, text ) :
        """`text` to tokenise"""
        self.lexer.input( text )
    
    def token( self ) :
        """Get the next token"""
        tok = self.lexer.token()
        return tok 

    # States
    states = (
               ( 'nowiki', 'exclusive' ),
               ( 'table', 'exclusive' ),
             )

    ## Tokens recognized by the ETLexer
    tokens = (
        # Text
        'NEWLINE', 'TEXT', 'ESCAPED_TEXT', 'SPECIALCHARS',
        'HTTP_URI', 'HTTPS_URI', 'WWW_URI', 'LINEBREAK',
        # Text markup
        'M_SPAN', 'M_BOLD', 'M_ITALIC', 'M_UNDERLINE', 'M_SUPERSCRIPT',
        'M_SUBSCRIPT', 'M_BOLDITALIC', 'M_ITALICUNDERLINE', 'M_BOLDUNDERLINE',
        'M_BOLDITALICUNDERLINE',
        # Inline Text blocks
        'LINK', 'MACRO', 'HTML', #'NESTEDLINK', 
        # Text blocks
        'HORIZONTALRULE', 'HEADING',
        'ORDLIST_START', 'UNORDLIST_START', 'DEFINITION_START', 'BQUOTE_START',
        'BTABLE_START', 'TABLE_CELLSTART',
        # Nowiki blocks
        'NOWIKI_OPEN', 'NOWIKITEXT', 'NOWIKI_CLOSE',
        # Endmarker
        'ENDMARKER',
    )

    # pipe, sqropen, sqrclose, paranopen, paranclose, angleopen, angleclose,
    spchars     = r' \\\|\[\]\{\}\<\>\#:=-'
    txtmarkup   = r"'\*/_`,^"
    anything    = r'.|\n|\r\n'
    endmarker   = r'\<\{\<\{\}\>\}\>'

    escchar     = r'\\'
    spac        = r'[ \t]*'
    space       = r'[ \t]+'
    ws          = r'[ \t\r\n]*'
    wspace      = r'[ \t\r\n]+'
    style       = r'\{[^{}\r\n]*?\}'

    escseq      = r'(%s.?)|(%s$)' % (escchar,escchar)
    newline     = r'\n|\r\n'
    text        = r'[^\r\n%s]+' % (txtmarkup+spchars)
    specialchars= r'[%s]' % (txtmarkup+spchars)
    # Block text
    hrule       = r'^-{4,}%s' % spac
    heading     = r'^%s((={1,6})|([hH][123456]\.))(%s)?' % (spac, style)
    btopen, btclose, btrow, btcell, bthead = '{', '}', '-', ' ' , '='
    btable      = r'^%s\|\|[ {}=-](%s)?' % (spac, style)
    nowikiopen  = r'^%s\{\{\{.*?$' % spac
    nowikinl    = r'(\n|\r\n)+'
    nowikitext  = r'^.+$'
    nowikiclose = r'^%s}}}%s$' % (spac, spac)
    ordmark     = r'^%s\#{1,5}(%s)?' % (spac, style)
    unordmark   = r'^%s\*{1,5}(%s)?' % (spac, style)
    defnmark    = r'^%s:[^\n\r]*::' % spac
    bqmark      = r'^%s\>{1,5}' % spac
    tblcellbegin= r'^%s\|=?(%s)?' % (spac, style)
    tblcellstart= r'%s\|=?(%s)?' % (spac, style)
    # Text markup
    tmark_span  = r"``(%s)?" % style
    tmark_bold  = r"(''|\*\*)(%s)?" % style
    tmark_italic= r"//(%s)?" % style
    tmark_uline = r"__(%s)?" % style
    tmark_sup   = r"\^\^(%s)?" % style
    tmark_sub   = r",,(%s)?" % style
    tmark_bi    = r"('/|/')(%s)?" % style
    tmark_iu    = r"(/_|_/)(%s)?" % style
    tmark_bu    = r"('_|_')(%s)?" % style
    tmark_biu   = r"('/_|_/')(%s)?" % style
    tmark_lbreak= r"<br>"
    # Inline text block
    link        = r'\[\[(%s)+?(?=\]\])\]\]' % anything
    nestedlink  = r'\[\[(%s)+?(?=\]\])\]\]' % link
    macro       = r'\{\{(%s)+?(?=\}\})\}\}' % anything
    html        = r'\[<(%s)+?(?=>\])>\]' % anything
    # Tokenize Complex regex
    http_schema    = r'http://'
    https_schema   = r'https://'
    www_domain     = r'www\.'
    uri_reserved   = r':;/@&=,\?\#\+\$'
    uri_mark       = r"_!'\(\)\*\.\-"
    uri_escape     = r'%'
    http_uri       = http_schema + r'[a-zA-Z0-9' + uri_escape + uri_reserved + uri_mark + r']+'
    https_uri      = https_schema + r'[a-zA-Z0-9' + uri_escape + uri_reserved + uri_mark + r']+'
    www_uri        = www_domain + r'[a-zA-Z0-9' + uri_escape + uri_reserved + uri_mark + r']+'

    
    ## Rules for the lexer.

    @TOKEN( escseq )
    def t_ESCAPED( self, t ):
        return self._onescaped( t )

    @TOKEN( endmarker )
    def t_ENDMARKER( self, t ):  
        return t

    @TOKEN(http_uri)
    def t_HTTP_URI( self, t ):
        return t

    @TOKEN(https_uri)
    def t_HTTPS_URI( self, t ):
        return t

    @TOKEN(www_uri)
    def t_WWW_URI( self, t ):
        return t

    @TOKEN( nowikiopen )
    def t_NOWIKI_OPEN( self, t ) :
        t.lexer.push_state('nowiki')
        return t

    @TOKEN( hrule )
    def t_HORIZONTALRULE( self, t ):
        self._incrlineno(t)
        return t

    @TOKEN( heading )
    def t_HEADING( self, t ):
        return t

    @TOKEN( ordmark )
    def t_ORDLIST_START( self, t ):
        return t

    @TOKEN( unordmark )
    def t_UNORDLIST_START( self, t ):
        return t

    @TOKEN( defnmark )
    def t_DEFINITION_START( self, t ):
        return t

    @TOKEN( bqmark )
    def t_BQUOTE_START( self, t ):
        return t

    @TOKEN( btable )
    def t_BTABLE_START( self, t ) :
        return t

    @TOKEN( tblcellbegin )
    def t_TABLE_CELLBEGIN( self, t ):
        t.lexer.push_state( 'table' )
        t = self._lextoken( 'TABLE_CELLSTART', t.value )
        return t

    @TOKEN( tmark_biu )
    def t_M_BOLDITALICUNDERLINE( self, t ) :
        return t

    @TOKEN( tmark_span )
    def t_M_SPAN( self, t ) :
        return t

    @TOKEN( tmark_bold )
    def t_M_BOLD( self, t ) :
        return t

    @TOKEN( tmark_italic )
    def t_M_ITALIC( self, t ) :
        return t

    @TOKEN( tmark_uline )
    def t_M_UNDERLINE( self, t ) :
        return t

    @TOKEN( tmark_sup )
    def t_M_SUPERSCRIPT( self, t ) :
        return t

    @TOKEN( tmark_sub )
    def t_M_SUBSCRIPT( self, t ) :
        return t

    @TOKEN( tmark_bi )
    def t_M_BOLDITALIC( self, t ) :
        return t

    @TOKEN( tmark_iu )
    def t_M_ITALICUNDERLINE( self, t ) :
        return t

    @TOKEN( tmark_bu )
    def t_M_BOLDUNDERLINE( self, t ) :
        return t

    @TOKEN( link )
    def t_LINK( self, t ):
        self._incrlineno(t)
        return t

    #@TOKEN( nestedlink )
    #def t_NESTEDLINK( self, t ):
    #    self._incrlineno(t)
    #    return t

    @TOKEN( macro )
    def t_MACRO( self, t ):
        self._incrlineno(t)
        return t

    @TOKEN( html )
    def t_HTML( self, t ):
        self._incrlineno(t)
        return t

    @TOKEN( newline )
    def t_NEWLINE( self, t ):
        self._incrlineno(t)
        return t

    @TOKEN( tmark_lbreak )
    def t_LINEBREAK( self, t ) :
        return t

    @TOKEN( text )
    def t_TEXT( self, t ):
        return t

    @TOKEN( specialchars )
    def t_SPECIALCHARS( self, t ):
        return t

    @TOKEN( nowikiclose )
    def t_nowiki_NOWIKI_CLOSE( self, t ):
        t.lexer.pop_state()
        return t

    @TOKEN( endmarker )
    def t_nowiki_ENDMARKER( self, t ):  
        return t

    @TOKEN( nowikinl )
    def t_nowiki_NEWLINE( self, t ):
        self._incrlineno(t)
        return t

    @TOKEN( nowikitext )
    def t_nowiki_NOWIKITEXT( self, t ):
        self._incrlineno(t)
        return t

    @TOKEN( tblcellstart )
    def t_table_TABLE_CELLSTART( self, t ):
        return t

    @TOKEN( newline )
    def t_table_NEWLINE( self, t ):
        t.lexer.pop_state()
        self._incrlineno(t)
        return t

    @TOKEN( escseq )
    def t_table_ESCAPED( self, t ):
        return self._onescaped( t )

    @TOKEN(http_uri)
    def t_table_HTTP_URI( self, t ):
        return t

    @TOKEN(https_uri)
    def t_table_HTTPS_URI( self, t ):
        return t

    @TOKEN(www_uri)
    def t_table_WWW_URI( self, t ):
        return t

    @TOKEN( tmark_biu )
    def t_table_M_BOLDITALICUNDERLINE( self, t ) :
        return t

    @TOKEN( tmark_span )
    def t_table_M_SPAN( self, t ) :
        return t

    @TOKEN( tmark_bold )
    def t_table_M_BOLD( self, t ) :
        return t

    @TOKEN( tmark_italic )
    def t_table_M_ITALIC( self, t ) :
        return t

    @TOKEN( tmark_uline )
    def t_table_M_UNDERLINE( self, t ) :
        return t

    @TOKEN( tmark_sup )
    def t_table_M_SUPERSCRIPT( self, t ) :
        return t

    @TOKEN( tmark_sub )
    def t_table_M_SUBSCRIPT( self, t ) :
        return t

    @TOKEN( tmark_bi )
    def t_table_M_BOLDITALIC( self, t ) :
        return t

    @TOKEN( tmark_iu )
    def t_table_M_ITALICUNDERLINE( self, t ) :
        return t

    @TOKEN( tmark_bu )
    def t_table_M_BOLDUNDERLINE( self, t ) :
        return t

    @TOKEN( link )
    def t_table_LINK( self, t ):
        self._incrlineno(t)
        return t

    @TOKEN( macro )
    def t_table_MACRO( self, t ):
        self._incrlineno(t)
        return t

    @TOKEN( html )
    def t_table_HTML( self, t ):
        self._incrlineno(t)
        return t

    @TOKEN( tmark_lbreak )
    def t_table_LINEBREAK( self, t ) :
        return t

    @TOKEN( text )
    def t_table_TEXT( self, t ):
        return t

    @TOKEN( specialchars )
    def t_table_SPECIALCHARS( self, t ):
        return t


    def t_error( self, t ):
        msg = 'Illegal character %s' % repr(t.value[0])
        self._error(msg, t)

    def t_nowiki_error( self, t ):
        msg = 'Illegal character %s' % repr(t.value[0])
        self._error(msg, t)

    def t_table_error( self, t ):
        msg = 'Illegal character %s' % repr(t.value[0])
        self._error(msg, t)


if __name__ == "__main__":
    def errfoo(lex, msg, a, b):
        print msg, a, b
        sys.exit()
    
    if len(sys.argv) > 1 :
        f = sys.argv[1]
        print "Lexing file %r ..." % f
        text = codecs.open(f, encoding='utf-8').read()
    else :
        text = "hello"

    etlex = ETLexer( errfoo )
    etlex.build()
    etlex.input( text )
    tok = etlex.token()
    while tok :
        print "- %15s" % tok.type, tok.lineno, tok.lexpos, '%r' % tok.value
        tok = etlex.token()
