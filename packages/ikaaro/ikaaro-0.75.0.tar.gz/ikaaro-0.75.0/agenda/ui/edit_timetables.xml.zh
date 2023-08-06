<?xml version="1.0" encoding="UTF-8"?>
<stl:block xmlns:stl="http://www.hforge.org/xml-namespaces/stl" xmlns="http://www.w3.org/1999/xhtml">



<form action=";edit_timetables" method="post" id="edit-timetables">
  <fieldset>
    <legend>Edit the timetable grid</legend>
    <p>
    You can specify timetables to limit the range when an event can be set.
    </p>
    <table class="form">
      <tr stl:repeat="timetable timetables">
        <td>
          <input class="checkbox" type="checkbox" value="${timetable/index}" name="ids"></input>
        </td>
        <td>
          From <input size="5" name="${timetable/startname}" type="text" value="${timetable/start}" maxlength="5"></input>
        </td>
        <td style="padding-left: 10px;">
          to <input size="5" name="${timetable/endname}" type="text" value="${timetable/end}" maxlength="5"></input>
        </td>
      </tr>
      <tr>
        <td></td>
        <td>
          From <input size="5" name="new_start" type="text" value="--:--" maxlength="5"></input>
        </td>
        <td style="padding-left: 10px;">
          to <input size="5" name="new_end" type="text" value="--:--" maxlength="5"></input>  <button name="action" type="submit" value="add" class="button-add">Add</button>
        </td>
      </tr>
    </table>

    <br></br>
    <button name="action" type="submit" value="remove" class="button-delete">Remove</button>  <button name="action" type="submit" value="update" class="button-ok">Update</button>
  </fieldset>
</form>

</stl:block>
