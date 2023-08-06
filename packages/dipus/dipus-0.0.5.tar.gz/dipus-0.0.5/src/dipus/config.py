#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import simplejson
import logging


class Config():
    port = 9876
    indexroot = "/tmp/dipus/index"
    password = None
    host = "0.0.0.0"

    def __init__(self, conffile):
        self.read(conffile)

    def create_defaultindexroot(self):
        if not os.path.exists(self.indexroot):
            os.makedirs(self.indexroot)  # createdefault dir
            logging.info("Default indexroot created: ".format(self.indexroot))

    def read(self, conffile):
        if conffile is None or not os.path.exists(conffile):
            self.create_defaultindexroot()
            return
        c = conffile[0]
        with open(conffile) as fp:
            d = simplejson.load(fp)
            if 'port' in d:
                self.port = d['port']
            if 'host' in d:
                self.host = d['host']
            if 'indexroot' in d:
                self.indexroot = d['indexroot']
            else:
                self.create_defaultindexroot()


if __name__ == '__main__':
    pass
