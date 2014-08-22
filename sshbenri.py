#!/usr/bin/env python
# coding:utf-8

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
    escapechar = getescapechar(depth)
    escapedcommand = command.replace('\\', '\\'*(2**depth))
    for char in specialchars:
        escapedcommand = escapedcommand.replace(char, escapechar+char)
        
    return escapedcommand
    
def createssh(hosts, common_options, config, command=None, depth=0):
    commands = []
    for host in hosts:
        # sshコマンドをつくる
        appconfig = config.get(host)
        if appconfig:
            expandedhosts = parsecsv(appconfig['host'])
            sshcommands = createssh(expandedhosts, common_options, config, depth=depth)
            commands += sshcommands
            depth += len(expandedhosts)
            continue

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

    if command:
        commands.append(command.strip())

    return commands

def executessh(hosts, common_options, execcmd, config=None, dryrun=False):
    if config is None: config = {}
    commands = createssh(hosts, common_options, config, command=execcmd)
    executecommand = quotecommands(commands)
    print executecommand
    if not dryrun:
        os.system(executecommand)

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
    parser.add_argument('-p', '--ports', dest='ports', help='forward port')
    parser.add_argument('-g', '--opts', dest='opts', help='global ssh options')
    parser.add_argument('-e', '--exec', dest='execcmd', help='execute comand')
    parser.add_argument('-n', '--dryrun', dest='dryrun', action='store_true', help='dryrun')
    parser.add_argument('hosts', help='target hosts A,B,C').completer=ChoicesCompleter(config.keys())
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    hosts = parsecsv(args.hosts)
    ports = parsecsv(args.ports)
    common_options = ['-t', '-A']
    if ports:
        common_options += _create_forwardopt(ports)

    if args.opts:
        common_options += parsecsv(opt.opts)

    config = loadconfig(None)
    executessh(hosts, common_options, args.execcmd, config=config, dryrun=args.dryrun)

if __name__=='__main__':
    main()
