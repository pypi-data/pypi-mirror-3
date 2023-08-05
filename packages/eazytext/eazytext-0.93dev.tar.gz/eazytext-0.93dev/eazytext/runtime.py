# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

import re
from   StringIO                 import StringIO
from   os.path                  import basename

from   zope.component           import getGlobalSiteManager

# Note :
# Special variables that the context should not mess with,
#       _m, _etxhash, _etxfile, StringIO

gsm = getGlobalSiteManager()

class StackMachine( object ) :
    def __init__( self,
                  ifile,
                  compiler,
                  etxconfig={},
                ):
        self.etxconfig = etxconfig
        self.bufstack = [ [] ]
        self.ifile = ifile
        self.compiler = compiler
        self.encoding = self.etxconfig['input_encoding']

    #---- Stack machine instructions

    def setencoding( self, encoding ):
        #self.encoding = encoding
        pass

    def append( self, value ) :
        self.bufstack[-1].append( value )
        return value

    def extend( self, value ) :
        if isinstance(value, list) :
            self.bufstack[-1].extend( value )
        else :
            raise Exception( 'Unable to extend context stack' )

    def pushbuf( self, buf=None ) :
        buf = []
        self.bufstack.append( buf )
        return buf

    def popbuf( self ) :
        return self.bufstack.pop(-1)

    def popbuftext( self ) :
        buf = self.popbuf()
        return ''.join( buf )

    def evalexprs( self, val, filters ) :
        filters = [ f.strip().split('.',1) for f in filters.split(',') if f ]
        unins = filters.pop(0) if filters and filters[0][0] == 'uni' else None
        skip  = filters.pop(0) if filters and filters[0][0] == 'n' else None
        # Default filters
        if skip == None :
            text = self.escfilters['uni']( self, val, unins )
        else :
            text = val
        # Pluggable filters
        if filters and skip == None :
            for filt in filters :
                text = self.escfilters.get( filt[0], None )( self, text, filt )
        return text

    def handlett( self, ttname, argstr ):
        ttplugins = self.etxconfig.get( 'ttplugins', {} )
        factory = ttplugins.get( ttname, None )
        ttplugin = factory and factory( argstr.strip() )
        html = ttplugin and self.ttplugin.handle( self ) or ''
        self.append( html )

    def handlemacro( self, macroname, argstr ):
        macroplugins = self.etxconfig.get( 'macroplugins', {} )
        factory = macroplugins.get( macroname, None )
        macroplugin = factory and factory( argstr.strip() )
        html = macroplugin and self.macroplugin.handle( self ) or ''
        self.append( html )

    def handleext( self, extname, argstr ):
        extplugins = self.etxconfig.get( 'extplugins', {} )
        factory = extplugins.get( extname, None )
        extplugin = factory and factory( argstr.strip() )
        html = extplugin and self.extplugin.handle( self ) or ''
        self.append( html )
