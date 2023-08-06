# Slideshow Screensaver
# Copyright (C) 2012 James Adney
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import ctypes
import os

class XScreenSaverInfo(ctypes.Structure):
  """ typedef struct { ... } XScreenSaverInfo; """
  _fields_ = [('window', ctypes.c_ulong), # screen saver window
              ('state', ctypes.c_int), # off,on,disabled
              ('kind', ctypes.c_int), # blanked,internal,external
              ('since', ctypes.c_ulong), # milliseconds
              ('idle', ctypes.c_ulong), # milliseconds
              ('event_mask', ctypes.c_ulong)] # events


def get_idle_time():

    xlib = ctypes.cdll.LoadLibrary('libX11.so')
    display = xlib.XOpenDisplay(os.environ['DISPLAY'])
    xss = ctypes.cdll.LoadLibrary('libXss.so.1')
    xss.XScreenSaverAllocInfo.restype = ctypes.POINTER(XScreenSaverInfo)
    xssinfo = xss.XScreenSaverAllocInfo()
    xss.XScreenSaverQueryInfo(display,
                              xlib.XDefaultRootWindow(display),
                              xssinfo)

    idle_time = xssinfo.contents.idle
    return idle_time


def is_idle(delay):
        idle_time = get_idle_time()
        print idle_time

        if idle_time >= delay:
            idle = True
        else:
            idle = False

        return idle
