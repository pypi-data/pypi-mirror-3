#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import os

from sphinx.builders import Builder
from sphinx.util.osutil import ensuredir, os_path
from sphinx.util.nodes import inline_all_toctrees
from sphinx.util.console import bold, darkgreen, brown
from sphinx.errors import SphinxError

from docutils import nodes, writers
from docutils.nodes import Text

import simplejson

import search_html_t  # template of search_dipus.html
import search_js_t  # template of search_dipus.js


class DipusWriter(writers.Writer):
    def __init__(self, builder):
        self.builder = builder
        writers.Writer.__init__(self)

    def getTitle(self, doctree):
        ''' return first text node as Title'''
        for node in doctree.traverse(Text):
            t = node.astext()
            if t:
                return t

    def write(self, docname, doctree, conf):
        title = self.getTitle(doctree)
        params = urllib.urlencode({
            'path': docname.encode('utf-8'),
            'title': title.encode('utf-8'),
            'message': doctree.astext().encode('utf-8'),
            '_index': conf['_index'],
            'password': conf['password']
            })

        url = conf['host_url'] + '/' + conf['_index']
        ret = urllib.urlopen(url, params).read()

        result = simplejson.loads(ret)
        
        if 'ok' not in result or result['ok'] is not True:
            print "Error"
            print result


class DipusBuilder(Builder):
    name = 'dipus'
    format = 'search'
    out_suffix = ''

    def output_templates(self, host_url, _index):
        host_url = host_url.rstrip("/")
        _index = _index.rstrip("/")
        
        dipus_url = "/".join([host_url, _index, "_search"])

        # TODO: fix if multiple html_static_path
        # TODO: should check files exist?
        path = self.config.html_static_path[0]
        if not os.path.exists(path):
            os.mkdir(path)
        js_path = os.path.join(path, "search_dipus.js")        
        js = search_js_t.template.format(dipus_url=dipus_url)
        with open(js_path, "w") as fp:
            fp.write(js)

        path = self.config.templates_path[0]
        if not os.path.exists(path):
            os.mkdir(path)
        html_path = os.path.join(path, "search_dipus.html")
        html = search_html_t.template.format()
        with open(html_path, "w") as fp:
            fp.write(html)

    def get_outdated_docs(self):
        return 'pass'

    def get_target_uri(self, docname, typ=None):
        return ''

    def prepare_writing(self, docnames):
        self.writer = DipusWriter(self)
        self.output_templates(self.config.dipus_host_url,
                              self.config.dipus_index)

    def write_doc(self, docname, doctree):
        if self.config.dipus_host_url is None:
            raise SphinxError("dipus_host_url is not set")
        if self.config.dipus_index is None:
            raise SphinxError("dipus_index is not set")

        conf = {
            'host_url': self.config.dipus_host_url,
            '_index': self.config.dipus_index,
            'password': self.config.dipus_password
            }

        self.writer.write(docname, doctree, conf)


def setup(app):
    app.add_config_value('dipus_host_url', None, '')
    app.add_config_value('dipus_index', None, '')
    app.add_config_value('dipus_password', None, '')
    app.add_builder(DipusBuilder)
