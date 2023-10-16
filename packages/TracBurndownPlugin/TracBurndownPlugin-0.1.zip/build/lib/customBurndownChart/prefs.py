# -*- coding: utf-8 -*-
'''
Created on Tue 16 Aug 2011

@author: leewei
'''
# ==============================================================================
# Copyright© 2011 LShift - Lee Wei <leewei@lshift.net>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from __future__            import with_statement
from config                import *
from trac.core             import *
from trac.admin            import IAdminPanelProvider
from trac.web.chrome       import ITemplateProvider, add_notice, add_warning
from pkg_resources         import resource_filename
from trac.util.text        import exception_to_unicode
from trac.util.translation import _

class BurndownChartAdminPanel(Component):
    """ Administrative configuration for custom BurnDown Charts. """
    implements(IAdminPanelProvider, ITemplateProvider)

    ############################################################################
    # IAdminPanelProvider methods #
    ############################################################################
    def get_admin_panels(self, req):
        """
            Return a list of available admin panels.

            The items returned by this function must be tuples of the form
            `(category, category_label, page, page_label)`.
        """

        if 'TRAC_ADMIN' in req.perm:
            yield ('lshift', _('LShift'), 'burndownchart', _('Burndown Chart'))

    def render_admin_panel(self, req, category, page, path_info):
        """
            Process a request for an admin panel.

            This function should return a tuple of the form `(template, data)`,
            where `template` is the name of the template to use and
            `data` is the data to be passed to the template.
        """

        req.perm.require('TRAC_ADMIN')
        options = [ 'daily_work_hours' ]
        if req.method == 'POST' and page == 'burndownchart':
            for option in options:
                self.config.set(SECTION_NAME, option, req.args.get(option))

            try:
                self.config.save()
                add_notice(req, _('Your changes have been saved.'))
            except Exception, e:
                self.log.error(
                    'Error writing to trac.ini: %s', exception_to_unicode(e))
                add_warning(req,
                    _("""Error writing to trac.ini, make sure it is writable by
                      the web server. Your changes have not been saved."""))

            req.redirect(req.href.admin(category, page))

        return 'admin_bdc.html', \
            dict((option, self.config.get(SECTION_NAME, option))
                for option in options)

    ############################################################################
    # ITemplateProvider methods #
    #  - Used to add the plugin's templates and htdocs
    ############################################################################
    def get_htdocs_dirs(self):
        """
            Return a list of directories with static resources (such as style
            sheets, images, etc.)

            Each item in the list must be a `(prefix, abspath)` tuple. The
            `prefix` part defines the path in the URL that requests to these
            resources are prefixed with.

            The `abspath` is the absolute path to the directory containing the
            resources on the local file system.
        """

        return [('prefs', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        """
            Return a list of directories containing the provided template files.
        """

        return [resource_filename(__name__, 'templates')]
