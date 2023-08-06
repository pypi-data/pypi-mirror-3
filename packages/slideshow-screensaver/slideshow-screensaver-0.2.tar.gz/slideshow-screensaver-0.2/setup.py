#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README') as f:
    long_description = f.read()

setup(name='slideshow-screensaver',
      version='0.2',
      description='Slideshow screensaver for GNU/Linux using OpenGL',
      keywords=['slideshow', 'screensaver', 'opengl'],
      author='James Adney',
      author_email='jfadney@gmail.com',
      url='https://github.com/jamesadney/slideshow-screensaver',
      license='GPL3',
      packages=find_packages(),
      scripts=["slidesaver-daemon", "screensaver.py"],
      long_description=long_description,
      install_requires=["distribute", "pyglet", "PIL"])
