# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from sphinxcontrib.infrae.buildout import BuildoutLexer
from sphinxcontrib.infrae.autointerface import setup as autointerface_setup

def setup(app):
    autointerface_setup(app)
    app.add_lexer('buildout', BuildoutLexer())

