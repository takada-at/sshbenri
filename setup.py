#!/usr/bin/env python

from distutils.core import setup
setup(name='sshbenri',
      version='0.0.6',
      description='ssh benri script',
      scripts=['scripts/sshbenri', 'scripts/rsyncbenri'],
      packages=['sshbenri'],
      )
