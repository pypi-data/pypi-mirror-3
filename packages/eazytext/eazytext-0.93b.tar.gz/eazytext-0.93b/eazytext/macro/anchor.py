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
h3. Anchor

: Description ::
    Create an anchor in the document which can be referenced else-wehere as page
    fragment. Accepts CSS styles for keyword arguments.
: Example ::
    [<PRE {{ Anchor( 'anchorname', 'display-text' ) }} >]
: Selector ::
    The generated achor tag can be selected (in CSS and JS) using class
    attribute, //etm-anchor//

Positional arguments,

|= anchor | anchor name as fragment, goes under @name attribute
|= text   | optional, text to be display at the anchor
"""

class Anchor( Macro ):
    """Macro plugin to generate a html anchor tag <a> that can be referenced as
    a page fragment elsewhere."""

    pluginname = 'Anchor'
    tmpl = '<a class="etm-anchor" name="%s" style="%s"> %s </a>'
    _doc = doc

    def __init__( self, *args, **kwargs ):
        args = list( args )
        self.anchor = args and args.pop( 0 ) or ''
        self.text = args and args.pop( 0 ) or '&#167;'
        self.style = constructstyle( kwargs )

    def __call__( self, argtext='' ):
        return eval( 'Anchor( %s )' % argtext )

    def html( self, node, igen, *args, **kwargs ) :
        return self.tmpl % ( self.anchor, self.style, self.text )

# Register this plugin
gsm.registerUtility( Anchor(), IEazyTextMacro, Anchor.pluginname )
