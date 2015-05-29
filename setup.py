#!/usr/bin/env python
from setuptools import setup

setup(name='sshbenri',
      version='0.0.7',
      description='ssh benri script',
      scripts=['scripts/sshbenri', 'scripts/rsyncbenri'],
      packages=['sshbenri'],
      )
