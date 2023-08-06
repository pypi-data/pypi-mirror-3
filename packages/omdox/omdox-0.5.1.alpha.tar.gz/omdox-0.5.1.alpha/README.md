## OMDOX

OMDOX is a lightweight documentation builder that utilises [jinja2][0] templates as placeholders for markdown and code.

Code samples are parsed with [pygments][1] and the content is parsed with markdown.

You're in total control of how it looks, feels and responds to different devices.

No magic, it's plain ol' html with a dash of jinja, markdown and pygments.

## Features


### Markdown 

All content inside of the {% block content %} is parsed as markdown.

### code

Any blocks of code inside code tags are parsed; eg


```<code lang="bash">
pip install omdox
</code>```


An attempt is made to match the lang attribute against [known pygments lexers][2]. If no match is found it defaults to python.



## Installation

```pip install omdox```

## Usage

1. Make folder for docs
2. Create layout.html inside of docs folder
2. Style as you see fit
3. Create documents that inherit layout.html in your /docs/ directory
5. cd '/docs/'
6. run ``omdox``

Your documentation will now be in /docs/_build

## Watching files for changes

You can run ``omdox --watch`` and only changed files will be built.

## What about static media?

Proceed as you would building a a normal site. Folders inside of `docs/` get copied into the final build. Just make sure to prefix all static media paths with the special template variable {{ROOT}}


## Settings

To override any default settings place a file called config.yaml in the root of the documentation and override any of the following values

* **BUILD_DIR** - the directory that the omdox will use to build the documents in.
* **EXCLUDED** - a tuple of files that should be excluded from the documentation build.
* **EXTENTIONS** - a tuple of extentions that will be tretated as jinja.
* **CONTENT_BLOCK** - the name of the block that will be rendered as markdown.
* **FILTERS** - a tuple of filters that the content block will be parsed through.
* **ROOT** - The root URL that will be used in templates to ensure paths to static media are correct

## Status

Early alpha.

## Issues

Create an issue, I'll be all over it like warm butter on hot bread.


### Writing Documentation 

OMDOX will not make you better at writing documentation, only practice will.

[0]: http://jinja.pocoo.org/docs/
[1]: http://pygments.org/
[2]: http://pygments.org/docs/lexers/
