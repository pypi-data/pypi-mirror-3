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
lspci, lsusb and similar tools implementation based on HAL.
"""

__author__ = "Andy Shevchenko <andy@smile.org.ua>"
__revision__ = "$Id: ListBus.py 33 2007-10-19 16:11:36Z andy $"

__all__ = ['ListBus']

from minihallib.HALManager import HALManager
from minihallib.HALDevice import HALDevice

class ListBus(HALManager):
    """ Emulate system's lspci, lsusb amd similar tools """
    def __init__(self):
        HALManager.__init__(self)
        self.__devices = {}

    def clear(self, bus=None):
        if bus is None:
            self.__devices = {}
        elif self.__devices.has_key(bus):
            del self.__devices[bus]
        else:
            return False
        return True

    def fill(self, bus):
        if bus is None:
            return False

        self.__devices[bus] = {}

        for udi in self.hal_manager.GetAllDevices():
            dev_obj = self.get_dev_obj(udi)
            dev_if = self.get_dev_if(dev_obj)
            if dev_if.PropertyExists('info.bus') and dev_if.GetProperty('info.bus') == bus:
                self.__devices[bus][udi] = HALDevice(dev_obj, None)

        return True

    def refresh(self, bus):
        if bus is None:
            return False

        self.clear(bus)
        return self.fill(bus)

    def get(self, udi, result=None):
        for bus in self.__devices.keys():
            if self.__devices[bus].has_key(udi):
                return self.__devices[bus][udi]
        return result

    def lsbus(self):
        return self.__devices.keys()

    def lsdev(self, bus=None, cls=None):
        """ Return tuples of connected devices by their bus and class """
        if bus is None:
            buses = self.__devices.keys()
        else:
            buses = [bus]

        result = []
        for bus in buses:
            for udi in self.__devices[bus].keys():
                device = self.__devices[bus][udi]
                dev_cls = (device.get('%s.device_class' % bus, 0) << 8) + device.get('%s.device_subclass' % bus, 0)
                if cls is None or cls == dev_cls:
                    result.append(udi)
        return result

