# Closure Depresolver
# Copyright (C) 2012  Paul Horn
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Scans a source JS file for Classes that may need a goog.provide or
goog.require.

Built on top of a source class which is part of the Closure Library calcdeps
build script.
"""

__author__ = 'knutwalker@gmail.com (Paul Horn)'

import re

_BASE_REGEX_STRING = '^\s*goog\.%s\(\s*[\'"](.+)[\'"]\s*\)'
_PROVIDE_REGEX = re.compile(_BASE_REGEX_STRING % 'provide')
_REQUIRES_REGEX = re.compile(_BASE_REGEX_STRING % 'require')

_MULTILINE_COMMENT_REGEX = re.compile(r'/\*.*?\*/', flags=re.DOTALL)
_ONELINE_COMMENT_REGEX = re.compile(r'//.*$')

_USES_METHOD = r'({namespace}(?:\.[a-z_][a-zA-Z0-9_]*)+)\s*\('
_USES_ENUM = r'({namespace}(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)(?:\.[A-Z_]+)(?:[^a-zA-Z0-9_]|$)'
_USES_CLASS = r'(?:new |=\s*)({namespace}(?:\.[a-z_][a-zA-Z0-9_]*)*(?:\.[A-Z][a-zA-Z0-9_]*)+)'
#TODO: use classmethod


#TODO: declare enum
_DECLARES_METHOD = r'^\s*({namespace}(?:\.[a-z_][a-zA-Z0-9_]*)+)\s*='
_DECLARES_CLASS = r'^\s*({namespace}(?:\.[a-z_][a-zA-Z0-9_]*)*(?:\.[A-Z][a-zA-Z0-9_]*)+)\s*=\s*function'


class Source(object):
    def __init__(self, path, namespaces=()):
        self.provides = set()
        self.requires = set()

        self.uses = set()
        self.declares = set()

        self._namespaces = set(namespaces) | set(['goog'])

        self._path = path
        with open(path) as fileobj:
            self._source = fileobj.read()

        self._scan()

    def __str__(self):
        return 'Source %s' % self._path

    def __hash__(self):
        return hash(self._path)

    @property
    def source(self):
        return self._source

    @property
    def path(self):
        return self._path

    def _use_ns(self):
        for namespace in self._namespaces:
            yield re.compile(_USES_METHOD.format(namespace=namespace))
            yield re.compile(_USES_ENUM.format(namespace=namespace))
            yield re.compile(_USES_CLASS.format(namespace=namespace))

    def _declare_ns(self):
        for namespace in self._namespaces:
            yield re.compile(_DECLARES_METHOD.format(namespace=namespace))
            yield re.compile(_DECLARES_CLASS.format(namespace=namespace))


    def _scan(self):
        source = _ONELINE_COMMENT_REGEX.sub('',
                    _MULTILINE_COMMENT_REGEX.sub('', self.source))

        source_lines = source.splitlines()
        for line in source_lines:
            match = _PROVIDE_REGEX.match(line)
            if match:
                self.provides.add(match.group(1))
            match = _REQUIRES_REGEX.match(line)
            if match:
                self.requires.add(match.group(1))

            for re_ in self._use_ns():
                match = re_.search(line)
                if match:
                    try:
                        module, fn = match.group(1).rsplit('.', 1)
                    except ValueError:
                        continue

                    if fn[0].isupper():
                        self.uses.add('%s.%s' % (module, fn))
                    else:
                        # do not use top level modules
                        if '.' in module:
                            self.uses.add(module)

            for re_ in self._declare_ns():
                match = re_.search(line)
                if match:
                    try:
                        module, fn = match.group(1).rsplit('.', 1)
                    except ValueError:
                        self.declares.add(match.group(1))
                        continue

                    if 'prototype' in module:
                        continue
                    if fn[0].isupper():
                        self.declares.add('%s.%s' % (module, fn))
                    else:
                        self.declares.add(module)
