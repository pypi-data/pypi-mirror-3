import fanstatic

import js.jqueryui

library = fanstatic.Library('jquery-timepicker-addon', 'resources')

timepicker_css = fanstatic.Resource(library, 'jquery-ui-timepicker-addon.css')

timepicker_js = fanstatic.Resource(library, 'jquery-ui-timepicker-addon.js',
    depends=[js.jqueryui.jqueryui])

timepicker = fanstatic.Group([timepicker_css, timepicker_js])

timepicker_nl = fanstatic.Resource(library,
    'localization/jquery-ui-timepicker-nl.js', depends=[timepicker])
