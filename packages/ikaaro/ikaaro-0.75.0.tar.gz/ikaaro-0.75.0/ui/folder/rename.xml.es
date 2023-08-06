<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns:stl="http://www.hforge.org/xml-namespaces/stl" xmlns="http://www.w3.org/1999/xhtml">

  <form action=";rename" method="post">
    <table style="margin-left: 20px; font-family: monospace;">
      <tr stl:repeat="item items">
        <td>
          <input type="hidden" value="${item/path}" name="paths"></input>
          ${item/path}
        </td>
        <td>
          ⇒ ${item/parent_path}<input style="font-family: monospace;" type="text" value="${item/name}" name="new_names"></input>
        </td>
      </tr>
    </table>
    <p><button type="submit" class="button-rename">Renombrar</button></p>
  </form>

</stl:block>
