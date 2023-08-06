from fanstatic import Library, Resource
from js.signals import signals

library = Library('crossroads.js', 'resources')

crossroads = Resource(library, 'crossroads.js',
                      minified='crossroads.min.js',
                      depends=[signals])
