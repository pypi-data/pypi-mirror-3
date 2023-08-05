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
Capability based plugin implementation for HAL handler.
"""

__author__ = "Andy Shevchenko <andy@smile.org.ua>"
__revision__ = "$Id: HALPlugin.py 16 2007-10-02 14:35:57Z andy $"

__all__ = ['HALPlugin']

import dbus

from minihallib.HALDevice import HALDevice

def udi_add_signal_receiver(bus, udi, name, call_back):
    bus.add_signal_receiver(call_back, name, 'org.freedesktop.Hal.Device', 'org.freedesktop.Hal', udi)

def udi_remove_signal_receiver(bus, udi, name, call_back):
    bus.remove_signal_receiver(call_back, name, 'org.freedesktop.Hal.Device', 'org.freedesktop.Hal', udi)

def make_hal_device(bus, udi, property_modified_cb=None):
    """ Make HALDevice object with 'PropertyModified' callback """
    dev_obj = bus.get_object('org.freedesktop.Hal', udi)
    hal_device = HALDevice(dev_obj, property_modified_cb)
    parent_udi = hal_device.get('info.parent')
    try:
        parent_obj = bus.get_object('org.freedesktop.Hal', parent_udi)
    except TypeError:
        parent_obj = None
    hal_device.set_parent(parent_obj)
    udi_add_signal_receiver(bus, udi, 'PropertyModified', hal_device.property_modified)
    return hal_device

class HALPlugin:
    """ Common HALEventer plugin """
    def __init__(self, bus, hal_manager, capability, property_modified_cb=None):
        self.__bus = bus
        self.__hal_manager = hal_manager
        self.__capability = capability
        self.property_modified_cb = property_modified_cb
        self.__devices = {}

    def add(self, udi):
        """ Add single device by its udi """
        dev_obj = self.__bus.get_object('org.freedesktop.Hal', udi)
        dev_if = dbus.Interface(dev_obj, 'org.freedesktop.Hal.Device')
        if dev_if.QueryCapability(self.__capability):
            self.__devices[udi] = make_hal_device(self.__bus, udi, self.property_modified_cb)
            return True
        return False

    def remove(self, udi, remove_cb=None):
        """ Remove single device by its udi """
        if self.__devices.has_key(udi):
            udi_remove_signal_receiver(self.__bus, udi, 'PropertyModified', self.__devices[udi].property_modified)
            if remove_cb is not None:
                remove_cb(self.__capability, udi)
            del self.__devices[udi]
            return True
        return False

    def fill(self):
        """ Fill devices list by current connected devices """
        for udi in self.__hal_manager.FindDeviceByCapability(self.__capability):
            self.__devices[udi] = make_hal_device(self.__bus, udi, self.property_modified_cb)

    def clear(self):
        """ Clear devices list """
        self.__devices.clear()

    def keys(self):
        """ Return list of connected devices """
        return self.__devices.keys()

    def get(self, udi, result=None):
        """ Get device by its udi """
        return self.__devices.get(udi, result)

