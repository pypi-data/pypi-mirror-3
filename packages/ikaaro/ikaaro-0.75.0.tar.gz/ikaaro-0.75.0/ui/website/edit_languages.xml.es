<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns:stl="http://www.hforge.org/xml-namespaces/stl" xmlns="http://www.w3.org/1999/xhtml">

  <!-- Edit Languages -->
  <fieldset>
    <legend>Edit the active languages</legend>
    <form action="" id="browse-list" method="post">
      <table summary="Configuration des langues">
        <thead>
          <tr>
            <th>Default</th>
            <th>Nombre</th>
            <th>Código</th>
          </tr>
        </thead>
        <tbody>
          <tr stl:repeat="language active_languages" class="${repeat/language/even}">
            <td stl:if="language/isdefault">Sí</td>
            <td stl:if="not language/isdefault">
              <input class="checkbox" type="checkbox" value="${language/code}" name="codes"></input>
            </td>
            <td>${language/name}</td>
            <td>${language/code}</td>
          </tr>
        </tbody>
      </table>
      <p>
        <button name="action" type="submit" value="change_default_language" class="button-ok">Change default</button>  <button name="action" type="submit" value="remove_languages" class="button-delete">Remove</button>
      </p>
    </form>
  </fieldset>

  <br></br>

  <!-- Add Language -->
  <fieldset>
    <legend>Agregar otro idioma</legend>
    <form action="" method="post">
      <select id="new-language" name="code">
        <option value="">Elije un idioma</option>
        <option stl:repeat="language not_active_languages" value="${language/code}">${language/name}</option>
      </select>
      <button name="action" type="submit" value="add_language" class="button-ok">Agregar</button>
    </form>
  </fieldset>

</stl:block>
