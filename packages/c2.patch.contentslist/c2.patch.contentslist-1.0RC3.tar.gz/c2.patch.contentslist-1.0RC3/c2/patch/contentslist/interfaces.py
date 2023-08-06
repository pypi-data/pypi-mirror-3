#!/usr/bin/env python
# encoding: utf-8
"""
interfaces.py

Created by Manabu TERADA on 2010-09-25.
Copyright (c) 2010 CMScom. All rights reserved.
"""
from zope.interface import Interface
from zope.schema import Bool, Int, List, TextLine

from c2.patch.contentslist import ContentslistMessageFactory as _


class IContentslistSchema(Interface):
    
    is_order_reverse = Bool(title=_(u'Default order reverse'), default=False,
            description=_(u'Order reverse view on contents tab when create folder, if checked it'))


class IContentslistConfig(IContentslistSchema):
    """"""