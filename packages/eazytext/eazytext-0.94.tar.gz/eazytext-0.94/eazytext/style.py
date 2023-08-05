# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

"""Change the mapping if the style shortcut for color need to be customized"""

import re

fgcolors = {
    'a'     : u'aquamarine',
    'b'     : u'blue',
    'c'     : u'crimson',
    'd'     : u'',
    'e'     : u'',
    'f'     : u'fuchsia',
    'g'     : u'green',
    'h'     : u'',
    'i'     : u'indigo',
    'j'     : u'',
    'k'     : u'khaki',
    'l'     : u'lavender',
    'm'     : u'maroon',
    'n'     : u'navy',
    'o'     : u'orange',
    'p'     : u'pink',
    'q'     : u'',
    'r'     : u'red',
    's'     : u'skyBlue',
    't'     : u'teal',
    'u'     : u'',
    'v'     : u'violet',
    'w'     : u'white',
    'x'     : u'',
    'y'     : u'yellow',
    'z'     : u'',
}

bgcolors = {
    'A'     : u'aquamarine',
    'B'     : u'blue',
    'C'     : u'',
    'D'     : u'',
    'E'     : u'',
    'F'     : u'fuchsia',
    'G'     : u'green',
    'H'     : u'',
    'I'     : u'indigo',
    'J'     : u'',
    'K'     : u'khaki',
    'L'     : u'lavender',
    'M'     : u'maroon',
    'N'     : u'navy',
    'O'     : u'orange',
    'P'     : u'pink',
    'Q'     : u'',
    'R'     : u'red',
    'S'     : u'skyBlue',
    'T'     : u'teal',
    'U'     : u'',
    'V'     : u'violet',
    'W'     : u'white',
    'X'     : u'',
    'Y'     : u'yellow',
    'Z'     : u'',
}

fntsize = {
    '+'    : u'font-size : larger',
    '++'   : u'font-size : large',
    '+++'  : u'font-size : x-large',
    '++++' : u'font-size : xx-large',
    '-'    : u'font-size : smaller',
    '--'   : u'font-size : small',
    '---'  : u'font-size : x-small',
    '----' : u'font-size : xx-small',
}

def style_color( m ) :
    return u'color: %s' % fgcolors[m[:1]]

def style_fontsize( m ) :
    return fntsize[m]

def style_background( m ) :
    return u'background-color: %s' % bgcolors[m]

def style_border( m ) :
    w, style, color = [ x.strip() for x in m[1:].split( ',' ) ]
    color = fgcolors[color] if len(color) == 1 else color
    return u'border : %spx %s %s' % ( w, style, color )

def style_margin( m ) :
    return u'margin : %spx' % m[:-1].strip()

def style_padding( m ) :
    return u'padding : %spx' % m[1:].strip()

def style_wcard( m ) :
    return m.strip()

space       = r'[ \t]*'
re_fg       = r'%s[a-z]%s;' % (space, space)
re_bg       = r'%s[A-Z]%s;' % (space, space)
re_incsize  = r'%s\+{1,4}%s;' % (space, space)
re_decsize  = r'%s\-{1,4}%s;' % (space, space)
re_border   = r'%s/%s[0-9]+%s,%s[a-z]+%s,%s[a-z]+%s;' % tuple( [space] * 7 )
re_margin   = r'%s[0-9]+%s\|%s;' % (space, space, space)
re_padding  = r'%s\|%s[0-9]+%s;' % (space, space, space)
re_wcard    = r'[^;]+?;'

re_list = [
    (re_fg,        style_color),
    (re_bg,        style_background),
    (re_incsize,   style_fontsize),
    (re_decsize,   style_fontsize),
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
        text += u';' if text[-1] != ';' else u''
        fns = map( lambda x : x[1], re_list )
        styles = []
        for x in re_master.findall(text) :
            for text, func in zip(x, fns) :
                text = text.strip()[:-1].strip() 
                if not text : continue
                try    : styles.append( func( text ) )
                except : pass
        style = u'; '.join(filter(None, styles))
    else :
        style = u''
    return style
