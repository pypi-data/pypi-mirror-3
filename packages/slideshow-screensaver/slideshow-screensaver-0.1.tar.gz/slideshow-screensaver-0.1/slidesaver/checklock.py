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

import dbus

def is_locked():
    session_bus = dbus.SessionBus()
    dbus_object = session_bus.get_object("org.gnome.ScreenSaver", "/")
    status = dbus_object.GetActive(dbus_interface="org.gnome.ScreenSaver")

    if status == 0:
        return False
    else:
        return True
