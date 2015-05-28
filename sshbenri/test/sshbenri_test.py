# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from itertools import chain
from sshbenri import sshbenri


def test_get_parser():
    """test argument parser
    :return:
    """
    parser = sshbenri._get_parser()
    args = parser.parse_args(["hoge,fuga"])
    hosts = list(chain.from_iterable(args.hosts))
    assert ["hoge", "fuga"] == hosts
    args = parser.parse_args(["hoge", "fuga"])
    hosts = list(chain.from_iterable(args.hosts))
    assert ["hoge", "fuga"] == hosts
    args = parser.parse_args(["hoge"])
    hosts = list(chain.from_iterable(args.hosts))
    assert ["hoge"] == hosts
