#!/usr/bin/env python

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

import sys
import os
import subprocess

import dbus

import pygame
from pygame.locals import *

from slidesaver import util

BLACK = (0, 0, 0)
FPS = 30
PICTURE_DIR = os.path.expanduser("~/Pictures")
UPDATE_PICTURE_EVENT = USEREVENT + 1

PICTURE_DELAY = 10000   # Time between pictures in milliseconds
TRANSITION_TIME = 1.5  # Transition time between photos in seconds.
_TRANS_INCR = int(255 / (TRANSITION_TIME * FPS)) # Opacity change per frame

PHOTO_APP_CMD = ["eog", "-n", "-f"]


# TODO: Can this be improved to make it more easily imported by other
#       applications?
#
# Class to encapsulate the entire application
class Screensaver():
    """..."""

    def __init__(self):
        """..."""
        # TODO: Is this the best place to call this
        pygame.init()

        self._set_screen_size()
        self._initialize_screen()
        self._initialize_clock()

        self.pics = util.Pictures(PICTURE_DIR)

        self.image = None
        self.old_image = None

        # List of images loaded
        self.image_paths = []
        self.paused = False

        self.run()

    def _set_screen_size(self):
        """..."""

        # get size of fullscreen display into screen_x, screen_y
        modes = pygame.display.list_modes()    # defaults to fullscreen
        modes.sort()                           # largest goes last
        self.screen_x, self.screen_y = modes[-1]
        self.screen_ratio = float(self.screen_x) / self.screen_y

    def _initialize_screen(self):
        """..."""

        self.screen = pygame.display.set_mode((self.screen_x, self.screen_y),
                                              pygame.FULLSCREEN)

        pygame.display.set_caption('Slideshow Screensaver')

    def _initialize_clock(self):
        self.fps_clock = pygame.time.Clock()

    def next_picture(self):

        random_pic = self.pics.get_random()
        self.image_paths.append(random_pic)

        image = pygame.image.load(random_pic).convert()

        # Resize image to fit on screen
        image_x, image_y = image.get_size()
        image_ratio = float(image_x) / image_y

        # Crop really wide images to fill screen
        if image_ratio >= self.screen_ratio:
            resized_y = self.screen_y
            resized_x = (resized_y * image_x) / image_y
        else:
            # Crop pretty wide images to fill screen
            if image_ratio >= 1:
                resized_x = self.screen_x
                resized_y = (resized_x * image_y) / image_x

            # Images that are square or vertically-oriented don't get cropped
            else:
                resized_y = self.screen_y
                resized_x = (resized_y * image_x) / image_y

        image = pygame.transform.scale(image, (resized_x, resized_y))

        # Center image
        image_rect = image.get_rect()
        image_rect.center = self.screen.get_rect().center

        # Set image as initally transparent
        image.set_alpha(0)

        if self.image:
            self.old_image = self.image
            self.old_image_rect = self.image_rect

        self.image = image
        self.image_rect = image_rect

    def run(self):

        # Load first picture and start timers
        self.next_picture()
        pygame.time.set_timer(UPDATE_PICTURE_EVENT, PICTURE_DELAY)

        # Hide mouse cursor
        pygame.mouse.set_visible(False)

        # Clear initial mouse event
        pygame.event.clear()

        while True:

            ### EVENT HANDLING ################################################

            for event in pygame.event.get():

                # Don't exit all the time when paused
                if self.paused:
                    if event.type == MOUSEBUTTONUP:
                        pygame.display.toggle_fullscreen()
                        self.paused = False

                else:
                    # Show new picture after delay
                    if event.type == UPDATE_PICTURE_EVENT:
                        self.next_picture()

                    # Space key pauses app and launches photo manager
                    elif event.type == KEYDOWN and event.key == K_SPACE:
                        pygame.display.toggle_fullscreen()
                        self.paused = True
                        command = PHOTO_APP_CMD + self.image_paths
                        subprocess.call(command)

                    elif event.type == KEYUP:
                        pass

                    # Exit if any other events are detected
                    elif event.type != pygame.NOEVENT:
                        self.quit()

                if event.type == pygame.QUIT:
                    self.quit()

            ## DRAW ALL THE THINGS ############################################
            if not self.paused:

                # Draw the background
                self.screen.fill(BLACK)

                # Draw image to screen
                self.screen.blit(self.image, self.image_rect)
                if self.old_image:
                    self.screen.blit(self.old_image, self.old_image_rect)
                pygame.display.update()

                #Fade out image
                self.image.set_alpha(self.image.get_alpha() + _TRANS_INCR)
                if self.old_image:
                    self.old_image.set_alpha(self.old_image.get_alpha() - _TRANS_INCR)

                self.fps_clock.tick(FPS)

    def quit(self):

        # Close screensaver quickly
        pygame.display.quit()

        pygame.quit()
        sys.exit()
        
        
def is_locked(session_bus):
    screensaver_object = session_bus.get_object("org.gnome.ScreenSaver", "/")
    active = screensaver_object.GetActive(dbus_interface="org.gnome.ScreenSaver")
    return active


def is_inhibited(session_bus):
    session_manager_object = session_bus.get_object("org.gnome.SessionManager", "/org/gnome/SessionManager")
    inhibited = session_manager_object.IsInhibited(8, dbus_interface="org.gnome.SessionManager")
    return inhibited


if __name__ == "__main__":
    
    session_bus = dbus.SessionBus()
    
    # Hack to avoid lock-screen freeze
    if is_locked(session_bus):
        sys.exit("Screensaver exiting because screen is locked.")
        
    if is_inhibited(session_bus):
        sys.exit("Screensaver inhibited")
        
    app = Screensaver()
