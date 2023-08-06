#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import logging

from bottle import Bottle, route, run, request, response, abort
from bottle import SimpleTemplate
import simplejson

from docstore import register, search

import config


app = Bottle()
conf = None


def auth(password):
    ''' not implemented yet '''
    return True


@app.route('/')
def index():
    return "index"


@app.route('/<_index>', method='POST')
def updateDocument(_index):
    password = request.forms.get('password')

    if auth(password) is False:
        abort("Forbidden")

    path = request.forms.get('path')
    if not path:
        abort(400, "path is not set")

    message = request.forms.get('message')
    if not message:
        abort(400, "message is not set")

    title = request.forms.get('title')
    if not title:
        title = ""
        
    posted = {
        '_index': _index.decode('utf-8'),
        'path': path.decode('utf-8'),
        'message': message.decode('utf-8'),
        'title': title.decode('utf-8')
        }

    ret = register(posted, conf.indexroot)

    return simplejson.dumps(ret)


@app.route('/<_index>/_search')
def query(_index):
    password = request.forms.get('password')
    if auth(password) is False:
        abort("Forbidden")

    query = request.query.get('q')

    results = search(_index, query, conf.indexroot)

    ret = {
        "total": len(results),
        "hits": results
        }


    json_response = simplejson.dumps(ret)
    response.content_type = 'application/json; charset=utf-8'

    callback_function = request.GET.get('callback')
    if callback_function:
        json_response = ''.join([callback_function, '(', json_response, ')'])

    return json_response


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Dipus: simple full-text search server')
    parser.add_argument('-c', '--config', nargs=1,
                        dest='conffile', action='store',
                        help='Config file path')
    args = parser.parse_args()

    if args.conffile is None:  # FIXME: why nargs ignored?
        parser.print_help()
        exit(0)

    conf = config.Config(args.conffile[0])
    
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s')

    run(app,
        host=conf.host, port=conf.port,
        reloader=True)
