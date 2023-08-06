import fanstatic

Library = fanstatic.Library('gocept.datetimewidget', 'resources')

calendar = fanstatic.Resource(
    Library, 'calendar.js')

calendar_setup = fanstatic.Resource(
    Library,
    'calendar-setup.js',
    depends=[calendar])

calendar_css_blue = fanstatic.Resource(
    Library, 'calendar-blue.css')

calendar_css_brown = fanstatic.Resource(
    Library, 'calendar-brown.css')

calendar_css_green = fanstatic.Resource(
    Library, 'calendar-green.css')

calendar_css_system = fanstatic.Resource(
    Library, 'calendar-system.css')

calendar_css_tas = fanstatic.Resource(
    Library, 'calendar-tas.css')

calendar_css_win2k = fanstatic.Resource(
    Library, 'calendar-win2k-1.css')

calendar_css_win2k_cold = fanstatic.Resource(
    Library, 'calendar-win2k-cold-1.css')

calendar_lang_al = fanstatic.Resource(
    Library, 'languages/calendar-al.js')

calendar_lang_bg = fanstatic.Resource(
    Library, 'languages/calendar-bg.js')

calendar_lang_big5 = fanstatic.Resource(
    Library, 'languages/calendar-big5.js')

calendar_lang_br = fanstatic.Resource(
    Library, 'languages/calendar-br.js')

calendar_lang_ca = fanstatic.Resource(
    Library, 'languages/calendar-ca.js')

calendar_lang_cs_win = fanstatic.Resource(
    Library, 'languages/calendar-cs-win.js')

calendar_lang_da = fanstatic.Resource(
    Library, 'languages/calendar-da.js')

calendar_lang_de = fanstatic.Resource(
    Library, 'languages/calendar-de.js')

calendar_lang_en = fanstatic.Resource(
    Library, 'languages/calendar-en.js')

calendar_lang_es = fanstatic.Resource(
    Library, 'languages/calendar-es.js')

calendar_lang_fr = fanstatic.Resource(
    Library, 'languages/calendar-fr.js')

calendar_lang_hu = fanstatic.Resource(
    Library, 'languages/calendar-hu.js')

calendar_lang_it = fanstatic.Resource(
    Library, 'languages/calendar-it.js')

calendar_lang_ja = fanstatic.Resource(
    Library, 'languages/calendar-ja.js')

calendar_lang_lt = fanstatic.Resource(
    Library, 'languages/calendar-lt.js')

calendar_lang_lv = fanstatic.Resource(
    Library, 'languages/calendar-lv.js')

calendar_lang_nl = fanstatic.Resource(
    Library, 'languages/calendar-nl.js')

calendar_lang_pt = fanstatic.Resource(
    Library, 'languages/calendar-pt.js')

calendar_lang_ro = fanstatic.Resource(
    Library, 'languages/calendar-ro.js')

calendar_lang_ru = fanstatic.Resource(
    Library, 'languages/calendar-ru.js')

calendar_lang_sp = fanstatic.Resource(
    Library, 'languages/calendar-sp.js')

calendar_lang_zh = fanstatic.Resource(
    Library, 'languages/calendar-zh.js')

datetimewidget = fanstatic.Resource(
    Library, 'datetimewidget.js',
    depends=[calendar,
             calendar_setup,
             calendar_css_system,
             calendar_lang_en])
