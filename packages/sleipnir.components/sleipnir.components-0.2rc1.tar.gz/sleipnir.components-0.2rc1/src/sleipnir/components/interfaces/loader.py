#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Interface Loader

Required by components to createt custom loaders used by LoaderManager
to plug new addins to Sleipnir derived programs
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__status__  = "alpha"
__version__ = "0.1"
__date__    = "20 January 2010"
__license__ = "See LICENSE file for details"

# Import Here any required modules for this module.

#pylint: disable-msg=W0232,R0903

__all__ = ['ILoader']

from ..entrypoint import Interface


class ILoader(Interface):
    """Implements a new loader for Sleipnir component system"""

    def load(self, entry_point=None):
        """Load addin located at 'entry_point'"""
