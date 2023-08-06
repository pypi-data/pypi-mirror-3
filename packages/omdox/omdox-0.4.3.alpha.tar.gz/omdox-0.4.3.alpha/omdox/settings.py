# import filters into this namespace
from omdox.filters import *
from jinja2 import Environment, FileSystemLoader, Template


# set up the defaults
# the name of the build dir
BUILD_DIR = '_build'
# exclude these directories and files
EXCLUDED = (
    '_build',
    '.sass-cache',
    'layout.html',
    '.DS_Store',
    'conf.py',
    'conf.pyc',
)
# which extentions to renderr?
EXTENTIONS = (
    '.html',
    '.css',
)
# the blocks to parse for code and markdown
CONTENT_BLOCK = 'content'
# exclude these files
FILTERS = (
   'pygmentize',
   'markdown',
)
# the root for urls and paths - forward slash essential
ROOT = '/'
JINJA_ENV = Environment( loader=FileSystemLoader('.'))
# overwrite the defaults from local conf
try:
    from conf import *
except ImportError, e:
    pass
