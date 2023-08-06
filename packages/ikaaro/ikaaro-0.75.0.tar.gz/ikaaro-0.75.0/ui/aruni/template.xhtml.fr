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

    <!-- Header -->
    <div id="header">
      <div id="links">
        <a title="${link/title}" stl:repeat="link usermenu" href="${link/href}" id="${link/id}">${link/title}</a>
      </div>
      <!-- Languages & Searchbar -->
      <table cellpadding="0" cellspacing="0" class="header-toolbar">
        <tr>
          <td class="languages">${languages}</td>
          <td class="search">
            <form action="/;browse_content" method="get">
              <input size="15" name="text" type="text" value="" class="search_box"></input>
            </form>
          </td>
        </tr>
      </table>
      <!-- Menu -->
      <ul id="menu" stl:if="menu">
        <li stl:repeat="menu menu" class="${menu/class}">
          <a title="${menu/title}" id="${menu/id}" href="${menu/path}" target="${menu/target}">${menu/title}</a>
        </li>
      </ul>
      <!-- Logo -->
      <a stl:if="logo_href" href="/" id="logo">
        <img src="${logo_href}"></img>
      </a>
      <div class="clear"></div>
    </div>

    <!-- Location & Views-->
    ${location}

    <!-- Body -->
    <div id="body">
      <h1 stl:if="page_title">${page_title}</h1>
      ${message}
      <table cellpadding="0" border="0" width="100%" cellspacing="0">
        <tr>
          <td valign="top" id="content">
            ${body}
          </td>
          <td valign="top" stl:if="context_menus" id="right">
            <stl:block stl:repeat="menu context_menus">${menu}</stl:block>
          </td>
        </tr>
      </table>
    </div>

    <!-- Footer -->
    <div id="footer">${footer}</div>
  </div>
  </body>
</html>
