from fanstatic import Library, Resource
import js.jquery

library = Library('jquery_mailcheck', 'resources')

mailcheck = Resource(library, 'jquery.mailcheck.js',
    minified='jquery.mailcheck.min.js',
    depends=[js.jquery.jquery])
