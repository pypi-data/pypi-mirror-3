#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# http://countergram.com/youtube-in-rst
# License: MIT
#
# XXX: try https://hg.rafaelmartins.eng.br/blohg/file/a09f8f0c6cad/blohg/rst/directives.py

from docutils import nodes

match = ['youtube', 'yt']


CODE = """\
<object type="application/x-shockwave-flash"
        width="%(width)s"
        height="%(height)s"
        class="youtube-embed"
        data="http://www.youtube.com/v/%(yid)s">
    <param name="movie" value="http://www.youtube.com/v/%(yid)s"></param>
    <param name="wmode" value="transparent"></param>%(extra)s
</object>
"""

<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/B9215EwPXrA" frameborder="0" allowfullscreen></iframe>

PARAM = """\n    <param name="%s" value="%s"></param>"""


def youtube(name, args, options, content, lineno,
            contentOffset, blockText, state, stateMachine):
    """ Restructured text extension for inserting youtube embedded videos.

    Usage example::

    ::

        .. youtube:: asdfjkl
            width=600
            height=400
            someOtherParam=value
    """
    if len(content) == 0:
        return
    string_vars = {
        'yid': content[0],
        'width': 460,
        'height': 390,
        'extra': ''
        }
    extra_args = content[1:] # Because content[0] is ID
    extra_args = [ea.strip().split("=") for ea in extra_args] # key=value
    extra_args = [ea for ea in extra_args if len(ea) == 2] # drop bad lines
    extra_args = dict(extra_args)
    if 'width' in extra_args:
        string_vars['width'] = extra_args.pop('width')
    if 'height' in extra_args:
        string_vars['height'] = extra_args.pop('height')
    if extra_args:
        params = [PARAM % (key, extra_args[key]) for key in extra_args]
        string_vars['extra'] = "".join(params)
    return [nodes.raw('', CODE % (string_vars), format='html')]


def makeExtension():
    youtube.content = True
    return youtube
