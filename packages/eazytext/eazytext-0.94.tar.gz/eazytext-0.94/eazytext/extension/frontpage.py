# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

# Gotcha : none
# Notes  : none
# Todo   : none

from   zope.component                  import getGlobalSiteManager

from   eazytext.extension              import Extension, nowiki2prop
from   eazytext.interfaces             import IEazyTextExtension
from   eazytext.utils                  import constructstyle

gsm = getGlobalSiteManager()

doc = """
h3. Frontpage

: Description ::
    Extension handler to translate meta information about wiki document into
    a front-page section for the document. Groups a collection of meta
    information like title, author, links and description about rest of the wiki
    document into separate <section>. Text is expected in a semi-structured
    format, which is a collection of key,value pairs separated by a '':''. A
    fresh key,value pair must begin with a new line flush with whitespace. If a
    new line begins with whitespace will either be ignored or interpreted as
    part of the previous key,value definition.

* Key name will be wrapped with a //<div>// element with class attribute
  ``{y}key``. The //<div>// element will also contain the key value in its
  data attribute ``{y}data-key``.
* Value will be wrapped with //<div>// element with class attribute ``{y}val``
* Each key,value pair (and its //<div>// wrapping) will be a encapsulated inside
  another //<div>// element with class attribute ``{y}info``
* All key,value pair encapsulated inside another //<div>// element with class
  attribute ``{y}fontpage``
* Finally the whole block will be encapsulated inside a <section> element
  with class attribute "etext-frontpage"
* EazyText formatting is accepted for value, in key,value pairs.

'' Example ''

> [<PRE {{{ Frontpage
> # { 'border' : '1px dashed gray', }
>
> Title : Alice in wonderland
> Author : [[ http://en.wikipedia.org/wiki/Lewis_Carroll | Lewis carroll ]]
> Description : Alice's Adventures in Wonderland (commonly shortened to Alice
>    in Wonderland) is an 1865 novel written by English author Charles Lutwidge
>    Dodgson under the pseudonym Lewis Carroll.[1] It tells of a girl named
>    Alice who falls down a rabbit hole into a fantasy world (Wonderland)
>    populated by peculiar, anthropomorphic creatures.
> 
> }}} >]

{{{ Frontpage
# { 'border' : '1px dashed gray', }

Title : Alice in wonderland
Author : [[ http://en.wikipedia.org/wiki/Lewis_Carroll | Lewis carroll ]]
Description : Alice's Adventures in Wonderland (commonly shortened to Alice
    in Wonderland) is an 1865 novel written by English author Charles Lutwidge
    Dodgson under the pseudonym Lewis Carroll.[1] It tells of a girl named
    Alice who falls down a rabbit hole into a fantasy world (Wonderland)
    populated by peculiar, anthropomorphic creatures.
 
}}}

"""


class Frontpage( Extension ) :
    """Extension handler to translate meta information about wiki document into
    a front-page section for the document.
    """
    tmpl       = '<section class="etext-frontpage" %s> %s </section>'
    tmpl_div   = '<div class="frontpage"> %s </div>'
    tmpl_k     = '<div class="key" data-key="%s"> %s </div>'
    tmpl_v     = '<div class="val"> %s </div>'
    tmpl_kv    = '<div class="info"> %s </div>'
    pluginname = 'Frontpage'
    etxconfig = {
        'nested' : True,
        'nested.article' : False,
        'nested.paragraph' : False,
        'include_skin' : False,
    }

    def __init__( self, *args ):
        pass

    def __call__( self, argtext='' ):
        return eval( 'Frontpage()' )

    def _parsekeyval( self, info, res ):
        try :
            key, value = info.split(':', 1)
            res.append((key.strip(' \t'), value.strip(' \t')))
        except : pass
        return 

    def _parseinfolines( self, text ):
        info = []
        res = []
        for l in text.splitlines() :
            if not l :
                continue
            elif l[0] in ' \t' and info :
                info.append( l.strip(' \t') )
                continue
            elif l[0] in ' \t' :
                continue
            elif info :
                self._parsekeyval( ' '.join(info), res )
                info = [l]
                continue
            info = [l]
        info and self._parsekeyval( ' '.join(info), res )
        return res

    def html( self , node, igen, *args, **kwargs ):
        from   eazytext import Translate
        style, text = nowiki2prop( node.text )
        style = style and 'style="%s"' % style
        etxconfig = dict( node.parser.etparser.etxconfig.items() )
        etxconfig.update( self.etxconfig )
        infos = self._parseinfolines( text )
        html = []
        for key, val in infos :
            t = Translate( etxtext=val, etxconfig=etxconfig )
            keyhtml = self.tmpl_k % (key, key)
            valhtml = self.tmpl_v % t( context={} )
            html.append( self.tmpl_kv % '\n'.join( [ keyhtml, valhtml ]) )
        divhtml = self.tmpl_div % '\n'.join(html)
        html = self.tmpl % ( style, divhtml )
        return html

# Register this plugin
gsm.registerUtility( Frontpage(), IEazyTextExtension, Frontpage.pluginname )
Frontpage._doc = doc
