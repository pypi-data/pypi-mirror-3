### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.scheduler.browser.interfaces import ITaskAddFormMenuTarget, ITaskActiveColumn, ITaskNextRunColumn
from ztfy.scheduler.interfaces import IScheduler

# import Zope3 packages
from z3c.table.column import Column, FormatterColumn
from zope.i18n import translate
from zope.interface import implements
from zope.traversing.api import getParent

# import local packages
from ztfy.blog.browser.container import ContainerBaseView
from ztfy.skin.form import DisplayForm
from ztfy.skin.menu import MenuItem
from ztfy.utils.security import unproxied

from ztfy.scheduler import _


class SchedulerTasksViewMenu(MenuItem):
    """Scheduler tasks view menu"""

    title = _("Tasks")


class TaskActiveColumn(Column):

    implements(ITaskActiveColumn)

    header = _("Active ?")
    weight = 50

    def renderCell(self, item):
        if item.active:
            return translate(_("Yes"), context=self.request)
        else:
            return translate(_("No"), context=self.request)


class TaskNextRunColumn(FormatterColumn, Column):

    implements(ITaskNextRunColumn)

    header = _("Next run")
    weight = 60

    formatterCategory = u'dateTime'
    formatterLength = u'short'

    def renderCell(self, item):
        scheduler = getParent(item)
        next = scheduler.getNextRun(item)
        if next:
            return self.getFormatter().format(next)
        return translate(_('N/A'), context=self.request)


class SchedulerTasksView(ContainerBaseView):
    """Scheduler tasks view"""

    implements(ITaskAddFormMenuTarget)

    legend = _("Scheduler's tasks")

    @property
    def values(self):
        return IScheduler(self.context).tasks


class SchedulerJobsViewMenu(MenuItem):
    """Scheduler jobs view menu"""

    title = _("Jobs")


class SchedulerJobsView(DisplayForm):
    """Scheduler jobs view"""

    title = _("Scheduler jobs")
    legend = _("List of currently scheduled jobs")

    @property
    def jobs(self):
        return unproxied(self.context.get_jobs())
