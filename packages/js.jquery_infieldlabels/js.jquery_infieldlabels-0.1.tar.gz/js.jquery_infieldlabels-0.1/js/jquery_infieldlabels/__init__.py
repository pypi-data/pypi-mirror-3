from fanstatic import Library, Resource
from js.jquery import jquery

library = Library('jquery_infieldlabels', 'resources')

infieldlabels_js = Resource(
    library,
    'infieldlabels.js',
    minified='infieldlabels.min.js',
    depends=[jquery]
)

infieldlabels = infieldlabels_js
