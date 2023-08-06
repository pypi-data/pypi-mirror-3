from fanstatic import Library, Resource
from js.jquery import jquery

library = Library('js.html5_upload', 'resources')
html5_upload = Resource(library, 'html5_upload.js', depends=[jquery])
