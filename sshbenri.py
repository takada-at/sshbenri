#!/usr/bin/env python
# coding:utf-8

import json
from optparse import OptionParser
import os
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
    return [val.lstrip().rstrip() for val in string.split(',')]

def createssh(hosts, common_options, confpath=None, command=None):
    commands = []
    config = loadconfig(confpath)
    for host in hosts:
        # sshコマンドをつくる
        appconfig = config.get(host)
        if appconfig:
            expandedhosts = parsecsv(appconfig['host'])
            sshcommand = createssh(expandedhosts, common_options, confpath)
            commands.append(sshcommand)
            continue

        if host.find('ssh ')==0:
            #もともとSSHコマンドの形をしてる場合はそのまま実行
            commands.append(host)
            continue

        port = 22
        if host.find(':')>=0:
            host, port = host.split(':')
            port = int(port)

        sshcommand = "ssh {host} ".format(host=host)
        if port != 22:
            sshcommand += "-p {port} ".format(port=port)

        if common_options:
            # 全部につけるオプション
            sshcommand += '%s ' % (' '.join(common_options),)

        commands.append(sshcommand)

    if command:
        command = "\'{command}\'".format(command=command)
        commands.append(command)

    executecommand = " ".join(commands)
    return executecommand

def executessh(hosts, common_options, execcmd, confpath=None, dryrun=False):
    executecommand = createssh(hosts, common_options, confpath, command=execcmd)
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
