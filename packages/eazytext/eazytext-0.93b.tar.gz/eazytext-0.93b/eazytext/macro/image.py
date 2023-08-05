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

doc ="""
h3. Image

: Description ::
    Embed Images in the doc. Try to use ''Link markup'' to embed images, if
    advanced styling is required, this macro can come in handy.
    Accepts CSS styles for keyword arguments.
: Example ::
    [<PRE {{ Image( '/photo.jpg' ) }} >]
: Selector ::
    The generated <img> tag can be selected (in CSS and JS) using class
    attribute, //etm-image//

Positional arguments,
|= src    | source-url for image, goes into @src attribute
|= alt    | alternate text, goes into @alt attribute

keyword argument,
|= height | optional, image height, goes into @height attribute
|= width  | optional, image width, goes into @width attribute
|= href   | optional, href, to convert the image into a hyper-link
"""

class Image( Macro ) :
    """Macro plugin to generate an image element <img>, optionally as a
    hyperlink."""
    _doc = doc
    pluginname = 'Image'
    tmpl = '<img class="etm-image" %s %s src="%s" alt="%s" style="%s"/>'
    a_tmpl = '<a href="%s"> %s </a>'

    def __init__( self, *args, **kwargs ) :
        args = list(args)
        self.src = args.pop(0) if args else None
        self.alt = args.pop(0) if args else None
        self.height = kwargs.pop( 'height', None )
        self.width = kwargs.pop( 'width', None )
        self.href = kwargs.pop( 'href', '' )
        self.style = constructstyle( kwargs )

    def __call__( self, argtext='' ):
        return eval( 'Image( %s )' % argtext )

    def html( self, node, igen, *args, **kwargs ) :
        hattr = self.height and ( 'height="%s"' % self.height ) or ''
        wattr = self.width and ( 'width="%s"' % self.width ) or ''
        img = self.tmpl % ( hattr, wattr, self.src, self.alt, self.style )
        # If the image is a link, enclose it with a 'anchor' dom-element.
        html = ( self.a_tmpl % (self.href, img) ) if self.href else img
        return html

# Register this plugin
gsm.registerUtility( Image(), IEazyTextMacro, Image.pluginname )
