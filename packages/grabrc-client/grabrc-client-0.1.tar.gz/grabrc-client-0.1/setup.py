#!/usr/bin/env python

from setuptools import setup

setup(name='grabrc-client',
      version='0.1',
      description='Lightweight, portable Github wrapper. \
Retrieval of dotfiles (.emacs, .vimrc, etc.) in any environment',
      author='Louis Li',
      author_email='pong@outlook.com',
      packages=['client'],
      entry_points = {
          'console_scripts': ['grabrc = client.client:main']
      }

    )
