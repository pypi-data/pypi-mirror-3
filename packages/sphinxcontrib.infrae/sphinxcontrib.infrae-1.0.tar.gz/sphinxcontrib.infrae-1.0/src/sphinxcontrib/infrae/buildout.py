# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from pygments.lexer import RegexLexer, bygroups
from pygments.token import Text, Comment, Name, String, Operator

__all__ = ['BuildoutLexer']

class BuildoutLexer(RegexLexer):
    """Lexer for zc.buildout configuration files.
    """
    name = 'BUILDOUT'
    aliases = ['buildout']
    filenames = ['*.cfg']
    mimetypes = ['text/x-buildout']

    tokens = {
        'root': [
            (r'[;#].*?$', Comment),
            (r'(\[)(.*?)(\])$',
             bygroups(Operator.Word, Name.Namespace, Operator.Word)),
            (r'(<=)(.+)$',
             bygroups(Operator.Word, Name.Namespace)),
            (r'(\S+)([ \t]*)([-+]?=)([ \t]*)',
             bygroups(Name.Property, Text, Operator.Word, Text), ('section', 'option')),
            ],
        'section': [
            (r'(\[)(.*?)(\])\n',
             bygroups(Operator.Word, Name.Namespace, Operator.Word), '#pop'),
            (r'(<=)(.+)\n',
             bygroups(Operator.Word, Name.Namespace)),
            (r'([ \t]*)[;#].*?\n', Comment),
            (r'([ \t]+)',
             bygroups(Text), 'option'),
            (r'(\S+)([ \t]*)([-+]?=)([ \t]*)',
             bygroups(Name.Property, Text, Operator.Word, Text), 'option'),
            (r'\n', Text, '#pop')
            ],
        'option': [
            (r'[^$\n]+', String),
            (r'\$\{', Operator.Word, 'variable'),
            (r'\n', String, '#pop'),
            ],
        'variable': [
            (r'\}', Operator.Word, '#pop'),
            (r'([^:]*)(:)([^}]*)',
             bygroups(Name.Namespace, Operator.Word, Name.Property)),
            ]
    }

