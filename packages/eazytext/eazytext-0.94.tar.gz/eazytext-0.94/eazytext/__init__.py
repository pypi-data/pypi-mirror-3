# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

__version__ = '0.94'

import codecs, sys
from   os.path                  import dirname, basename, join
from   copy                     import deepcopy
from   datetime                 import datetime as dt
from   paste.util.converters    import asbool

from   zope.component           import getGlobalSiteManager
import pkg_resources            as pkg

from   eazytext.utils           import ConfigDict

# Import macro-plugins so that they can register themselves.
import eazytext.macro
import eazytext.macro.anchor
import eazytext.macro.clear
import eazytext.macro.html
import eazytext.macro.image
import eazytext.macro.images
import eazytext.macro.redirect
import eazytext.macro.span
import eazytext.macro.toc
import eazytext.macro.yearsbefore
# Import extension-plugins so that they can register themselves.
import eazytext.extension
import eazytext.extension.code
import eazytext.extension.nested
import eazytext.extension.frontpage

from   eazytext.interfaces      import IEazyTextMacro, \
                                       IEazyTextTemplateTags, \
                                       IEazyTextExtension
from   eazytext.parser          import ETParser

DEFAULT_ENCODING = 'utf-8'
DEVMOD = False

defaultconfig = ConfigDict()
defaultconfig.__doc__ = u"""Configuration setting for eazytext wiki engine."""

defaultconfig['strict_undefined']    = {
    'default' : False,
    'types'   : (bool,),
    'help'    : "Boolean to raise exception for undefined context variables. "
                "If set to false, undefined variables will be silently "
                "digested as 'None' string."
}

defaultconfig['directories']                   = {
    'default' : '.',
    'types'   : ('csv', list),
    'help'    : "List of directories to look for the .etx file"
}

defaultconfig['module_directory']              = {
    'default' : None,
    'types'   : (str,),
    'help'    : "path to store the compiled .py file (intermediate file)"
}

defaultconfig['escape_filters']                = {
    'default' : '',
    'types'   : ('csv', list),
    'help'    : "Comma separated list of default escape filters to be "
                "applied during expression substitution."
}

defaultconfig['input_encoding']                = {
    'default' : 'utf-8',
    'types'   : (str,),
    'help'    : "Default input encoding for .etx file."
}

defaultconfig['plugin_packages']               = {
    'default' : '',
    'types'   : ('csv',list),
    'help'    : "Comma separated list of plugin packages that needs to be "
                "imported, before compiling .etx files."
}

defaultconfig['skinfile']                      = {
    'default' : 'default.css',
    'types'   : (str,),
    'help'    : "Default skin file to include translated html file, use this "
                "option along with `include_skin`."
}

defaultconfig['include_skin']                  = {
    'default' : False,
    'types'   : (bool,),
    'help'    : "CSS file (skin) can be either included in the generated html "
                "or can be linked separately (using <link> tag)."
}

defaultconfig['obfuscatemail']                 = {
    'default' : False,
    'types'   : (bool,),
    'help'    : "If set to true, the email-id generated using [[ mailto:... ]] "
                "markup will be obfuscated."
}

defaultconfig['nested']                        = {
    'default' : False,
    'types'   : (bool,),
    'help'    : "Denotes that the parser is invoked by a parent parser, may "
                "be because of a plugin"
}

defaultconfig['nested.paragraph']              = {
    'default' : True,
    'types'   : (bool,),
    'help'    : "Boolean, if True generate <p> wrapping for text paragraphs. "
                "Otherwise skip <p> wrapping for text paragraphs."
}

defaultconfig['nested.article']                = {
    'default' : True,
    'types'   : (bool,),
    'help'    : "Boolean, if True generate <article> wrapping for html text. "
                "Otherwise skip <article> wrapping for block text. The "
                "generated article element will have class attribute `etblk` "
                "if config parameter `nested` is True. Otherwise, they will have "
                "class attribute `etpage`."
}

defaultconfig['stripscript']                   = {
    'default' : True,
    'types'   : (bool,),
    'help'    : "Do not allow any <script> tag in the finally generated HTML "
                "text."
}

defaultconfig['ashtml']                        = {
    'default' : False,
    'types'   : (bool,),
    'help'    : "If set to true generate html text enclosed within "
                "<html><body> tags, else wrap them with just <article> tag."
}

defaultconfig['memcache']                      = {
    'default' : True,
    'types'   : (bool,),
    'help'    : "In memory cache for compiled intermediate file (.py file)"
}

defaultconfig['text_as_hashkey']               = {
    'default' : False,
    'types'   : (bool,),
    'help'    : "Use input text to generate the tag-key for memcache."
}


def normalizeconfig( config ):
    """Convert the string representation of config parameters into
    programmable types. It is assumed that all config parameters are atleast
    initialized with default value.
    """
    config_ = dict( defaultconfig.items() )
    config_.update( config )
    config = config_
    config['devmod'] = asbool( config.get('devmod', DEVMOD) )
    config['strict_undefined'] = asbool( config['strict_undefined'] )
    try :
        config['directories'] = [
            x.strip() for x in config['directories'].split(',') if x.strip()
        ]
    except :
        pass
    config['module_directory'] = config['module_directory'] or None
    try :
        config['escape_filters'] = [
            x.strip() for x in config['escape_filters'].split(',') if x.strip()
        ]
    except :
        pass
    try :
        config['plugin_packages'] = [
            x.strip() for x in config['plugin_packages'].split(',') if x.strip()
        ]
    except :
        pass

    booleans = [
        'include_skin', 'obfuscatemail', 'nested', 'nested.paragraph',
        'stripscript',  'ashtml', 'memcache', 'text_as_hashkey'
    ]
    for x in booleans : config[x] = asbool( config[x] )

    return config


macroplugins = {}           # { plugin-name : instance }
extplugins   = {}           # { plugin-name : instance }
ttplugins    = {}           # { plugin-name : instance }
init_status  = 'pending'
def initplugins( etxconfig, force=False ):
    """Load the following plugin-types,
        * template-plugins  (IEazyTextTemplateTags),
        * macro-plugins     (IEazyTextMacro),
        * extension-plugins (IEazyTextExtension)
    """
    global init_status, macroplugins, extplugins, ttplugins
    if init_status == 'progress' :
        return etxconfig

    if (force == True) or etxconfig.get( 'macroplugins', None ) == None :
        # Load and classify plugins
        init_status = 'progress'
        gsm = getGlobalSiteManager()

        # Load plugin packages
        packages = etxconfig.get( 'plugin_packages', [] )
        if isinstance( packages, basestring ):
            packages = [ x.strip(' \t') for x in packages.split(',') ]
        [ __import__(pkg) for pkg in filter(None, packages) ]

        # Gather plugins template tag handlers, filter-blocks
        for x in gsm.registeredUtilities() :
            if x.provided == IEazyTextMacro:        # macro-plugins
                macroplugins[x.name] = x.component
            elif x.provided == IEazyTextExtension:    # extension-plugins
                extplugins[x.name] = x.component
            elif x.provided == IEazyTextTemplateTags :        # tt-plugins
                ttplugins[x.name] = x.component
            else :
                continue
            if not hasattr( x.component, 'pluginname' ) :
                raise Exception( 'Plugins should have the attribute `pluginname`' )
            etxconfig['macroplugins'] = macroplugins
            etxconfig['extplugins'] = extplugins
            etxconfig['ttplugins'] = ttplugins

        init_status = 'done'
    return etxconfig


#---- APIs for executing Eazytext wiki markup

class Translate( object ):
    def __init__( self, etxloc=None, etxtext=None, etxconfig={} ):
        """`etxconfig` parameter will find its way into every object defined
        by wiki processor.
            TODO : somehow find a way to pass the arguments to `body` function
        """
        self.etxconfig = dict( defaultconfig.items() )
        self.etxconfig.update( etxconfig )
        self.etxconfig.setdefault( 'devmod', DEVMOD )
        # Initialize plugins
        self.etxconfig = initplugins(
                self.etxconfig, force=self.etxconfig['devmod'] )
        self.etxloc, self.etxtext = etxloc, etxtext
        self.etparser = ETParser( etxconfig=self.etxconfig )

    def __call__( self, entryfn='body', context={} ):
        from   eazytext.compiler import Compiler
        self.compiler = Compiler( etxtext=self.etxtext,
                                  etxloc=self.etxloc,
                                  etxconfig=self.etxconfig,
                                  etparser=self.etparser
                                )
        context['_etxcontext'] = context
        module = self.compiler.execetx( context=context )
        entry = getattr( module, entryfn )
        html = entry() if callable( entry ) else ''
        return html

def etx_cmdline( etxloc, **kwargs ):
    from eazytext.compiler import Compiler

    htmlfile  = kwargs.get( 'ofile', '' )
    etxconfig = dict(defaultconfig.items())
    # directories, module_directory, devmod
    etxconfig.update( kwargs )
    etxconfig['module_directory'] = u'.'
    etxconfig['include_skin'] = True
    etxconfig['ashtml'] = True

    # Parse command line arguments and configuration
    context = eval( etxconfig.pop( 'context', '{}' ))
    debuglevel = etxconfig.pop( 'debuglevel', 0 )
    show = etxconfig.pop( 'show', False )
    dump = etxconfig.pop( 'dump', False )
    encoding = etxconfig['input_encoding']

    # Initialize plugins)
    etxconfig.setdefault( 'devmod', DEVMOD )
    etxconfig = initplugins( etxconfig, force=etxconfig['devmod'] )

    # Setup parser
    etparser = ETParser( etxconfig=etxconfig, debug=debuglevel )
    compiler = Compiler( etxloc=etxloc, etxconfig=etxconfig, etparser=etparser )
    pyfile = compiler.etxfile+'.py'
    if not htmlfile :
        htmlfile = basename( compiler.etxfile ).rsplit('.', 1)[0] + '.html'
        htmlfile = join( dirname(compiler.etxfile), htmlfile )

    if debuglevel :
        print "AST tree ..."
        tu = compiler.toast()
    elif show :
        print "AST tree ..."
        tu = compiler.toast()
        tu.show()
    elif dump :
        from  eazytext.ast import Context
        tu = compiler.toast()
        rctext =  tu.dump( Context() )
        text = codecs.open( compiler.etxfile, encoding=encoding ).read()
        if rctext[:-1] != text :
            print "Mismatch ..."
            sys.exit(1)
        else : print "Success ..."
    else :
        print "Generating py / html file ... "
        pytext = compiler.topy( etxhash=compiler.etxlookup.etxhash )
        # Intermediate file should always be encoded in 'utf-8'
        codecs.open(pyfile, mode='w', encoding=DEFAULT_ENCODING).write(pytext)

        t = Translate( etxloc=etxloc, etxconfig=etxconfig )
        html = t( context=deepcopy(context) )
        codecs.open( htmlfile, mode='w', encoding=encoding).write( html )

        # This is for measuring performance
        st = dt.now()
        [ Translate( etxloc=etxloc, etxconfig=etxconfig )( context=deepcopy(context) )
          for i in range(2)]
