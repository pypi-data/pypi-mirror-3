import os
from fanstatic import Library, Resource
from js.jquery import jquery

library = Library('jquery_iphonecheckboxes', 'resources')



iphonecheckboxes_css = Resource(
    library,
    'style.css',
    depends=[jquery]
)

iphonecheckboxes_js = Resource(
    library,
    os.path.join('jquery','iphone-style-checkboxes.js'),
    depends=[jquery, iphonecheckboxes_css]
)

iphonecheckboxes = iphonecheckboxes_js
