# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

"""Change the mapping if the style shortcut for color need to be customized"""

import re

fgcolors = {
    'a'     : 'aquamarine',
    'b'     : 'blue',
    'c'     : 'crimson',
    'd'     : '',
    'e'     : '',
    'f'     : 'fuchsia',
    'g'     : 'green',
    'h'     : '',
    'i'     : 'indigo',
    'j'     : '',
    'k'     : 'khaki',
    'l'     : 'lavender',
    'm'     : 'maroon',
    'n'     : 'navy',
    'o'     : 'orange',
    'p'     : 'pink',
    'q'     : '',
    'r'     : 'red',
    's'     : 'skyBlue',
    't'     : 'teal',
    'u'     : '',
    'v'     : 'violet',
    'w'     : 'white',
    'x'     : '',
    'y'     : 'yellow',
    'z'     : '',
}

bgcolors = {
    'A'     : 'aquamarine',
    'B'     : 'blue',
    'C'     : '',
    'D'     : '',
    'E'     : '',
    'F'     : 'fuchsia',
    'G'     : 'green',
    'H'     : '',
    'I'     : 'indigo',
    'J'     : '',
    'K'     : 'khaki',
    'L'     : 'lavender',
    'M'     : 'maroon',
    'N'     : 'navy',
    'O'     : 'orange',
    'P'     : 'pink',
    'Q'     : '',
    'R'     : 'red',
    'S'     : 'skyBlue',
    'T'     : 'teal',
    'U'     : '',
    'V'     : 'violet',
    'W'     : 'white',
    'X'     : '',
    'Y'     : 'yellow',
    'Z'     : '',
}

fntsize = {
    '+'    : 'font-size : larger',
    '++'   : 'font-size : large',
    '+++'  : 'font-size : x-large',
    '++++' : 'font-size : xx-large',
    '-'    : 'font-size : smaller',
    '--'   : 'font-size : small',
    '---'  : 'font-size : x-small',
    '----' : 'font-size : xx-small',
}

def style_color( m ) :
    s = 'color: %s' % fgcolors[m[:1]]
    z = fntsize.get( m[1:], '' )
    s += ('; %s' % z) if z else ''
    return s

def style_background( m ) :
    return 'background-color: %s' % bgcolors[m]

def style_border( m ) :
    w, style, color = [ x.strip() for x in m[1:].split( ',' ) ]
    color = fgcolors[color] if len(color) == 1 else color
    return 'border : %spx %s %s' % ( w, style, color )

def style_margin( m ) :
    return 'margin : %spx' % m[:-1].strip()

def style_padding( m ) :
    return 'padding : %spx' % m[1:].strip()

def style_wcard( m ) :
    return m.strip()

space       = r'[ \t]*'
re_fg       = r'%s[a-z]%s[+-]{0,4};' % (space, space)
re_bg       = r'%s[A-Z]%s;' % (space, space)
re_border   = r'%s/%s[0-9]+%s,%s[a-z]+%s,%s[a-z]+%s;' % tuple( [space] * 7 )
re_margin   = r'%s[0-9]+%s\|%s;' % (space, space, space)
re_padding  = r'%s\|%s[0-9]+%s;' % (space, space, space)
re_wcard    = r'[^;]+?;'

re_list = [
    (re_fg,        style_color),
    (re_bg,        style_background),
    (re_border,    style_border),
    (re_margin,    style_margin),
    (re_padding,   style_padding),
    (re_wcard,     style_wcard),
]
re_master = re.compile(
    '|'.join([ r'(%s)' % r for r in map( lambda x : x[0], re_list ) ])
)

def stylemarkup( text ) :
    if text :
        text += ';' if text[-1] != ';' else ''
        fns = map( lambda x : x[1], re_list )
        styles = []
        for x in re_master.findall(text) :
            for text, func in zip(x, fns) :
                text = text.strip()[:-1].strip() 
                if not text : continue
                try    : styles.append( func( text ) )
                except : pass
        style = '; '.join(filter(None, styles))
    else :
        style = ''
    return style
