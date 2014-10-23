# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from .. import rsyncbenri

def test_executersync():
    hosts = ['host']
    srcpath = './'
    destpath = './'
    cmd = rsyncbenri.createcommand(hosts, srcpath, destpath)
    expect = "rsync -rv {src} {host}:'{dst}'".format(src=srcpath, dst=destpath, host=hosts[0])
    assert expect == cmd

    hosts = ['gw', 'host']
    cmd = rsyncbenri.createcommand(hosts, srcpath, destpath)
    expect = "rsync -rv -e 'ssh -t -A gw ssh' {src} {host}:'{dst}'".format(src=srcpath, dst=destpath, host=hosts[-1])
    assert expect == cmd





