from fanstatic import Library, Resource

library = Library('css3_github_buttons',
                  'resources/css3-github-buttons',
                  ignores=('*.txt',
                           '*.md',
                           '*.html',
                           '\.*')
                 )

buttons = Resource(library,
                   'gh-buttons.css'
                  )

# Define the resources in the library like this.
# For options and examples, see the fanstatic documentation.
# resource1 = Resource(library, 'style.css')
