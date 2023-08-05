# -*- coding: utf-8 -*-
# Copyright (C) 2011 Pythonheads, all rights reserved.

from django import template
from django.template.loader import render_to_string
import re

register = template.Library()

WHITESPACE='\t '

def _walk(obj, cb):
    '''
    Walk over a structure, call cb for everything that is not a list 
    or a dict
    
    '''
    if isinstance(obj, dict):
        for k in obj.iterkeys():
            obj[k] = _walk(obj[k], cb)
        return obj
    elif isinstance(obj, list):
        for ix, k in enumerate(obj):
            obj[ix] = _walk(k, cb)
        return obj
    else:
        return cb(obj)

def walk(obj, cb): 
    # Make sure nothing is ever returned
    _walk(obj, cb)
    
class SimpleParser(object):
    def parse(self, defs):
        seen = 0
        indent = 0
        d = {}
        buf = []
        for line in defs.split('\n'):
            # ignore empty lines
            if len(line.strip()) < 1:
                continue

            # find the indent count
            if seen == 0:
                for c in line:
                    if c not in WHITESPACE:
                        break
                    indent += 1

            # Take the usable part of the line
            line = line[indent:]

            # Is it a continuation?
            cont = line[0] in WHITESPACE
            if not cont and  buf:
                k, v = '\n'.join(buf).split(':', 1)
                d[k] = v.strip()
                buf = []
            buf += [line,]
        
            seen += 1 # line count
        k, v = '\n'.join(buf).split(':', 1)
        d[k] = v.strip()

        return d

class YamlParser(object):
    def parse(self, defs):
        import yaml # Yaml is actually amazing at handling most use cases
        return yaml.load(defs)

class MnmlParser(object):
    def parse(self, defs):
        import mnml 
        
        def build_tree(items):
            d = {}
            for item in items:
                d[item] = build(items)
            return d 
        foo = build_tree(mnml.load(defs))
        return foo


parsers = {'yaml': YamlParser(),
           'simple': SimpleParser()}

class IncNode(template.Node):
    def __init__(self, nodelist, template_name, parser_name):
        self.nodelist = nodelist
        self.template_name = template.Variable(template_name)
        self.parser_name = parser_name

    def render(self, context):
        defs = self.nodelist.render(context)
        extra_context = parsers[self.parser_name].parse(defs)
        def cb(obj):
            if obj.startswith('$'):
                return template.Variable(obj[1:]).resolve(context)
            else:
                return obj
        walk(extra_context, cb)
        content = render_to_string(self.template_name.resolve(context), 
                                   extra_context,
                                   context_instance=context)
        return content

def do_inc(parser, token):    
    nodelist = parser.parse(('endinc',))
    try:
        args = token.contents.split()
        tag_name = args[0]
        template_name = args[1]
        
        if len(args) == 3:
            parser_name = args[2]
        else:
            parser_name = 'simple'

    except ValueError:
        raise template.TemplateSyntaxError(
            '%r tag requires at least one argument' % (token.contents.split()[0],))
    
    parser.delete_first_token()
    return IncNode(nodelist, template_name, parser_name)

register.tag('inc', do_inc)
