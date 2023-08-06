<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="${language}" xmlns:stl="http://www.hforge.org/xml-namespaces/stl" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>${title}</title>
    <base href="${base_uri}"/>
    <!-- Meta -->
    <meta content="text/html; charset=UTF-8" http-equiv="Content-Type"></meta>
    <meta lang="${meta/lang}" content="${meta/content}" stl:repeat="meta meta_tags" name="${meta/name}"></meta>  <!-- Canonical URL for search engines -->  <link href="${canonical_uri}" rel="canonical"></link>  <!-- CSS -->  <link stl:repeat="style styles" type="text/css" href="${style}" rel="stylesheet"></link>
    <!-- JavaScript -->
    <script stl:repeat="script scripts" type="text/javascript" src="${script}"></script>
    <!-- Icon -->
    <link type="${favicon_type}" href="${favicon_href}" rel="shortcut icon"></link>
  </head>
  <body>
    <div id="page">
      ${location} ${message} ${body}
    </div>
  </body>
</html>
