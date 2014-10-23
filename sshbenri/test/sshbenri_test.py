# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from .. import sshbenri

def test_escape():
    assert r'ssh -i \~/key'   == sshbenri.escape('ssh -i ~/key', 1)
    assert r'ssh -i \\\~/key' == sshbenri.escape('ssh -i ~/key', 2)

def test_create_remote_command():
    hosts = ['host0', 'host1']
    cmd = 'echo $HOME && echo \$HOME && date +"%Y-%m-%d"'
    assert "'"+r'echo \$HOME \&\& echo \\\$HOME \&\& date +"%Y-%m-%d"'+"'" == sshbenri.create_remote_command(hosts, cmd)
