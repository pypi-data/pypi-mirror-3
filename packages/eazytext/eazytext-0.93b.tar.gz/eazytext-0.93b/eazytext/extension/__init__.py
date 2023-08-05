# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

"""
h3. EazyText Extensions

EazyText Extension is a plugin framework to extend wiki engine itself. One
can define new markups, text formats etc ... and integrate it with EazyText as
an extension.

h3. Extension Framework

Extented wiki text can be added into the main document by enclosing them within
triple curly braces '' \{\{{ ... }}} ''. Everything between the curly braces
are passed directly to the extension module, which, in most of the cases will
return a translated HTML text. The general format while using a wiki extension
is,

> \{\{{''extension-name'' //{c} extension arguments similar to python function call convention//
> # { ''property-name'' : //value//, ''property-name'' : //value//, ... }
>
> ''extension-text ...''
>
> }}}

* ''extension-name'', should be one of the valid extensions.
* ''parameter-strings'', a sequence of arugments to coded in python's function calling
  convention.
* ''property-name'', property name can be a property accepted by the extension
  module or can be CSS property. Note that, the entire property block should
  be marked by a beginning ''hash (#)''
* ''extension-text'', the actual text that get passed on to the extension class.
"""

from   zope.interface       import implements

from   eazytext.interfaces  import IEazyTextExtension

class Extension( object ):
    """Base class from with extension-plugin implementers must derive from."""
    implements( IEazyTextExtension )

    def __init__( self, *args, **kwargs ):
        pass

    def __call__( self, argtext='' ):
        return eval( 'Extension( %s )' % argtext )

    def onparse( self, node ):
        pass

    def headpass1( self, node, igen ):
        pass

    def headpass2( self, node, igen ):
        pass

    def generate( self, node, igen, *args, **kwargs ) :
        html = self.html( node, igen, *args, **kwargs )
        html and igen.puttext( html )

    def tailpass( self, node, igen ):
        pass

    def html( self, node, igen, *args, **kwargs ):
        """Can be overriden by the deriving class to provide the translated html
        that will be substituted in the place of the extennsion() calls.
        """
        return ''


def nowiki2prop( text ):
    # Fetch the properties
    proplines = []
    lines = text.splitlines() 
    while lines and lines[0].lstrip().startswith('#') :
        proplines.append( lines.pop(0).lstrip('#') )
    remtext = '\n'.join( lines )
    try    :
        prop  = proplines and eval( ''.join( proplines )) or {}
        style = '; '.join([ '%s : %s' % (k,v) for k,v in prop.items() ])
    except :
        style = ''
    return style, remtext
