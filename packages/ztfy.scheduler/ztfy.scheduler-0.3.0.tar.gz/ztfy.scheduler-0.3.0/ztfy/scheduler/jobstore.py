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
import logging
logger = logging.getLogger('ztfy.scheduler')
import os

from datetime import datetime

# import Zope3 interfaces
from zope.intid.interfaces import IIntIds

# import local interfaces
from ztfy.scheduler.interfaces import ISchedulerMemcachedLockerInfo

# import Zope3 packages
from lovely.memcached.interfaces import IMemcachedClient
from zope.component import getUtility, queryUtility
from zope.component.interfaces import ISite
from zope.site import hooks

# import local packages
from apscheduler.job import Job
from apscheduler.jobstores.base import JobStore
from apscheduler.jobstores.shelve_store import ShelveJobStore as BaseShelveJobStore
from apscheduler.util import itervalues
from ztfy.utils.property import cached_property
from ztfy.utils.traversing import getParent


class ShelveJobStore(BaseShelveJobStore):
    """Shelve job store, modified to store persistent tasks"""

    def __init__(self, scheduler, path):
        super(ShelveJobStore, self).__init__(path)
        self.scheduler = scheduler
        self._timestamp = None

    @property
    def timestamp(self):
        stat = os.stat(self.path)
        return stat.st_mtime

    @property
    def job_ids(self):
        return [job.id for job in self.jobs]

    def add_job(self, job):
        job_id = str(job.name)
        if job_id in self.job_ids:
            return
        job.id = job_id
        self.jobs.append(job)
        self.store[job.id] = { 'id': job.id,
                               'runs': job.runs,
                               'next_run_time': job.next_run_time }
        self.store.sync()
        self._timestamp = self.timestamp

    def update_job(self, job):
        if self.store.has_key[job.id]:
            job_dict = self.store[job.id]
        else:
            job_dict = { 'id': job.id }
        job_dict['next_run_time'] = job.next_run_time
        job_dict['runs'] = job.runs
        self.store[job.id] = job_dict
        self.store.sync()
        self._timestamp = self.timestamp

    def remove_job(self, job):
        BaseShelveJobStore.remove_job(self, job)
        self.store.sync()
        self._timestamp = self.timestamp

    def load_jobs(self):
        if self._timestamp == self.timestamp:
            return
        logger.info("Data updated, reloading jobs states from shelve database...")
        jobs = []
        old_site = hooks.getSite()
        site = getParent(self.scheduler, ISite)
        try:
            hooks.setSite(site)
            intids = getUtility(IIntIds)
            for job_dict in itervalues(self.store):
                try:
                    _name, task_id = job_dict['id'].split('::')
                    task = intids.queryObject(int(task_id))
                    if task is not None:
                        task = task.getRealTask(task.getRoot())
                        info = task.getSchedulingInfo()
                        trigger = task.getTrigger()
                        job = Job(trigger, task, args=[], kwargs={}, misfire_grace_time=1, coalesce=True,
                                  name=job_dict['id'], max_runs=info.max_runs, max_instances=1)
                        job.id = job_dict['id']
                        job.runs = job_dict['runs']
                        job.next_run_time = trigger.get_next_fire_time(start_date=datetime.now())
                        jobs.append(job)
                except Exception:
                    logger.exception('Unable to restore job "%s"', job_dict['id'])
        finally:
            hooks.setSite(old_site)
            self.jobs = jobs
            self._timestamp = self.timestamp



_ts_marker = object()

class MemcachedJobStore(JobStore):
    """Memcached job store, used to store persistent tasks in Memcached
    
    Memcached jobstore uses several entries:
     - one entry for each job
     - one entry to set the job ids list
    To reduce conflicts between schedulers, each key also contains scheduler internal ID
    """

    def __init__(self, scheduler):
        info = ISchedulerMemcachedLockerInfo(scheduler, None)
        assert info is not None
        self.scheduler = scheduler
        self.internal_id = scheduler.internal_id
        self.namespace = info.locks_namespace
        self.jobs = []
        self.memcached = queryUtility(IMemcachedClient, info.memcached_client)
        self._timestamp = None

    @cached_property
    def timestamp_key(self):
        return '%s::timestamp' % self.internal_id

    @property
    def timestamp(self):
        return self.memcached.query(self.timestamp_key, _ts_marker, ns=self.namespace)

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value
        if self.memcached is not None:
            self.memcached.set(value, self.timestamp_key, ns=self.namespace)

    @cached_property
    def jobs_key(self):
        return '%d::jobs' % self.internal_id

    def job_key(self, job):
        if isinstance(job, (str, unicode)):
            job_id = job
        else:
            job_id = job.id
        return '%d::%s' % (self.internal_id, job_id)

    @property
    def job_ids(self):
        return [job.id for job in self.jobs]

    def add_job(self, job):
        job_id = str(job.name)
        if job_id in self.job_ids:
            return
        job.id = job_id
        self.jobs.append(job)
        self.update_job(job)
        # set memcached jobs list
        if self.memcached is not None:
            key = self.jobs_key
            jobs = self.memcached.query(key, ns=self.namespace)
            if jobs is None:
                jobs = set()
            jobs.add(job.id)
            self.memcached.set(jobs, key, ns=self.namespace, lifetime=0)
        self.timestamp = datetime.utcnow()

    def update_job(self, job):
        if self.memcached is not None:
            key = self.job_key(job)
            job_dict = self.memcached.query(key, {}, ns=self.namespace)
            job_dict['id'] = job.id
            job_dict['runs'] = job.runs
            job_dict['next_run_time'] = job.next_run_time
            self.memcached.set(job_dict, key, ns=self.namespace, lifetime=0)
        self.timestamp = datetime.utcnow()

    def remove_job(self, job):
        if self.memcached is not None:
            # remove job entry
            key = self.job_key(job)
            self.memcached.invalidate(key, ns=self.namespace)
            # remove job id from jobs list
            key = self.jobs_key
            jobs = self.memcached.query(key, ns=self.namespace)
            if jobs is None:
                jobs = set()
            if job.id in jobs:
                jobs.remove(job.id)
            self.memcached.set(jobs, key, ns=self.namespace, lifetime=0)
        self.jobs.remove(job)
        self.timestamp = datetime.utcnow()

    def load_jobs(self):
        if self._timestamp == self.timestamp:
            return
        logger.info("Data updated, reloading jobs states from memcached server...")
        jobs = []
        old_site = hooks.getSite()
        site = getParent(self.scheduler, ISite)
        try:
            hooks.setSite(site)
            if self.memcached is not None:
                intids = getUtility(IIntIds)
                key = self.jobs_key
                for job_id in self.memcached.query(key, (), ns=self.namespace):
                    try:
                        key = self.job_key(job_id)
                        job_dict = self.memcached.query(key, None, ns=self.namespace)
                        if job_dict is not None:
                            _name, task_id = job_dict['id'].split('::')
                            task = intids.queryObject(int(task_id))
                            if task is not None:
                                task = task.getRealTask()
                                info = task.getSchedulingInfo()
                                trigger = task.getTrigger()
                                job = Job(trigger, task, args=[], kwargs={}, misfire_grace_time=1, coalesce=True,
                                          name=job_dict['id'], max_runs=info.max_runs, max_instances=1)
                                job.id = job_dict['id']
                                job.runs = job_dict['runs']
                                job.next_run_time = trigger.get_next_fire_time(start_date=datetime.now())
                                jobs.append(job)
                    except Exception:
                        logger.exception('Unable to restore job "%s"', job_id)
        finally:
            hooks.setSite(old_site)
            self.jobs = jobs
            self._timestamp = self.timestamp

    def close(self):
        pass

    def __repr__(self):
        return '<%s (%s)>' % (self.__class__.__name__, self.namespace)
