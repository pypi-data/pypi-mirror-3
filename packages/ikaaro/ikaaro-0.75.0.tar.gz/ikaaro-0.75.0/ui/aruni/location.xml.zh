<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns:stl="http://www.hforge.org/xml-namespaces/stl" xmlns="http://www.w3.org/1999/xhtml" stl:if="location">

  <!-- Location & Views-->
  <div id="location">
    <div stl:if="breadcrumb" id="breadcrumbs">
      <span stl:repeat="item breadcrumb"><a title="${item/name}" stl:omit-tag="not item/url" href="${item/url}">${item/short_name}</a><stl:inline stl:if="not repeat/item/end">/</stl:inline></span>
    </div>
    <div stl:if="tabs" id="tabs">
      [ <span stl:repeat="menu tabs" class="menu ${menu/class}">  <a href="${menu/name}">${menu/label}</a>  <stl:inline stl:if="not repeat/menu/end">|</stl:inline>  </span> ]
    </div>
  </div>
  <div class="clear"></div>

</stl:block>
