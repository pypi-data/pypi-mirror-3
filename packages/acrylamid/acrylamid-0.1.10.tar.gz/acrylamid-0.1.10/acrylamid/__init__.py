#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
# 
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
# 
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of posativ <info@posativ.org>.

VERSION = "0.1.10-dev"
VERSION_SPLIT = tuple(VERSION.split('-')[0].split('.'))

import sys
reload(sys); sys.setdefaultencoding('utf-8')

import os, logging, locale
from optparse import OptionParser, make_option, OptionGroup

from acrylamid import defaults
from acrylamid import filters
from acrylamid import views
from acrylamid.utils import check_conf, yamllike, ColorFormatter

log = logging.getLogger('acrylamid')
sys.path.insert(0, os.path.dirname(__package__))


class Acryl:
    """Main class for acrylamid functionality.  It handles initialization,
    defines default behavior, and also pushes the request through all
    steps until the output is rendered and we're complete."""
    
    def __init__(self):
        """Sets configuration and environment and creates the Request
        object"""
        
        usage = "usage: %prog [options] init\n" + '\n' \
                + "init     - initializes base structure\n" \
                + "gen      - rendering blog\n"
#                + "srv (-p) - serving on port p (8000) and auto-rendering changes\n"
        
        options = [
            make_option("-v", "--verbose", action="store_const", dest="verbose",
                              help="debug information", const=logging.DEBUG),
            make_option("-q", "--quit", action="store_const", dest="verbose",
                              help="be silent (mostly)", const=logging.WARN,
                              default=logging.INFO),
            make_option("-f", "--force", action="store_true", dest="force",
                              help="force overwriting", default=False),
            make_option("-c", "--config", dest="conf", help="alternate conf.yaml",
                              default="conf.yaml"),
            make_option("--version", action="store_true", dest="version",
                               help="print version details", default=False),                  
            ]
            
            
        parser = OptionParser(option_list=options, usage=usage)
        ext_group = OptionGroup(parser, "conf.yaml override")
        
        for key, value in yamllike(defaults.conf).iteritems():
            if key in ['views.', 'filters.']: continue
            ext_group.add_option('--'+key.replace('_', '-'), action="store",
                            dest=key, metavar=value, type=type(value) if type(value) != list else str)
                            
        parser.add_option_group(ext_group)
        (options, args) = parser.parse_args()
            
        console = logging.StreamHandler()
        console.setFormatter(ColorFormatter('%(message)s'))
        if options.verbose == logging.DEBUG:
            fmt = '%(msecs)d [%(levelname)s] %(name)s.py:%(lineno)s:%(funcName)s %(message)s'
            console.setFormatter(ColorFormatter(fmt))
        log = logging.getLogger('acrylamid')
        log.addHandler(console)
        log.setLevel(options.verbose)
        
        env = {'VERSION': VERSION, 'VERSION_SPLIT': VERSION_SPLIT}
        if options.version:
            print "acrylamid" + ' ' + env['VERSION']
            sys.exit(0)
        
        if len(args) < 1:
            parser.print_usage()
            sys.exit(1)
        
        # -- init -- #
        # TODO: acrylamid init --layout_dir=somedir to overwrite defaults
        
        if 'init' in args:
            if len(args) == 2:
                defaults.init(args[1], options.force)
            else:
                defaults.init(overwrite=options.force)
            sys.exit(0)
        
        try:
            conf = yamllike(open(options.conf).read())
        except OSError:
            log.critical('no config file found: %s. Try "acrylamid init".', options.conf)
            sys.exit(1)
        
        assert check_conf(conf)
                
        conf['acrylamid_name'] = "acrylamid"
        conf['acrylamid_version'] = env['VERSION']

        conf['output_dir'] = conf.get('output_dir', 'output/')
        conf['entries_dir'] = conf.get('entries_dir', 'content/')
        conf['layout_dir'] = conf.get('layout_dir', 'layouts/')
        
        conf.update(dict((k,v) for k,v in options.__dict__.iteritems() if v != None))

        # -- run -- #
                    
        if args[0] in ['gen', 'generate', 'render']:
            self.req = {'conf': conf, 'env': env, 'data': {}}
            
            self.run()
            # from filters.md import Markdown
            # md = Markdown()
            # print md('Hallo $$beta$$-Welt', [],  *['math'])
            #self.run(request)
                
    def initialize(self, request):
        """The initialize step further initializes the Request by
        setting additional information in the ``data`` dict,
        registering plugins, and entryparsers.
        """
        
        conf = request['conf']
        env = request['env']

        # initialize the locale, will silently fail if locale is not
        # available and uses system's locale
        try:
            locale.setlocale(locale.LC_ALL, conf.get('lang', ''))
        except (locale.Error, TypeError):
            # invalid locale
            locale.setlocale(locale.LC_ALL, '')
            log.warn("unsupported locale '%s', set to '%s'", conf['lang'], locale.getlocale()[0])
        conf['lang'] = locale.getlocale()

        if not conf.has_key('www_root'):
            log.warn('no `www_root` specified, using localhost:8000')
            conf['www_root'] = 'http://localhost:8000/'
        
        env['protocol'] = conf['www_root'][0:conf['www_root'].find('://')]
        # take off the trailing slash for base_url
        if conf['www_root'].endswith("/"):
            conf['www_root'] = conf['www_root'][:-1]

        # import and initialize plugins
        filters.initialize(conf.get("ext_dir", []), request['conf'], request['env'],
                              exclude=conf.get("ext_ignore", []),
                              include=conf.get("ext_include", []))
        views.initialize(conf.get("ext_dir", []), request['conf'], request['env'])

        ns = filters.__dict__
        exec(''.join(conf['filters.'])) in ns
        ns = views.__dict__
        exec(''.join(conf['views.'])) in ns
        
    def run(self):
        """This is the main loop for acrylamid.  This method will run
        the handle callback to allow registered handlers to handle
        the request. If nothing handles the request, then we use the
        ``_acrylamid_handler``.
        """
        request = self.req
        conf = self.req['conf']
        self.initialize(request)
        
        from acrylamid.core import start, handle
        from acrylamid.filters import get_filters, FilterList
        from acrylamid.views import get_views
        
        request = start(request)
        request = handle(request)
        
        filtersdict = get_filters()
        _views = get_views()
        
        for v in _views:
            log.debug(v)
            for i, entry in enumerate(request['entrylist']):
                if not v.__filters__: break
                
                log.debug(entry.filename)
                entry.content = entry.source
                entryfilters = entry.get('filters', [])
                if isinstance(entryfilters, basestring):
                    entryfilters = [entryfilters]
                viewsfilters = views.filters+getattr(views, v.__module__).filters
                
                _filters = FilterList()
                for f in entryfilters+viewsfilters:
                    x,y = f.split('+')[:1][0], f.split('+')[1:]
                    if filtersdict[x] not in _filters:
                        _filters.append((x, filtersdict[x], y))
                
                for i, f, args in _filters:
                    f.__dict__['__matched__'] = i
                    entry.content = f(entry.content, entry, *args)
            
            v(request)
