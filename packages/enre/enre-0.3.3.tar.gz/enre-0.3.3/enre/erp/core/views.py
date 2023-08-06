# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django import http
from enre.qx.views import ApplicationView as _ApplicationView
from enre.views import ScriptView
from enre.erp.core.models import Application
from django.core.urlresolvers import ViewDoesNotExist, resolve

class Module(ScriptView):
    name = None
    path = None
    script_class = None
    color = None


class ApplicationView(_ApplicationView):
    name = None
    script_template = 'enre/erp/core/application.js'
    script_class = 'enre.erp.Application'
    scripts_src = [settings.STATIC_URL + 'enre/qx/theme/simple.js',
                   settings.STATIC_URL + 'enre/erp/core/erp_core.js']
    theme_url = None
    theme_class = None
    modules = {}

    def get_context_data(self, **kwargs):
        data = super(ApplicationView, self).get_context_data(**kwargs)
        data['apps_list'] = Application.objects.all()
        data['app_view_name'] = resolve(self.request.path).url_name;
        return data

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if kwargs.has_key('path'):
            path = kwargs['path']
            if len(path) == 0 and len(self.modules) > 0:
                redirect_path = self.request.path + self.modules[0].path
                return http.HttpResponseRedirect(redirect_path)
            elif len(self.modules) > 0 and len(context['apps_list']) > 0:
                paths = []
                module_content = None
                for module in self.modules:
                    if not isinstance(module, Module):
                        raise ValueError("Bad module type '%s'" % type(module))
                    paths.append(module.path)
                    if module.path == path:
                        module_content = module.dispatch(request, *args, **context)
                        context['module_content'] = module_content.rendered_content
                        context['current_module'] = module
                    pass
                if not module_content:
                    raise ViewDoesNotExist("Module path '%s' not found" % path)
                context['modules_list'] = self.modules
            pass
        return self.render_to_response(context)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ApplicationView, self).dispatch(request, *args, **kwargs)

    pass


class AccessModule(Module):
    name = 'Access'
    path = 'access'
    template_name = 'enre/erp/core/access.js'
    script_class = 'enre.erp.core.Access'
    color = '#4169E1'


class ReferencesModule(Module):
    name = 'References'
    path = 'references'
    template_name = 'enre/erp/core/references.js'
    script_class = 'enre.erp.core.References'
    color = '#5F9EA0'


class SettingsView(ApplicationView):
    name = 'Settings'
    modules = [AccessModule(), ReferencesModule()]


