#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid.py

import sys
import os
import logging
from acrylamid.utils import yamllike

from os.path import exists, isfile, isdir, join

log = logging.getLogger('acrylamid.defaults')

def init(root='.', overwrite=False):
    
    dirs = ['%(entries_dir)s/', '%(layout_dir)s/', '%(output_dir)s/']
    files = {'conf.yaml': conf,
             '%(output_dir)s/blog.css': css,
             '%(layout_dir)s/main.html': main,
             '%(layout_dir)s/entry.html': entry,
             '%(layout_dir)s/articles.html': articles,
             '%(entries_dir)s/sample entry.txt': kafka}
             
    default = yamllike(conf)
    default['output_dir'] = default.get('output_dir', 'output/').rstrip('/')
    default['entries_dir'] = default.get('entries_dir', 'content/').rstrip('/')
    default['layout_dir'] = default.get('layout_dir', 'layouts/').rstrip('/')
    
    if root != '.' and not exists(root):
        os.mkdir(root)
                
    for directory in dirs:
        directory = join(root, directory % default)
        if exists(directory) and not isdir(directory):
            log.critical('Unable to create %s. Please remove this file', directory)
            sys.exit(1)
        elif not exists(directory):
            os.mkdir(directory)
            log.info('create  %s', directory)
        else:
            log.info('skip  %s already exists', directory)
    
    for path, content in files.iteritems():
        path = join(root, path % default)
        if exists(path) and not isfile(path):
            log.critical('%s must be a regular file' % path)
            sys.exit(1)
        elif not exists(path) or overwrite == True:
            f = open(path, 'w')
            f.write(content)
            f.close()
            log.info('create  %s', path)
        else:
            log.info('skip  %s already exists', path)


conf =  '''
blog_title: A descriptive blog title

author: anonymous
website: http://example.org/
email: info@example.org

www_root: http://example.org/
lang: de_DE
strptime: %d.%m.%Y, %H:%M
encoding: utf-8

disqus_shortname: yourname

views.filters: ['markdown+codehilite(css_class=highlight)', 'hyphenate']

views.index.filters: ['summarize', 'h1']
views.entry.filters: ['h1']
views.feeds.filters: ['h2']
'''.strip()

css = '''
@import url(pygments.css);
body {
  background-color: white; }

#blogheader {
  margin-bottom: 10px;
  padding: 10px;
  font-family: Palatino, "Times New Roman", serif;
  text-decoration: none;
  text-align: center; }
  #blogheader #blogtitle h2 {
    padding-top: 1.5em; }
    #blogheader #blogtitle h2 a {
      color: black;
      text-decoration: none; }
  #blogheader #mainlinks {
    padding: 1em; }
    #blogheader #mainlinks li {
      display: inline-block;
      margin: 0 2em 0 2em; }
    #blogheader #mainlinks a {
      color: black;
      text-decoration: none;
      font-family: Palatino, "Times New Roman", serif; }
      #blogheader #mainlinks a:hover {
        text-shadow: #888888 0px 0px 1px; }

#blogbody {
  margin: 0 auto;
  width: 800px; }
  #blogbody .posting {
    padding: 1em;
    margin-top: 64px;
    margin-bottom: 64px; }
    #blogbody .posting .postheader .subject {
      margin-bottom: -0.7em; }
      #blogbody .posting .postheader .subject a {
        color: black;
        font: bold medium Palatino, "Times New Roman";
        text-decoration: none; }
        #blogbody .posting .postheader .subject a:hover {
          text-shadow: #aaaaaa 0px 0px 2px; }
    #blogbody .posting .postheader .date {
      font: 0.7em "Georgia";
      float: right; }
    #blogbody .posting .postbody {
      text-align: justify;
      padding: 1em;
      font-family: Palatino, "Times New Roman", serif;
      font-size: 11pt; }
      #blogbody .posting .postbody h2 {
        font: 12pt Palatino, "Times New Roman", serif;
        font-weight: bold;
        color: #888888;
        border-bottom: 1px dotted #888888; }
      #blogbody .posting .postbody h3, #blogbody .posting .postbody h4 {
        font: 12pt Palatino, "Times New Roman", serif;
        font-weight: bold;
        color: #888888;
        padding-left: 4px; }
      #blogbody .posting .postbody a {
        text-decoration: none;
        color: #cc0000; }
        #blogbody .posting .postbody a:visited {
          color: #aa0000; }
        #blogbody .posting .postbody a:hover {
          color: #ff190d;
          text-shadow: #ff6666 0px 0px 1px; }
      #blogbody .posting .postbody p {
        line-height: 1.3em; }
      #blogbody .posting .postbody dl {
        padding-left: 16px; }
        #blogbody .posting .postbody dl dt {
          font-weight: bold;
          color: #444444;
          padding: 6px 92px 3px 0;
          padding-top: 9px; }
      #blogbody .posting .postbody ul {
        padding: 10px 0 10px 40px;
        list-style-type: disc; }
      #blogbody .posting .postbody li {
        padding-top: 3px; }
      #blogbody .posting .postbody pre, #blogbody .posting .postbody code {
        font-family: Bitstream Vera Sans Mono, monospace;
        font-size: 13px; }
      #blogbody .posting .postbody blockquote {
        border-left: 3pt solid #aaaaaa;
        padding-left: 1em;
        padding-right: 1em;
        margin-left: 1em;
        font: italic small Verdana, Times, sans-serif;
        color: #222222; }
        #blogbody .posting .postbody blockquote em {
          font-weight: bold; }
      #blogbody .posting .postbody img {
        max-width: 700px;
        margin: 0em 20px;
        -moz-box-shadow: 0px 0px 9px black;
        -webkit-box-shadow: 0px 0px 9px black;
        box-shadow: 0px 0px 4px black; }
      #blogbody .posting .postbody .amp {
        color: #666666;
        font-family: "Warnock Pro", "Goudy Old Style", "Palatino", "Book Antiqua", serif;
        font-style: italic; }
      #blogbody .posting .postbody .caps {
        font-size: 0.92em; }
      #blogbody .posting .postbody .highlight {
        border: 1px solid #cccccc;
        padding-left: 1em;
        margin-bottom: 10px;
        margin-top: 10px;
        background: none repeat scroll 0 0 #f0f0f0;
        overflow: auto; }
    #blogbody .posting .postfooter p {
      margin: 0 0 0 0;
      font-style: italic; }
    #blogbody .posting .postfooter a {
      color: #111111;
      font-family: Palatino, "times new roman", serif;
      font-weight: bold;
      font-size: 0.9em;
      text-decoration: none; }
      #blogbody .posting .postfooter a:hover {
        color: #111111;
        text-shadow: #aaaaaa 0px 0px 1px; }
  #blogbody .page {
    margin-top: -20px;
    font: bold medium Palatino, "Times New Roman", serif;
    color: black;
    text-decoration: none;
    border-bottom: 1px dotted black; }
    #blogbody .page:hover {
      text-shadow: #aaaaaa 0px 0px 1px; }

#blogfooter {
  margin-top: 10px;
  padding: 10px;
  text-align: center;
  font: medium Palatino, "Times New Roman", serif; }
  #blogfooter a {
    font-weight: bold;
    text-decoration: none;
    border-bottom: 1px dotted black;
    color: #cc0000; }
    #blogfooter a:hover {
      text-shadow: #ee6688 0px 0px 1px;
      color: #ff190d; }

#disqus_thread {
  padding-top: 24px; }

object[type="application/x-shockwave-flash"] {
  -moz-box-shadow: 0px 0px 12px #777777;
  -webkit-box-shadow: 0px 0px 12px #777777;
  box-shadow: 0px 0px 12px #777777;
  margin-left: 15px;
  text-align: center; }

.shadow {
  -moz-box-shadow: 0px 0px 9px black;
  -webkit-box-shadow: 0px 0px 9px black;
  box-shadow: 0px 0px 4px black; }

.floatright {
  float: right; }

.floatleft {
  float: left; }
'''.strip()

main = r'''
<!DOCTYPE html
  PUBLIC "-//W3C//DTD XHTML 1.1 plus MathML 2.0//EN"
         "http://www.w3.org/Math/DTD/mathml2/xhtml-math11-f.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
 <head>
  <title>
      {%- if type != 'item' -%}
        {{ blog_title }}
      {%- else -%}
        {{ title }}
      {%- endif -%}
  </title>
  <meta http-equiv="Content-Type" content="text/xhtml; charset=utf-8" />
  <meta http-equiv="content-language" content="de, en" />
  {% if type == 'item' -%}
  <meta name="description" content="{{ description }}" />
  <meta name="keywords" content="{{ tags | join(', ') }}" />
  {%- endif %}
  <link media="all" href="/blog.css" type="text/css" rel="stylesheet" />
  <link href="/favicon.ico" rel="shortcut icon" />
  <link href="/" rel="home" />
  <link href="/atom/" type="application/atom+xml" rel="alternate" title="Atom-Feed" />
  <link href="/rss/" type="application/rss+xml" rel="alternate" title="RSS-Feed" />
 </head>
 <body>
    <div id="blogheader">
        <div id="blogtitle">
            <h2>
                <a href="/" class="blogtitle">{{ blog_title }}</a>
            </h2>
        </div>
        <div id="mainlinks">
            <ul>
                <li><a href="/">blog</a></li>
                <li><a href="/atom/">atom</a></li>
                <li><a href="/rss/">rss</a></li>
                <li><a href="/articles/">articles</a></li>
            </ul>
        </div>
    </div>
    <div id="blogbody">
        {{ entrylist }}
        {% if type in ['tag', 'page'] %}
            {% if prev %}
                <a href="{{ prev }}" class="page floatright">
                ältere Beiträge →
                </a>
            {% endif %}
            {% if next %}
                <a href="{{ next }}" class="page floatleft">
                ← neuere Beiträge
                </a>
            {% endif %}
        {%- endif  %}
    </div>
    <div id="blogfooter">
        <p>
            written by <a href="mailto:{{ email }}">{{ author }}</a>
        </p>
        <a href="http://creativecommons.org/licenses/by-nc-sa/2.0/de/">
            <img src="/img/cc.png" alt="by-nc-sa" />
        </a>
    </div>
    {% if disqus_shortname and type == 'page' %}
    <script type="text/javascript">
        /* * * CONFIGURATION VARIABLES: EDIT BEFORE PASTING INTO YOUR WEBPAGE * * */
        var disqus_shortname = '{{ disqus_shortname }}'; // required: replace example with your forum shortname

        /* * * DON'T EDIT BELOW THIS LINE * * */
        (function () {
            var s = document.createElement('script'); s.async = true;
            s.type = 'text/javascript';
            s.src = '{{ protocol }}://' + disqus_shortname + '.disqus.com/count.js';
            (document.getElementsByTagName('HEAD')[0] || document.getElementsByTagName('BODY')[0]).appendChild(s);
        }());
    </script>
    {% endif %}
 </body>
</html>'''.strip()

entry = r'''
<div class="posting">
    <div class="postheader">
        <h1 class="subject">
            <a href="{{ permalink }}">{{ title }}</a>
        </h1>
        <span class="date">{{ date.strftime("%d.%m.%Y, %H:%M") }}</span>
    </div>
    <div class="postbody">        
        {{ content }}
    </div>
    <div class="postfooter">
        {% if disqus_shortname and type == 'page' %}
            <a class="floatright" href="{{ www_root + permalink }}#disqus_thread">Kommentieren</a>
        {% endif %}
        {% if tags %}
            <p>verschlagwortet als
                {% for link in tags | tagify -%}
                    <a href="{{ link.href }}">{{ link.title }}</a>
                    {%- if loop.revindex > 2 -%}
                    ,
                    {%- elif loop.revindex == 2 %}
                    und 
                    {% endif %}
                {% endfor %}
            </p>
        {% else %}
            <p>nicht verschlagwortet</p>
        {% endif %}
    </div>
    <div class="comments">
        {% if disqus_shortname and type == 'item' %}
        <div id="disqus_thread"></div>
        <script type="text/javascript">
            var disqus_shortname = '{{ disqus_shortname }}'; // required: replace example with your forum shortname

            // The following are highly recommended additional parameters. Remove the slashes in front to use.
            var disqus_identifier = "{{ www_root + permalink }}";
            var disqus_url = "{{ www_root + permalink }}";

            /* * * DON'T EDIT BELOW THIS LINE * * */
            (function() {
                var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
                dsq.src = '{{ protocol }}://' + disqus_shortname + '.disqus.com/embed.js';
                (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
            })();
        </script>
        <noscript>
            <p>Please enable JavaScript to view the <a href="{{ protocol }}://disqus.com/?ref_noscript">comments powered by Disqus.</a></p>
        </noscript>
        <a href="{{ protocol }}://disqus.com" class="dsq-brlink">
            blog comments powered by <span class="logo-disqus">Disqus</span>
        </a>
        {% endif %}
    </div>
</div>'''.strip()

articles = r'''
<xhtml>
    <head>
        <title>{{ blog_title }} – Artikelübersicht</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <link rel="stylesheet" type="text/css" media="all," href="/blog.css" />
        <link rel="shortcut icon" href="/favicon.ico" />
        <link rel="name" href="/" />
        <link rel="alternate" title="Atom-Feed" type="application/atom+xml" href="/atom/" />
        <link rel="alternate" title="RSS-Feed" type="application/rss+xml" href="/rss/" />
    </head>
    <body>
        <div id="blogheader">
            <div id="blogtitle">
                <h2>
                    <a href="/" class="blogtitle">{{ blog_title }}</a>
                </h2>
            </div>
            <div id="mainlinks">
                <ul>
                    <li>
                        <a href="/">blog</a>
                    </li>
                    <li>
                        <a href="/atom/">atom</a>
                    </li>
                    <li>
                        <a href="/rss/">rss</a>
                    </li>
                    <li>
                        <a href="/articles/">articles</a>
                    </li>
                </ul>
            </div>
        </div>
        <div id="blogbody">
            <div class="posting">
                <div class="postheader">
                    <span class="date">{{ num_entries }} Beiträge</span>
                </div>
                <div class="postbody">
                    {% for year in articles|sort(reverse=True) %}
                    <h2>{{ year }}</h2>
                    <ul>
                        {% for entry in articles[year] %}
                            <li>
                                <span>{{ entry[0].strftime('%d.%m.%Y: ') }}</span>
                                <a href="{{entry[1]}}">{{ entry[2] }}</a>
                            </li>
                        {% endfor %}
                    </ul>
                    {% endfor %}
                </div>
            </div>
        </div>
        <div id="blogfooter">
            <p>
                written by
                <a href="mailto:{{ email }}">{{ author }}</a>
            </p>
            <a href="http://creativecommons.org/licenses/by-nc-sa/2.0/de/">
                <img src="/img/cc.png" alt="by-nc-sa" />
            </a>
        </div>
    </body>
</xhtml>
'''

kafka = '''
---
title: Die Verwandlung
author: Franz Kafka
tags: [Franz Kafka, Die Verwandlung]
---

Als Gregor Samsa eines Morgens aus unruhigen Träumen erwachte, fand er sich in
seinem Bett zu einem ungeheueren Ungeziefer verwandelt. Er lag auf seinem
panzerartig harten Rücken und sah, wenn er den Kopf ein wenig hob, seinen
gewölbten, braunen, von bogenförmigen Versteifungen geteilten Bauch, auf
dessen Höhe sich die Bettdecke, zum gänzlichen Niedergleiten bereit, kaum noch
erhalten konnte. Seine vielen, im Vergleich zu seinem sonstigen Umfang
kläglich dünnen Beine flimmerten ihm hilflos vor den Augen.

»Was ist mit mir geschehen?« dachte er. Es war kein Traum, sein Zimmer, ein
richtiges, nur etwas zu kleines Menschenzimmer, lag ruhig zwischen den vier
wohlbekannten Wänden, über dem Tisch, auf dem eine auseinandergepackte
Musterkollektion von Tuchwaren ausgebreitet war -- Samsa war Reisender --, hing
das Bild, das er vor kurzem aus einer illustrierten Zeitschrift ausgeschnitten
und in einem hübschen, vergoldeten Rahmen untergebracht hatte. Es stellte eine
Dame dar, die, mit einem Pelzhut und einer Pelzboa versehen, aufrecht dasaß
und einen schweren Pelzmuff, in dem ihr ganzer Unterarm verschwunden war, dem
Beschauer entgegenhob.'''.strip()
