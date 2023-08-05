#! /usr/bin/env python

# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

import os, sys, codecs
from   random           import choice
from   optparse         import OptionParser
from   os.path          import abspath, join, isfile, isdir, basename
from   eazytext         import etx_cmdline

THISDIR = abspath( '.' )
STDDIR = join( THISDIR, 'stdfiles' )
STDFILES = [ join(STDDIR, f) for f in os.listdir(STDDIR) ]
FILENAME = 'mixline.etx'

lines = []
[ lines.extend( open(f).read().splitlines() ) for f in STDFILES if isfile(f) ]

def mixedlines( size=100 ):
    return '\n'.join([ choice(lines) for i in range(size) ])

def test_mixlines( count=100 ) :
    while count :
        wikitext = mixedlines()
        open( FILENAME, 'w' ).write( wikitext )
        etx_cmdline( FILENAME )
        count -= 1

def _option_parse() :
    '''Parse the options and check whether the semantics are correct.'''
    parser = OptionParser(usage="usage: %prog [options] filename")
    options, args   = parser.parse_args()
    return options, args

if __name__ == '__main__' :
    options, args = _option_parse()
    test_mixlines()
