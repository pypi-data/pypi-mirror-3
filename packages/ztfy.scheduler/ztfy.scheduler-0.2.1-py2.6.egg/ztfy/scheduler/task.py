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
import logging
logger = logging.getLogger('ztfy.scheduler')

from persistent import Persistent

# import Zope3 interfaces
from zope.container.interfaces import IObjectRemovedEvent
from zope.location.interfaces import ILocation, ISite

# import local interfaces
from ztfy.scheduler.interfaces import *

# import Zope3 packages
from ZEO import ClientStorage
from ZODB import DB
from zope.app.publication.zopepublication import ZopePublication
from zope.component import adapter
from zope.component.interfaces import ObjectEvent
from zope.event import notify
from zope.interface import implements
from zope.location import locate
from zope.schema import getFields, getFieldNames
from zope.schema.fieldproperty import FieldProperty
from zope.site import hooks
from zope.traversing import api as traversing_api

# import local packages
from ztfy.utils.traversing import getParent

from ztfy.scheduler import _


class ScheduledTaskEvent(ObjectEvent):

    implements(IScheduledTaskEvent)

    def __init__(self, object, job):
        self.object = object
        self.job = job


class UnscheduledTaskEvent(ObjectEvent):

    implements(IUnscheduledTaskEvent)


class BaseTask(Persistent):
    """Base jobs management class"""

    implements(ILocation)

    active = FieldProperty(ISchedulerTask['active'])
    server_name = FieldProperty(ISchedulerTask['server_name'])
    server_port = FieldProperty(ISchedulerTask['server_port'])
    server_storage = FieldProperty(ISchedulerTask['server_storage'])
    internal_id = None

    def __init__(self):
        self.__parent__ = self.__name__ = None

    @property
    def runnable(self):
        return self.active

    def schedule(self):
        raise NotImplementedError, _("The 'schedule' method must be implemented by BaseTask subclasses")

    def reset(self):
        self.schedule()

    def connect(self):
        self._v_storage = getattr(self, '_v_storage', None) or ClientStorage.ClientStorage((str(self.server_name), self.server_port),
                                                                                           storage=self.server_storage,
                                                                                           wait=False)
        self._v_db = getattr(self, '_v_db', None) or DB(self._v_storage)
        return self._v_db

    def reset_connection(self):
        if hasattr(self, '_v_conn'):
            delattr(self, '_v_conn')
        if hasattr(self, '_v_db'):
            self._v_db.close()
            delattr(self, '_v_db')
        if hasattr(self, '_v_storage'):
            delattr(self, '_v_storage')

    def get_root(self, db=None):
        if db is None:
            db = self.connect()
        self._v_conn = getattr(self, '_v_conn', None) or db.open()
        return self._v_conn.root()[ZopePublication.root_name]

    def __call__(self):
        logger.info("Starting task %s" % traversing_api.getName(self))
        try:
            self._run()
        except:
            logger.exception("An error during execution of task %s" % traversing_api.getName(self))
        else:
            logger.info("Task %s finished without error" % traversing_api.getName(self))

    def _run(self):
        root = self.get_root()
        try:
            task = traversing_api.traverse(root, traversing_api.getPath(self))
            site = getParent(task, ISite)
            hooks.setSite(site)
            if task.runnable:
                task.run(self._v_db, root, site)
        except:
            logger.exception(_("Can't execute scheduled job %r") % self)

    def run(self, db, root, site):
        raise NotImplementedError, _("The 'run' method must be implemented by BaseTask subclasses")


class CronTask(BaseTask):
    """Cron-style task class"""

    implements(ISchedulerCronTask)

    schema = ISchedulerCronTaskInfo

    year = FieldProperty(ISchedulerCronTask['year'])
    month = FieldProperty(ISchedulerCronTask['month'])
    day = FieldProperty(ISchedulerCronTask['day'])
    week = FieldProperty(ISchedulerCronTask['week'])
    day_of_week = FieldProperty(ISchedulerCronTask['day_of_week'])
    hour = FieldProperty(ISchedulerCronTask['hour'])
    minute = FieldProperty(ISchedulerCronTask['minute'])
    second = FieldProperty(ISchedulerCronTask['second'])

    def schedule(self):
        scheduler = traversing_api.getParent(self).getScheduler()
        if scheduler is None:
            return
        notify(UnscheduledTaskEvent(self))
        active = False
        if self.active:
            fields = getFields(ISchedulerCronTaskInfo)
            for name in getFieldNames(ISchedulerCronTaskInfo):
                if getattr(self, name) != fields[name].default:
                    active = True
                    break
        if active:
            job = scheduler.add_cron_job(self,
                                         year=self.year or u'*',
                                         month=self.month or u'*',
                                         day=self.day or u'*',
                                         week=self.week or u'*',
                                         day_of_week=self.day_of_week or u'*',
                                         hour=self.hour or u'*',
                                         minute=self.minute or u'*',
                                         second=self.second or u'0')
            locate(job, scheduler)
            notify(ScheduledTaskEvent(self, job))


class DateTask(BaseTask):
    """Date-style task class"""

    implements(ISchedulerDateTask)

    schema = ISchedulerDateTaskInfo

    start_date = FieldProperty(ISchedulerDateTask['start_date'])

    def schedule(self):
        scheduler = traversing_api.getParent(self).getScheduler()
        if scheduler is None:
            return
        notify(UnscheduledTaskEvent(self))
        if self.active:
            job = scheduler.add_date_job(self, date=self.start_date)
            locate(job, scheduler)
            notify(ScheduledTaskEvent(self, job))


class LoopTask(DateTask):
    """Interval-based task class"""

    implements(ISchedulerLoopTask)

    schema = ISchedulerLoopTaskInfo

    repeat = FieldProperty(ISchedulerLoopTask['repeat'])
    weeks = FieldProperty(ISchedulerLoopTask['weeks'])
    days = FieldProperty(ISchedulerLoopTask['days'])
    hours = FieldProperty(ISchedulerLoopTask['hours'])
    minutes = FieldProperty(ISchedulerLoopTask['minutes'])
    seconds = FieldProperty(ISchedulerLoopTask['seconds'])

    def schedule(self):
        scheduler = traversing_api.getParent(self).getScheduler()
        if scheduler is None:
            return
        notify(UnscheduledTaskEvent(self))
        if self.active:
            job = scheduler.add_interval_job(self,
                                             start_date=self.start_date,
                                             weeks=self.weeks,
                                             days=self.days,
                                             hours=self.hours,
                                             minutes=self.minutes,
                                             seconds=self.seconds)
            locate(job, scheduler)
            notify(ScheduledTaskEvent(self, job))


@adapter(ISchedulerTask, IObjectRemovedEvent)
def handleRemovedTask(task, event):
    notify(UnscheduledTaskEvent(task))
