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
from persistent.interfaces import IPersistent
from transaction.interfaces import ITransactionManager
from ZODB.interfaces import IConnection
from zope.app.appsetup.interfaces import IDatabaseOpenedWithRootEvent
from zope.component.interfaces import ISite
from zope.container.interfaces import IObjectAddedEvent, IObjectRemovedEvent
from zope.intid.interfaces import IIntIds

# import local interfaces
from ztfy.scheduler.interfaces import IScheduledTaskEvent, IUnscheduledTaskEvent
from ztfy.scheduler.interfaces import ISchedulerHandler, IScheduler, ISchedulerTask

# import Zope3 packages
from zope.site import hooks
from zope.app.folder.folder import Folder
from zope.app.publication.zopepublication import ZopePublication
from zope.component import adapter, getUtility, getUtilitiesFor, queryUtility
from zope.interface import implements, implementer
from zope.traversing.api import getParent

# import local packages
from apscheduler.scheduler import Scheduler as SchedulerBase

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
    id = task.internal_id = intids.queryId(task)
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


class Scheduler(Folder):

    implements(IScheduler)

    @property
    def tasks(self):
        return [t for t in self.values() if ISchedulerTask.providedBy(t)]

    def getScheduler(self):
        handler = queryUtility(ISchedulerHandler)
        if handler is None:
            return None
        intids = getUtility(IIntIds)
        return handler.schedulers.get(intids.queryId(self))

    def start(self):
        handler = queryUtility(ISchedulerHandler)
        if handler is None:
            return
        scheduler = handler.schedulers.get(self)
        if scheduler is None:
            intids = getUtility(IIntIds)
            scheduler = handler.schedulers[intids.register(self)] = SchedulerBase()
        else:
            scheduler.shutdown(0)
        scheduler.start()
        for task in self.tasks:
            task.schedule()

    def stop(self):
        handler = queryUtility(ISchedulerHandler)
        if handler is None:
            return
        intids = getUtility(IIntIds)
        scheduler = handler.schedulers.get(intids.queryId(self))
        if scheduler is not None:
            scheduler.shutdown(0)

    def get_jobs(self):
        scheduler = self.getScheduler()
        if scheduler is None:
            return _("No scheduler found !")
        return scheduler.get_jobs()

    def getNextRun(self, task):
        handler = queryUtility(ISchedulerHandler)
        if handler is None:
            return None
        intids = getUtility(IIntIds)
        job = handler.jobs.get(intids.queryId(task))
        if job and job.trigger:
            now = datetime.now()
            return job.trigger.get_next_fire_time(now)


@adapter(IScheduler, IObjectAddedEvent)
def handleNewScheduler(scheduler, event):
    scheduler.start()


@adapter(IScheduler, IObjectRemovedEvent)
def handleRemovedScheduler(scheduler, event):
    scheduler.stop()


@adapter(IDatabaseOpenedWithRootEvent)
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


# IPersistent adapters copied from zc.twist package
# also register this for adapting from IConnection
@adapter(IPersistent)
@implementer(ITransactionManager)
def transactionManager(obj):
    conn = IConnection(obj) # typically this will be
                            # zope.app.keyreference.persistent.connectionOfPersistent
    try:
        return conn.transaction_manager
    except AttributeError:
        return conn._txn_mgr
        # or else we give up; who knows.  transaction_manager is the more
        # recent spelling.


logger.warning("""In a ZEO context, this package must be included only once from a "master" ZEO client""")
