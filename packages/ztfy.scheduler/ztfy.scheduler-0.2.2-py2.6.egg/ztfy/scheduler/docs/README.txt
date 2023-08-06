======================
ztfy.scheduler package
======================

.. contents::

What is ztfy.scheduler ?
========================

ztfy.scheduler is a base package for those which need to build scheduled tasks which can run:

 - on a cron-style base,
 - at a given date/time (like the "at" command)
 - at a given interval.

Scheduling is done through the APScheduler (http://packages.python.org/APScheduler/) package and
so all these kinds of tasks can be scheduled with the same sets of settings.


How to use ztfy.scheduler ?
===========================

A set of ztfy.scheduler usages are given as doctests in ztfy/scheduler/doctests/README.txt


Known bugs
==========

 - Sometimes, deleting a task doesn't delete the matching job and the whole scheduler have to
   be restarted, generally via a whole server shutdown and restart.
