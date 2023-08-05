# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

import imp, os, codecs
from   os.path                  import isfile, isdir, abspath, basename, \
                                       join, dirname
from   hashlib                  import sha1

from   eazytext.parser          import ETParser
from   eazytext.codegen         import InstrGen
from   eazytext.runtime         import StackMachine

class Compiler( object ):
    _memcache = {}
    def __init__( self,
                  etxloc=None,
                  etxtext=None,
                  # Wiki options
                  etxconfig={},
                  # ETParser options
                  etparser=None,
                  # InstrGen options
                  igen=None,
                ):
        # Source Eazytext
        if isinstance( etxloc, WikiLookup ) :
            self.etxlookup = etxloc
        elif etxloc or etxtext :
            self.etxlookup = WikiLookup(
                etxloc=etxloc, etxtext=etxtext, etxconfig=etxconfig
            )
        else :
            raise Exception( 'To compile, provide a valid eazytext source' )
        self.etxfile = self.etxlookup.etxfile
        self.pyfile = self.etxlookup.pyfile
        self.etxconfig = etxconfig
        # Parser phase
        self.etxparser = etparser or ETParser( etxconfig=self.etxconfig )
        # Instruction generation phase
        self.igen = igen or InstrGen( self, etxconfig=self.etxconfig )

    def __call__( self, etxloc=None, etxtext=None, etparser=None ):
        etparser = etparser or self.etparser
        clone = Compiler( etxloc=etxloc, etxtext=etxtext,
                          etxconfig=self.etxconfig, etparser=etparser
                        )
        return clone

    def execetx( self, code=None, context={} ):
        """Execute the wiki text (python compiled) under module's context
        `module`.
        """
        # Stack machine
        _m  = StackMachine( self.etxfile, self, etxconfig=self.etxconfig )
        # Module instance for the etx file
        module = imp.new_module( self.modulename )
        module.__dict__.update({ self.igen.machname : _m })
        module.__dict__.update( context )
        # Load etx translated python code
        code = code or self.etx2code()
        # Execute the code in module's context
        exec code in module.__dict__, module.__dict__
        return module

    def etx2code( self ):
        """Code loading involves, picking up the intermediate python file from
        the cache (if disk persistence is enabled and the file is available)
        or, generate afresh using `igen` Instruction Generator.
        """
        code = self._memcache.get( self.etxlookup.hashkey, None 
               ) if self.etxconfig['devmod'] == False else None
        if code : return code
        pytext = self.etxlookup.pytext
        if pytext :
            etxhash = None
            code = compile( pytext, self.etxfile, 'exec' )
        else :
            pytext = self.topy( etxhash=self.etxlookup.etxhash )
            code = compile( pytext, self.etxfile, 'exec' )
            self.etxlookup.pytext = pytext

        if self.etxconfig['memcache'] :
            self._memcache.setdefault( self.etxlookup.hashkey, code )
        return code

    def toast( self ):
        etxtext = self.etxlookup.etxtext
        tu = self.etxparser.parse( etxtext, etxfile=self.etxfile )
        return tu

    def topy( self, *args, **kwargs ):
        encoding = self.etxconfig['input_encoding']
        tu = self.toast()
        etxtext = self.etxlookup.etxtext
        kwargs.update( etxhash=self.etxlookup.etxhash )
        if tu :
            tu.validate()
            tu.headpass1( self.igen )                   # Head pass, phase 1
            tu.headpass2( self.igen )                   # Head pass, phase 2
            tu.generate( self.igen, *args, **kwargs )   # Generation
            tu.tailpass( self.igen )                    # Tail pass
            return self.igen.codetext()
        else :
            return None

    modulename = property(lambda s : basename( s.etxfile ).split('.', 1)[0] )



class WikiLookup( object ) :
    ETXCONFIG = [ 'directories', 'devmod' ]
    NOETXFILE = '<Source provided as raw text>'
    def __init__( self, etxloc=None, etxtext=None, etxconfig={} ):
        self.directories = etxconfig.get('directories', [])
        self.devmod = etxconfig['devmod']
        self.etxconfig = etxconfig
        self.encoding = etxconfig['input_encoding']
        self._etxhash, self._pytext = None, None
        if etxloc :
            self.etxfile = self._locateetx( etxloc, self.directories )
            self.pyfile = self.computepyfile( etxloc, etxconfig )
            self.etxloc, self.noetxfile, self._etxtext = etxloc, False, None
        elif etxtext :
            self._etxtext = \
                etxtext.decode('utf-8') if isinstance(etxtext, str) else etxtext
            self.etxfile = self.NOETXFILE
            self.noetxfile, self.etxloc = True, None
            self.pyfile = None
        else :
            raise Exception( 'Invalid eazytext source !!' )

    def _getetxtext( self ):
        if self._etxtext == None :
            self._etxtext = codecs.open( self.etxfile, encoding=self.encoding ).read()
        return self._etxtext

    def _getpytext( self ):
        if self.devmod :
            return None
        if self.pyfile and isfile(self.pyfile) and self._pytext == None :
            self._pytext = codecs.open( self.pyfile, encoding=self.encoding ).read()
        return self._pytext

    def _setpytext( self, pytext ):
        if self.pyfile :
            d = dirname(self.pyfile)
            os.makedirs(d) if d and not isdir(d) else None
            codecs.open( self.pyfile, mode='w', encoding=self.encoding ).write(pytext)
            return len(pytext)
        return None

    def _getetxhash( self ):
        if self._etxhash == None and self._etxtext :
            enc = self.etxconfig['input_encoding']
            self._etxhash = sha1( self._etxtext.encode(enc) ).hexdigest()
        return self._etxhash

    def _gethashkey( self ):
        usetext = self.etxconfig['text_as_hashkey'] or self.noetxfile
        return self.etxhash if usetext else self.etxfile

    def _locateetx( self, etxloc, dirs ):
        # If etxloc is relative to one of the wiki directories
        files = filter( lambda f : isfile(f), [ join(d, etxloc) for d in dirs ])
        if files : return files[0]

        # If etxloc is provided in asset specification format
        try :
            mod, loc = etxloc.split(':', 1)
            _file, path, _descr = imp.find_module( mod )
            etxfile = join( path.rstrip(os.sep), loc )
            return etxfile
        except :
            return None

        raise Exception( 'Error locating etx file %r' % etxloc )

    def computepyfile( self, etxloc, etxconfig ) :
        """Plainly compute the intermediate file, whether it exists or not is
        immaterial.
        """
        module_directory = etxconfig['module_directory']
        if module_directory == '.' :
            pyfile = join( dirname(etxloc), basename(etxloc)+'.py' 
                     ) if etxloc.startswith(os.sep) else etxloc+'.py'
        elif module_directory :
            etxloc = etxloc[1:] if etxloc.startswith(os.sep) else etxloc
            pyfile = join( module_directory, etxloc+'.py' )
        else :
            pyfile = None
        return pyfile

    etxtext = property( _getetxtext )
    pytext  = property( _getpytext, _setpytext )
    etxhash = property( _getetxhash )
    hashkey = property( _gethashkey )


def supermost( module ):
    """Walk through the module inheritance all the way to the parent most
    module, and return the same
    """
    parmod = module.parent
    while parmod : module, parmod = parmod, parmod.parent
    return module
