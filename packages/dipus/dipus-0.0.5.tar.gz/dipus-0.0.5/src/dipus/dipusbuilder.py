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

DEFAULT_HOST = "localhost"
DEFAULT_PORT = "9876"


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
            'doc_url': conf['doc_url'],
            'password': conf['password']
            })

        url = conf['server_url'] + '/' + conf['_index']
        ret = urllib.urlopen(url, params).read()

        result = simplejson.loads(ret)

        if 'ok' not in result or result['ok'] is not True:
            print "Error"
            print result


class DipusBuilder(Builder):
    name = 'dipus'
    format = 'search'
    out_suffix = ''

    def output_templates(self, server_url, _index):
        dipus_url = "/".join([server_url, _index, "_search"])

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

    def check_deprecated_params(self):
        if self.config.dipus_host_url is not None:
            raise SphinxError("dipus_host_url is deprecated. \
use dipus_server_url")

    def prepare_writing(self, docnames):
        self.check_deprecated_params()

        self.writer = DipusWriter(self)
        if self.config.dipus_server_url is None:
            self.config.dipus_server_url = "http://{0}:{1}".format(
                DEFAULT_HOST, DEFAULT_PORT)
        if self.config.dipus_doc_url is None:
            html_dir = os.path.join(self.outdir, 'html')
            self.config.dipus_doc_url = "file:///{0}".format(html_dir)
        if self.config.dipus_index is None:
            # if dipus_index is not set, use project name
            p_name = self.config.project.encode('utf-8')
            self.config.dipus_index = urllib.quote(p_name)

        self.config.dipus_server_url = self.config.dipus_server_url.rstrip("/")
        self.config.dipus_index = self.config.dipus_index.rstrip("/")

        self.output_templates(self.config.dipus_server_url,
                              self.config.dipus_index)

    def write_doc(self, docname, doctree):
        conf = {
            'server_url': self.config.dipus_server_url,
            'doc_url': self.config.dipus_doc_url,
            '_index': self.config.dipus_index,
            'password': self.config.dipus_password
            }

        self.writer.write(docname, doctree, conf)


def setup(app):
    app.add_config_value('dipus_server_url', None, '')
    app.add_config_value('dipus_doc_url', None, '')
    app.add_config_value('dipus_index', None, '')
    app.add_config_value('dipus_password', None, '')

    # deperecated
    app.add_config_value('dipus_host_url', None, '')
    app.add_builder(DipusBuilder)
