from fanstatic import Library, Resource
from js.jquery import jquery

library = Library('jquery_tools', 'resources')

# Define the resources in the library like this.
# For options and examples, see the fanstatic documentation.
jquery_tools = Resource(library, 'jquery.tools.min.js', depends=[jquery,])
