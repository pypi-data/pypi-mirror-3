import os
from distutils.core import setup
from omdox import get_version

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

setup(
    name='omdox',
    version=get_version(),
    license = 'BSD 3 Clause',
    description='A lightweight documentation builder.',
    long_description=open('README.md').read(),
    author='Obscure Metaphor',
    url='https://github.com/obscuremetaphor/omdox',
    author_email='hello@obscuremetaphor.co.uk',
    packages=[
        'omdox',
    ],
    classifiers=[
        'Topic :: Documentation',
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Documentation',
    ],
    scripts=[
        'bin/omdox'
    ],
    install_requires = [
        'jinja2',
        'pygments',
        'beautifulsoup4',
        'markdown2']
)
