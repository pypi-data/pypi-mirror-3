#!/usr/bin/env python
# encoding: utf-8
"""
extender.py

Created by Manabu TERADA on 2010-09-21.
Copyright (c) 2010 CMScom. All rights reserved.
"""
from Products.Archetypes.atapi import BooleanField
from Products.Archetypes.atapi import BooleanWidget
from archetypes.schemaextender.field import ExtensionField
from zope.component import adapts
from zope.component import queryUtility
from zope.interface import implements
from Products.ATContentTypes.interface import IATFolder

from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from c2.patch.contentslist import ContentslistMessageFactory as _
from c2.patch.contentslist.interfaces import IContentslistConfig

class C2BooleanField(ExtensionField, BooleanField):
    """ """

class ContentsListExtender(object):
    adapts(IATFolder)
    implements(IOrderableSchemaExtender)
    
    fields = [
        C2BooleanField('is_listing_reverse',
            #required = False,
            languageIndependent = True,
            schemata = 'settings',
            # default = True,
            widget = BooleanWidget(
                description=_(u'help_is_listing_reverse', default=u'This enables reverse viewing on contents tab in this folder.'),
                label = _(u'label_is_listing_reverse', default=u'Enable reverse viewing'),
                visible={'view' : 'hidden',
                         'edit' : 'visible'},
                ),
            ),
    ]
    
    def __init__(self, context):
        self.context = context
        config = queryUtility(IContentslistConfig)
        is_order_reverse = getattr(config, 'is_order_reverse', False)
        self.fields[0].default = is_order_reverse

    def getFields(self):
        return self.fields

    def getOrder(self, original):
        """
        """
        return original