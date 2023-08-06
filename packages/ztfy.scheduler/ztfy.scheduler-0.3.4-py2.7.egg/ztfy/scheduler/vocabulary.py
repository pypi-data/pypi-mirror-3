### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT ulthar.net>
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


# import standard packages

# import Zope3 interfaces
from zope.schema.interfaces import IVocabularyFactory

# import local interfaces
from ztfy.scheduler.interfaces import ISchedulerLocker, ISchedulerTaskSchedulingMode

# import Zope3 packages
from lovely.memcached.interfaces import IMemcachedClient
from zope.componentvocabulary.vocabulary import UtilityVocabulary
from zope.interface import classProvides

# import local packages


class SchedulerLockersVocabulary(UtilityVocabulary):
    """Scheduler lock modes vocabulary"""

    classProvides(IVocabularyFactory)

    interface = ISchedulerLocker
    nameOnly = True


class SchedulerTaskSchedulingModesVocabulary(UtilityVocabulary):
    """Scheduler tasks scheduling modes vocabulary"""

    classProvides(IVocabularyFactory)

    interface = ISchedulerTaskSchedulingMode
    nameOnly = True


class MemcachedClientsVocabulary(UtilityVocabulary):
    """Memcached clients vocabulary"""

    classProvides(IVocabularyFactory)

    interface = IMemcachedClient
    nameOnly = True
