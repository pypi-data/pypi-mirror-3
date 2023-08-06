# import filters into this namespace
from omdox.filters import *
from jinja2 import Environment, FileSystemLoader, Template


# set up the defaults

# exclude these directories and files
EXCLUDED = (
    '_build',
    'layout.html',
    '.DS_Store'
)
# which extentions to renderr?
EXTENTIONS = (
    '.html',
)
# the blocks to parse for code and markdown
CONTENT_BLOCK = 'content'
# exclude these files
FILTERS = (
   'pygmentize',
   'markdown',
)
# the jinja environment
JINJA_ENV = Environment( loader=FileSystemLoader('.'))
# overwrite the defaults from local conf
try:
    from conf import *
except ImportError:
    pass
