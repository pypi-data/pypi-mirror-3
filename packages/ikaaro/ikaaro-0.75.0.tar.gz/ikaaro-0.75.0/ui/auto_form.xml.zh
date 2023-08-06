<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns:stl="http://www.hforge.org/xml-namespaces/stl" xmlns="http://www.w3.org/1999/xhtml">

${before}

<form enctype="${enctype}" stl:omit-tag="not actions" id="${form_id}" class="autoform" method="${method}" name="autoform" onsubmit="${onsubmit}">
  <fieldset>
    <legend stl:if="title">${title}</legend>
    <p stl:if="description">${description}</p>
    <stl:block stl:repeat="field fields_list">${field}</stl:block>
    <div stl:if="actions" class="autoform-actions">
      <stl:block stl:repeat="action actions">${action}</stl:block>
    </div>
  </fieldset>
  <script type="text/javascript">
    document.getElementById("${first_widget}").focus();
  </script>
</form>

${after}

</stl:block>
