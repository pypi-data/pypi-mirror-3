# import filters into this namespace
import os
from omdox.filters import *
from jinja2 import Environment, FileSystemLoader, Template
import yaml
# 
try:
    stream = open('%s/config.yaml' % os.getcwd(), 'r')
    config = yaml.load(stream)
    stream.close()
except IOError:
    config = {}

# set up the defaults
# the name of the build dir
try:
    BUILD_DIR = config['BUILD_DIR']
except KeyError:
    BUILD_DIR = '_build'
# exclude these directories and files
try:
    EXCLUDED = config['EXCLUDED']
except KeyError:
    EXCLUDED = (
        '_build',
        '.sass-cache',
        'layout.html',
        '.DS_Store',
        'config.yaml',
        'conf.py',
        'conf.pyc',
    )
# which extentions to renderr?
try:
    EXTENSIONS = config['EXTENSIONS']
except KeyError:
    EXTENTIONS = (
        '.html',
        '.css',
    )
# the blocks to parse for code and markdown
try:
    CONTENT_BLOCK = config['CONTENT_BLOCK']
except KeyError:
    CONTENT_BLOCK = 'content'
# exclude these files
try:
    FILTERS = config['FILTERS']
except KeyError:
    FILTERS = (
       'pygmentize',
       'markdown',
    )
# the root for urls and paths - forward slash essential
try:
    ROOT = config['ROOT']
except KeyError:
    ROOT = '/'
JINJA_ENV = Environment( loader=FileSystemLoader('.'))
