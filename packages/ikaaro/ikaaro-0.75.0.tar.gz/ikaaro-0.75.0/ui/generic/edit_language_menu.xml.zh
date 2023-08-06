<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns:stl="http://www.hforge.org/xml-namespaces/stl" xmlns="http://www.w3.org/1999/xhtml">

<div stl:if="display" class="context-menu">
  <div class="context-menu-title">${title}</div>
  <form action="${action}" name="edit-languages" method="get" id="edit-language">
    <fieldset stl:if="items">
      <legend>Languages</legend>
      <ul>
        <li stl:repeat="item items" class="${item/class}">
          <input type="checkbox" id="edit-language-${item/name}" checked="${item/selected}" value="${item/name}" name="edit_language"></input>
          <label for="edit-language-${item/name}">${item/title}</label>
        </li>
      </ul>
    </fieldset>
    <fieldset stl:if="fields">
      <legend>Fields</legend>
      <ul>
        <li stl:repeat="field fields" class="${field/class}">
          <input type="checkbox" id="field-${field/name}" checked="${field/selected}" value="${field/name}" name="fields"></input>
          <label for="field-${field/name}">${field/title}</label>
        </li>
      </ul>
    </fieldset>
    <input stl:repeat="field hidden_fields" type="hidden" value="${field/value}" name="${field/name}"></input>
    <p>
      <button type="submit" class="button-ok">Update</button>
    </p>
  </form>
</div>

</stl:block>
