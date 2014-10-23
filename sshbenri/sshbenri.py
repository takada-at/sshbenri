#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

u"""
 sshbenri
 ========
 多重SSHを便利に使うためのスクリプト
"""

import json
import argcomplete
from argcomplete.completers import ChoicesCompleter
from argparse import ArgumentParser
import os
import re
import sys

def loadconfig(path=None):
    """
    コンフィグのロード
    """
    if path is None:
        path = os.path.expanduser('~/.sshbenri.py')

    if not os.path.exists(path): return {}
    G = {}
    L = {}
    execfile(path, G, L)
    return L['hosts']

def parsecsv(string):
    if not string: return []
    return [val.strip() for val in string.split(',')]

def quotecommands(commands):
    """
    SSHコマンドのクオート

    Arguments:
      commands(list): ssh command list
    """
    depth = len(commands)-1
    res   = ""
    for depth, command in enumerate(commands):
        escapechar = getescapechar(depth)
        escapedcommand = escape(command, depth)
        res += ' ' + escapedcommand

    return res.strip()

def getescapechar(depth):
    x = (2 ** depth) - 1
    return '\\' * int(x)

specialchars = ['$', '~', '&', '|']
def escape(command, depth):
    """
    コマンドのエスケープ

    Arguments:
      command(str): コマンド
      depth(int): 深さ

    Example::

    >>> escape('ssh -i ~/key', 1)
    'ssh -i \\~/'
    """
    escapechar = getescapechar(depth)
    escapedcommand = command.replace('\\', '\\'*(2**depth))
    for char in specialchars:
        escapedcommand = escapedcommand.replace(char, escapechar+char)

    return escapedcommand

def createssh(hosts, common_options, config, depth=0):
    """
    多段SSHコマンドをリストの形で作成
    """
    commands = []
    for host in hosts:
        # sshコマンドをつくる
        sshcommand = 'ssh '
        if common_options:
            # 全部につけるオプション
            sshcommand += '%s ' % (' '.join(common_options),)

        if host.find('ssh ')==0:
            #もともとSSHコマンドの形をしてる場合はそのまま実行
            sshcommand += host[4:]
        else:
            sshcommand += host

        commands.append(sshcommand.strip())
        depth += 1

    return commands

def expandhosts(hosts, config):
    """
    コンフィグの設定を読み込んで、ホストを展開
    """
    res = []
    for host in hosts:
        if host in config:
            expandedhosts = parsecsv(config[host].get('host', host))
        else:
            expandedhosts = [host]

        res += expandedhosts

    return res

def create_remote_command(hosts, execcmd):
    """
    リモートで実行するコマンドを作成
    """
    cmd = "'{cmd}'".format(cmd=execcmd.strip())
    cmd = escape(cmd, len(hosts)-1)
    return cmd

def executessh(hosts, common_options, execcmd, config=None, dryrun=False):
    """
    sshコマンドの作成と実行

    Arguments:
      hosts(list): 複数ホストのリスト
      common_options(list): sshコマンドのオプション
      execcmd(str): リモートで実行するコマンド
      config(dict): 設定
      dryrun(bool): Falseなら表示のみ
    """
    if config is None: config = {}
    hosts = expandhosts(hosts, config)
    commands = createssh(hosts, common_options, config)
    executecommand = quotecommands(commands)
    if execcmd:
        executecommand += ' ' + create_remote_command(hosts, execcmd)

    print(executecommand)
    if not dryrun:
        os.system(executecommand)

def executersync(hosts, common_options, srcpath, destpath, config=None, dryrun=False, rsyncopt=''):
    """
    rsyncコマンドの作成と実行

    Arguments:
      hosts(list): 複数ホストのリスト
      common_options(list): sshコマンドのオプション
      srcpath(str): ローカルパス
      destpath(str): リモートパス
      config(dict): 設定
      dryrun(bool): Falseなら表示のみ
      rsyncopt(str): rsyncのオプション
    """
    if config is None: config = {}
    hosts = expandhosts(hosts, config)
    if not hosts: return
    opts = ['-rv']
    if rsyncopt:
        opts.append(rsyncopt)

    if len(hosts)>1:
        commands = createssh(hosts[:-1], common_options, config)
        executecommand = quotecommands(commands)
        opts.append("-e '{sshcomd} ssh'".format(sshcomd=executecommand))

    cmds = ['rsync']
    cmds += opts
    cmds += [srcpath, "{host}:'{destpath}'".format(host=hosts[-1], destpath=destpath)]
    cmd = " ".join(cmds)
    print(cmd)
    if not dryrun:
        os.system(cmd)

def create_ssh_command(hosts, common_options, execcmd, config=None, dryrun=False):
    if config is None: config = {}
    commands = createssh(hosts, common_options, config, command=execcmd)
    executecommand = quotecommands(commands)
    return executecommand

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
