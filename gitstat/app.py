# coding=utf-8

from __future__ import print_function

import gitstat.author

from os.path import basename
from os.path import isdir
from git import Repo
from influxdb import InfluxDBClient

class GitStatLoader:

    def __init__(self, influx_cfg, gitstat_cfg):
        host = influx_cfg['host']
        port = influx_cfg['port']
        user = influx_cfg['user']
        password = influx_cfg['password']
        dbname = influx_cfg['database']
        self.branch = gitstat_cfg['branch']
        self.measurement = gitstat_cfg['measurement']
        self.influx = InfluxDBClient(host, port, user, password, dbname)


    def load(self, path):
        print("Start load stat data for %s" % path)
        if isdir(path):
            recs = self.parse_repo(path, self.branch)
            if recs: self.send_data(recs)
        else:
            raise ValueError("Invalid git repo path: %s" % (path))


    def send_data(self, recs):
        self.influx.write_points(
            [self.make_line_point(r) for r in recs],
            protocol='line'
        )


    def make_line_point(self, rec):
        epoch = rec['authored_date']
        point_str = "%s,author=%s,app=%s files=%d,add=%d,mod=%d,del=%d,cnt=1 %d" % (
                self.measurement,
                rec['author'],
                rec['app'],
                rec['files'],
                rec['addition'],
                rec['modification'],
                rec['deletion'],
                epoch * 1000000000 # influxdb accepts nano-second
        )
        if type(point_str) is unicode:
            return point_str
        else:
            return unicode(point_str, 'utf-8')


    def parse_repo(self, root_dir, branch):
        if root_dir.endswith('/'):
           root_dir = root_dir[:-1]
        app = basename(root_dir)
        repo = Repo(root_dir)
        recs = []
        for c in repo.iter_commits(branch):
            st = c.stats.total
            rec = {
                'app'           : app,
                'author'        : self.normalize_author(c.author.name),
                'authored_date' : c.authored_date,
                'files'         : st['files'],
                'addition'      : st['insertions'],
                'modification'  : st['lines'],
                'deletion'      : st['deletions']
            }
            print("app=%s branch=%s commit=%s" % (app, self.branch, c.hexsha))
            recs.append(rec)
        return recs


    def normalize_author(self, author):
        return gitstat.author.mapping.get(author, author)
