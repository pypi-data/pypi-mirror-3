# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

"""
h3. An introduction to multi-pass compilation implemented on the AST

Once the //abstract-syntax-tree// (AST) is constructed, the tree will be walked
multiple times by calling the methods headpass1(), headpass2(), generate()
and tailpass() on each node and all of its child nodes. Interface
specifications //IEazyTextTemplateTags//, //IEazyTextExtension// and
//IEazyTextMacro// will provide the entry points for the implementing plugin.

"""

from   zope.interface   import Interface

class IEazyText( Interface ):
    """Base class for all //eazytext module's// interface specifications. Right
    now following interface specs. derive from this base class,
      > IEazyTextMacro
      > IEazyTextExtension
      > IEazyTextTemplateTags
    """


class IEazyTextMacro( IEazyText ) :
    """Interface specification for eazytext's macro-plugin. All methods defined
    by this specification will accept a parameter //node// which contain
    following attributes,
      *  ''node.parser''            PLY Yacc parser
      *  ''node.macrotext''         Raw macro text between \{{ ... \}}
      *  ''node.parser.etparser''   ETParser() object

    where `etparser` has following useful attributes,
      *  ''etparser.ctx''         Context for AST construction.
      *  ''etparser.etxconfig''   Configuration parameters
      *  ''etparser.tu''          Translation Unit for the parsed text
      *  ''etparser.text''        Raw wiki text.
      *  ''etparser.pptext''      Preprocessed wiki text.
      *  ''etparser.html''        Converted HTML code from Wiki text

    # If any of the specified method receives //igen// as a parameter, it can be
      used to directly generate stack machine instruction.
    # If \__call\__ method is defined by plugin-component, it will be used to
      create a new clone of the plugin-component passing in wiki-markup's
      argument text. As a general thumb-rule, implement \__call\__ method using
      keyword-arguments.
    """
    
    def __call__( argtext ) :
        """Return an clone of plugin-component using macro markup's arguments,
        //argtext//.
        """

    def onparse( node ):
        """Method will be invoked after parsing the text and while instantiating
        the AST node corresponding to the macro, multi-pass compilation starts
        after instantiating the AST node. If this method returns a
        string, it will be assumed as html and prefixed to the wikipage.
        """

    def headpass1( node, igen ):
        """Method will be invoked during //headpass1// phase, which is the first
        phase in multi-pass compilation. //igen// object can be used to directly generate
        the stack machine instruction. //node// is the AST's NonTerminal node
        representing the macro.
        """

    def headpass2( node, igen ):
        """Method will be invoked during //headpass2// phase, which happens
        after //headpass1//. //igen// object can be used to directly generate
        the stack machine instruction. //node// is the AST's NonTerminal node
        representing the macro.
        """

    def generate( node, igen, *args, **kwargs ):
        """Method will be Invoked during //generate// phase, which happens after
        //onparse//, //headpass1//, and //headpass2//. //igen// object can be
        used to directly generate the stack machine instruction. //node// is
        the AST's NonTerminal node representing the macro.
        """

    def tailpass( node, igen ):
        """Method will be invoked during //tailpass// phase, which happens after 
        //generate//. //igen// object can be used to directly generate the stack
        machine instruction. //node// is the AST's NonTerminal node
        representing the macro.
        """


class IEazyTextExtension( IEazyText ) :
    """Interface specification for eazytext's extension-plugin.
    All methods defined by this specification will accept a parameter //node//
    which contain following attributes,
      *  ''node.parser''          PLY Yacc parser
      *  ''node.text''            Raw extension text between {{{ ... }}}
      *  ''node.parser.etparser'' ETParser() object

    where `etparser` has following useful attributes,
      *  ''etparser.etxconfig'' Configuration parameters
      *  ''etparser.tu''        Translation Unit for the parsed text
      *  ''etparser.text''      Raw wiki text.
      *  ''etparser.pptext''    Preprocessed wiki text.
      *  ''etparser.html''      Converted HTML code from Wiki text

    # If any of the specified method receives //igen// as a parameter, it can be
      used to directly generate stack machine instruction.
    # If \__call\__ method is defined by plugin-component, it will be used to
      create a new clone of the plugin-component passing in wiki-markup's
      argument text.  As a general thumb-rule, implement \__call\__ method using
      keyword-arguments.
    """
    
    def __call__( argtext ) :
        """Return an clone of plugin-component using extension markup's
        arguments, //argtext//.
        """

    def onparse( node ):
        """Method will be invoked after parsing the text and while instantiating
        the AST node corresponding to the extension, multi-pass compilation
        starts after instantiating the AST node. If this method returns a
        string, it will be assumed as html and prefixed to the wikipage.
        """

    def headpass1( node, igen ):
        """Method will be invoked during //headpass1// phase, which is the first
        phase in multi-pass compilation. //igen// object can be used to directly
        generate the stack machine instruction. //node// is the AST's
        NonTerminal node representing the extension-block.
        """

    def headpass2( node, igen ):
        """Method will be invoked during //headpass2// phase, which happens
        after //headpass1//. //igen// object can be used to directly generate
        the stack machine instruction. //node// is the AST's NonTerminal node
        representing the extension-block.
        """

    def generate( node, igen, *args, **kwargs ):
        """Method will be invoked during //generate// phase, which happens after
        //onparse//, //headpass1//, //headpass2//. //igen// object can be used
        to directly generate the stack machine instruction. //node// is the
        AST's NonTerminal node representing the extension-block.
        """

    def tailpass( node, igen ):
        """Method will be invoked during //tailpass// phase, which happens after
        //generate//.  //igen// object can be used to directly generate
        the stack machine instruction. //node// is the AST's NonTerminal node
        representing the extension-block.
        """


class IEazyTextTemplateTags( IEazyText ) :
    """Interface speficiation for eazytext's templated-tags plugin. All methods
    defined by this specification will accept a parameter //node// which
    contain following attributes,
      *  ''node.parser''          PLY Yacc parser
      *  ''node.htmltext''        Raw text between \[< ... \>]
      *  ''node.parser.etparser'' ETParser() object

    where `etparser` has following useful attributes,
      *  ''etparser.etxconfig'' Configuration parameters
      *  ''etparser.tu''        Translation Unit for the parsed text
      *  ''etparser.text''      Raw wiki text.
      *  ''etparser.pptext''    Preprocessed wiki text.
      *  ''etparser.html''      Converted HTML code from Wiki text

    # If any of the specified method receives //igen// as a parameter, it can be
      used to directly generate stack machine instruction.
    # If \__call\__ method is defined by plugin-component, it will be used to
      create a new clone of the plugin-component passing in wiki-markup's
      arguments.  As a general thumb-rule, implement \__call\__ method using
      keyword-arguments.
    """

    def onparse( node ):
        """Method will be invoked after parsing the text and while instantiating
        the AST node corresponding to the template-tag, multi-pass compilation
        starts after instantiating the AST node. If this method returns a
        string, it will be assumed as html and prefixed to the wikipage.
        """

    def headpass1( node, igen ):
        """Method will be invoked during //headpass1// phase, which is the first
        phase in multi-pass compilation. //igen// object can be used to directly
        generate the stack machine instruction. //node// is the AST's
        NonTerminal node representing the template-tag.
        """

    def headpass2( node, igen ):
        """Method will be invoked during //headpass2// phase, which happens
        after //headpass1//. //igen// object can be used to directly generate
        the stack machine instruction. //node// is the AST's NonTerminal node
        representing the template-tag.
        """

    def generate( node, igen, *args, **kwargs ):
        """Method will be invoked during //generate// phase, which happens after
        //onparse//, //headpass1//, //headpass2//. //igen// object can be used
        to directly generate the stack machine instruction. //node// is the
        AST's NonTerminal node representing the template-tag.
        """

    def tailpass( node, igen ):
        """Method will be invoked during //tailpass// phase, which happens after
        //generate//.  //igen// object can be used to directly generate
        the stack machine instruction. //node// is the AST's NonTerminal node
        representing the template-tag.
        """
