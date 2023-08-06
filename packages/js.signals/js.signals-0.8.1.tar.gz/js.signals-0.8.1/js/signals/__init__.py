from fanstatic import Library, Resource

library = Library('js-signals', 'resources')

signals = Resource(library, 'signals.js',
                   minified='signals.min.js')
