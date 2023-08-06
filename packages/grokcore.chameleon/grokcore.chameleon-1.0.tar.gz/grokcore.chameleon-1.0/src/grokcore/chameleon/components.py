##############################################################################
#
# Copyright (c) 2006-2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Chameleon page template components"""

import os
import sys
import martian

from grokcore.component import GlobalUtility, implements, name
from grokcore.view import interfaces
from grokcore.view.components import GrokTemplate
import zope.i18n
from chameleon.zpt.template import PageTemplate, PageTemplateFile
from chameleon.tales import PythonExpr
from chameleon.tales import StringExpr
from chameleon.tales import NotExpr
from chameleon.tales import ExistsExpr
from chameleon.tales import ImportExpr
from chameleon.tales import StructureExpr
from z3c.pt.expressions import PathExpr, ProviderExpr


#
# Chameleon Zope Page Templates...
#
class PageTemplate(PageTemplate, GrokTemplate):
    """A `z3c.pt` page template suitable for use with views.

    This page template implementation is different from `z3c.pt`
    implementation in two respects:

    - It sets ``python`` as default mode (instead of ``path``)
    - It injects any views ``static`` variable in template namespace.
    """
    default_expression = 'python'  # Use the chameleon default

    expression_types = {
        'python': PythonExpr,
        'string': StringExpr,
        'not': NotExpr,
        'path': PathExpr,
        'provider': ProviderExpr,
        'exists': ExistsExpr,
        'import': ImportExpr,
        'structure': StructureExpr,
        }


class PageTemplateFile(PageTemplate, PageTemplateFile):
    """A `z3c.pt` page template file suitable for use with views.

    This implementation is different from `z3c.pt` implementation in
    two respects:

    - It sets ``python`` as default mode (instead of ``path``)
    - It injects any views ``static`` variable in template namespace.
    """
    default_expression = 'python'


class ChameleonPageTemplate(GrokTemplate):

    def setFromString(self, string):
        self._filename = None
        self._template = PageTemplate(string)

    def setFromFilename(self, filename, _prefix=None):
        self._filename = filename
        self._prefix = _prefix
        self._template = PageTemplateFile(os.path.join(_prefix, filename))
        return

    @property
    def macros(self):
        return self._template.macros

    def render(self, view):
        context = self.getNamespace(view)

        if 'target_language' not in context:
            try:
                target_language = zope.i18n.negotiate(context['request'])
            except:
                target_language = None
            context['target_language'] = target_language

        return self._template(**context)

class ChameleonPageTemplateFile(ChameleonPageTemplate):

    def __init__(self, filename, _prefix=None):
        self.__grok_module__ = martian.util.caller_module()
        if _prefix is None:
            module = sys.modules[self.__grok_module__]
            _prefix = os.path.dirname(module.__file__)
        self.setFromFilename(filename, _prefix)


class ChameleonPageTemplateFactory(GlobalUtility):
    implements(interfaces.ITemplateFileFactory)
    name('cpt')

    def __call__(self, filename, _prefix=None):
        return ChameleonPageTemplate(filename=filename, _prefix=_prefix)
