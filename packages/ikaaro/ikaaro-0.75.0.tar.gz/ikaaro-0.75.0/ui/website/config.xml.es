<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns:stl="http://www.hforge.org/xml-namespaces/stl" xmlns="http://www.w3.org/1999/xhtml">

  <form action="" stl:if="newmodules" method="post">
    <fieldset>
      <legend>New modules</legend>
      <p>
      New modules have been detected, pleae click the button below to initialize them:
      </p>
      <ul>
        <li stl:repeat="module newmodules">${module}</li>
      </ul>
      <button type="submit" class="button-ok">Initialize new modules</button>
    </fieldset>
    <br></br>
  </form>

  <stl:block stl:repeat="group groups">
    <h3>${group/title}</h3>
    <table stl:repeat="item group/items" class="new-resource-thumb">
      <tr>
        <td valign="top" style="width: 48px">
          <a href="${item/url}"><img alt="" src="${item/icon}"></img></a>
        </td>
        <td valign="top">
          <a href="${item/url}">${item/title}</a>
          <p>${item/description}</p>
        </td>
      </tr>
    </table>
    <div class="clear"></div>
  </stl:block>

</stl:block>
