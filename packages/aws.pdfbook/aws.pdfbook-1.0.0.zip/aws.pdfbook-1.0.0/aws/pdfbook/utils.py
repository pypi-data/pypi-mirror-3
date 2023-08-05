# -*- coding: utf-8 -*-
# $Id: utils.py 243978 2011-08-31 10:58:00Z thomasdesvenain $
"""Misc utilities"""

from Products.Five.browser import BrowserView
from interfaces import IPDFTransformer
from zope.component import queryMultiAdapter
from zope.publisher.interfaces.browser import IBrowserView
from Products.CMFCore.utils import getToolByName

from aws.pdfbook.interfaces import IPDFOptions

class PDFBookEnabled(BrowserView):

    def __call__(self):
        if 'portal_factory' in self.request.URL:
            return False

        context = self.context
        transformer = queryMultiAdapter((context, self.request), name=u'printlayout')
        portal = getToolByName(context, 'portal_url').getPortalObject()
        options = IPDFOptions(portal)
        return bool(transformer) and (context.portal_type not in options.disallowed_types)
