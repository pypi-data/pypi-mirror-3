from fanstatic import Library, Resource

library = Library('augment.js', 'resources')
augment = Resource(library, "augment.js", minified="augment.min.js")
