#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README') as f:
    long_description = f.read()

setup(name='slideshow-screensaver',
      version='0.1',
      description='Slideshow screensaver for Gnome based on Pygame',
      keywords=['slideshow', 'screensaver', 'gnome'],
      author='James Adney',
      author_email='jfadney@gmail.com',
      url='https://github.com/jamesadney/slideshow-screensaver',
      license='GPL3',
      packages=find_packages(),
      scripts=["watch-idle.py", "screensaver.py"],
      long_description=long_description,

      # Also requires dbus-python and python-gobject
      install_requires=["distribute", "pygame"])
