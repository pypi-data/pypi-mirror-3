## OMDOC

OMDOC is a lightweight documentation builder that utilises [jinja2][0] templates as placeholders for markdown and code.

Code samples are parsed with [pygments][1] and the content is parsed with markdown.

You're in total control of how it looks, feels and responds to different ddevices.

## Features

### code

Any blocks of code inside code tags are parsed; eg

```<code lang="bash">
pip install omdoc
</code>```


An attempt is made to match the lang attribute against [known pygments lexers][2]. If no match is found it defaults to python.


## Installation

```pip install omdoc```

## Usage

1. Make folder for docs
2. Create layout.html
3. Create pages that inherit layout.html
4. style pages as you see fit
5. run ``omdoc``

Your documentation will now be in <docs>/_build


[0]: http://jinja.pocoo.org/docs/
[1]: http://pygments.org/
[2]: http://pygments.org/docs/lexers/
