from fanstatic import Library, Resource
from js.jquery import jquery

library = Library('jquery_elastic', 'resources')

elastic = Resource(library,
                   'jquery.elastic.source.js',
                   depends=[jquery])
