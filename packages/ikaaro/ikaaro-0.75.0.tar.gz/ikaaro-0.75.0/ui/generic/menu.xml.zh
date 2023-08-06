<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns:stl="http://www.hforge.org/xml-namespaces/stl" xmlns="http://www.w3.org/1999/xhtml">

<div stl:if="items" class="context-menu">
  <div class="context-menu-title">${title}</div>
  <ul>
    <li stl:repeat="item items" class="${item/class}">
      <img height="16" alt="" src="${item/src}" width="16" stl:if="item/src"></img>
      <a stl:omit-tag="not item/href" href="${item/href}">${item/title}</a>
    </li>
  </ul>
</div>

</stl:block>
