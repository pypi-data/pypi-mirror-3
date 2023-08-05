# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

# Gotcha : none
# Notes  : none
# Todo   : none

from   pygments                        import highlight
from   pygments.formatters             import HtmlFormatter
from   pygments.lexers                 import get_lexer_by_name

from   zope.component                  import getGlobalSiteManager

from   eazytext.extension              import Extension, nowiki2prop
from   eazytext.interfaces             import IEazyTextExtension
from   eazytext.lib                    import constructstyle
import eazytext.extension.ttlpygment

gsm = getGlobalSiteManager()

doc = """
h3. Code

: Description ::
    Syntax highlighting for code-snippet. Highlighting is available for
    [[ http://pygments.org/docs/lexers/ | several-dozen formats ]].
    Property key-value pairs accepts CSS styling attributes.

'' Example ''

> [<PRE {{{ Code C
>   struct process {
>     struct process *next;
>     const char *name;
>     PT_THREAD((* thread)(struct pt *, process_event_t, process_data_t));
>     struct pt pt;
>     unsigned char state;
>   };
> }}} >]

{{{ Code C
struct process {
  struct process *next;
  const char *name;
  PT_THREAD((* thread)(struct pt *, process_event_t, process_data_t));
  struct pt pt;
  unsigned char state;
};
}}}

To highlight a different syntax, supply the syntax name as a parameter like,
> [<PRE {{{ Code <syntax-name> >]

To disable line numbers while highlighting add parameter 'noln'. The default
is to list the line numbers.
> [<PRE {{{ Code <syntax-name> nonl >]
"""


class Code( Extension ) :
    """Extension plugin for syntax highlighting code-blocks. For highlighting, the
    plugin uses pygments library, hence a large collection of text-types can
    be highlighted, http://pygments.org/languages/
    """

    tmpl       = '<div class="etext-code" style="%s"> %s </div>'
    style_tmpl = '<style type="text/css"> %s </style>'
    code_tmpl  = '<div class="codecont"> %s </div>'
    pluginname = 'Code'

    def __init__( self, *args ):
        self.lexname = args and args[0].lower() or 'text'
        self.linenos = 'noln' not in args
        self.formatter = HtmlFormatter( linenos=self.linenos )

    def __call__( self, argtext='' ):
        parts   = argtext.split(',')
        lexname = parts.pop(0) if parts else 'text'
        linenos = parts.pop(0) if parts else ''
        return eval( 'Code( %r, %r )' % (lexname, linenos) )

    def headpass1( self, node, igen ):
        ctx = node.parser.etparser.ctx
        if hasattr(ctx, 'ext_code_stylehtml_done') : return

        style = self.formatter.get_style_defs('.highlight')
        self.stylehtml = self.style_tmpl % style
        ctx.ext_code_stylehtml_done = True
        igen.puttext( self.stylehtml )

    def html( self , node, igen, *args, **kwargs ):
        style, text = nowiki2prop( node.text )
        try :
            lexer = get_lexer_by_name( self.lexname )
            code  = highlight( text.strip('\r\n'), lexer, self.formatter )
            html  = self.tmpl % ( '', (self.code_tmpl % code) )
        except:
            raise
            if node.parser.etparser.debug : raise
            html = text
        return html

# Register this plugin
gsm.registerUtility( Code(), IEazyTextExtension, Code.pluginname )
Code._doc = doc
