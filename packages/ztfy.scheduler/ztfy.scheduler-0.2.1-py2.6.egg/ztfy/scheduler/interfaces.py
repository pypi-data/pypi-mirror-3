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
from zope.component.interfaces import IObjectEvent
from zope.container.interfaces import IContainer

# import local interfaces

# import Zope3 packages
from zope.container.constraints import containers, contains
from zope.interface import Interface, Attribute
from zope.schema import TextLine, Bool, Int, List, Datetime

# import local packages

from ztfy.scheduler import _


class IScheduledTaskEvent(IObjectEvent):
    """Interface for events notified when a task is scheduled"""

    job = Attribute(_("Event job"))


class IUnscheduledTaskEvent(IObjectEvent):
    """Interface for events notified when a task is unscheduled"""


class ISchedulerTask(Interface):
    """Base interface for scheduler jobs"""

    containers('ztfy.scheduler.interfaces.IScheduler')

    active = Bool(title=_("Active task"),
                  description=_("You can disable a task by selectin 'No'"),
                  required=True,
                  default=False)

    server_name = TextLine(title=_("ZEO server name"),
                           description=_("Hostname of ZEO server"),
                           required=True,
                           default=u'localhost')

    server_port = Int(title=_("ZEO server port"),
                      description=_("Port number of ZEO server"),
                      required=True,
                      default=8100)

    server_storage = TextLine(title=_("ZEO server storage"),
                              description=_("Storage name on ZEO server"),
                              required=True,
                              default=u'1')

    internal_id = Attribute(_("Internal ID"))

    def schedule():
        """Schedule job execution"""

    def connect():
        """Open ZEO connection"""

    def get_root(db=None):
        """Get ZEO database root"""

    def run(db, root, site):
        """Launch job execution"""


class ISchedulerTaskWriter(Interface):
    """Scheduler jobs writer interface"""

    def reset():
        """Re-schedule job execution"""

    def reset_connection():
        """Reset job ZEO connection"""


class ISchedulerCronTaskInfo(Interface):
    """Base interface for cron-style scheduled tasks"""

    year = TextLine(title=_("Years"),
                    description=_("Years for which to schedule the job"),
                    required=False,
                    default=u'*')

    month = TextLine(title=_("Months"),
                     description=_("Months (1-12) for which to schedule the job"),
                     required=False,
                     default=u'*')

    day = TextLine(title=_("Month days"),
                   description=_("Days (1-31) for which to schedule the job"),
                   required=False,
                   default=u'*')

    week = TextLine(title=_("Weeks"),
                    description=_("Year weeks (1-53) for which to schedule the job"),
                    required=False,
                    default=u'*')

    day_of_week = TextLine(title=_("Week days"),
                           description=_("Week days (0-6, with 0 as monday) for which to schedule the job"),
                           required=False,
                           default=u'*')

    hour = TextLine(title=_("Hours"),
                    description=_("Hours (0-23) for which to schedule the job"),
                    required=False,
                    default=u'*')

    minute = TextLine(title=_("Minutes"),
                      description=_("Minutes (0-59) for which to schedule the job"),
                      required=False,
                      default=u'*')

    second = TextLine(title=_("Seconds"),
                      description=_("Seconds (0-59) for which to schedule the job"),
                      required=False,
                      default=u'0')


class ISchedulerCronTask(ISchedulerTask, ISchedulerCronTaskInfo, ISchedulerTaskWriter):
    """Interface for cron-style scheduled tasks"""


class ISchedulerDateTaskInfo(Interface):
    """Base interface for date-based scheduled tasks"""

    start_date = Datetime(title=_("First execution date"),
                          description=_("Date from which scheduling should start"),
                          required=False)


class ISchedulerDateTask(ISchedulerTask, ISchedulerDateTaskInfo, ISchedulerTaskWriter):
    """Interface for date-based scheduled tasks"""


class ISchedulerLoopTaskInfo(ISchedulerDateTaskInfo):
    """Base interface for interval-based scheduled tasks"""

    repeat = Int(title=_("Number of iterations"),
                 description=_("Number of times the job will be executed ; set to 0 for infinite execution"),
                 required=True,
                 default=0)

    weeks = Int(title=_("Weeks interval"),
                description=_("Number of weeks between executions"),
                required=True,
                default=0)

    days = Int(title=_("Days interval"),
                description=_("Number of days between executions"),
                required=True,
                default=0)

    hours = Int(title=_("Hours interval"),
                description=_("Number of hours between executions"),
                required=True,
                default=0)

    minutes = Int(title=_("Minutes interval"),
                description=_("Number of minutes between executions"),
                required=True,
                default=0)

    seconds = Int(title=_("Seconds interval"),
                description=_("Number of seconds between executions"),
                required=True,
                default=0)


class ISchedulerLoopTask(ISchedulerTask, ISchedulerLoopTaskInfo, ISchedulerTaskWriter):
    """Interface for interval-based scheduled tasks"""


class ISchedulerHandler(Interface):
    """Scheduler management marker interface"""


class IScheduler(IContainer):
    """Tasks manager interface"""

    contains(ISchedulerTask)

    tasks = List(title=_("Scheduler tasks"),
                 description=_("List of tasks assigned to this scheduler"),
                 required=False)

    def getScheduler():
        """Retrieve effective tasks scheduler"""

    def start():
        """Start scheduler"""

    def stop():
        """Stop scheduler execution"""

    def get_jobs():
        """Get text output of running jobs"""

    def getNextRun(task):
        """Get next execution time of given task"""
