#!/usr/bin/env python
# coding:utf-8

u"""
 sshbenri
 ========
 多重SSHを便利に使うためのスクリプト
"""

import json
from optparse import OptionParser
import os
import re
import sys
    
def loadconfig(path=None):
    if path is None:
        path = os.path.expanduser('~/.projectconfig.py')
        
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
    for command in reversed(commands):
        escapechar = getescapechar(depth)
        escapedcommand = escape(command, depth)
        res = escapedcommand + ' ' +res
        depth -= 1

    return res.strip()

def getescapechar(depth):
    if depth == 0:
        n = 0
    elif depth == 1:
        n = 1
    else:
        n = 2 ** (depth-1) + 1
    return '\\' * int(n)

reg = re.compile(r'([\$~])')
def escape(command, depth):
    escapechar = getescapechar(depth)
    escapedcommand = re.sub(reg, escapechar+r'\\1', command)
    return escapedcommand
    
def createssh(hosts, common_options, confpath=None, command=None, redirectin=None, depth=0):
    commands = []
    config = loadconfig(confpath)
    for host in hosts:
        # sshコマンドをつくる
        appconfig = config.get(host)
        if appconfig:
            expandedhosts = parsecsv(appconfig['host'])
            sshcommands = createssh(expandedhosts, common_options, confpath, depth=depth)
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
            port = 22
            if host.find(':')>=0:
                host, port = host.split(':')
                port = int(port)

            sshcommand += host
            if port != 22:
                sshcommand += "-p {port} ".format(port=port)

        commands.append(sshcommand.strip())
        depth += 1

    if command:
        commands.append("'"+command.strip()+"'")
        if redirectin:
            commands + '< {redirectin}'.format(redirectin=redirectin)

    return commands

def executessh(hosts, common_options, execcmd, confpath=None, dryrun=False):
    commands = createssh(hosts, common_options, confpath, command=execcmd)
    executecommand = quotecommands(commands)
    print executecommand
    if not dryrun:
        os.system(executecommand)

def _create_forwardopt(ports):
    res = []
    for fport in ports:
        res.append("-L{port}:localhost:{port}".format(port=fport))

    return res

def main():
    usage = "usage: %prog [options] HOST[,HOST..]"
    parser = OptionParser(usage=usage)
    parser.add_option('-p', '--ports', dest='ports', help='forward port')
    parser.add_option('-g', '--opts', dest='opts', help='global ssh options')
    parser.add_option('-e', '--exec', dest='execcmd', help='execute comand')
    parser.add_option('-n', '--dryrun', dest='dryrun', action='store_true', help='dryrun')
    opt, args = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        exit()

    hosts = parsecsv(args[0])
    ports = parsecsv(opt.ports)
    common_options = ['-t', '-A']
    if ports:
        common_options += _create_forwardopt(ports)

    if opt.opts:
        common_options += parsecsv(opt.opts)

    executessh(hosts, common_options, opt.execcmd, dryrun=opt.dryrun)

if __name__=='__main__':
    main()
