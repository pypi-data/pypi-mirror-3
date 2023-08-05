import fanstatic

import js.jqueryui

library = fanstatic.Library('jquery-timepicker-addon', 'resources')

timepicker_css = fanstatic.Resource(library, 'jquery-ui-timepicker-addon.css')

timepicker_js = fanstatic.Resource(library, 'jquery-ui-timepicker-addon.js',
    depends=[js.jqueryui.jqueryui])

timepicker = fanstatic.Group([timepicker_css, timepicker_js])

timepicker_ca = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-ca.js', depends=[timepicker])

timepicker_cs = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-cs.js', depends=[timepicker])

timepicker_de = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-de.js', depends=[timepicker])

timepicker_el = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-el.js', depends=[timepicker])

timepicker_es = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-es.js', depends=[timepicker])

timepicker_et = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-et.js', depends=[timepicker])

timepicker_fi = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-fi.js', depends=[timepicker])

timepicker_fr = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-fr.js', depends=[timepicker])

timepicker_he = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-he.js', depends=[timepicker])

timepicker_hu = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-hu.js', depends=[timepicker])

timepicker_id = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-id.js', depends=[timepicker])

timepicker_it = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-it.js', depends=[timepicker])

timepicker_ja = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-ja.js', depends=[timepicker])

timepicker_lt = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-lt.js', depends=[timepicker])

timepicker_nl = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-nl.js', depends=[timepicker])

timepicker_pl = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-pl.js', depends=[timepicker])

timepicker_pt_BR = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-pt-BR.js', depends=[timepicker])

timepicker_pt = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-pt.js', depends=[timepicker])

timepicker_ro = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-ro.js', depends=[timepicker])

timepicker_ru = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-ru.js', depends=[timepicker])

timepicker_sk = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-sk.js', depends=[timepicker])

timepicker_tr = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-tr.js', depends=[timepicker])

timepicker_vi = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-vi.js', depends=[timepicker])
