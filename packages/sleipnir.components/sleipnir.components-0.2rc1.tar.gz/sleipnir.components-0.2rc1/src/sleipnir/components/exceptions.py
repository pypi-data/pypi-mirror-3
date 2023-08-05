#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Exceptions for Sleipnir component system"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__status__  = "alpha"
__version__ = "0.1"
__date__    = "20 January 2010"
__license__ = "See LICENSE file for details"

# Import Here any required modules for this module.

__all__ = ['CoreError']


#pylint: disable-msg=C0103
def N_(string):
    """
    No-op translation marker, inlined here to avoid importing from
    `trac.util`
    """

    return string


#pylint: disable-msg=R0903
class CoreError(Exception):
    """Exception base class for errors"""

    title = N_('Core Error')

    def __init__(self, message, title=None, show_traceback=False):
        """
        If title is given, it will be displayed as the large header
        above the error message
        """
        # pylint: disable-msg=E1002
        Exception.__init__(self, message)
        self.title = title
        self._message = message
        self.show_traceback = show_traceback

    @property
    def message(self):
        """Retrieve message error"""
        return self._message

    # pylint: disable-msg=E1101,E0102
    @message.setter
    def message(self, value):
        """Set message error"""
        self._message = value

    def __unicode__(self):
        return unicode(self.message)
