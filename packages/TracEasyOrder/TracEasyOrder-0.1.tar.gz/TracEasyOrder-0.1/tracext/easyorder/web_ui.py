from trac.core import Component, implements
from trac.web.api import IRequestFilter
from trac.web.chrome import ITemplateProvider, add_script


class EasyOrderModule(Component):
    implements(IRequestFilter, ITemplateProvider)

    # IRequestFilter methods
    def pre_process_request(self, req, handler):
        return handler

    def post_process_request(self, req, template, data, content_type):
        if req.path_info.startswith('/admin/ticket/'):
            add_script(req, 'easyorder/js/jquery.tablednd.0.7.min.js')
            add_script(req, 'easyorder/js/easyorder.js')
        return template, data, content_type

    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename
        return [('easyorder', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        return()
