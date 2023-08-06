#!/usr/bin/env python

import os
import pyglet

import Image

from slidesaver import util

PICTURE_DIR = os.path.expanduser("~/Pictures")
CROP = True

class AppWindow(pyglet.window.Window):

    def __init__(self):

        super(AppWindow, self).__init__(fullscreen=True)

        #Hide mouse cursor
        self.set_mouse_visible(False)

        self.pics = util.Pictures(PICTURE_DIR)
        self.screen_x = self.width
        self.screen_y = self.height
        self.screen_ratio = float(self.screen_x) / self.screen_y
        self.center_x = self.screen_x // 2
        self.center_y = self.screen_y // 2
        self.transitioning = False
        self.old_picture = None
        self.picture = None

        self.load_new_image()

    def increase_opacity(self, dt):
        if self.picture.opacity <= 255 and self.transitioning:
            if self.picture.opacity + 2 > 255:
                self.picture.opacity = 255
                if self.old_picture:
                    self.old_picture.opacity = 0
            else:
                self.picture.opacity += 2
                if self.old_picture:
                    self.old_picture.opacity -= 2
        else:
            self.transitioning = False

    def zoom(self, dt):
        self.picture.scale += .05 * dt
        if self.old_picture:
            self.old_picture.scale += .05 * dt

    def load_new_image(self, dt=None):
        random_pic = self.pics.get_random()

        temp_image = Image.open(random_pic)

        # Resize image to fit on screen
        image_x, image_y = temp_image.size
        image_ratio = float(image_x) / image_y

        # Crop horizontally-oriented images to fill the screen
        if CROP and image_ratio > 1:
            if image_ratio >= self.screen_ratio:
                resized_y = self.screen_y
                resized_x = (resized_y * image_x) // image_y
            else:
                resized_x = self.screen_x
                resized_y = (resized_x * image_y) // image_x
        else:
            if image_ratio >= self.screen_ratio:
                resized_x = self.screen_x
                resized_y = (resized_x * image_y) // image_x
            else:
                resized_y = self.screen_y
                resized_x = (resized_y * image_x) // image_y

        temp_image = temp_image.resize((resized_x, resized_y))
        raw_image = temp_image.tostring()

        self.image = pyglet.image.ImageData(resized_x,
                                            resized_y,
                                            'RGB',
                                            raw_image,
                                            pitch= -resized_x * 3)

        # Set anchor of sprite to center of image
        self.image.anchor_x = self.image.width // 2
        self.image.anchor_y = self.image.height // 2

        if self.picture:
            self.old_picture = self.picture

        self.picture = pyglet.sprite.Sprite(self.image)

        # Move sprite to center
        self.picture.set_position(self.center_x, self.center_y)
        self.picture.opacity = 0
        self.transitioning = True


def quit(window):
    window.close()
    pyglet.app.exit()


if __name__ == "__main__":

    app = AppWindow()
    pyglet.clock.schedule_interval(app.increase_opacity, 1.0 / 120)
    pyglet.clock.schedule_interval(app.load_new_image, 10)
#    pyglet.clock.schedule_interval(app.zoom, 1.0 / 30)

    @app.event
    def on_draw():
        app.clear()
        app.picture.draw()
        if app.old_picture:
            app.old_picture.draw()

    @app.event
    def on_key_press(symbol, modifiers):
        quit(app)

    @app.event
    def on_mouse_press(x, y, button, modifiers):
        quit(app)

    @app.event
    def on_mouse_scroll(x, y, scroll_x, scroll_y):
        quit(app)

    @app.event
    def on_mouse_motion(x, y, dx, dy):
        quit(app)

    pyglet.app.run()
