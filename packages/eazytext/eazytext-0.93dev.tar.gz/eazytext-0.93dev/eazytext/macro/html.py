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

gsm = getGlobalSiteManager()

doc = """
h3. Html

: Description ::
    Embed HTML text within wiki doc. Firstly, try to use ''\[< ... \>]'' markup
    to get the desired result, if advanced styling is required then use this
    macro.
: Example ::
    [<PRE {{ Html( '<b>hello world</b>' ) }} >]

Positional arguments,
|= html | HTML text
"""

class Html( Macro ) :
    """Embed HTML text within wiki doc. Firstly, try to use ''\[< ... \>]'' markup
    to get the desired result, if advanced styling is required then use this
    macro.
    """
    pluginname = 'Html'
    _doc = doc

    def __init__( self, html='' ) :
        self.htmltext  = html

    def __call__( self, argtext='' ):
        return eval( 'Html( %s )' % argtext )

    def html( self, node, igen, *args, **kwargs ) :
        return self.htmltext


# Register this plugin
gsm.registerUtility( Html(), IEazyTextMacro, Html.pluginname )
