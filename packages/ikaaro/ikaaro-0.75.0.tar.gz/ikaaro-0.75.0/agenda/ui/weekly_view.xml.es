<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns:stl="http://www.hforge.org/xml-namespaces/stl" xmlns="http://www.w3.org/1999/xhtml">

  <table width="100%" border="0" class="timetable">
    <tr>
      <th></th>
      <th stl:repeat="header timetable_data/headers" colspan="${header/width}" class="${header/class}">
        ${header/header}
      </th>
    </tr>

    <tr stl:repeat="row timetable_data/body">
      <th width="9%" class="time">
        ${row/start}-${row/end}
      </th>
      <stl:block stl:repeat="item row/items">
        <stl:block stl:repeat="cell item/cells">
          <div stl:if="cell/new">${cell/ns}</div>

          <div stl:if="cell/free">
            <td valign="top" colspan="${cell/colspan}" class="free add-event-area">
              <a stl:if="cell/newurl" href="${cell/newurl}" rel="fancybox" class="add-event">
                <img height="16" width="16" src="${add_icon}"></img>
              </a>
            </td>
          </div>
        </stl:block>
      </stl:block>
    </tr>

  <!-- FULL DAYS SPECIAL BEHAVIOUR -->
    <tr id="full-day-events" stl:if="timetable_data/full_day_events">
      <th class="time">Full day</th>
      <td valign="top" colspan="${item/width}" stl:repeat="item timetable_data/full_day_events">
        <table width="100%" class="event">
          <tr stl:repeat="event item/events">
            ${event/ns}
          </tr>
        </table>
      </td>
    </tr>
  </table>

</stl:block>
