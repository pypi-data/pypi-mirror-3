<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns:stl="http://www.hforge.org/xml-namespaces/stl" xmlns="http://www.w3.org/1999/xhtml">

  <p class="batchcontrol">${msg}</p>
  <ul stl:if="control" class="batch-pages">
    <li stl:if="previous">
      <a title="« Previous" href="${previous}" class="previous">« Previous</a>
    </li>
    <li stl:repeat="page pages">
      <a stl:if="page/uri" href="${page/uri}" class="${page/css}">${page/number}</a>  <span stl:if="not page/uri" class="ellipsis">…</span>
    </li>
    <li stl:if="next">
      <a title="Next »" href="${next}" class="next">Next »</a>
    </li>
  </ul>

</stl:block>
