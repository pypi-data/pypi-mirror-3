#!/usr/bin/env python
# -*- coding: utf-8 -*-

import simplejson


class Config():
    port = 9876
    indexroot = None
    password = None
    host = "0.0.0.0"

    def __init__(self, conffile):
        self.read(conffile)
    
    def read(self, conffile):
        with open(conffile) as fp:
            d = simplejson.load(fp)
            if 'port' in d:
                self.port = d['port']
            if 'host' in d:
                self.host = d['host']
            if 'indexroot' not in d:
                raise Exception("No indexroot setting in config.json")
            self.indexroot = d['indexroot']
    
    
if __name__ == '__main__':
    pass

