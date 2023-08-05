# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

# Gotcha : None
# Notes  : None
# Todo   : None

import datetime     as dt

from   zope.component       import getGlobalSiteManager

from   eazytext.macro       import Macro
from   eazytext.interfaces  import IEazyTextMacro
from   eazytext.lib         import constructstyle

gsm = getGlobalSiteManager()

doc = """
h3. YearsBefore

: Description ::
    Generate a string (based on a template) describing time elapsed since
    the given (day,month,year). The described time is in UTC.
    Accepts CSS styles for keyword arguments.
: Example ::
    [<PRE {{ YearsBefore('past %s', '2008', color="red" ) }} >]
: Selector ::
    The generated span element can be selected (in CSS and JS) using class
    attribute, //etm-yearsbefore//

Positional arguments,
|= template | template string.
|= fromyear | from year

keyword argument,
|= frommonth | from month
|= fromday   | from day
"""

class YearsBefore( Macro ) :
    """Macro plugin to generate dynamic text based on a reference date to
    current date, rendered using a template string.
    """
    _doc = doc
    pluginname = 'YearsBefore'
    tmpl = '<span class="etm-yearsbefore" style="%s">%s</span>'

    def __init__( self, *args, **kwargs ) :
        args = list(args)
        utc = dt.datetime.utcnow()
        self.template  = args.pop(0) if args else 'past %s'
        fromyear = kwargs.get( 'fromyear', 2000 )
        frommonth = kwargs.get( 'frommonth', 1 )
        fromday = kwargs.get( 'fromday', 1 )
        try :
            self.fromyear  = int(fromyear)
            self.frommonth = int(frommonth)
            self.fromday   = int(fromday)
        except :
            self.fromyear  = utc.year
            self.frommonth = utc.month
            self.fromday   = utc.day
        self.style = constructstyle( kwargs )

    def __call__( self, argtext='' ):
        return eval( 'YearsBefore( %s )' % argtext )

    def html( self, node, igen, *args, **kwargs ) :
        utc   = dt.datetime.utcnow()
        date  = dt.datetime( self.fromyear, self.frommonth, self.fromday )
        delta = utc - date
        days  = delta.days
        
        if days > 0 :
            years  = days/365
            months = (days%365) / 30
            years  = '' if years == 0 \
                     else ( '1 year' if years == 1 else '%s years' % years )
            months = '' if months == 0 \
                     else ( '1 month' if months == 1 else '%s months' % months )
            text   = "%s, %s" % ( years, months )
        else :
            text = 'sometime'
        string = self.template % text

        return self.tmpl % (self.style, string)

# Register this plugin
gsm.registerUtility( YearsBefore(), IEazyTextMacro, YearsBefore.pluginname )
