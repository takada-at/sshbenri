# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import os
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

def escape_quote(string, depth):
    """
    全体を''でクオートする。先にクオートのエスケープをする
    """
    esc = getescapechar(depth+1)
    string = string.replace("'", "'{esc}''".format(esc=esc))
    return string

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
    depth = len(hosts)-1
    cmd = execcmd.strip()
    cmd = escape(cmd, depth)
    cmd = "'"+escape_quote(cmd, depth)+"'"
    return cmd

def create_ssh_command(hosts, common_options, execcmd, config=None, dryrun=False):
    if config is None: config = {}
    commands = createssh(hosts, common_options, config, command=execcmd)
    executecommand = quotecommands(commands)
    return executecommand

