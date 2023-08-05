# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

from   os.path      import join, splitext, isfile, abspath, basename
from   StringIO     import StringIO
from   copy         import deepcopy

prolog = """
from   StringIO             import StringIO
"""

footer = """
_etxhash = %r
_etxfile = %r
"""

class InstrGen( object ) :
    machname = '_m'

    def __init__( self, compiler, etxconfig={} ):
        self.compiler = compiler
        self.devmod = etxconfig['devmod']
        self.etxconfig = etxconfig
        self.outfd = StringIO()
        self.pyindent = ''
        self.optimaltext = []
        self.pytext = None
        # prolog for python translated template
        self.encoding = etxconfig['input_encoding']

    def __call__( self ):
        clone = InstrGen( self.compiler, etxconfig=self.etxconfig )
        return clone

    def cr( self, count=1 ) :
        self.outfd.write( '\n'*count )
        self.outfd.write( self.pyindent )

    def codeindent( self, up=None, down=None, indent=True ):
        self.flushtext()
        if up != None :
            self.pyindent += up
        if down != None :
            self.pyindent = self.pyindent[:-len(down)]
        if indent : 
            self.outfd.write( self.pyindent )

    def codetext( self ) :
        return self.pytext

    #---- Generate Instructions

    def initialize( self ):
        self.outfd.write( prolog )
        self.cr()

    def comment( self, comment ) :
        if self.devmod :
            self.flushtext()
            self.cr()
            self.outfd.write( '# ' + ' '.join(comment.rstrip('\r\n').splitlines()) )

    def flushtext( self ) :
        if self.optimaltext :
            self.cr()
            self.outfd.write( '_m.extend( %s )' % self.optimaltext )
            self.optimaltext = []

    def puttext( self, text, force=False ):
        self.optimaltext.append( text )
        if force :
            self.flushtext()

    def pushbuf( self ):
        self.flushtext()
        self.cr()
        self.outfd.write( '_m.pushbuf()' )

    def putstatement( self, stmt ):
        self.flushtext()
        self.cr()
        self.outfd.write( stmt.rstrip('\r\n') )

    def popreturn( self, astext=True ):
        self.flushtext()
        self.cr()
        if astext == True :
            self.outfd.write( 'return _m.popbuftext()' )
        else :
            self.outfd.write( 'return _m.popbuf()' )

    def evalexprs( self, code, filters ) :
        self.flushtext()
        self.cr()
        self.outfd.write('_m.append( _m.evalexprs(%s, %r) )' % (code, filters))

    def handlett( self, ttname, argstr ):
        self.flushtext()
        self.cr()
        self.outfd.write('_m.handlett( %r, %r )' % (ttname, argstr) )

    def handlemacro( self, macroname, argstr ):
        self.flushtext()
        self.cr()
        self.outfd.write('_m.handlemacro( %r, %r )' % (macroname, argstr) )

    def handleext( self, extname, argstr ):
        self.flushtext()
        self.cr()
        self.outfd.write('_m.extname( %r, %r )' % (extname, argstr) )

    def popcompute( self, astext=True ):
        self.flushtext()
        self.cr()
        if astext == True :
            self.outfd.write( '_m.append( _m.popbuftext() )' )
        else :
            self.outfd.write( '_m.append( _m.popbuf() )' )

    def footer( self, etxhash, etxfile ):
        self.cr()
        self.outfd.write( footer % (etxhash, etxfile) )

    def finish( self ):
        self.pytext = self.outfd.getvalue()
