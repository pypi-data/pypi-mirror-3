import fanstatic
import js.jquery

library = fanstatic.Library('jquery_cookie', 'resources')

cookie = fanstatic.Resource(
    library, 'jquery.cookie.js', depends=[js.jquery.jquery])
