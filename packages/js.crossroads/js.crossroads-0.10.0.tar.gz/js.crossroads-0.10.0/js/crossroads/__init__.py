from fanstatic import Library, Resource

library = Library('crossroads.js', 'resources')

crossroads = Resource(library, 'crossroads.js',
                      minified='crossroads.min.js')
