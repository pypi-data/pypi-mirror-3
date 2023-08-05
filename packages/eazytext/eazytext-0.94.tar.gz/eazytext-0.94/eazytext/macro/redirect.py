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

class Redirect( Macro ) :
    """
    Just sets the ``redirect`` attribute in
    node.parser.etparser.redirect to the the argument that is passed
    """
    pluginname = 'Redirect'

    def __init__( self, redireclink='' ) :
        self.redirect = redireclink

    def __call__( self, argtext='' ):
        return eval( 'Redirect( %s )' % argtext )

    def html( self, node, igen, *args, **kwargs ) :
        node.parser.etparser.redirect = self.redirect
        return ''

# Register this plugin
gsm.registerUtility( Redirect(), IEazyTextMacro, Redirect.pluginname )
