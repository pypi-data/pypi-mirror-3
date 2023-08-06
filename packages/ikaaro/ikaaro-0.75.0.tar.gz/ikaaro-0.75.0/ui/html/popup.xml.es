<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns:stl="http://www.hforge.org/xml-namespaces/stl" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>${text/title}</title>
    <!-- CSS -->
    <link stl:repeat="style styles" type="text/css" href="${style}" rel="stylesheet"></link>
    <script src="/ui/jquery.js" type="text/javascript"></script>
    <script src="/ui/javascript.js" type="text/javascript"></script>
    <script type="text/javascript" src="${script}" stl:repeat="script scripts"></script>
    <script type="text/javascript">
      $(document).ready(function() {
        tabme();
      })
      ${additional_javascript}
    </script>
  </head>

  <body class="popup">
    <div id="body">

      <!-- tabs -->
      <p class="tabme">
        <a href="#browse" onclick="tabme_show(event, this)" stl:if="show_browse">Browse</a>  <a href="#external" onclick="tabme_show(event, this)" stl:if="show_external">External Link</a>  <a href="#insert" onclick="tabme_show(event, this)" stl:if="show_insert">Insert</a>  <a href="#upload" onclick="tabme_show(event, this)" stl:if="show_upload">Upload</a>
      </p>

      <!-- Message -->
      <div stl:if="message" id="message">${message}</div>

      <!-- Browse -->
      <div stl:if="show_browse" id="browse">
        <h3>${text/browse}</h3>
        <!-- Breadcrumb -->
        <div id="maintitle">
          <div id="breadcrumbs">
            <label>Localización:</label>
            <span stl:repeat="x breadcrumb">
              <a title="${x/title}" href="${x/url}">${x/short_title}</a> /
            </span>
          </div>
        </div>
        <div class="clear"></div>
        ${browse_table}
      </div>

      <!-- External Link -->
      <div stl:if="show_external" id="external">
        <fieldset>
          <legend>${text/extern}</legend>
          <form>
            <table cellpadding="0" cellspacing="0">
              <tr>
                <td>
                  <label for="uri">URI</label><br></br>
                  <input size="40" id="uri" type="text" value="http://" name="uri"></input>
                </td>
              </tr>
            </table>
            <br></br>
            <button type="button" value="" onclick="select_element('${element_to_add}', $('#uri').val(), '');" class="button-ok"> Agregar </button>
          </form>
        </fieldset>
      </div>

      <!-- New Web or Wiki Page -->
      <div stl:if="show_insert" id="insert">
        <fieldset>
          <legend>${text/insert}</legend>
          <form action="${text/method}#insert" method="post">
            <input type="hidden" value="${target_path}" name="target_path"></input>
            <input type="hidden" value="${target_id}" name="target_id"></input>  <input type="hidden" value="${mode}" name="mode"></input>
            <input type="hidden" value="" name="name"></input>
            <table cellpadding="0" cellspacing="0">
              <tr>
                <td>
                  <label for="title">Title</label><br></br>
                  <input size="40" id="title" type="text" name="title"></input>
                </td>
              </tr>
            </table>
            <br></br>
            <button name="action" type="submit" value="add_resource" class="button-ok">Aceptar</button>
          </form>
        </fieldset>
      </div>

      <!-- Upload -->
      <div stl:if="show_upload" id="upload">
        <fieldset>
          <legend>${text/upload}</legend>
          <form action="${text/method}#upload" enctype="multipart/form-data" method="post">
            <input type="hidden" value="${target_path}" name="target_path"></input>
            <input type="hidden" value="${target_id}" name="target_id"></input>
            <input id="mode" type="hidden" value="${mode}" name="mode"></input>
            <table cellpadding="0" cellspacing="0">
              <tr>
                <td>
                  <label for="title">Title</label><br></br>
                  <input size="40" id="title" type="text" name="title"></input>
                </td>
              </tr>
              <tr>
                <td>
                  <label for="file">Fichero</label><br></br>
                  <input size="35" id="file" type="file" name="file"></input>
                </td>
              </tr>
            </table>
            <br></br>
            <button name="action" type="submit" value="upload" class="button-upload">Upload</button>
          </form>
        </fieldset>
      </div>

    </div>
  </body>
</html>
