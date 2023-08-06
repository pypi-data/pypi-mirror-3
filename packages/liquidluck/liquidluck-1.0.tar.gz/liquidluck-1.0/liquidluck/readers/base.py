#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Reader, read content, parse to html.

:copyright: (c) 2012 by Hsiaoming Yang (aka lepture)
:license: BSD
'''

import os
import datetime
import logging
from liquidluck.options import settings, g


class BaseReader(object):
    SUPPORT_TYPE = None
    """
    Base Reader, all readers must inherit this module. e.g.:

        ``MarkdownReader(BaseReader)``

    New reader required:
        - ``SUPPORT_TYPE``
        - ``render``

    New reader optional:
        - ``start``
    """
    def __init__(self, filepath=None):
        self.filepath = filepath

    @property
    def short_filepath(self):
        return self.filepath[len(g.source_directory) + 1:]

    def start(self):
        return None

    def support(self):
        _type = self.SUPPORT_TYPE
        if isinstance(_type, basestring):
            return self.filepath.endswith('.' + _type)
        if isinstance(_type, list) or isinstance(_type, tuple):
            for _t in _type:
                if isinstance(_t, basestring) and \
                   self.filepath.endswith('.' + _t):
                    return True
        return False

    def render(self):
        raise NotImplementedError

    def run(self):
        try:
            return self.render()
        except Exception as e:
            logging.error(e)


class Post(object):
    meta = {}

    def __init__(self, filepath, content, title=None, meta=None):
        self.filepath = filepath
        self.content = content
        if title:
            self.title = title
        else:
            self.title = meta.pop('title')

        if meta:
            self.meta = meta

    @property
    def author(self):
        return Author(self.meta.get('author', settings.author))

    @property
    def embed_author(self):
        """define in settings::

            authors = {
                "lepture": {
                    "name": "Hsiaoming Yang",
                    "website": "http://lepture.com",
                    "email": "lepture@me.com",
                }
            }
        """
        author = self.author
        if author.website:
            return '<a href="%s">%s</a>' % (author.website, author.name)
        if author.email:
            return '<a href="mailto:%s">%s</a>' % (author.email, author.name)
        return author.name

    @property
    def date(self):
        date = self.meta.get('date', None)
        if date:
            return to_datetime(date)
        return None

    @property
    def public(self):
        return self.meta.get('public', 'true') == 'true'

    @property
    def category(self):
        category = self.meta.get('category', None)
        if category:
            return category
        #: historical reason
        return self.meta.get('folder', None)

    @property
    def tags(self):
        tags = self.meta.get('tags', None)
        if not tags:
            return []
        if isinstance(tags, (list, tuple)):
            return tags
        return [tag.strip() for tag in tags.split(",")]

    @property
    def summary(self):
        return self.meta.get('summary', None)

    @property
    def template(self):
        return self.meta.get('template', None)

    @property
    def filename(self):
        path = os.path.split(self.filepath)[1]
        return os.path.splitext(path)[0]

    def __getattr__(self, key):
        try:
            return super(Post, self).__getattr__(key)
        except:
            pass
        if key in self.meta:
            return self.meta[key]
        raise AttributeError


class Author(object):
    def __init__(self, author):
        self.author = author

        __ = settings.authors or {}
        self._d = __.get(author, {})

    def __str__(self):
        return self.author

    def __repr__(self):
        return self.author

    @property
    def name(self):
        return self._d.get('name', self.author)

    @property
    def website(self):
        return self._d.get('website', None)

    @property
    def email(self):
        return self._d.get('email', None)


def to_datetime(value):
    supported_formats = [
        '%a %b %d %H:%M:%S %Y',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%dT%H:%M',
        '%Y%m%d %H:%M:%S',
        '%Y%m%d %H:%M',
        '%Y-%m-%d',
        '%Y%m%d',
    ]
    for format in supported_formats:
        try:
            return datetime.datetime.strptime(value, format)
        except ValueError:
            pass
    logging.error('Unrecognized date/time: %r' % value)
    raise ValueError('Unrecognized date/time: %r' % value)
