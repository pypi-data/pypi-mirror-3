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
Implement simple logging module.
"""

__author__ = "Andy Shevchenko <andy@smile.org.ua>"
__revision__ = "$Id: Log.py 33 2007-10-19 16:11:36Z andy $"

__all__ = ['logger']

import sys
import logging

# Debug levels
DEBUG_TABLE = {
    1:      [9, "DEBUG[1]"],
    2:      [8, "DEBUG[2]"],
    5:      [7, "DEBUG[5]"],
    10:     [6, "DEBUG[10]"],
    20:     [5, "DEBUG[20]"],
    50:     [4, "DEBUG[50]"],
    100:    [3, "DEBUG[100]"],
    200:    [2, "DEBUG[200]"],
}

def add_levels(table):
    """ Add custom logging levels """
    for level in table.keys():
        logging.addLevelName(table[level][0], table[level][1])

add_levels(DEBUG_TABLE)

def convert_level(level, table):
    """ Convert logging levels using lookup table """
    # Look up level in the table.
    try:
        return table[level][0]
    except KeyError:
        # Search closest level
        keys = table.keys()
        keys.sort()
        for key in keys:
            if level < key:
                return table[key][0]
        return table[keys[-1]][0]

class Log:
    """ Simply logger """
    def __init__(self):
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s",
                                      "%b %d %H:%M:%S")
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        self.logger = logging.getLogger("miniHalLib")
        self.logger.addHandler(handler)

    def set_logger(self, new_logger):
        """ Update logger object """
        self.logger = new_logger

    def set_log_level(self, level):
        """ Setup level of logging """
        self.logger.setLevel(level)

    def set_debug_level(self, level):
        """ Setup debug level of logging """
        if level == 0:
            new_level = logging.DEBUG
        else:
            new_level = convert_level(level, DEBUG_TABLE)
        self.set_log_level(new_level)

    def log(self, level, msg):
        """ Print message at given level """
        self.logger.log(level, msg)

    def debug(self, level, msg):
        """ Print debug message """
        if level == 0:
            new_level = logging.DEBUG
        else:
            new_level = convert_level(level, DEBUG_TABLE)
        self.log(new_level, msg)

    def info(self, msg):
        """ Print info message """
        self.log(logging.INFO, msg)

    def warning(self, msg):
        """ Print warning message """
        self.log(logging.WARNING, msg)

    def error(self, msg):
        """ Print error message """
        self.log(logging.ERROR, msg)

logger = Log()

