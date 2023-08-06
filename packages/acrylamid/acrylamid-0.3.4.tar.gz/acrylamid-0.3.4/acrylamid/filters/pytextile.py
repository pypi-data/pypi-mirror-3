# Copyright 2012 sebix <szebi@gmx.at>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

from acrylamid.filters import Filter
from acrylamid.errors import AcrylamidException

try:
    from textile import textile
except ImportError:
    textile = None


class PyTextile(Filter):

    match = ['Textile', 'textile', 'pytextile', 'PyTextile']
    version = '1.0.0'

    conflicts = ['Markdown', 'reStructuredText', 'HTML', 'Pandoc']
    priority = 70.0

    def init(self, conf, env):

        if textile is None:
            raise ImportError('Textile: PyTextile not available')

    def transform(self, text, entry, *args):

        return textile(text)
