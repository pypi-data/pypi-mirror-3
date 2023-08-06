# import filters into this namespace
from omdox.filters import *


# set up the defaults
# exclude these directories
EXCLUDED_DIRNAMES = (
    '_build',
)
# the blocks to parse for code and markdown
CONTENT_BLOCK = 'content'
# exclude these files
EXCLUDED_FILENAMES = (
    'layout.html',
)
# use these filters when rendering
FILTERS = (
   'pygmentize',
   'markdown',
)

# overwrite the defaults from local conf
try:
    from conf import *
except ImportError:
    pass
