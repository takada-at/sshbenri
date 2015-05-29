#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

"""
 sshbenri
 ========
 多重SSHを便利に使うためのスクリプト
"""

from argparse import ArgumentParser
from itertools import chain
import os

from .compat import input_func
from . import core
from .core import parsecsv


def executessh(hosts, common_options, execcmd, config={}, dryrun=False,
               execute_targets=None):
    """
    create and execute ssh command

    Arguments:
      hosts(list): list of host names
      common_options(list): ssh option
      execcmd(str): remote execute command
      config(dict): setting
      dryrun(bool): if False, does not execute
    """
    expanded_hosts = core.expandhosts(hosts, config)
    if execute_targets:
        targets = execute_targets
    else:
        targets = core.get_target(host=hosts[-1],
                                  hosts=expanded_hosts,
                                  config=config,
                                  sync_all=False)
    cmds = []
    for i, host in enumerate(expanded_hosts):
        if host not in targets:
            continue
        commands = core.createssh(expanded_hosts[:i+1], common_options, config)
        executecommand_t = core.quotecommands(commands)
        if execcmd:
            executecommand_t += ' ' + core.create_remote_command(hosts, execcmd)
        cmds.append(executecommand_t)

    cmds.reverse()
    executecommand = "; ".join(cmds)
    print(executecommand)
    if not dryrun:
        os.system(executecommand)
    return executecommand


def _create_forwardopt(ports):
    res = []
    for fport in ports:
        res.append("-L{port}:localhost:{port}".format(port=fport))

    return res


def readscript():
    script = ""
    while True:
        res = input_func("> ")
        if res.rstrip() == "":
            break
        script += res + " "

    print(script)
    return script


def _get_parser():
    parser = ArgumentParser(description='generate ssh command')
    parser.add_argument('-c', '--config', type=os.path.expanduser)
    parser.add_argument(
        '-p', '--ports', dest='ports', help='forward port', type=parsecsv)
    parser.add_argument('-g', '--opts', dest='opts', help='global ssh options')
    parser.add_argument('-e', '--exec', dest='execcmd', help='execute comand')
    parser.add_argument('--execute-target', dest='execute_target',
                        nargs='*')
    parser.add_argument(
        '-n', '--dryrun', dest='dryrun', action='store_true', help='dryrun')
    parser.add_argument(
        '-i', '--stdin', action='store_true', help='read script from stdin',
        )
    parser.add_argument('hosts', help='ssh hosts', type=parsecsv,
                        nargs='+')
    return parser


def main():
    parser = _get_parser()
    args = parser.parse_args()
    hosts = list(chain.from_iterable(args.hosts))
    ports = args.ports
    common_options = ['-t', '-A']
    if ports:
        common_options += _create_forwardopt(ports)

    if args.opts:
        common_options += parsecsv(args.opts)

    if args.stdin:
        args.execcmd = readscript()

    config = core.loadconfig(args.config)
    executessh(hosts, common_options, args.execcmd,
               config=config, dryrun=args.dryrun,
               execute_targets=args.execute_target)

if __name__ == '__main__':
    main()
