#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

"""
rsyncbenri
=============

"""

from argparse import ArgumentParser
import os
import sys
from . import core
from .core import (parsecsv)


def createcommand(hosts, srcpath, destpath, config={}, rsyncopt='', sshopts=''):
    """
    create rsync command

    Arguments:
      hosts(list): list of host names
      srcpath(str): local path
      destpath(str): remote path
      config(dict): setting
      rsyncopt(str): rsync option
      sshopt(str): ssh option


    Example::

    >>> createcommand(['gw', 'host'], './local/', '~/remote/')
    "rsync -e 'ssh -t -A gw ssh' -rv ./local/ host:'~/remote/'"
    """
    common_options = ['-t', '-A']
    if sshopts:
        common_options += sshopts.split()

    hosts = core.expandhosts(hosts, config)
    if not hosts:
        return
    opts = ['-rv']
    if rsyncopt:
        opts.append(rsyncopt)

    if len(hosts) > 1:
        commands = core.createssh(hosts[:-1], common_options, config)
        executecommand = core.quotecommands(commands)
        quoteescape = core.escape_quote(executecommand, 0)
        opts.append("-e '{sshcomd} ssh'".format(sshcomd=quoteescape))

    depth = len(hosts)
    dest = "'{}'".format(core.escape(destpath, depth - 1))
    cmds = ['rsync']
    cmds += opts
    cmds += [srcpath,
             "{host}:{destpath}".format(host=hosts[-1], destpath=dest)]
    cmd = " ".join(cmds)
    return cmd


def executersync(hosts, srcpath, destpath, config={},
                 dryrun=False, rsyncopt='', sshopts='', syncproxy=False):
    """
    create and execute rsync command

    Arguments:
      hosts(list): list of host names
      srcpath(str): local path
      destpath(str): remote path
      config(dict): setting
      dryrun(bool): if True, does not execute command
      rsyncopt(str): rsync option
      sshopt(str): ssh option
    """
    if not os.path.exists(os.path.expanduser(srcpath)):
        sys.stderr("warning: {} does not exists\n".format(srcpath))

    expanded_hosts = core.expandhosts(hosts, config)
    targets = core.get_rsync_target(host=hosts[-1],
                                    hosts=expanded_hosts,
                                    config=config,
                                    sync_all=syncproxy)
    cmds = []
    for i, host in enumerate(expanded_hosts):
        if host not in targets:
            continue
        cmd = createcommand(expanded_hosts[:i+1], srcpath, destpath,
                            config, rsyncopt,
                            sshopts)
        cmds.append(cmd)

    cmds.reverse()
    cmd = "; ".join(cmds)
    print(cmd)
    if not dryrun:
        os.system(cmd)


def _get_parser():
    parser = ArgumentParser(description='generate ssh command')
    parser.add_argument('-c', '--config', type=os.path.expanduser)
    parser.add_argument(
        '-n', '--dryrun', dest='dryrun', action='store_true', help='dryrun')
    parser.add_argument('--opts', dest='opts', help='rsync opt', default='')
    parser.add_argument(
        '--sshopts', dest='sshopts', help='ssh opt', default='')
    parser.add_argument(
        '--syncproxy', action='store_true', help='rsync to proxy server')
    parser.add_argument('srcpath')
    parser.add_argument('dest', nargs='+')
    return parser


def handle_dest(dest):
    hosts = []
    for item in dest[:-1]:
        hosts += parsecsv(item)

    if ':' not in dest[-1]:
        raise ValueError('invalid dest path %' % dest[-1])
    host, path = dest[-1].split(':')
    hosts += parsecsv(host)
    return hosts, path


def main():
    parser = _get_parser()
    args = parser.parse_args()
    hosts, dest = handle_dest(args.dest)
    config = core.loadconfig(args.config)
    executersync(hosts, args.srcpath, dest, config=config, dryrun=args.dryrun,
                 rsyncopt=args.opts, sshopts=args.sshopts,
                 syncproxy=args.syncproxy)

if __name__ == '__main__':
    main()
