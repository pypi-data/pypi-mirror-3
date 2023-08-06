from fanstatic import Library, Resource

library = Library('suggest.js', 'resources')

suggest = Resource(library, 'suggest.js',
                   minified='suggest.min.js')
