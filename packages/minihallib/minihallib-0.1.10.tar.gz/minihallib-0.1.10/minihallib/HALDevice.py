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
Device with its properties as the dict interface.
"""

__author__ = "Andy Shevchenko <andy@smile.org.ua>"
__revision__ = "$Id: HALDevice.py 36 2007-11-11 12:18:30Z andy $"

__all__ = ['HALDevice', 'Device']

import dbus

from minihallib.Log import logger

class HALDevice:
    """ Special class to store device and its dbus connection """
    def __init__(self, dev_obj, property_modified_cb=None):
        self.__dev_obj = dev_obj
        self.property_modified_cb = property_modified_cb
        self.__dev_if = dbus.Interface(self.__dev_obj, 'org.freedesktop.Hal.Device')
        self.__properties = self.__dev_if.GetAllProperties()
        self.__parent = None

    def dbg(self, level, msg):
        logger.debug(level, "%s: %s" % (self.__class__.__name__, msg))

    def keys(self):
        return self.__properties.keys()

    def has_key(self, key):
        return self.__properties.has_key(key)

    def __delitem__(self, key):
        if self.__properties.has_key(key):
            del self.__properties[key]

    def __setitem__(self, key, xproperty):
        self.__properties[key] = xproperty

    def __getitem__(self, key):
        return self.__properties[key]

    def get(self, key, result=None):
        return self.__properties.get(key, result)

    def udi(self):
        return self.get('info.udi')

    def interface(self, dbus_interface='org.freedesktop.Hal.Device'):
        return dbus.Interface(self.__dev_obj, dbus_interface)

    def update_property(self, xproperty):
        """ Called when single property has been modified """
        (name, added, removed) = xproperty
        self.dbg(100, "Property is modified: '%s'" % name)

        try:
            modified = self.__dev_if.PropertyExists(name)
            if modified:
                self.__properties[name] = self.__dev_if.GetProperty(name)
                self.dbg(50, "Property '%s' has been updated, new value: '%s'" % (name, self.__properties[name]))
        except dbus.DBusException, e:
            logger.warning("%s" % str(e))
            modified = False

        if not modified:
            if self.__properties.has_key(name):
                del self.__properties[name]

        if self.property_modified_cb is not None:
            self.property_modified_cb(self, name, modified)

    def property_modified(self, changes, properties_list):
        """ Property modified event handler """
        self.dbg(50, "%d properties are modified" % changes)
        for xproperty in properties_list:
            self.update_property(xproperty)

    def set_parent(self, parent=None):
        self.__parent = parent

    def get_parent(self):
        return self.__parent

class Device:
    """ Represent HALDevice in more abstract and readonly way """
    def __init__(self, hal_device):
        self.hal_device = hal_device

    def dbg(self, level, msg):
        logger.debug(level, "%s: %s" % (self.__class__.__name__, msg))

    def get(self, key, result=None):
        return self.hal_device.get(key, result)

    def udi(self):
        return self.hal_device.udi()

