#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

u"""
 rsyncbenri
 ===========
 多重SSHでrsyncを便利にする
"""

import argcomplete
from argparse import ArgumentParser
import os
import sys
from . import core
from .core import (loadconfig, parsecsv)

def createcommand(hosts, srcpath, destpath, config={}, dryrun=False, rsyncopt='', sshopts=''):
    common_options = ['-t', '-A']
    if sshopts:
        common_options += sshopts.split()

    hosts = core.expandhosts(hosts, config)
    if not hosts: return
    opts = ['-rv']
    if rsyncopt:
        opts.append(rsyncopt)

    if len(hosts)>1:
        commands = core.createssh(hosts[:-1], common_options, config)
        executecommand = core.quotecommands(commands)
        quoteescape = core.escape_quote(executecommand, 0)
        opts.append("-e '{sshcomd} ssh'".format(sshcomd=quoteescape))

    cmds = ['rsync']
    cmds += opts
    cmds += [srcpath, "{host}:'{destpath}'".format(host=hosts[-1], destpath=destpath)]
    cmd = " ".join(cmds)
    return cmd

def executersync(hosts, srcpath, destpath, config={}, dryrun=False, rsyncopt='', sshopts=''):
    """
    rsyncコマンドの作成と実行

    Arguments:
      hosts(list): 複数ホストのリスト
      srcpath(str): ローカルパス
      destpath(str): リモートパス
      config(dict): 設定
      dryrun(bool): Falseなら表示のみ
      rsyncopt(str): rsyncのオプション
    """
    if not os.path.exists(os.path.expanduser(srcpath)):
        sys.stderr("warning: {} does not exists\n".format(srcpath))

    cmd = createcommand(hosts, srcpath, destpath, config, dryrun, rsyncopt, sshopts)
    print(cmd)
    if not dryrun:
        os.system(cmd)

def main():
    config = loadconfig()
    parser = ArgumentParser(description='generate ssh command')
    parser.add_argument('-n', '--dryrun', dest='dryrun', action='store_true', help='dryrun')
    parser.add_argument('--opts', dest='opts', help='rsync opt', default='')
    parser.add_argument('--sshopts', dest='sshopts', help='ssh opt', default='')
    parser.add_argument('srcpath')
    parser.add_argument('dest')
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    host, dest = args.dest.split(':')
    hosts = parsecsv(host)
    config = loadconfig(None)
    executersync(hosts, args.srcpath, dest, config=config, dryrun=args.dryrun, rsyncopt=args.opts, sshopts=args.sshopts)

if __name__=='__main__':
    main()
