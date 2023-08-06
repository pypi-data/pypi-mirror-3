Dipus
=========

Dipus is a simple full-text search server using `Whoosh <http://packages.python.org/Whoosh/>`_. Dipus is
integrated to the `Sphinx document builder <http://sphinx.pocoo.org/>`_ .

You can search document quickly and with N-gram.


How to install
--------------------

::

  % pip install dipus

Dependencies
+++++++++++++++

- Python 2.7
- Sphinx
- whoosh
- simplejson
- bottle

How to Use
--------------

Start dipus server
+++++++++++++++++++++++++++++++++++

::

  python -m dipus.websetup -c conf.json

conf.json example

::

  {
    "port": 9876,
    "indexroot": "/path/to/test/index"
  }

Register sphinx document
+++++++++++++++++++++++++++++++++++

1. Add extention to your conf.py::

     extensions = ['dipus.dipusbuilder']
     dipus_host_url = "http://localhost:9876"
     dipus_doctitle = "test_rst"
     #dipus_docroot = "http://localhost/doc/test_rst"
     dipus_docroot = "file:///path/to/some/where/"

2. Run builder::

     % sphinx-build -b dipus source build

   CAUTHION: builder will *overwrite* _static/search_dipus.js and
   _template/search_dipus.html.

3. copy search file:

   Note: This required once when after you change conf.py dipus realated values.

     % cp _template/search_dipus.html _template_search.html

   If you have created your own search.html, please merge it.

4. make html as usual::

     % make html

Please note about builder is done quickly. But registeration itself on
the server is not so quick. Please be patiant until all your document
is registerd.



Search from sphinx document
++++++++++++++++++++++++++++++++






Requirements
----------------

- sphinx
- whoosh
- simplejson
- bottle
