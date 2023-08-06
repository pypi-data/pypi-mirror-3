#!/usr/bin/env python

import os.path
from liquidluck.cli import load_settings, load_posts
from liquidluck.writers.base import load_jinja

ROOT = os.path.abspath(os.path.dirname(__file__))


def test_load_settings():
    path = os.path.join(ROOT, 'source/settings.py')
    load_settings(path)

    from liquidluck.options import settings
    assert settings.author == 'lepture'
    assert settings.perpage == 30


def test_load_posts():
    load_posts(os.path.join(ROOT, 'source/post'))
    from liquidluck.options import g
    assert len(g.public_posts) > 0


def test_load_jinja():
    load_jinja()
