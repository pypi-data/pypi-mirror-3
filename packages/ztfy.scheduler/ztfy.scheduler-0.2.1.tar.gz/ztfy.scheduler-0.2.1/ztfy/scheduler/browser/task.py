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
from z3c.language.switch.interfaces import II18n

# import local interfaces
from ztfy.blog.browser.interfaces.skin import IEditFormButtons
from ztfy.scheduler.browser.interfaces import ITaskAddFormMenuTarget
from ztfy.scheduler.interfaces import ISchedulerTask, ISchedulerCronTaskInfo, ISchedulerDateTaskInfo, ISchedulerLoopTaskInfo

# import Zope3 packages
from z3c.form import field, button
from z3c.formjs import jsaction
from zope.interface import implements
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.blog.browser.skin import BaseAddForm, BaseEditForm
from ztfy.skin.menu import MenuItem

from ztfy.scheduler import _


class BaseTaskAddForm(BaseAddForm):

    implements(ITaskAddFormMenuTarget)

    @property
    def title(self):
        return II18n(self.context).queryAttribute('title', request=self.request)

    legend = _("Adding new scheduler task")

    fields = field.Fields(ISchedulerTask).omit('__parent__', '__name__')

    def add(self, task):
        self.context[task.__class__.__name__] = task

    def nextURL(self):
        return '%s/@@tasks.html' % absoluteURL(self.context, self.request)


class SchedulerTaskEditFormMenu(MenuItem):

    title = _("Connection settings")


class SchedulerTaskEditForm(BaseEditForm):

    title = _("Task properties")
    legend = _("Define task ZEO connection")

    fields = field.Fields(ISchedulerTask).omit('__parent__', '__name__', 'active')
    buttons = button.Buttons(IEditFormButtons)

    @button.handler(buttons['submit'])
    def submit(self, action):
        super(SchedulerTaskEditForm, self).handleApply(self, action)

    def applyChanges(self, data):
        result = super(BaseTaskScheduleForm, self).applyChanges(data)
        if result:
            self.context.reset_connection()
        return result

    @jsaction.handler(buttons['reset'])
    def reset(self, event, selector):
        return '$.ZBlog.form.reset(this.form);'


class TaskScheduleFormMenu(MenuItem):

    title = _("Schedule")


class BaseTaskScheduleForm(BaseEditForm):

    title = _("Schedule selected task")

    buttons = button.Buttons(IEditFormButtons)

    @button.handler(buttons['submit'])
    def submit(self, action):
        super(BaseTaskScheduleForm, self).handleApply(self, action)

    def applyChanges(self, data):
        result = super(BaseTaskScheduleForm, self).applyChanges(data)
        if result:
            self.context.reset()
        return result

    @jsaction.handler(buttons['reset'])
    def reset(self, event, selector):
        return '$.ZBlog.form.reset(this.form);'


class CronTaskScheduleForm(BaseTaskScheduleForm):

    legend = _("Define cron-style task execution times")

    fields = field.Fields(ISchedulerTask).select('active') + \
             field.Fields(ISchedulerCronTaskInfo).omit('__parent__')


class DateTaskScheduleForm(BaseTaskScheduleForm):

    legend = _("Define date-based task execution time")

    fields = field.Fields(ISchedulerTask).select('active') + \
             field.Fields(ISchedulerDateTaskInfo).omit('__parent__')


class LoopTaskScheduleForm(BaseTaskScheduleForm):

    legend = _("Define repeatable task executions")

    fields = field.Fields(ISchedulerTask).select('active') + \
             field.Fields(ISchedulerLoopTaskInfo).omit('__parent__')
