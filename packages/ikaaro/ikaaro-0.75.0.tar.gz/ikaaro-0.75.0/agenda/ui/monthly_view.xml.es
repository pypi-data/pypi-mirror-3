<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns:stl="http://www.hforge.org/xml-namespaces/stl" xmlns="http://www.w3.org/1999/xhtml">

<table width="100%">
  <colgroup width="14%" span="7"></colgroup>

  <tr>
    <th stl:repeat="day days_of_week">
      <span>${day/name}</span>
    </th>
  </tr>

  <tr valign="top" stl:repeat="week weeks">
    <td stl:repeat="day week" class="day add-event-area">
      <span stl:if="not day/selected" class="bold">${day/nday}</span>  <span stl:if="day/selected" class="cal-day-selected">${day/nday}</span>  <a stl:if="day/url" href="${day/url}" rel="fancybox" class="add-event">  <img height="16" width="16" src="${add_icon}"></img></a>

      <div style="background-color: ${event/color}" stl:repeat="event day/events" class="event ${event/status}">
      ${event/stream}
      </div>
    </td>
  </tr>
</table>

</stl:block>
