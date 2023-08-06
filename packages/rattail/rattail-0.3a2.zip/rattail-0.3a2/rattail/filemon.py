#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
``rattail.filemon`` -- Windows File Monitor
"""

import sys
import subprocess

from edbob.filemon import win32_server


class FileMonitorService(win32_server.FileMonitorService):
    """
    Implements the Rattail file monitor Windows service.
    """

    _svc_name_ = "Rattail File Monitor"
    _svc_display_name_ = "Rattail : File Monitoring Service"

    appname = 'rattail'


def exec_server_command(command):
    """
    Executes ``command`` against the file monitor Windows service, i.e. one of:

    * ``'install'``
    * ``'start'``
    * ``'stop'``
    * ``'remove'``
    """
    subprocess.call([sys.executable, __file__, command])


if __name__ == '__main__':
    import win32serviceutil
    win32serviceutil.HandleCommandLine(FileMonitorService)
