#!/usr/bin/env python

import sys
import re

from distutils.core import setup
from os.path import join, dirname

version = re.search("__version__ = '([^']+)'",
                    open('acrylamid/__init__.py').read()).group(1)

requires = ['Jinja2>=2.4', 'Markdown>=2.0.1']
kw = {}

if sys.version_info < (3, 0):
    requires.append('translitcodec>=0.2')
else:
    kw['use_2to3'] = True
    kw['use_2to3_exclude_fixers'] = ['lib2to3.fixes.execfile', ]

if '--full' in sys.argv:
    requires.extend([
        'pygments',
        'docutils',
        'smartypants',
        'asciimathml',
        'pytextile',
    ])

setup(
    name='acrylamid',
    version=version,
    author='posativ',
    author_email='info@posativ.org',
    packages=[
        'acrylamid', 'acrylamid.filters', 'acrylamid.views', 'acrylamid.lib',
        'acrylamid.defaults', 'acrylamid.tasks'],
    scripts=['bin/acrylamid'],
    package_data={
        'acrylamid.filters': ['hyph/*.txt'],
        'acrylamid.defaults': ['misc/*', 'xhtml/*', 'html5/*']},
    url='https://github.com/posativ/acrylamid/',
    license='BSD revised',
    description='yet another static blog generator',
    data_files=[
        'README.rst',
    ],
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
    ],
    install_requires=requires,
    tests_require=[
        'tox',
        'konira',
        'cram'
    ],
    **kw
)
