#!/usr/bin/env python
# -*- coding: utf-8 -*-

import simplejson


class Config():
    port = 9876
    indexroot = None
    password = None
    host = "localhost"

    def __init__(self, conffile):
        self.read(conffile)
    
    def read(self, conffile):
        with open(conffile) as fp:
            d = simplejson.load(fp)
            self.port = d['port']
            self.indexroot = d['indexroot']
            self.host = d['host']
    
    
if __name__ == '__main__':
    pass

