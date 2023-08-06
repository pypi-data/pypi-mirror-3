#!/usr/bin/env python
# encoding: utf-8
"""
config.py

Created by Manabu TERADA on 2010-09-25.
Copyright (c) 2010 CMScom. All rights reserved.
"""

from persistent import Persistent
from zope.interface import implements
from c2.patch.contentslist.interfaces import IContentslistConfig

class ContentslistConfig(Persistent):
    """ utility to hold the configuration related to Contents list """
    implements(IContentslistConfig)

    def __init__(self):
        self.is_order_reverse = False

    def getId(self):
        """ return a unique id to be used with GenericSetup """
        return 'contentslist_config'