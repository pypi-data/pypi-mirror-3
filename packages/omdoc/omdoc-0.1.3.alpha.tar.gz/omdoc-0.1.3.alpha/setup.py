import os
from distutils.core import setup
from omdoc import get_version

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

setup(
    name='omdoc',
    version=get_version(),
    license = 'BSD 3 Clause',
    description='A lightweight documentation builder.',
    long_description=open('README.md').read(),
    author='Obscure Metaphor',
    url='https://github.com/obscuremetaphor/omdoc',
    author_email='hello@obscuremetaphor.co.uk',
    packages=[
        'omdoc',
    ],
    classifiers=[
        'Topic :: Documentation',
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Documentation',
    ],
    scripts=[
        'bin/omdoc'
    ],
    install_requires = [
        'jinja2',
        'pygments',
        'beautifulsoup4',
        'markdown']
)
