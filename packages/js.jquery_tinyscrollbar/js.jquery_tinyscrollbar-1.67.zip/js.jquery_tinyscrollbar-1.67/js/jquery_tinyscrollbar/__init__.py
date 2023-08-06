import fanstatic
import js.jquery

library = fanstatic.Library('jquery_tinyscrollbar', 'resources')

jquery_tinyscrollbar = fanstatic.Resource(
    library,
    'jquery.tinyscrollbar.js',
    minified='jquery.tinyscrollbar.min.js',
    depends=[js.jquery.jquery]
)
