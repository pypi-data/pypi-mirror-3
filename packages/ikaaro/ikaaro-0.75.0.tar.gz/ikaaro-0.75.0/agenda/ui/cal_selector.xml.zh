<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns:stl="http://www.hforge.org/xml-namespaces/stl" xmlns="http://www.w3.org/1999/xhtml">

  <div id="cal-selector">

    <form method="get" id="attributes">
      <input size="10" type="hidden" class="dateField" id="date" value="${start}" name="start"></input>
      <span id="mini-cal-button"></span>
      <script type="text/javascript">
        function selectDate(calendar, date) {
          $("#date").val(date);
          if (calendar.dateClicked) {
            $("#attributes").submit();
          }
        };
        jQuery( "input.dateField" ).dynDateTime({
          ifFormat: "%Y-%m-%d",
          onSelect: function(calendar, date){selectDate(calendar, date);},
          firstDay: ${first_weekday},
          button: ".next()" });
      </script>
    </form>

    <ul id="cal-selector-today-link">
      <li>
        <a title="Come back to today" href="${link_today/link}">${link_today/title}</a>
      </li>
    </ul>

    <ul id="cal-selector-navigation-links">
      <li>
        <a href="${navigation_links/previous/link}">«</a>
      </li>
      <li>
        <a href="${navigation_links/next/link}">»</a>
      </li>
    </ul>

    <span id="cal-selector-title">${title}</span>

    <ul id="cal-selector-view-links">
      <li stl:repeat="link calendar_view_links" class="${link/css}">
        <a href="${link/link}" class="${link/css}">${link/title}</a>
      </li>
    </ul>
    <div class="clear"></div>

  </div>

</stl:block>
