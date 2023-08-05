#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Dummy Logger"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__status__  = "alpha"
__version__ = "0.1"
__date__    = "28 March 2010"
__license__ = "See LICENSE file for details"


__all__ = ['dummy']


class _DummyLogger(dict):
    """A Dummy Logger"""

    def noop(self, *args, **kwargs):
        """noop method"""
        pass

    def __getattr__(self, name):
        if name in ('critical', 'debug', 'error', 'info', 'warning'):
            return self.noop
        return self

#pylint: disable-msg=C0103
dummy = _DummyLogger()
