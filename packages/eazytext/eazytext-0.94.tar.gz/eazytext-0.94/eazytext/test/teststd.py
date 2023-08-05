#! /usr/bin/env python

# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

import os, sys
from   optparse         import OptionParser
from   os.path          import abspath, join, isfile, isdir, basename
from   eazytext         import etx_cmdline

THISDIR = abspath( '.' )
STDDIR = join( THISDIR, 'stdfiles' )
STDREFDIR = join( THISDIR, 'stdfiles', 'ref' )

contexts = {
}
def test_stdfiles() :
    for f in sorted( os.listdir( STDDIR )) :
        filepath = join( STDDIR, f )
        if f.endswith('.etx') :
            print '%r ...' % f
            etx_cmdline( filepath, context=contexts.get(f, '{}') )
            print
    print  
    print "Reference checking ... "
    for f in os.listdir( STDDIR ) :
        outfile = join( STDDIR, f )
        if f.startswith('.') or f.endswith( '.etx' ) or isdir(outfile) : continue
        reffile = join( STDREFDIR, f )
        refpytext = open(reffile).read()
        pytext = open(outfile).read()
        print "%25r : %s" % ( basename(f), refpytext==pytext)

def _option_parse() :
    '''Parse the options and check whether the semantics are correct.'''
    parser = OptionParser(usage="usage: %prog [options] filename")

    options, args   = parser.parse_args()

    return options, args

if __name__ == '__main__' :
    options, args = _option_parse()
    test_stdfiles()
