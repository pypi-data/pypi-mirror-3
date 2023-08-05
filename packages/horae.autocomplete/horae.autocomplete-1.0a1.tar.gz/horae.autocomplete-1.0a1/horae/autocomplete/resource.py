from fanstatic import Library, Resource
from js.jqueryui import jqueryui

library = Library('horae.autocomplete', 'static')

css = Resource(library, 'autocomplete.css')
js = Resource(library, 'autocomplete.js', depends=[jqueryui, ])
