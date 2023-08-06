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
from datetime import datetime
import logging
logger = logging.getLogger('ztfy.scheduler')

# import Zope3 interfaces
from zope.component.interfaces import ISite, IComponentRegistry
from zope.container.interfaces import IObjectAddedEvent, IObjectRemovedEvent
from zope.intid.interfaces import IIntIds
from zope.processlifetime import IDatabaseOpenedWithRoot

# import local interfaces
from ztfy.scheduler.interfaces import IScheduledTaskEvent, IUnscheduledTaskEvent, \
                                      ISchedulerLocker, ISchedulerHandler, IScheduler

# import Zope3 packages
from zope.app.publication.zopepublication import ZopePublication
from zope.component import adapter, getUtility, getUtilitiesFor, queryUtility
from zope.container.folder import Folder
from zope.event import notify
from zope.i18n import translate
from zope.interface import implements, alsoProvides, noLongerProvides
from zope.schema.fieldproperty import FieldProperty
from zope.site import hooks
from zope.site.site import SiteManagerContainer
from zope.traversing.api import getParent

# import local packages
from apscheduler.jobstores.ram_store import RAMJobStore
from apscheduler.scheduler import Scheduler as SchedulerBase
from ztfy.i18n.property import I18nTextProperty
from ztfy.security.property import RolePrincipalsProperty
from ztfy.utils.property import cached_property
from ztfy.utils.site import NewSiteManagerEvent

from ztfy.scheduler import _


class SchedulerHandler(object):

    implements(ISchedulerHandler)

    def __init__(self):
        self.schedulers = {}
        self.jobs = {}


@adapter(IScheduledTaskEvent)
def handleScheduledTask(event):
    handler = queryUtility(ISchedulerHandler)
    if handler is None:
        return
    intids = getUtility(IIntIds)
    task = event.object
    id = task.internal_id = intids.register(task)
    handler.jobs[id] = event.job


@adapter(IUnscheduledTaskEvent)
def handleUnscheduledTask(event):
    handler = queryUtility(ISchedulerHandler)
    if handler is None:
        return
    task = event.object
    job = handler.jobs.get(task.internal_id)
    if job is not None:
        scheduler = getParent(task).getScheduler()
        if (scheduler is not None) and (job in scheduler.get_jobs()):
            scheduler.unschedule_job(job)


class Scheduler(Folder, SiteManagerContainer):
    """Scheduler main class"""

    implements(IScheduler)

    title = I18nTextProperty(IScheduler['title'])
    _locker_name = FieldProperty(IScheduler['locker_name'])

    @property
    def locker_name(self):
        return self._locker_name

    @locker_name.setter
    def locker_name(self, value):
        if value != self._locker_name:
            self.stop()
            if self._locker_name is not None:
                locker = queryUtility(ISchedulerLocker, self._locker_name)
                if (locker is not None) and locker.marker_interface.providedBy(self):
                    noLongerProvides(self, locker.marker_interface)
            self._locker_name = value
            if value:
                locker = getUtility(ISchedulerLocker, value)
                alsoProvides(self, locker.marker_interface)
            self.start()

    managers = RolePrincipalsProperty(IScheduler['managers'], role='ztfy.SchedulerManager')
    operators = RolePrincipalsProperty(IScheduler['operators'], role='ztfy.SchedulerOperator')

    @property
    def tasks(self):
        return list(self.values())

    @property
    def history(self):
        result = []
        [ result.extend(task.history) for task in self.tasks ]
        return result

    @cached_property
    def internal_id(self):
        intids = queryUtility(IIntIds)
        if intids is not None:
            return intids.register(self)

    def setSiteManager(self, sm):
        self.stop()
        SiteManagerContainer.setSiteManager(self, sm)
        notify(NewSiteManagerEvent(self))
        IComponentRegistry(self.getSiteManager()).registerUtility(self, IScheduler, '')
        self.start()

    def getScheduler(self):
        handler = queryUtility(ISchedulerHandler)
        if handler is None:
            return None
        int_id = self.internal_id
        if int_id is not None:
            return handler.schedulers.get(int_id)

    def start(self):
        handler = queryUtility(ISchedulerHandler)
        if handler is None:
            return
        scheduler = handler.schedulers.get(self)
        if scheduler is None:
            int_id = self.internal_id
            if int_id is not None:
                scheduler = handler.schedulers[int_id] = SchedulerBase()
                locker = self.getLocker()
                if locker is None:
                    jobsStore = RAMJobStore()
                else:
                    jobsStore = locker.getJobsStore(self)
                    scheduler.add_interval_job(jobsStore.load_jobs, name="Shared jobs checker",
                                               minutes=1, jobstore='default')
                scheduler.add_jobstore(jobsStore, 'scheduler_%d' % int_id)
        else:
            scheduler.shutdown(0)
        if scheduler is not None:
            scheduler.start()
            for task in self.tasks:
                task.schedule()

    def stop(self):
        handler = queryUtility(ISchedulerHandler)
        if handler is None:
            return
        int_id = self.internal_id
        if int_id is not None:
            scheduler = handler.schedulers.get(int_id)
            if scheduler is not None:
                scheduler.shutdown(0)

    def getJobs(self):
        scheduler = self.getScheduler()
        if scheduler is None:
            return (translate(_("No scheduler found !")),)
        return scheduler.get_jobs()

    def getNextRun(self, task):
        handler = queryUtility(ISchedulerHandler)
        if handler is None:
            return None
        job = handler.jobs.get(self.internal_id)
        if job and job.trigger:
            now = datetime.now()
            return job.trigger.get_next_fire_time(now)

    def getLocker(self):
        if not self.locker_name:
            return None
        return queryUtility(ISchedulerLocker, self.locker_name)

    def getLock(self, task=None):
        if not self.locker_name:
            return True
        locker = self.getLocker()
        if locker is not None:
            lock = locker.getLock(self, task)
            if lock is not None:
                return (locker, lock)
        # Don't give lock is selected locker can't be found !!
        return False


@adapter(IScheduler, IObjectAddedEvent)
def handleNewScheduler(scheduler, event):
    scheduler.start()


@adapter(IScheduler, IObjectRemovedEvent)
def handleRemovedScheduler(scheduler, event):
    scheduler.stop()


@adapter(IDatabaseOpenedWithRoot)
def handleOpenedDatabase(event):
    manager = queryUtility(ISchedulerHandler)
    if manager is None:
        return
    db = event.database
    connection = db.open()
    root = connection.root()
    root_folder = root.get(ZopePublication.root_name, None)
    for site in root_folder.values():
        if ISite(site, None) is not None:
            hooks.setSite(site)
            for _name, scheduler in getUtilitiesFor(IScheduler):
                logger.warning("Starting tasks scheduler")
                scheduler.start()


logger.warning("""In a ZEO context, this package must be included only once from a "master" ZEO client,""" +
               """except if you define correct locking mode.""")
