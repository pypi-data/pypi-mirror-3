#!/usr/bin/env python
# encoding: utf-8
"""
configlet.py

Created by Manabu TERADA on 2010-09-25.
Copyright (c) 2010 CMScom. All rights reserved.
"""
from zope.component import adapts, queryUtility
from zope.component import getMultiAdapter
from zope.formlib.form import FormFields
from zope.interface import implements
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.app.controlpanel.form import ControlPanelForm
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.utils import getToolByName

from c2.patch.contentslist.interfaces import IContentslistSchema
from c2.patch.contentslist.interfaces import IContentslistConfig
from c2.patch.contentslist import ContentslistMessageFactory as _


class ContentslistControlPanelAdapter(SchemaAdapterBase):
    adapts(IPloneSiteRoot)
    implements(IContentslistSchema)

    def getIsOrderReverse(self):
        util = queryUtility(IContentslistConfig)
        return getattr(util, 'is_order_reverse', u"")

    def setIsOrderReverse(self, value):
        util = queryUtility(IContentslistConfig)
        if util is not None:
            util.is_order_reverse = value

    is_order_reverse = property(getIsOrderReverse, setIsOrderReverse)


class ContentslistControlPanel(ControlPanelForm):

    form_fields = FormFields(IContentslistSchema)

    label = _(u'Contents list settings')
    description = _(u'')
    form_name = _('Contentslist settings')

