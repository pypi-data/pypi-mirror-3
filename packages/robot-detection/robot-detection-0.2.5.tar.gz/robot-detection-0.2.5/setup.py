#! /usr/bin/env python

from setuptools import setup, find_packages

setup(name="robot-detection",
      version="0.2.5",
      author="Rory McCann",
      author_email="rory@technomancy.org",
      py_modules=['robot_detection'],
      summary="Library for detecting if a HTTP User Agent header is likely to be a bot",
      url="http://www.celtic-knot-creator.com/robot-detection/",
)
