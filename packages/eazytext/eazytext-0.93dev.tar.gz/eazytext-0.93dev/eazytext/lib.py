# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

import re, sys

HTML_CHARS = [ '"', "'", '&', '<', '>' ]
ENDMARKER  = '<{<{}>}>'

def escape_htmlchars( text ) :
    """If the text is not supposed to have html characters, escape them"""
    text = re.compile( r'&', re.MULTILINE | re.UNICODE ).sub( '&amp;', text )
    text = re.compile( r'"', re.MULTILINE | re.UNICODE ).sub( '&quot;', text )
    text = re.compile( r'<', re.MULTILINE | re.UNICODE ).sub( '&lt;', text )
    text = re.compile( r'>', re.MULTILINE | re.UNICODE ).sub( '&gt;', text )
    return text


def split_style( style ) :
    """`style` can be a CSS style dictionary or string. If dictionary, it can
    have one non-CSS key 'style'. This key can contain the CSS property as a
    string or as another dictionary, in which case the dictionary can once
    again be treated as `style`"""
    style   = style or {}
    s_style = ''
    if isinstance( style, dict ) :
        inner_style = style.pop( 'style', {} )
    elif isinstance( style, (str, unicode) ) :
        inner_style = style
        style       = {}
    if isinstance( inner_style, dict ) and inner_style :
        d_style, s_style = split_style( inner_style )
        style.update( d_style )
    elif isinstance( inner_style, ( str, unicode )) :
        s_style = inner_style
    return style, s_style

def constructstyle( kwargs, defcss={}, styles='' ) :
    """Construct styles for macros and extensions based on the style passed as
    function arguments, extension properties and defaults style dictionary"""
    d_style, s_style = split_style( kwargs.pop( 'style', {} ))
    css    = {}             # A new dictionary instance
    css.update( defcss )
    css.update( d_style )
    css.update( kwargs )

    style = '; '.join([ "%s: %s" % (k,v) for k,v in css.items() ])
    style = '; '.join(filter(None, [style, s_style, styles ]))
    return style

def obfuscatemail( text ) :
    """Obfuscate email id"""
    return '@'.join([ n[:-3] + '...' for n in text.split( '@', 1 ) ])

def is_matchinghtml( text ) :
    """Check whether html special characters are present in the document."""
    return [ ch for ch in HTML_CHARS if ch in text ]

def wiki_properties( text ) :
    """Parse wiki properties, in the begining of the text,
        @ .....
        @ .....
    Should be a python consumable dictionary.
    Return property, remaining-text.
    """
    props = []
    # Strip off leading newlines
    textlines = text.lstrip( '\n\r' ).split('\n')
    for i in range(len( textlines )) :
        l = textlines[i].lstrip(' \t')
        if len(l) and l[0] == '@' :
            props.append( l[1:] )
            continue
        break;
    text = '\n'.join( textlines[i:] )
    try :
        props = eval( ''.join( props ) ) if props else {}
    except :
        log.error( sys.exc_info() )
        props = {}
    return props, text

