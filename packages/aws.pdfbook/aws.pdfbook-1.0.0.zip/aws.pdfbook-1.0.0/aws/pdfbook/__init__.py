# -*- coding: utf-8 -*-
# $Id: __init__.py 116190 2010-04-26 20:36:44Z glenfant $
"""aws.pdfbook component for Plone"""

import logging
from Products.CMFCore import utils

from config import PROJECTNAME

logger = logging.getLogger(PROJECTNAME)
from zope.i18nmessageid import MessageFactory
translate = MessageFactory(PROJECTNAME)
