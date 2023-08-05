# -*- coding: utf-8 -*-
"""Recipe cpzexp"""

import logging
import os
import shutil
import sys
import pkg_resources
import zc.buildout

logger = logging.getLogger('my315ok.recipe.cpzexp')


class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

    def configure(self):
        source = self.options.get('source')
 
        destinations = self.options.get('destinations', '')
        destinations = [d for d in destinations.splitlines() if d]
        if not destinations:
            parts = self.buildout['buildout']['parts']
            part_names = parts.split()
            destinations = []
            for part_name in part_names:
                part = self.buildout[part_name]
                if part.get('recipe') == 'plone.recipe.zope2instance':
                    destinations.append(part['location'])
        for dir in [source] + destinations:
            if not os.path.exists(dir):
                logger.error('path %r does not exist.', dir)
                sys.exit(1)
            if not os.path.isdir(dir):
                logger.error('path %r must be a directory.', dir)
                sys.exit(1)
        self.destinations = destinations
        self.source = source

    def install(self):
        """Installer"""
        self.configure()
        zexp_files = [f for f in os.listdir(self.source) if f.endswith('.zexp')]
        if len(zexp_files) == 0:
            logger.warn('source %r contains no .zexp files.', self.source)
            return tuple()

        created = []
        if not self.destinations:
            logger.warn('No destinations specified.')
            return tuple()

        for destination in self.destinations:
            import_dir = os.path.join(destination, 'import')
            if not os.path.exists(import_dir):
                logger.info("Creating directory %s" % import_dir)
                os.mkdir(import_dir)
                created.append(import_dir)
            if not os.path.isdir(import_dir):
                logger.error("%r is not a directory." % import_dir)
                sys.exit(1)
            for zexp_file in zexp_files:
                file_path = os.path.join(self.source, zexp_file)
                shutil.copy(file_path, import_dir)
                created.append(os.path.join(import_dir, zexp_file))

        logger.info('Copied %d zexp files.' % len(zexp_files))

        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.

        # XXX Returning 'created' here gives test errors now.  We will
        # have to see if this is really needed in our use case, as the
        # zope instances likely get removed anyway.  But if a source
        # file was removed meanwhile, we will have to remove it in the
        # destinations as well.  But zc.buildout should do this
        # automatically and even when returning 'created' I do not see
        # that happening.  So we will ignore it.
        return tuple()

    # It is easiest if the updater does the same as the installer.
    update = install