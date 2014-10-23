#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

u"""
 rsyncbenri
 ===========
 多重SSHでrsyncを便利にする
"""

import argcomplete
from argcomplete.completers import ChoicesCompleter
from argparse import ArgumentParser
from .sshbenri import (executersync, loadconfig, parsecsv)

def main():
    config = loadconfig()
    parser = ArgumentParser(description='generate ssh command')
    parser.add_argument('-n', '--dryrun', dest='dryrun', action='store_true', help='dryrun')
    parser.add_argument('-g', '--opts', dest='opts', help='rsync opt', default='')
    parser.add_argument('srcpath')
    parser.add_argument('dest')
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    host, dest = args.dest.split(':')
    hosts = parsecsv(host)
    common_options = ['-t', '-A']
    config = loadconfig(None)
    executersync(hosts, common_options, args.srcpath, dest, config=config, dryrun=args.dryrun, rsyncopt=args.opts)

if __name__=='__main__':
    main()
