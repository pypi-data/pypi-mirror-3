# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

# Gotcha : None
# Notes  : None
# Todo   : None

from   zope.component       import getGlobalSiteManager

from   eazytext.macro       import Macro
from   eazytext.interfaces  import IEazyTextMacro
from   eazytext.lib         import constructstyle

gsm = getGlobalSiteManager()

doc = """
h3. Span

: Description ::
    Create a span element. Try using ~``...~`` markup to generate span
    elements, if advanced styling is required, this macro can come in handy.
    Accepts CSS styles for keyword arguments.
: Example ::
    [<PRE {{ Span( 'hello world' ) }} >]
: Selector ::
    The generated span tag can be selected (in CSS and JS) using class
    attribute, //etm-span//

Positional arguments,
|= text   | optional, text for the span element
"""

class Span( Macro ) :
    """Macro plugin to generate a span element, which can be used for styling
    portions of inline text.
    """
    _doc = doc
    pluginname = 'Span'
    tmpl = '<span class="etm-span" style="%s"> %s </span>'

    def __init__( self, *args, **kwargs ):
        self.text = len(args) > 0 and args[0] or ''
        self.style = constructstyle( kwargs )

    def __call__( self, argtext='' ):
        return eval( 'Span( %s )' % argtext )

    def html( self, node, igen, *args, **kwargs ):
        return self.tmpl % ( self.style, self.text )

# Register this plugin
gsm.registerUtility( Span(), IEazyTextMacro, Span.pluginname )
