from fanstatic import Library, Resource

library = Library('glyphicons', 'resources')

glyphicons = Resource(library, 'glyphicons.css',
                      minified='glyphicons.min.css')
