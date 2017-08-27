#!/usr/bin/env bash

zip gitstat_load.zip    \
    gitstat/__init__.py \
    gitstat/app.py      \
    gitstat/version.py  \
    gitstat/author.py   \
    load_gitstat.py     \
    config.ini.sample   \
    requirements.txt    \
    README.md

mkdir -p /tmp/gitstat
GIT_REV=$(git rev-parse --short HEAD)
OLD_DIR=$(pwd)
sed -e "s/%TOKEN%/$GIT_REV/" gitstat/version.py > /tmp/gitstat/version.py
cd /tmp
zip -u $OLD_DIR/gitstat_load.zip gitstat/version.py
cd $OLD_DIR
