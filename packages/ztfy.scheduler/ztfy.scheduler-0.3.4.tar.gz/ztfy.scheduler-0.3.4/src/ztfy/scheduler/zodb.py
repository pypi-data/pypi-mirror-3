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
from ztfy.scheduler.interfaces import IZODBPackingTask

# import Zope3 packages
from ZEO import ClientStorage
from ZODB import DB
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.scheduler.task import BaseTask


class ZODBPackingTask(BaseTask):
    """ZODB packing task"""

    implements(IZODBPackingTask)

    zeo_server_name = FieldProperty(IZODBPackingTask['zeo_server_name'])
    zeo_server_port = FieldProperty(IZODBPackingTask['zeo_server_port'])
    zeo_server_storage = FieldProperty(IZODBPackingTask['zeo_server_storage'])
    zeo_username = FieldProperty(IZODBPackingTask['zeo_username'])
    zeo_password = FieldProperty(IZODBPackingTask['zeo_password'])
    zeo_realm = FieldProperty(IZODBPackingTask['zeo_realm'])
    pack_time = FieldProperty(IZODBPackingTask['pack_time'])

    def run(self, db, root, site, report):
        zeo_server_name = self.zeo_server_name or self.server_name
        zeo_server_port = self.zeo_server_port or self.server_port
        zeo_server_storage = self.zeo_server_storage or self.server_storage
        report.write("Server name = %s:%d\n" % (zeo_server_name, zeo_server_port))
        report.write("Server storage = %s\n" % zeo_server_storage)
        report.write("Packed transactions older than %d days\n" % self.pack_time)
        storage = ClientStorage.ClientStorage((str(zeo_server_name), zeo_server_port),
                                              storage=zeo_server_storage,
                                              username=self.zeo_username or '',
                                              password=self.zeo_password or '',
                                              realm=self.zeo_realm,
                                              wait=False)
        target_db = DB(storage)
        target_db.pack(days=self.pack_time)
        report.write('\nPack successful !\n')
