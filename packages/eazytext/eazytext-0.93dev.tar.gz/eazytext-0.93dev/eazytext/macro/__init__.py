# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

"""
h3. EazyText Macro framework

Macros are direct function calls that can be made from wiki text into the wiki
engine, provided, there is a macro by that name available. Most probably the
macro will return a html content, which will be used to replace the macro
call. More specifically the macro call will be directly evaluated as python
code and thus follows all the function calling rules and conventions of
python. 

To expound it further, let us take a specific example of ''YearsBefore''
macro, which computes the time elapsed from a given (month,day,year) and
composes a string like "2 years 2 months before",

Definition of YearsBefore macro,
> [<PRE YearsBefore( template, fromyear=2008, frommonth=1, fromday=1, **kwargs ) >]

''A small primer on python function calls'',
* Arguments to python functions are of two types, positional and keyword. Other
  types of argument passing are not of concern here.
* Position arguments are specified first in a function call, where the first
  passed parameter is recieved as the first argument, second passed parameter
  is recieved as the second argument and so on. All positional parameters
  are mandatory.
* Keyword arguments are received next. Keyword arguments also carry a
  default value, if in case it is not passed.

With this in mind, we will try to decipher ''YearsBefore'' macro

* ''YearsBefore'', is the name of the macro function.
* ''template'', is the first mandatory positional argument providing the
  template of output string.
* ''fromyear'', is the second mandatory positional argument, specifying the
  year.
* ''frommonth'', is optional keyword argument, specifying the month.
* ''fromday'', is option keyword argument, specifying the day.
* ''kwargs'', most of the macro functions have this last arguments to accept a
  variable number of keyword arguments. One use case for this is to
  pass styling attributes.

Use case,
> [<PRE started this activity and running this for \
  {{ YearsBefore('past %s', fromyear='2008') }} >]

> started this activity and running this for {{ YearsBefore('past %s',
  fromyear='2008') }}

=== Styling paramters

To get the desired CSS styling for the element returned by macro, pass in the styling
attributes as keyword arguments, like,

> [<PRE started this activity and running this for 
  {{ YearsBefore('past %s', '2008', color="red" ) }} >]

> started this activity and running this for 
> {{ YearsBefore('past %s', '2008', color="red" ) }}

Note that, the attribute name is represented as local variable name inside the
macro function. If you are expert CSS author, you will know that there are
CSS-style attribute-names like ''font-size'', ''font-weight'' which are not
valid variables, so, style attribute-names which contain a ''hypen''
cannot be passed as a keyword argument. As an alternative, there is a special
keyword argument (to all macro functions) by name ''style'', which directly
accepts ''semicolon (;)'' seperated style attributes, like,

> [<PRE started this activity and running this for 
   {{ YearsBefore('past %s', '2008', color="red", style="font-weight: bold; font-size: 200%" ) }} >]

> started this activity and running this for 
> {{ YearsBefore('past %s', '2008', color="red", style="font-weight: bold; font-size: 200%" ) }}
"""

from   zope.interface       import implements

from   eazytext.interfaces  import IEazyTextMacro

class Macro( object ):
    """Base class from with macro-plugin implementers must derive from."""
    implements( IEazyTextMacro )

    def __init__( self, *args, **kwargs ):
        pass

    def __call__( self, argtext='' ):
        return eval( 'Macro( %s )' % argtext )

    def onparse( self, node ):
        pass

    def headpass1( self, node, igen ):
        pass

    def headpass2( self, node, igen ):
        pass

    def generate( self, node, igen, *args, **kwargs ) :
        html = self.html( node, igen, *args, **kwargs )
        html and igen.puttext( html )

    def tailpass( self, node, igen ):
        pass

    def html( self, node, igen, *args, **kwargs ):
        """Can be overriden by the deriving class to provide the translated html
        that will be substituted in the place of the macro() calls.
        """
        return ''
