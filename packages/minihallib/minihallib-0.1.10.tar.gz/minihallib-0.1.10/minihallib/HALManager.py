# -*- coding: UTF-8 -*-
# vim: ts=4 sw=4 et:
#
# Copyright (C) 2007 Andy Shevchenko
#
# Licensed under the Academic Free License version 2.1
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""
Core management.
"""

__author__ = "Andy Shevchenko <andy@smile.org.ua>"
__revision__ = "$Id: HALManager.py 28 2007-10-16 13:11:50Z andy $"

__all__ = ['HALManager']

import dbus
import dbus.service
import gobject

dbus_version = getattr(dbus, 'version', (0, 0, 0))
if dbus_version >= (0, 41, 0):
    import dbus.glib
if dbus_version >= (0, 80, 0):
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)

# Start gobject and dbus.glib threads
gobject.threads_init()
dbus.glib.init_threads()

class HALManager:
    def __init__(self):
        self.bus = dbus.SystemBus()
        self.hal_manager_obj = self.bus.get_object('org.freedesktop.Hal', '/org/freedesktop/Hal/Manager')
        self.hal_manager = dbus.Interface(self.hal_manager_obj, 'org.freedesktop.Hal.Manager')

    def get_dev_obj(self, udi):
        return self.bus.get_object('org.freedesktop.Hal', udi)

    def get_dev_if(self, dev_obj, interface='org.freedesktop.Hal.Device'):
        return dbus.Interface(dev_obj, interface)

