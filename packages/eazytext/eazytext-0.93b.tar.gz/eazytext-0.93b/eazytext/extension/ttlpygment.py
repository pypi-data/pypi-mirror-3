# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

from pygments.lexer import RegexLexer
from pygments.token import *

try :
    from tayra.lexer  import TTLLexer
except :
    TTLLexer = None

if TTLLexer :
    class TemplateLexer( RegexLexer ):
        name = 'ttl'
        aliases = ['tayra-template', 'tayratemplate', 'ttl']
        filenames = ['*.ttl']

        comm1  = [
                ( TTLLexer.escseq, Punctuation ),
        ]
        tokens = {
            'root': comm1 + [
                ( TTLLexer.commentline, Comment ),
                ( TTLLexer.statement, Generic.Strong ),
                ( TTLLexer.pass_, Generic.Strong ),
                ( TTLLexer.emptyspace, Text ),
                ( TTLLexer.indent, Text ),
                ( TTLLexer.nl, Text ),
                ( TTLLexer.spchars, Text ),
                ( TTLLexer.text, Text ),
                # States
                ( TTLLexer.commentopen, Comment, 'comment' ),
                ( TTLLexer.filteropen, Operator, 'filter' ),
                ( TTLLexer.openexprs, Operator, 'exprs' ),
                ( TTLLexer.tagopen, Keyword, 'tag' ),
                # Directives
                ( TTLLexer.doctype, Generic.Declaration ),
                ( TTLLexer.charset, Generic.Declaration ),
                ( TTLLexer.body, Generic.Declaration ),
                ( TTLLexer.importas, Generic.Declaration ),
                ( TTLLexer.inherit, Generic.Declaration ),
                ( TTLLexer.implement, Generic.Declaration ),
                ( TTLLexer.use, Generic.Declaration ),
                # Blocks
                ( TTLLexer.interface, Name.Function ),
                ( TTLLexer.function, Name.Function ),
                ( TTLLexer.if_, Keyword ),
                ( TTLLexer.elif_, Keyword ),
                ( TTLLexer.else_, Keyword ),
                ( TTLLexer.for_, Keyword ),
                ( TTLLexer.while_, Keyword ),
            ],
            'tag' : comm1 + [
                ( TTLLexer.squote, Operator ),
                ( TTLLexer.dquote, Operator ),
                ( TTLLexer.equal, Operator ),
                ( TTLLexer.nl, Text ),
                ( TTLLexer.space, Text ),
                ( TTLLexer.atom, Keyword.Type ),
                ( TTLLexer.tag_text, Text ),
                ( TTLLexer.tag_spchars, Text ),
                # Open new state
                ( TTLLexer.openexprs, Operator, 'exprs' ),
                ( TTLLexer.openbrace, Operator, 'style' ),
                ( TTLLexer.tagend, Keyword, '#pop' ),
                ( TTLLexer.tagclose, Keyword, '#pop' ),
            ],
            'exprs': comm1 + [
                ( TTLLexer.string, String ),
                ( TTLLexer.closebrace, Operator, '#pop' ),
                ( TTLLexer.nl, Text ),
                ( TTLLexer.text, Text ),
            ],
            'style': comm1 + [
                ( TTLLexer.string, String ),
                ( TTLLexer.nl, Text ),
                ( TTLLexer.style_text, Text ),
                ( TTLLexer.style_spchars, Text ),
                ( TTLLexer.openexprs, Operator, 'exprs' ),
                ( TTLLexer.closebrace, Operator, '#pop' ),
            ],
            'comment': [
                ( TTLLexer.commenttext, Comment ),
                ( TTLLexer.commentclose, Comment, '#pop' ),
            ],
            'filter': [
                ( TTLLexer.filtertext, Text ),
                ( TTLLexer.filterclose, Operator, '#pop' ),
            ],
        }
else :
    class TemplateLexer( RegexLexer ): pass
