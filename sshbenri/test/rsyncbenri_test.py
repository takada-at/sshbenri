# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import imp
import os
from mock import Mock
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

def test_createcommand():
    hosts = ['gw', 'host1']
    cmd = rsyncbenri.createcommand(hosts, '~/', '~/')
    expect = "rsync -rv -e 'ssh -t -A gw ssh' ~/ host1:'\\~/'"
    assert expect == cmd


def test_createcommand2():
    hosts = ['gw', 'host1']
    os.system = Mock()
    rsyncbenri.executersync(hosts, '~/', '~/', syncproxy=True)
    assert 1 == os.system.call_count
    args = os.system.call_args_list[0][0][0]
    arg1 = args.split('; ')[0]
    assert "rsync -rv -e 'ssh -t -A gw ssh' ~/ host1:'\~/'" == arg1
    assert "rsync -rv ~/ gw:'~/'" == args.split('; ')[1]
    imp.reload(os)


def test_createcommand3():
    config = dict(someapp={'host': "gw,host1"})
    os.system = Mock()
    rsyncbenri.executersync(['someapp'], '~/', '~/', config=config, syncproxy=True)
    assert 1 == os.system.call_count
    args = os.system.call_args_list[0][0][0]
    arg1 = args.split('; ')[0]
    assert "rsync -rv -e 'ssh -t -A gw ssh' ~/ host1:'\~/'" == arg1
    assert "rsync -rv ~/ gw:'~/'" == args.split('; ')[1]
    imp.reload(os)



