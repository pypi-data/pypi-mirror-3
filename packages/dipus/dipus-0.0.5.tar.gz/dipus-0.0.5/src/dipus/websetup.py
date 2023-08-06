#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging

from bottle import Bottle, route, run, request, response, abort
from bottle import Jinja2Template
from bottle import static_file
import simplejson

import docstore

import config


app = Bottle()
conf = None


def ret_jsonp(request, ret):
    json_response = simplejson.dumps(ret)
    response.content_type = 'application/json; charset=utf-8'

    callback_function = request.GET.get('callback')
    if callback_function:
        json_response = ''.join([callback_function, '(', json_response, ')'])

    return json_response


def auth(password):
    ''' not implemented yet '''
    return True


@app.route('/')
def index():
    distdir = os.path.dirname(os.path.abspath(__file__))
    tpl = os.path.join(distdir, '_templates/index.tpl')
    return Jinja2Template(name=tpl).render(var='var')


@app.route('/favicon.ico')
def favicon():
    pass


@app.route('/_static/<filename:path>')
def static_files(filename):
    distdir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(distdir, '_static')
    return static_file(filename, root=static_dir)


@app.route('/_list/')
def listindex():
    ''' return index list '''
    password = request.forms.get('password')
    if auth(password) is False:
        abort(403)

    ret = {
        "list": docstore.listindex(conf.indexroot)
        }

    return ret_jsonp(request, ret)


@app.route('/<_index>', method='POST')
def updateDocument(_index):
    password = request.forms.get('password')

    if auth(password) is False:
        abort(403)

    path = request.forms.get('path')
    if not path:
        abort(400, "path is not set")

    message = request.forms.get('message')
    if not message:
        abort(400, "message is not set")

    title = request.forms.get('title')
    if not title:
        title = ""

    doc_url = request.forms.get('doc_url')
    if not doc_url:
        doc_url = ""

    posted = {
        '_index': _index.decode('utf-8'),
        'path': path.decode('utf-8'),
        'message': message.decode('utf-8'),
        'title': title.decode('utf-8'),
        'doc_url': doc_url.decode('utf-8')
        }

    ret = docstore.register(posted, conf.indexroot)

    return simplejson.dumps(ret)


@app.route('/_msearch/')
def multisearch():
    password = request.forms.get('password')
    if auth(password) is False:
        abort(403)  # forbidden

    query = request.query.get('q')
    indexes = request.query.get('indexes')
    if query is None or indexes is None or len(indexes) == 0:
        abort(400, "query or indexes is not set")

    results = []
    total = 0

    for idx in indexes.split(","):
        if idx in docstore.listindex(conf.indexroot):
            s_r = docstore.search(idx, query, conf.indexroot)
            for r in s_r:  # flatten
                results.append(r)
            total += len(s_r)

    ret = {
        "total": total,
        "hits": results
        }

    return ret_jsonp(request, ret)


@app.route('/<_index>/_search')
def query(_index):
    password = request.forms.get('password')
    if auth(password) is False:
        abort(403)

    query = request.query.get('q')

    results = docstore.search(_index, query, conf.indexroot)

    ret = {
        "total": len(results),
        "hits": results
        }

    return ret_jsonp(request, ret)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Dipus: simple full-text search server')
    parser.add_argument('-c', '--config', nargs='?',
                        dest='conffile', action='store',
                        help='Config file path')
    args = parser.parse_args()
    conf = config.Config(args.conffile)

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s')

    run(app,
        host=conf.host, port=conf.port,
        reloader=True)
