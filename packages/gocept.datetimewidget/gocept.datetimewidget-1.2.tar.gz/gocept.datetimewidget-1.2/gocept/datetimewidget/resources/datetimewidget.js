var dtwLanguageLoaded = false;

function dateTimeWidgetLoadLanguageFile(url){
    // this method loads a languagefile for the datetimewidget
    // TODO: move this functionality into zc.resourcelibrary

    if (dtwLanguageLoaded==true){
        return;
    }
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = url;
    document.getElementsByTagName('head')[0].appendChild(script);
    dtwLanguageLoaded = true;
}


function dateSelected(cal, date) {
  cal.sel.value = date; // just update the date in the input field.
  if (cal.dateClicked && !cal.multiple)
    // if we add this call we close the calendar on single-click.
    // just to exemplify both cases, we are using this only for the 1st
    // and the 3rd field, while 2nd and 4th will still require double-click.
    cal.callCloseHandler();
}


function getMultipleDateClosedHandler(input_id, MA) {
  return function(cal) {
    var el = document.getElementById(input_id);

    // reset initial content.
    el.value = "";
    MA.length = 0;

    // sort dates in ascending order
    var date_keys = new Array();
    for (var i in cal.multiple)
      date_keys.push(i);
    date_keys.sort()

    // walk the calendar's multiple dates selection hash
    for (var j in date_keys) {
      i = date_keys[j];
      var d = cal.multiple[i];
      if (d) {
        el.value += d.print("%Y-%m-%d ");
        MA[MA.length] = d;
      }
    }
    cal.hide();
    return true;
  }
}

function enabledWeekdays(enabled_weekdays) {
  return function(date) {
    // Return true if the selected day should be disabled.
    weekday = date.getDay();
    for (var enabled_wd in enabled_weekdays) {
      if (weekday == enabled_weekdays[enabled_wd])
        return false;
    }
    return true;
  }
}
