from fanstatic import Library, Resource

library = Library('modernizr', 'resources')

modernizr = Resource(library, 'modernizr.js', minified='modernizr-min.js')
