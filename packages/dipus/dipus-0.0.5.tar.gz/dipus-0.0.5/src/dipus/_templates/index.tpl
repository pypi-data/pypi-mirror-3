<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Dipus server</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- Le styles -->
    <link href="_static/css/bootstrap.css" rel="stylesheet">
    <link href="_static/css/dipus.css" rel="stylesheet">
    <style>
      body {
        padding-top: 60px; /* 60px to make the container go all the
        way to the bottom of the topbar */
      }
    </style>
    <link href="_static/css/bootstrap-responsive.css"
        rel="stylesheet">

    <!-- Le HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->

    <!-- Le fav and touch icons -->
    <link rel="shortcut icon" href="_static/ico/favicon.ico">
    <link rel="apple-touch-icon-precomposed" sizes="144x144"
		  href="_static/ico/apple-touch-icon-144-precomposed.png">
    <link rel="apple-touch-icon-precomposed" sizes="114x114"
		  href="_static/ico/apple-touch-icon-114-precomposed.png">
    <link rel="apple-touch-icon-precomposed" sizes="72x72"
		  href="_static/ico/apple-touch-icon-72-precomposed.png">
    <link rel="apple-touch-icon-precomposed"
		  href="_static/ico/apple-touch-icon-57-precomposed.png">
  </head>

  <body>

    <div class="navbar navbar-inverse navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container">
          <a class="btn btn-navbar" data-toggle="collapse"
			 data-target=".nav-collapse">
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </a>
          <a class="brand" href="/">Dipus</a>
          <div class="nav-collapse collapse">
            <ul class="nav">
              <li class="active"><a href="/">Search</a></li>
              <li><a href="#admin"><del>Admin</del></a></li>
            </ul>
          </div><!--/.nav-collapse -->
        </div>
      </div>
    </div>

    <div class="container">
	  <h2>Search</h2>
       <form id="search" class="form-search">
         <div id="indexes">
         </div>
         <input id="q" type="text" style="width: 300px" class="input-medium search-query">
         <button type="submit" class="btn">Search</button>
      </form>
	  <hr>
      <div id="search-results">
      </div>

    </div> <!-- /container -->

    <!-- Le javascript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster
    -->
    <script src="_static/js/jquery-1.8.1.min.js"></script>
    <script src="_static/js/search_dipus.js"></script>
  </body>
</html>
