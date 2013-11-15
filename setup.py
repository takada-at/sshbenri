#!/usr/bin/env python

from distutils.core import setup
import os
setup(name='sshbenri',
      version='0.0.1',
      description='ssh benri script',
      scripts=['scripts/sshbenri'],
      py_modules=['sshbenri'],
      requires=['argcomplete'],
     )
