# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2010 kent1 <kent1@arscenic.info>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

__version__ = '0.1.0'
__author__ = 'kent1'
__email__ = 'kent1@arscenic.info'
__packagename__ = 'Piwik4Trac'
__license__ = 'GNU/GPL v3'
__url__ = 'http://technique.arscenic.org/services-web/subversion-et-trac/ameliorer-et-optimiser-trac/article/trac-et-piwik-analyse-des'
__summary__ = 'Trac plugin to enable your trac environment to be logged' + \
                  ' by a Piwik server'

import pkg_resources
from trac.config import Option, BoolOption
from trac.core import Component, implements
from trac.env import IEnvironmentSetupParticipant
from trac.web.chrome import ITemplateProvider
from trac.util.translation import domain_functions

_, tag_, N_, add_domain = domain_functions('piwik4trac', ('_', 'tag_', 'N_', 'add_domain'))

# ==============================================================================
# Piwik Configuration
# ==============================================================================
class PiwikConfig(Component):
    def __init__(self):
        import pkg_resources # here or with the other imports
        # bind the 'foo' catalog to the specified locale directory
        locale_dir = pkg_resources.resource_filename(__name__, 'locale')
        add_domain(self.env.path, locale_dir)
        
    tracking_site = Option(
        'piwik', 'tracking_site', None,
        """Piwik's tracked site ID.
        This ID is needed to know which site is tracked.""")
    tracking_server = Option(
        'piwik', 'tracking_server', None,"""_('Option tracking_server')"""
        )

# ==============================================================================
# Piwik Resources
# ==============================================================================
class PiwikResources(Component):
    implements(ITemplateProvider)
    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        """Return the absolute path of a directory containing additional
        static resources (such as images, style sheets, etc).
        """
        yield 'piwik', pkg_resources.resource_filename(__name__, 'htdocs')

    def get_templates_dirs(self):
        """Return the absolute path of the directory containing the provided
        Genshi templates.
        """
        yield pkg_resources.resource_filename(__name__, 'templates')

# ==============================================================================
# Upgrade Code
# ==============================================================================
class PiwikSetup(Component):
    env = config = log = None # make pylink happy
    implements(IEnvironmentSetupParticipant)

    def environment_created(self):
        "Nothing to do when an environment is created"""
        pass
    
    def environment_needs_upgrade(self, db):
        pass

    def upgrade_environment(self, db):
        # Although we're only migrating configuration stuff and there's no
        # database queries involved, which could be done on other places,
        # I'm placing the migration code here so that it only happens once
        # and the admin notices that a migration was done.
        pass
