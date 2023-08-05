#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2011, Cédric Krier
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""a simple command line interface for roundup
"""
__version__ = '0.1'
__all__ = ['Roundup']

import cmd
import xmlrpclib
import ConfigParser
import os
import urlparse
import urllib
import re
import fcntl
import termios
import struct
from functools import wraps
from pydoc import pager
from textwrap import fill

LINK_TO = re.compile(r'.*to "(.*)".*')
DESIGNATOR = re.compile(r'([^\d]+)(\d+)')


def server_required(func):
    "Decorator for server required"
    @wraps(func)
    def server_wrapper(self, *args, **kwargs):
        if self.roundup_server is None:
            return
        return func(self, *args, **kwargs)
    return server_wrapper


def designator_required(func):
    "Decorator for designator required"
    @wraps(func)
    def designator_wrapper(self, *args, **kwargs):
        if not self.designator:
            return
        return func(self, *args, **kwargs)
    return designator_wrapper


def line_required(func):
    "Decorator for line required"
    @wraps(func)
    def line_wraper(self, line, *args, **kwargs):
        if not line:
            return
        return func(self, line, *args, **kwargs)
    return line_wraper


class Roundup(cmd.Cmd):
    """Roundup"""

    @property
    def prompt(self):
        if self.designator:
            return '%s@%s: ' % (self.designator, self.section)
        return '%s: ' % self.section

    def __init__(self, *args, **kwargs):
        cmd.Cmd.__init__(self, *args, **kwargs)
        self.config = ConfigParser.ConfigParser()
        self.config.read([
                'roundup.cfg',
                os.path.expanduser('~/.roundup.cfg'),
                ])
        self.roundup_server = None
        self.schema = None
        self.section = None
        self.designator = None
        self.links = {}

    @line_required
    def do_use(self, line):
        """use [section]
        Use the configuration of section"""
        if not line:
            return
        parts = list(urlparse.urlsplit(self.config.get(line, 'url')))
        username = urllib.quote(self.config.get(line, 'username'), '')
        password = urllib.quote(self.config.get(line, 'password'), '')
        parts[1] = '%s:%s@%s' % (username, password, parts[1])
        url = urlparse.urlunsplit(parts)
        self.roundup_server = xmlrpclib.ServerProxy(url, allow_none=True)
        self.schema = dict((x, dict(y))
            for x, y in self.roundup_server.schema().iteritems())
        self.section = line
        self.links = {}

    def complete_use(self, text, line, begidx, endidx):
        "Complete use"
        if line.count(' ') > 1:
            return
        if not text:
            return self.config.sections()
        else:
            return [s for s in self.config.sections()
                if s.startswith(text)]

    def format(self, classname, prop, value):
        "Format value"
        definitions = self.schema[classname]
        mlink = LINK_TO.match(definitions[prop])
        if mlink is None:
            return '%s' % value
        else:
            link = mlink.group(1)
            if isinstance(value, list):
                values = [self.display(link, v, False)
                    for v in value]
                return ','.join(values)
            else:
                return self.display(link, value, False)

    @server_required
    def display(self, classname, itemid, multiline=True):
        "Display item"
        try:
            properties = self.config.get(self.section, classname).split(',')
            if not multiline:
                properties = properties[:1]
        except ConfigParser.NoOptionError:
            if multiline:
                properties = []
            else:
                properties = self.schema[classname]
                if 'name' in properties:
                    properties = ['name']
                elif 'content' in properties:
                    properties = ['content']
                else:
                    properties = properties.keys()[:1]
        if not itemid:
            if multiline:
                return [''] * len(properties)
            else:
                return ''
        values = self.roundup_server.display(classname + itemid, *properties)
        if not properties:
            properties = values.keys()
        output = []
        for prop in properties:
            value = values[prop]
            if multiline:
                fmt = self.format(classname, prop, value)
                if '\n' in fmt:
                    output.append('%s:' % prop)
                    output.append(fmt)
                else:
                    output.append('%s: %s' % (prop, fmt))
            else:
                output.append(self.format(classname, prop, value))
        if multiline:
            return output
        else:
            return output[0]

    @staticmethod
    def split_designator(designator):
        "Split designator into classname and itemid"
        match = DESIGNATOR.match(designator)
        if match is None:
            return None, None
        return match.group(1), match.group(2)

    def do_get(self, line):
        """get [designator]
        Get item specify by designator"""
        classname, itemid = self.split_designator(line)
        if classname is None or itemid is None:
            self.designator = None
            return
        try:
            self.print_(self.display(classname, itemid))
        except xmlrpclib.Fault:
            self.designator = None
            return
        self.designator = line

    def complete_get(self, text, line, begidx, endidx):
        "Complete get"
        if line.count(' ') > 1:
            return
        if not text:
            return self.schema.keys()
        else:
            return [c for c in self.schema.iterkeys()
                if c.startswith(text)]

    @server_required
    @line_required
    @designator_required
    def do_show(self, line):
        """show [property]
        Show property of designator"""
        classname, _ = self.split_designator(self.designator)
        try:
            definitions = self.schema[classname]
        except KeyError:
            return
        properties = map(str.strip, line.split(' '))
        if not all(p in definitions for p in properties):
            return
        values = self.roundup_server.display(self.designator, *properties)
        output = []
        for prop in properties:
            value = values[prop]
            mlink = LINK_TO.match(definitions[prop])
            if mlink is None:
                output.append('%s: %s' % (prop,
                        self.format(classname, prop, value)))
            else:
                link = mlink.group(1)
                if isinstance(value, list):
                    output.append('%s:' % prop)
                    output.append('-- ')
                    for itemid in value:
                        output.append('%s%s' % (link, itemid))
                        output.extend(self.display(link, itemid))
                        output.append('-- ')
                else:
                    output.append('%s%s' % (link, value))
                    output.extend(self.display(link, value))
        self.print_(output)

    @designator_required
    def complete_show(self, text, line, begidx, endidx):
        "Complete show"
        classname, _ = self.split_designator(self.designator)
        definitions = self.schema[classname]
        if not text:
            return definitions.keys()
        else:
            return [p for p in definitions if p.startswith(text)]

    def get_links(self, link):
        "Prefetch linked classname"
        if link not in self.links:
            ids = self.roundup_server.filter(link, None, {})
            self.links[link] = dict((itemid, self.display(link, itemid, False))
                for itemid in ids)
        return self.links[link]

    @server_required
    def do_search(self, line):
        """search [classname] [property: value],...
        Search"""
        self.designator = None
        if not line:
            return
        if ' ' in line:
            classname, line = line.split(' ', 1)
            attributes = {}
            try:
                definitions = self.schema[classname]
            except KeyError:
                return
            for attribute in line.split(','):
                try:
                    attr, value = (x.strip for x in attribute.split(':', 1))
                except ValueError:
                    continue
                try:
                    mlink = LINK_TO.match(definitions[attr])
                except KeyError:
                    continue
                if mlink is None:
                    attributes[attr] = value
                else:
                    link = mlink.group(1)
                    values = dict((v, k)
                        for k, v in self.get_links(link).iteritems())
                    try:
                        attributes[attr] = values[value]
                    except KeyError:
                        continue
        else:
            classname = line
            attributes = {}
        if classname not in self.schema:
            return
        ids = self.roundup_server.filter(classname, None, attributes)
        output = []
        for itemid in ids:
            output.append('%s%s: %s' % (classname, itemid,
                    self.display(classname, itemid, False)))
        self.print_(output)

    @server_required
    def complete_search(self, text, line, begidx, endidx):
        "Complete search"
        classname = line[7:]
        other = None
        if ' ' in classname:
            classname, other = classname.split(' ', 1)
        if classname in self.schema and other is not None:
            definitions = self.schema[classname]
            if line[begidx - 1] == ':':
                prop = line[:begidx - 1][7 + len(classname) + 1:]\
                    .split(',')[-1]
                if prop in definitions:
                    try:
                        mlink = LINK_TO.match(definitions[prop])
                    except KeyError:
                        return
                    if mlink is None:
                        return
                    else:
                        link = mlink.group(1)
                        values = self.get_links(link)
                        if not text:
                            return values.values()
                        return [v + ',' for v in values.itervalues()
                            if v.startswith(text)]
                return
            if not text:
                return [p + ':' for p in definitions]
            return [p + ':' for p in definitions if p.startswith(text)]
        else:
            if not classname:
                return self.schema.keys()
            else:
                return [c for c in self.schema.keys()
                    if c.startswith(classname)]

    def emptyline(self):
        "Do nothing on empty line"
        return

    def do_EOF(self, line):
        "Stop"
        print
        return True

    @staticmethod
    def print_(text):
        "Output text"
        if os.name == 'posix':
            height, width, _, _ = struct.unpack('HHHH',
                fcntl.ioctl(0, termios.TIOCGWINSZ,
                    struct.pack('HHHH', 0, 0, 0, 0)))
        else:
            height, width = 25, 70
        width = min(width, 79)

        def layout(text):
            "layout the output"
            for line in text:
                if line == '-- ':
                    yield '-' * width
                else:
                    if '\n' in line:
                        indent = '  '
                    else:
                        indent = ' '
                    for subline in line.splitlines():
                        yield fill(subline, width, initial_indent=indent,
                            subsequent_indent=indent)
        text = '\n'.join(layout(text))
        if len(text.splitlines()) > height:
            pager(text)
        else:
            print text

if __name__ == '__main__':
    Roundup().cmdloop()
