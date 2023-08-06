<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns:stl="http://www.hforge.org/xml-namespaces/stl" xmlns="http://www.w3.org/1999/xhtml">

<form action=";edit_preferences" method="post">
  <fieldset>
    <legend>Edit Preferences</legend>
    <table>
      <tr>
        <td>
          <label for="user-language">Preferred Language</label>
          <br></br>
          <select name="user_language" id="user-language">
            <option value="">-- not defined --</option>
            <option stl:repeat="language languages" selected="${language/is_selected}" value="${language/code}">${language/name}</option>
          </select>
        </td>
      </tr>
      <tr>
        <td>
          <label for="user-language">Timezone</label>
          <br></br>
          <select name="user_timezone" id="user-timezone">
            <option value="">-- not defined (use server's local time) --</option>
            <option stl:repeat="timezone timezones" selected="${timezone/is_selected}" value="${timezone/name}">${timezone/name}</option>
          </select>
        </td>
      </tr>
    </table>
    <p>
    <button type="submit" class="button-ok">Save</button>
    </p>
  </fieldset>
</form>

</stl:block>
