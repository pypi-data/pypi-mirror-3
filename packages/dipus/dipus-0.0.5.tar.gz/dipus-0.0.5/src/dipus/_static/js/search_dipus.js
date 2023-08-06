/*
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

jQuery.makeSearchSummary = function(text, keywords, hlwords) {
  var textLower = text.toLowerCase();
  var start = 0;
  $.each(keywords, function() {
    var i = textLower.indexOf(this.toLowerCase());
    if (i > -1)
      start = i;
  });
  start = Math.max(start - 120, 0);
  var excerpt = ((start > 0) ? '...' : '') +
  $.trim(text.substr(start, 240)) +
  ((start + 240 - text.length) ? '...' : '');
  var rv = $('<div class="context"></div>').text(excerpt);
  $.each(hlwords, function() {
	  var hlword = hlwords.join("").toLowerCase();
      rv = rv.highlightText(hlword, 'highlighted');
  });
  return rv;
};

/**
 *  Search Module
 */
var Search = {
  _dipus_url: "/_msearch/",
  _index: null,
  _pulse_status : -1,

  init : function (){
      var params = $.getQueryParameters();
      if (params.q) {
          var query = params.q[0];
          $('input[name="q"]')[0].value = query;
          this.performSearch(query);
      }
  },
  stopPulse : function() {
      this._pulse_status = 0;
  },

  startPulse : function() {
    if (this._pulse_status >= 0)
        return;
    function pulse() {
      Search._pulse_status = (Search._pulse_status + 1) % 4;
      var dotString = '';
      for (var i = 0; i < Search._pulse_status; i++)
        dotString += '.';
      Search.dots.text(dotString);
      if (Search._pulse_status > -1)
        window.setTimeout(pulse, 500);
    };
    pulse();
  },
	
  /**
   * perform a search for something
   */
  performSearch : function(query, indexes) {
	// create the required interface elements
    $('#search-results').text('');
    this.out = $('#search-results');
    this.title = $('<h2>' + _('Searching') + '</h2>').appendTo(this.out);
    this.dots = $('<span></span>').appendTo(this.title);
    this.status = $('<p style="display: none"></p>').appendTo(this.out);
    this.output = $('<ul class="search"/>').appendTo(this.out);


    $('#search-progress').text(_('Preparing search...'));
    this.startPulse();

    this.query(query, indexes);
  },

  query : function(query, indexes) {
	var hlterms = [];
    var highlightstring = '?highlight=' + $.urlencode(hlterms.join(" "));

	$('#search-progress').empty();

	var url = this._dipus_url +
		 "?q=" + $.urlencode(query) + 
		 "&indexes=" + $.urlencode(indexes.join(","));
	  $.ajax({
		  url: url,
		  dataType: 'jsonp',
		  success: function(json){
			  for(var i = 0; i < json.hits.length; i++){
				  var hit = json.hits[i];
				  var indexlabel = '<span class="label label-info">' + hit._index + '</span>';
				  var listItem = $('<li style="display:none"></li>');
				  var msgbody = hit._source.message;
				  listItem.append($('<a/>').attr('href',
												 hit._source.doc_url + "/" + 
												 hit._source.path + ".html" +
												 highlightstring + query).html(indexlabel + hit._source.title));
				  if (msgbody) {
					  listItem.append($.makeSearchSummary(msgbody, Array(query), Array(query)));
					  Search.output.append(listItem);
					  listItem.slideDown(5);
				  } else {
					  // no source available, just display title
					  Search.output.append(listItem);
					  listItem.slideDown(5);
				  }
			  };
			  Search.stopPulse();
			  Search.title.text('');  // just remove "Searching..."
			  if (json.hits.length === 0){
				  Search.status.text(_('Your search did not match any documents. Please make sure that all words are spelled correctly and that you\'ve selected enough categories.'));
			  }else{
				  Search.status.text(_('Search finished, found %s page(s) matching the search query.').replace('%s', json.hits.length));
              }
			  Search.status.fadeIn(500);
		  },
		  error: function(XMLHttpRequest, textStatus, errorThrown) {
			  console.log(textStatus, errorThrown);
		  }
	  });
  }
};

/**
 * get index list from dipus server 
 * and create table
 */
function get_index_list(){
	var url = "/_list/";
	$.ajax({
		url: url,
		dataType: 'jsonp',
		success: function(json){
			if (!json.list || json.list.length === 0){
				$('#indexes').text(_("No indexes"));
				return;
			}
			
			var table = $('<table class="table"></table>');
			var selected = "";
			for(var i =0 ; i < json.list.length; i++){
				var td = '<td><input type="checkbox"' + (i === 0 ? 'checked': "") + '>';
				td += '<label class="checkbox">' + json.list[i] + '</label> </td>';
				table.append($('<tr>' + td + '</tr>'));
				
			}
			$('#indexes').append(table);
		},
		error: function(XMLHttpRequest, textStatus, errorThrown) {
			console.log(textStatus, errorThrown);
		}
	});
};

/**
 *  * small helper function to urlencode strings
 *  */
jQuery.urlencode = encodeURIComponent;
/**
 *  * highlight a given string on a jquery object by wrapping it in
 *  * span elements with the given class name.
 *  */
jQuery.fn.highlightText = function(text, className) {
  function highlight(node) {
    if (node.nodeType == 3) {
      var val = node.nodeValue;
      var pos = val.toLowerCase().indexOf(text);
      if (pos >= 0 && !jQuery(node.parentNode).hasClass(className)) {
        var span = document.createElement("span");
        span.className = className;
        span.appendChild(document.createTextNode(val.substr(pos, text.length)));
        node.parentNode.insertBefore(span, node.parentNode.insertBefore(
          document.createTextNode(val.substr(pos + text.length)),
          node.nextSibling));
        node.nodeValue = val.substr(0, pos);
      }
    }
    else if (!jQuery(node).is("button, select, textarea")) {
      jQuery.each(node.childNodes, function() {
        highlight(this);
      });
    }
  }
  return this.each(function() {
    highlight(this);
  });
};

// TODO: i18n
function _(s){return s;}

$(document).ready(function() {
	$("#q").focus();
	get_index_list();
	$("#search").submit(function() {
		var indexes = [];
		$("input[type='checkbox']:checked").each( 
			function() { 
				indexes.push($(this).next('label').text());
			} 
		);

		var query = $("#q").val();
		if (query !== "" && indexes.length > 0){
			Search.performSearch(query, indexes);
		}
		return(false);
	});

});
