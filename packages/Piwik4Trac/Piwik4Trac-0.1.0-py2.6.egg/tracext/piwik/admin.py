# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2010 kent1 <kent1@arscenic.info>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

import pkg_resources
from trac.admin import IAdminPanelProvider
from trac.config import Option, _TRUE_VALUES
from trac.core import Component, implements
from trac.web.chrome import add_stylesheet,add_script
from trac.util.translation import domain_functions

_, tag_, N_, add_domain = domain_functions('piwik4trac', ('_', 'tag_', 'N_', 'add_domain'))
        
class PiwikAdmin(Component):
    config = env = log = None
    options = {}
    implements(IAdminPanelProvider)
    
    def __init__(self):
        locale_dir = pkg_resources.resource_filename(__name__, 'locale')
        add_domain(self.env.path, locale_dir)
        
    # IAdminPanelProvider methods
    def get_admin_panels(self, req):
        if req.perm.has_permission('TRAC_ADMIN'):
            yield ('piwik', 'Piwik', 'analytics', _('Title analytics'))

    def render_admin_panel(self, req, cat, page, path_info):
        if req.locale is not None: 
            add_script(req, 'piwik/%s.js' % req.locale)
        add_stylesheet(req, 'piwik/piwik.css')
        if req.method.lower() == 'post':
            self.config.set('piwik', 'tracking_site',
                            req.args.get('tracking_site'))
            self.config.set('piwik', 'tracking_server',
                            req.args.get('tracking_server'))
            self.config.save()
        self.update_config()
        return 'piwik_admin.html', {'piwik': self.options}

    def update_config(self):
        for option in [option for option in Option.registry.values()
                       if option.section == 'piwik']:
            if option.name in ('admin_logging', 'authenticated_logging',
                               'outbound_link_tracking'):
                value = self.config.getbool('piwik', option.name,
                                            option.default)
                option.value = value
            else:
                value = self.config.get('piwik', option.name,
                                        option.default)
                option.value = value
            self.options[option.name] = option
