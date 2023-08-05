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
Wrapper around HAL devices and their events.
"""

__author__ = "Andy Shevchenko <andy@smile.org.ua>"
__revision__ = "$Id: HALWrapper.py 24 2007-10-16 06:00:18Z andy $"

__all__ = ['HALWrapper']

import threading
import Queue
import time

from minihallib.Log import logger
from minihallib.HALHandler import HALHandler

# Keep CPU available
IDLE_TIMEOUT    = 0.05

class MsgReceiver(threading.Thread):
    """ Basic class to handle received HAL events """
    def __init__(self, receiver, sleep_time=IDLE_TIMEOUT):
        threading.Thread.__init__(self)
        self.__receiver = receiver
        self.sleep_time = sleep_time
        self.queue = Queue.Queue()
        self.__exit = False

    def dbg(self, level, msg):
        logger.debug(level, "%s: %s" % (self.__class__.__name__, msg))

    def push(self, msg, data):
        self.queue.put((msg, data))

    def run(self):
        """ Thread loop """
        self.dbg(100, "Running...")
        while not self.__exit:
            if self.queue.empty():
                time.sleep(self.sleep_time)
                continue

            result = self.queue.get(False)
            self.__receiver(result)

    def quit(self):
        self.__exit = True

class MsgSender(threading.Thread):
    """ Thread to asynchronously send HAL events """
    def __init__(self, hal_handler, sleep_time=IDLE_TIMEOUT):
        threading.Thread.__init__(self)
        self.__hal_handler = hal_handler
        self.sleep_time = sleep_time
        self.__receivers = {}
        self.__exit = False

    def dbg(self, level, msg):
        logger.debug(level, "%s: %s" % (self.__class__.__name__, msg))

    def register_receiver(self, capability, receiver):
        self.dbg(20, "Register receiver for '%s'" % capability)
        self.__receivers[capability] = MsgReceiver(receiver)
        self.__receivers[capability].start()

    def unregister_receiver(self, capability):
        if self.__receivers.has_key(capability):
            self.dbg(20, "Unregister receiver for '%s'" % capability)
            self.__receivers[capability].quit()
            del self.__receivers[capability]

    def run(self):
        """ Thread loop """
        while not self.__exit:
            result = self.__hal_handler.poll_message()

            if result is None:
                time.sleep(self.sleep_time)
                continue

            msg, capability, data = result
            if self.__receivers.has_key(capability):
                self.__receivers[capability].push(msg, data)

    def quit(self):
        self.__exit = True

class HALWrapper:
    """ Wrapper for HAL handler and message sender """
    def __init__(self):
        self.hal_wrapped_objs = {}
        self.handler = HALHandler()
        self.msgsender = MsgSender(self.handler)

    def dbg(self, level, msg):
        logger.debug(level, "%s: %s" % (self.__class__.__name__, msg))

    def get(self, capability, result=None):
        """ Return object with given capability if it was registered """
        return self.hal_wrapped_objs.get(capability, result)

    def clear_events(self):
        while self.handler.poll_message() is not None:
            pass

    def register(self, hwc):
        """ Register 'PropertyModified' callback and message receiver """
        if self.hal_wrapped_objs.has_key(hwc.capability):
            logger.error("'%s' already registered" % hwc.capability)
            return False

        self.dbg(100, "Register '%s'" % hwc.capability)

        self.hal_wrapped_objs[hwc.capability] = hwc

        self.handler.register_plugin(hwc.capability, hwc.property_modified_cb)
        self.msgsender.register_receiver(hwc.capability, hwc.receiver)

        return True

    def unregister(self, hwc):
        """ Unregister 'PropertyModified' callback and message receiver """
        if self.hal_wrapped_objs.has_key(hwc.capability):
            hwc.quit()

            self.handler.unregister_plugin(hwc.capability)
            self.msgsender.unregister_receiver(hwc.capability)

            self.dbg(100, "Unregister '%s'" % hwc.capability)
            return True

        logger.error("'%s' isn't registered" % hwc.capability)
        return False

    def start(self):
        """ Run HAL eventer interface """
        self.handler.start()
        self.msgsender.start()

    def stop(self):
        """ Stop HAL eventer interface """
        for capability in self.hal_wrapped_objs.keys():
            self.unregister(self.hal_wrapped_objs[capability])

        self.msgsender.quit()
        self.handler.quit()

class TestCls:
    def __init__(self, capability=None):
        self.capability = capability
        self.property_modified_cb = self.property_modified_cb_f
        self.receiver = self.receiver_f

    def quit(self):
        print 'Quiting... (%s)' % self.capability

    def property_modified_cb_f(self, hal_device, name, modified):
        print self.capability, name, modified

    def receiver_f(self, pkt):
        print self.capability, pkt

def test(time_circle):
    wrapper = HALWrapper()
    wrapper.register(TestCls('volume'))
    wrapper.register(TestCls('net'))
    try:
        wrapper.start()
        for xstep in xrange(time_circle):
            print "%d..." % (xstep+1)
            time.sleep(1)
        wrapper.stop()
    except KeyboardInterrupt:
        wrapper.stop()

