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
Thread to handle HAL events.
"""

__author__ = "Andy Shevchenko <andy@smile.org.ua>"
__revision__ = "$Id: HALHandler.py 22 2007-10-06 17:06:49Z andy $"

__all__ = ['HALHandler']

import Queue

from minihallib.HALEventerThread import HALEventerThread

class HALHandlerThread(HALEventerThread):
    """ Thread to handle HAL events """
    def __init__(self, handler):
        HALEventerThread.__init__(self)
        self.handler = handler

    def device_init(self, capability):
        for udi in self.plugins[capability].keys():
            self.handler.push_message("device init", capability, self.plugins[capability].get(udi))

    def device_add(self, capability, udi):
        self.handler.push_message("device added", capability, self.plugins[capability].get(udi))

    def device_remove(self, capability, udi):
        self.handler.push_message("device removed", capability, self.plugins[capability].get(udi))

class HALHandler:
    """ HAL events wrapper """
    def __init__(self):
        self.queue = Queue.Queue()
        self.thread = HALHandlerThread(self)
        self.thread.setDaemon(True)

    def register_plugin(self, capability, property_modified=None, fill=True):
        self.thread.register_plugin(capability, property_modified, fill)

    def unregister_plugin(self, capability, clear=True):
        self.thread.unregister_plugin(capability, clear)

    def start(self):
        self.thread.start()

    def quit(self):
        self.thread.quit()
        self.thread.join()

    def push_message(self, msg, capability, data):
        """ Puts an item into message queue.
        msg is a string (for example, 'device added').
        capability is a string name of registered capability (for example, 'volume').
        data is a dictionary. """
        self.queue.put((msg, capability, data))

    def poll_message(self):
        """ Takes one message from queue and returns (msg, capability, data) tuple or
        None if there is no messages. """
        try:
            return self.queue.get(False)
        except Queue.Empty:
            return None

