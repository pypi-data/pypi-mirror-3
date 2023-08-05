# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

# Gotcha : None
# Notes  : None
# Todo   :
#   1. Add TOC with pos='inline'

from   random       import choice
from   copy         import copy, deepcopy

from   zope.component       import getGlobalSiteManager

from   eazytext.macro       import Macro
from   eazytext.interfaces  import IEazyTextMacro
from   eazytext.lib         import constructstyle, escape_htmlchars
from   eazytext.ast         import Heading, BASICTEXT

gsm = getGlobalSiteManager()

doc = """
h3. Toc

: Description ::
    Macro to generate Table of contents.  Accepts CSS styles for keyword
    arguments.
: Example ::
    [<PRE {{ Toc() }} >]
: Selector ::
    The generated table-of-contents containing element can be selected
    (in CSS and JS) using class attribute, //etm-toc//

Positional arguments, //None//

keyword argument,
|= summary    | optional, summary for table of contents
|= maxheadlen | optional, number of characters to display for each title.
"""

class Toc( Macro ):
    """Macro plugin to generate table-of-contents for the embedding wiki
    document based on head elements, h1, h2, h3, h4, h5.
    """
    _doc = doc
    pluginname    = 'Toc'
    tmpl          = '<details class="etm-toc" style="%s"> %s </details>'
    summary_tmpl  = '<summary> %s </summary>'
    headlist_tmpl = '<ul> %s </ul>'
    toca_tmpl     = '<li><a class="level-%s" href="%s"> %s </a></li>'

    htags = [ '', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6' ]

    MAXHEADLEN = 30
    SUMMARY    = 'Table of Contents'

    def __init__( self, **kwargs ) :
        try    : self.maxheadlen = int(kwargs.pop( 'maxheadlen', self.MAXHEADLEN ))
        except : self.maxheadlen = self.MAXHEADLEN
        self.summary = kwargs.pop( 'summary', self.SUMMARY )
        self.style  = constructstyle( kwargs )

    def __call__( self, argtext='' ):
        return eval( 'Toc( %s )' % argtext )

    def headpass1( self, node, igen ) :
        etparser = node.parser.etparser
        try :
            headings = node.getroot().filter( lambda n : isinstance(n, Heading) )
            headlist = []
            for h in headings :
                text = ''.join([
                  n.dump(None)
                  for n in h.filter( lambda n : isinstance(n, BASICTEXT) )
                ])
                text = escape_htmlchars(
                            text[:self.maxheadlen] + \
                            ('...' if len(text) > self.maxheadlen else '')
                       )
                headlist.append( self.toca_tmpl % (h.level, '#'+text, text) )
            headlist = self.headlist_tmpl % '\n'.join( headlist )
            summary = self.summary_tmpl % self.summary
            html = self.tmpl % ( self.style, '\n'.join([summary, headlist]) )
        except :
            if node.parser.etparser.debug : raise
            html = 'Unable to generate the TOC, ' + \
                            'Wiki page not properly formed ! <br></br>'
        self.htmltext = html

    def generate( self, node, igen, *args, **kwargs ):
        igen.puttext( self.htmltext )

# Register this plugin
gsm.registerUtility( Toc(), IEazyTextMacro, Toc.pluginname )
