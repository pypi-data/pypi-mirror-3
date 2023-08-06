from fanstatic import Library, Resource

library = Library('angularjs', 'resources')

angular = Resource(library, 'angular-1.0.1.js',
                   minified='angular-1.0.1.min.js')
