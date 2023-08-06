#!/usr/bin/env python
# -*- coding: utf-8 -*-

template = """/*
 *  * search_dipus
 *  * ~~~~~~~~~~~~~~
 *  *
 *  * Dipus JavaScript utilties for the full-text search.
 *  * This files is based on searchtools.js of Sphinx.
 *  *
 *  * :copyright: Copyright 2007-2012 by the Sphinx team.
 *  * :license: BSD, see LICENSE for details.
 *  *
 *  */


/**
 *  * helper function to return a node containing the
 *  * search summary for a given text. keywords is a list
 *  * of stemmed words, hlwords is the list of normal, unstemmed
 *  * words. the first one is used to find the occurance, the
 *  * latter for highlighting it.
 *  */

jQuery.makeSearchSummary = function(text, keywords, hlwords) {{
  var textLower = text.toLowerCase();
  var start = 0;
  $.each(keywords, function() {{
    var i = textLower.indexOf(this.toLowerCase());
    if (i > -1)
      start = i;
  }});
  start = Math.max(start - 120, 0);
  var excerpt = ((start > 0) ? '...' : '') +
  $.trim(text.substr(start, 240)) +
  ((start + 240 - text.length) ? '...' : '');
  var rv = $('<div class="context"></div>').text(excerpt);
  $.each(hlwords, function() {{
    rv = rv.highlightText(this, 'highlighted');
  }});
  return rv;
}};

/**
 *  Search Module
 */
var Search = {{
  _dipus_url: "{dipus_url}",
  _index: null,
  _pulse_status : -1,

  init : function (){{
      var params = $.getQueryParameters();
      if (params.q) {{
          var query = params.q[0];
          $('input[name="q"]')[0].value = query;
          this.performSearch(query);
      }}
  }},
  stopPulse : function() {{
      this._pulse_status = 0;
  }},

  startPulse : function() {{
    if (this._pulse_status >= 0)
        return;
    function pulse() {{
      Search._pulse_status = (Search._pulse_status + 1) % 4;
      var dotString = '';
      for (var i = 0; i < Search._pulse_status; i++)
        dotString += '.';
      Search.dots.text(dotString);
      if (Search._pulse_status > -1)
        window.setTimeout(pulse, 500);
    }};
    pulse();
  }},

  /**
   * perform a search for something
   */
  performSearch : function(query) {{
    // create the required interface elements
    this.out = $('#search-results');
    this.title = $('<h2>' + _('Searching') + '</h2>').appendTo(this.out);
    this.dots = $('<span></span>').appendTo(this.title);
    this.status = $('<p style="display: none"></p>').appendTo(this.out);
    this.output = $('<ul class="search"/>').appendTo(this.out);

    $('#search-progress').text(_('Preparing search...'));
    this.startPulse();

    this.query(query);
  }},

  query : function(query) {{
    var hlterms = [];
    var highlightstring = '?highlight=' + $.urlencode(hlterms.join(" "));

    $('#search-progress').empty();

    var url = this._dipus_url + "?q=" + $.urlencode(query);
      $.ajax({{
          url: url,
          dataType: 'jsonp',
          success: function(json){{
              for(var i = 0; i < json.hits.length; i++){{
                  var hit = json.hits[i];
                  var listItem = $('<li style="display:none"></li>');
                  var msgbody = hit._source.message;
                  if (DOCUMENTATION_OPTIONS.FILE_SUFFIX == '') {{
                      // dirhtml builder
                      var dirname = hit._source.path;
                      if (dirname.match(/\/index\/$/)) {{
                          dirname = dirname.substring(0, dirname.length-6);
                      }} else if (dirname == 'index/') {{
                          dirname = '';
                      }}
                      listItem.append($('<a/>').attr('href',
                                                     DOCUMENTATION_OPTIONS.URL_ROOT + dirname +
                                                     highlightstring + query).html(hit._source.title));
                  }} else {{
                      // normal html builders
                      listItem.append($('<a/>').attr('href',
                                                     hit._source.path + DOCUMENTATION_OPTIONS.FILE_SUFFIX +
                                                     highlightstring + query).html(hit._source.title));
                  }}
                  if (msgbody) {{
                      listItem.append($.makeSearchSummary(msgbody, Array(query), Array(query)));
                      Search.output.append(listItem);
                      listItem.slideDown(5);
                  }} else if (DOCUMENTATION_OPTIONS.HAS_SOURCE) {{
                      $.get(DOCUMENTATION_OPTIONS.URL_ROOT + '_sources/' +
                            hit._source.path + '.txt', function(data) {{
                                if (data != '') {{
                                    listItem.append($.makeSearchSummary(data, Array(query), hlterms));
                                    Search.output.append(listItem);
                                }}
                                listItem.slideDown(5);
                            }});
                  }} else {{
                      // no source available, just display title
                      Search.output.append(listItem);
                      listItem.slideDown(5);
                  }}
              }};
              Search.stopPulse();
              Search.title.text(_('Search Results'));
              if (json.hits.length === 0){{
                  Search.status.text(_('Your search did not match any documents. Please make sure that all words are spelled correctly and that you\\'ve selected enough categories.'));
              }}else{{
                  Search.status.text(_('Search finished, found %s page(s) matching the search query.').replace('%s', json.hits.length));
              }}
              Search.status.fadeIn(500);
          }},
          error: function(XMLHttpRequest, textStatus, errorThrown) {{
              console.log(textStatus, errorThrown);
          }}
      }});
  }}
}};

$(document).ready(function() {{
  Search.init();
}});
"""
