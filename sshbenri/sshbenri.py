#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

u"""
 sshbenri
 ========
 多重SSHを便利に使うためのスクリプト
"""

import argcomplete
from argcomplete.completers import ChoicesCompleter
from argparse import ArgumentParser
import os

from . import core

def executessh(hosts, common_options, execcmd, config={}, dryrun=False):
    """
    sshコマンドの作成と実行

    Arguments:
      hosts(list): 複数ホストのリスト
      common_options(list): sshコマンドのオプション
      execcmd(str): リモートで実行するコマンド
      config(dict): 設定
      dryrun(bool): Falseなら表示のみ
    """
    hosts = core.expandhosts(hosts, config)
    commands = core.createssh(hosts, common_options, config)
    executecommand = core.quotecommands(commands)
    if execcmd:
        executecommand += ' ' + core.create_remote_command(hosts, execcmd)

    print(executecommand)
    if not dryrun:
        os.system(executecommand)

def _create_forwardopt(ports):
    res = []
    for fport in ports:
        res.append("-L{port}:localhost:{port}".format(port=fport))

    return res

def main():
    config = loadconfig()
    parser = ArgumentParser(description='generate ssh command')
    parser.add_argument('-p', '--ports', dest='ports', help='forward port', type=parsecsv)
    parser.add_argument('-g', '--opts', dest='opts', help='global ssh options')
    parser.add_argument('-e', '--exec', dest='execcmd', help='execute comand')
    parser.add_argument('-n', '--dryrun', dest='dryrun', action='store_true', help='dryrun')
    parser.add_argument('hosts', help='target hosts A,B,C', type=parsecsv).completer=ChoicesCompleter(config.keys())
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    hosts = args.hosts
    ports = args.ports
    common_options = ['-t', '-A']
    if ports:
        common_options += _create_forwardopt(ports)

    if args.opts:
        common_options += parsecsv(opt.opts)

    config = loadconfig(None)
    executessh(hosts, common_options, args.execcmd, config=config, dryrun=args.dryrun)

if __name__=='__main__':
    main()
