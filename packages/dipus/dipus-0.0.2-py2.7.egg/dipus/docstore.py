#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import Queue
import threading
from datetime import datetime

from whoosh import index
from whoosh import writing
from whoosh.fields import Schema, STORED, NGRAM, TEXT, DATETIME, ID
from whoosh.qparser import QueryParser
from whoosh.analysis import NgramAnalyzer, NgramWordAnalyzer
from whoosh import highlight


schema = Schema(
    title=TEXT(stored=True),
    path=ID(stored=True, unique=True),  # TODO: non-alphabetical filename.
    content=NGRAM(stored=True, phrase=False, minsize=2, maxsize=4),
    date=DATETIME(stored=True)
    )

num_worker_threads = 1  # no need to use multiple threads
occured_error = None
# TODO: implements the way to reset error.


def register_worker():
    def commit(posted):
        try:
            ixpath = os.path.join(posted['indexroot'],
                                  posted['_index'])
            ix = open_index(ixpath)
            writer = ix.writer()

            writer.update_document(
                title=posted['title'],
                path=posted['path'],
                date=datetime.now(),
                content=posted['message']
                )
            writer.commit(optimize=True)
            ix.close()
        except index.IndexError, e:  # use for returning error
            print "IndexError", e
            occured_error = e
        except writing.IndexingError, e:
            print "IndexingError", e
            occured_error = e

    while True:
        posted = taskq.get()
        commit(posted)
        taskq.task_done()


def open_index(indexdir):
    if not os.path.exists(indexdir):
        os.makedirs(indexdir)
        index.create_in(indexdir, schema)

    return index.open_dir(indexdir)


def isErrorOccured():
    ''' check if error is occured or not'''
    return occured_error


def register(posted, indexroot):
    """ register to index about the posted document
    Note about register itself will be done by register worker.
    This function is return ok if no error is occured.
    """
    posted['indexroot'] = indexroot
    taskq.put(posted)

    ret = {
        "ok": True,
        "_index": posted["_index"],
        "_path": posted["path"]
        }
    if isErrorOccured():
        ret['ok'] = False
        ret['message'] = str(occured_error)

    return ret


def search(_index, query, indexroot):
    if query is None:
        return {}
    ixpath = os.path.join(indexroot, _index)
    ix = open_index(ixpath)
    parser = QueryParser("content", schema=ix.schema)
    q = parser.parse(query.decode('utf-8'))

    ret = []
    with ix.searcher() as searcher:
        for r in searcher.search(q):
            # TODO: Without N-gramed text formatter
            # t = r.highlights('content', top=1)
            t = r['content']
            result = {
                "_index": _index,
                "_id": r.docnum,
                "_source": {
                "title": r['title'],
                "path": r['path'],
                "postDate": r['date'].isoformat(),
                "message": t
                }
            }
            ret.append(result)

    return ret

#
# Creating Task Queue due to commit is too slow
#

taskq = Queue.Queue()
for i in range(num_worker_threads):
    t = threading.Thread(target=register_worker)
    t.daemon = True
    t.start()


if __name__ == '__main__':
    ix = open_index("../index/test_rst")
    query = "テスト"
    parser = QueryParser("content", schema=ix.schema)
    q = parser.parse(query.decode('utf-8'))

    with ix.searcher() as searcher:
        for hit in searcher.search(q, terms=True):
            print "-----"
            print("Contains:", hit.matched_terms())
            print hit.highlights('content')


