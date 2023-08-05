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
Basic thread to wait for HAL events.
"""

__author__ = "Andy Shevchenko <andy@smile.org.ua>"
__revision__ = "$Id: HALEventerThread.py 34 2007-11-11 11:53:05Z andy $"

__all__ = ['HALEventerThread']

import threading
import time
import gobject

from minihallib.Log import logger
from minihallib.HALManager import HALManager
from minihallib.HALPlugin import HALPlugin

class HALEventerThread(threading.Thread, HALManager):
    """ Thread to wait for HAL events """
    def __init__(self):
        threading.Thread.__init__(self)
        HALManager.__init__(self)

        self.hal_manager.connect_to_signal('DeviceAdded', self.device_added_callback)
        self.hal_manager.connect_to_signal('DeviceRemoved', self.device_removed_callback)

        self.plugins = {}
        self.loop = gobject.MainLoop()

    def dbg(self, level, msg):
        logger.debug(level, "%s: %s" % (self.__class__.__name__, msg))

    def register_plugin(self, capability, property_modified_cb=None, fill=True):
        """ Register plugin for given capability """
        if self.plugins.has_key(capability):
            logger.error("Plugin for capability '%s' is already registered" % capability)
            return False

        self.plugins[capability] = HALPlugin(self.bus, self.hal_manager, capability, property_modified_cb)
        self.dbg(20, "Plugin '%s' has been registered" % capability)
        if fill:
            self.plugins[capability].fill()
        return True

    def unregister_plugin(self, capability, clear=True):
        """ Unregister plugin for given capability """
        if self.plugins.has_key(capability):
            if clear:
                self.plugins[capability].clear()
            self.dbg(20, "Unregistering plugin '%s'..." % capability)
            del self.plugins[capability]
            return True

        logger.error("Plugin for capability '%s' isn't registered" % capability)
        return False

    def device_init(self, capability):
        """ Virtual function will be called with connected devices at start """
        pass

    def run(self):
        """ Thread loop """
        self.dbg(20, "Waiting for media...")
        for capability in self.plugins.keys():
            self.device_init(capability)
        self.loop.run()

    def quit(self):
        self.dbg(20, "Exiting...")
        self.loop.quit()

    def device_add(self, capability, udi):
        """ Virtual function will be called when device is added """
        pass

    def device_remove(self, capability, udi):
        """ Virtual function will be called when device is removed """
        pass

    def device_added_callback(self, udi):
        """ DBus message handler """
        self.dbg(50, "Adding device: %s..." % udi)
        for capability in self.plugins.keys():
            if self.plugins[capability].add(udi):
                self.device_add(capability, udi)

    def device_removed_callback(self, udi):
        """ DBus message handler """
        self.dbg(50, "Removing %s..." % udi)
        for capability in self.plugins.keys():
            self.plugins[capability].remove(udi, self.device_remove)

def test(time_circle):
    """ Test suite """
    eventer = HALEventerThread()

    #eventer.register_plugin('volume')
    eventer.register_plugin('net')
    eventer.unregister_plugin('foo bar')
    eventer.register_plugin('storage')

    try:
        eventer.start()
        for xstep in xrange(time_circle):
            print "%d..." % (xstep+1)

            if xstep == time_circle/2:
                eventer.register_plugin('volume')
                #eventer.register_plugin('net')
                eventer.register_plugin('storage')
                eventer.unregister_plugin('storage')

                print "Registered plugins:", eventer.plugins.keys()

            time.sleep(1)
        eventer.quit()
    except KeyboardInterrupt:
        eventer.quit()

