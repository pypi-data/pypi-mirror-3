# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

"""
h2. Templated Tags

HTML tags with common usage pattern are pre-templated and can be used by
attaching the template name with HTML markup
''\[<''. And the text contained within '' \[< .... >] '' are interpreted by
the template. For example, most of the pre-formatted text in this page are
generated using ''PRE'' template, like,
   > \[<PRE preformatted text \>]

   > [<PRE preformatted text >]
"""

# Gotcha : None
# Notes  : None
# Todo   : None

from   zope.component       import getGlobalSiteManager
from   zope.interface       import implements

from   eazytext.utils       import escape_htmlchars
from   eazytext.interfaces  import IEazyTextTemplateTags

gsm = getGlobalSiteManager()

class TT( object ):
    implements( IEazyTextTemplateTags )

    def onparse( self, node ):
        pass

    def headpass1( self, node, igen ):
        pass

    def headpass2( self, node, igen ):
        pass

    def generate( self, node, igen, *args, **kwargs ):
        pass

    def tailpass( self, node, igen ):
        pass


class TTAbbr( TT ):
    """Show the abbreviated text, the expanded full text will be shown by
    hovering over the abbreviated text.
    """
    pluginname = 'ABBR'
    template = u'<abbr class="etttag" title="%s">%s</abbr>'
    def generate( self, node, igen, *args, **kwargs ):
        args  = node.text.split(',')
        cont  = escape_htmlchars( args and args.pop(0).strip() or '' )
        title = escape_htmlchars( args and args.pop(0).strip() or '' )
        html  =  self.template % ( title, cont )
        igen.puttext( html )
    example = u'[<ABBR WTO, World Trade organisation >]'


class TTAddr( TT ) :
    """Encapsulate address text inside <address> tag. Note that comma inside
    the text will automatically be replaced with <br/>"""
    pluginname = 'ADDR'
    template = u'<address class="etttag">%s</address>'
    def generate( self, node, igen, *args, **kwargs ):
        text = escape_htmlchars( node.text ).replace(u',', u'<br/>')
        igen.puttext( self.template % text )
    example = u"[<ADDR 1, Presidency, St. Mark's Road, Bangalore-1 >]"


class TTFixme( TT ):
    """A simple FIXME motif to associate with a any particular text."""
    pluginname = 'FIXME'
    template = u'<span class="etttag fixme">%s</span> %s'
    def generate( self, node, igen, *args, **kwargs ):
        igen.puttext( self.template % (u'FIXME', node.text) )
    example = u'[<FIXME The parser is yet to support unicode>]'


class TTPre( TT ):
    """Preformated text. Text inside this template will be spanned (using span
    element) and styled with //pre//.
    """
    pluginname = 'PRE'
    template = u'<span class="etttag pre">%s</span>'
    def generate( self, node, igen, *args, **kwargs ) :
        igen.puttext( self.template % escape_htmlchars( node.text ))
    example = u'[<PRE sample text >]'


class TTQ( TT ) :
    """Inline quotes using html's <q> tag. For blockquotes use the wiki markup
    //(>)// from the beginning of the line flush with whitespace.
    """
    pluginname = 'Q'
    template = u'<q class="etttag">%s</q>'
    def generate( self, node, igen, *args, **kwargs ):
        igen.puttext( self.template % escape_htmlchars( node.text ))
TTQ.example = u"""[<Q
Emptying the heart of desires,
Filling the belly with food,
Weakening the ambitions,
Toughening the bones.
>]
"""


class TTSmileySmile( TT ):
    """A simple smiley, a happy one."""
    pluginname = ':-)'
    template = u'<span class="etttag smile">%s</span>'
    def generate( self, node, igen, *args, **kwargs ):
        igen.puttext( self.template % '&#9786;' )
    example = u'[<:-)>] '


class TTSmileySad( TT ):
    """A simple smiley, a sad one."""
    pluginname = ':-('
    template = u'<span class="etttag sad">%s</span>'
    def generate( self, node, igen, *args, **kwargs ):
        igen.puttext( self.template % '&#9785;' )
    example = u'[<:-(>]'


class TTFnt( TT ) :
    """Style encapsulated text with CSS fonts. The font styling will be applied
    only to the text contained inside the template. """
    pluginname = 'FNT'
    template = u'<span class="etttag fnt" style="font: %s">%s</span>'
    def generate( self, node, igen, *args, **kwargs ):
        try :
            style, innerHTML = node.text.split( u';', 1 )
        except :
            style, innerHTML = u'', node.text
        style, innerHTML = escape_htmlchars(style), escape_htmlchars(innerHTML)
        igen.puttext( self.template % (style, innerHTML) )
TTFnt.example = u"""[<FNT italic bold 12px/30px Georgia, serif ;
This text is specially fonted >]
"""


class TTFootnote( TT ) :
    """A Footnote reference."""
    pluginname = 'FOOTNOTE'
    template = u'<sup class="etttag footnote">' + \
               u'<a href="#%s" style="text-decoration: none;">%s' + \
               u'</a></sup>'
    def generate( self, node, igen, *args, **kwargs ):
        text = escape_htmlchars( node.text.strip() )
        igen.puttext( self.template % (text, text) )
TTFootnote.example = u"""... mentioned by Richard Feynman
[<FN 1 >], initially proposed by Albert Einstein  [<FN 2 >]

And foot-note content can be specified using the Wiki-extension language,
like,

{{{ Footnote //footnote-title//
1 German-born Swiss-American theoretical physicist, philosopher and
author who is widely regarded as one of the most influential and best
known scientists and intellectuals of all time. He is often regarded as
the father of modern physics.

2 American physicist known for his work in the path integral
formulation of quantum mechanics, the theory of quantum electrodynamics.
}}}
"""

for k, cls in globals().items() :
    if k.startswith( 'TT' ) and hasattr( cls, 'pluginname' ) :
        gsm.registerUtility( cls(), IEazyTextTemplateTags, cls.pluginname.lower() )
