from fanstatic import Library, Resource, Group
from js.jquery import jquery

library = Library('lightbox', 'resources')

lightbox_css = Resource(library, 'css/lightbox.css',)
lightbox_js = Resource(library, 'js/lightbox.js', minified='js/lightbox.min.js',
                       depends=[jquery,])

lightbox = Group([lightbox_css, lightbox_js])
