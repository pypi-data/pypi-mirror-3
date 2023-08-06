<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns:stl="http://www.hforge.org/xml-namespaces/stl" xmlns="http://www.w3.org/1999/xhtml">

<div class="block-widget block-widget-${name}">
  <div stl:if="title">
    <label for="${name}" class="title">${title}</label>  <span title="This field is required" stl:if="mandatory" class="field-is-missing">*</span>  <span title="${tip}" stl:if="tip">(?)</span>
  </div>
  <div class="field-error" stl:if="error">${error}</div>
  <div stl:repeat="widget widgets" class="widget">${widget}</div>
</div>
<div class="clear" stl:if="endline"></div>

</stl:block>
