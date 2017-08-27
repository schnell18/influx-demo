#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function

import ConfigParser
import sys

from os.path import expanduser
from gitstat.app import GitStatLoader
from gitstat.version import version_text
from time import time


if __name__ == '__main__':
    t0 = time()
    print("Git stat time series loader (%s)" % (version_text,))
    if len(sys.argv) < 2:
        raise Exception("Git repository paths are expected")

    config = ConfigParser.RawConfigParser()
    config.read(expanduser('~/.influxdemo/config.ini'))
    gitstat_cfg = {t[0]: t[1] for t in config.items('gitstat')}
    influx_cfg = {t[0]: t[1] for t in config.items('influxdb')}

    loader = GitStatLoader(influx_cfg, gitstat_cfg)
    for root_dir in sys.argv[1:]:
        t = loader.load(root_dir)
    t1 = time()
    print("Elapse: %d seconds" % int(t1 - t0))
