#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Sleipnir component loaders

A set of Stateless component loaders to allow Sleipnir to dinamically
add functionality to the core
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import Here any required modules for this module.

import imp
import sys
import os.path

from glob import glob
from itertools import ifilter

from pkg_resources import Environment
from pkg_resources import working_set
from pkg_resources import UnknownExtra
from pkg_resources import VersionConflict
from pkg_resources import DistributionNotFound

__all__ = ['ComponentManager']

try:
    from sleipnir.core.log import log
except ImportError:
    from ._log import dummy as log

from . import constants
from .interfaces import loader
from .entrypoint import ExtensionPoint
from .components import Component, implements


class EggsLoader(Component):
    """A loader component to instantiate Egg based plugins"""

    implements(loader.ILoader)

    def __init__(self):
        super(EggsLoader, self).__init__()

    def load(self, spath, **kwargs):
        """
        Loader that loads any eggs on the search path and `sys.path`
        """

        def _log_error(item, ex):
            """Sugar error method"""
            uex = ex.message
            if isinstance(ex, DistributionNotFound):
                log.plugins.debug('Skip "%s": ("%s" not found)', item, uex)
            elif isinstance(ex, VersionConflict):
                log.plugins.error('Skip "%s": (conflicts "%s")', item, uex)
            elif isinstance(ex, UnknownExtra):
                log.plugins.error('Skip "%s": (unknown extra "%s")', item, uex)
            elif isinstance(ex, ImportError):
                log.plugins.error('Skip "%s": ("%s")', item, uex)
            else:
                log.plugins.error('Skip "%s": %s)', item, uex)

        en_auto = kwargs.get('auto_enable', None)

        distros, errors = working_set.find_plugins(
            Environment([path for path in spath if path])
            )
        for dct in ifilter(lambda x: x not in working_set, distros):
            working_set.add(dct)
        for dist, ex in errors.iteritems():
            _log_error(dist, ex)

        entry_points = kwargs.get('entry_points', constants.__entry_point__)
        entries = working_set.iter_entry_points(entry_points)
        for epo in sorted(entries, key=lambda entry: entry.name):
            log.plugins.debug('Load %s from %s', epo.name, epo.dist.location)
            try:
                epo.load(require=True)
            #pylint: disable-msg=W0703
            except Exception, ex:
                _log_error(epo, ex)
            else:
                pdir = os.path.dirname(epo.dist.location)
                #pylint: disable-msg=E1101
                enabled = self.compmgr.is_component_enabled(epo.module_name)
                if type(en_auto) in (str, unicode,):
                    if not enabled and pdir.startswith(en_auto):
                        self.compmgr.enable_component(epo.module_name)


class PyLoader(Component):
    """A component loader to add simple python script plugins"""

    implements(loader.ILoader)

    def __init__(self):
        super(PyLoader, self).__init__()

    def load(self, spath, **kwargs):
        """
        Loader that look for Python source files in the plugins directories,
        which simply get imported, thereby registering them with the component
        manager if they define any components
        """

        en_auto = kwargs.get('auto_enable', None)

        for path in spath:
            for pfile in glob(os.path.join(path, '*.py')):
                try:
                    pname = os.path.basename(pfile[:-3])
                    if pname not in sys.modules:
                        log.plugins.debug(
                            'Loading plugin %s from %s' % (pname, pfile))
                        imp.load_source(pname, pfile)
                except ImportError, ex:
                    log.plugins.error(
                        'Failed to load plugin from %s: %s', pfile, ex.message)
                else:
                    pdir = os.path.dirname(path)
                    #pylint: disable-msg=E1101
                    enabled = self.compmgr.is_component_enabled(pname)
                    if type(en_auto) in (str, unicode,):
                        if not enabled and pdir.startswith(en_auto):
                            self.compmgr.enable_component(pname)


class LoaderManager(Component):
    """A Facility to load plugins in application"""

    loaders = ExtensionPoint(loader.ILoader)

    def __init__(self):
        super(LoaderManager, self).__init__()

    #pylint: disable-msg=W0102
    def load(self, expath=[], **kwargs):
        """Load plugins found in 'expath'"""

        lfilter = kwargs.get('lfilter', lambda x: True)
        en_auto = kwargs.get('auto_enable', None)

        if type(expath) in (str, unicode,):
            expath = (expath,)

        search_path = {}
        for path in expath:
            path = os.path.normcase(os.path.realpath(path))
            search_path.setdefault(path, path)
        search_path = search_path.values()
        for loaders in ifilter(lfilter, self.loaders):
            loaders.load(search_path, **kwargs)
