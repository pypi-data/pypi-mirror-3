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
                redirect_path = self.request.path + self.modules.items()[0][0]
                return http.HttpResponseRedirect(redirect_path)
            elif len(self.modules) > 0 and len(context['apps_list']) > 0:
                if not self.modules.has_key(path):
                    raise ViewDoesNotExist("Module path '%s' not found" % path)
                module = self.modules[path]
                if issubclass(module.__class__, Module):
                    module_content = module.dispatch(request, *args, **context)
                else:
                    raise ValueError("Bad module type '%s'" % type(module))
                context['module_content'] = module_content.rendered_content
                context['current_module'] = module
                modules_list = []
                for module in self.modules:
                    item = self.modules[module]
                    setattr(item, 'path', module)
                    modules_list.append(item)
                context['modules_list'] = modules_list
            pass
        return self.render_to_response(context)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ApplicationView, self).dispatch(request, *args, **kwargs)

    pass


class SettingsView(ApplicationView):
    name = 'Settings'

    modules = {
        'access': Module(
            name = 'Access',
            template_name = 'enre/erp/core/access.js',
            script_class = 'enre.erp.core.Access'
        ),
        'references': Module(
            name='References',
            template_name = 'enre/erp/core/references.js',
            script_class = 'enre.erp.core.References'
        )
    }



# -------- TEST -------- #

class AppView1(ApplicationView):
    name = 'Application-1'
    modules = {
        'testapp': Module(
            name='Test Module1-1',
            template_name='enre/erp/core/test_module.js',
            script_class='TestModule',
            color='#CD853F'
        ),
        'testapp2': Module(
            name='Test Module1-2',
            template_name='enre/erp/core/test_module.js',
            script_class='TestModule',
            color='#2E8B57'
        ),
        'testapp3': Module(
            name='Test Module1-3',
            template_name='enre/erp/core/test_module.js',
            script_class='TestModule'
        ),
        'testapp4': Module(
            name='Test Module1-4',
            template_name='enre/erp/core/test_module.js',
            script_class='TestModule'
        ),
        'testapp5': Module(
            name='Test Module1-5',
            template_name='enre/erp/core/test_module.js',
            script_class='TestModule'
        ),
        'testapp6': Module(
            name='Test Module1-6',
            template_name='enre/erp/core/test_module.js',
            script_class='TestModule'
        )

        #'testapp': ApplicationModule(name='Test Module', template_name='testapp.js')
    }

    def __init__(self, **kwargs):
        super(AppView1, self).__init__(**kwargs)

    pass


class AppView2(ApplicationView):
    name = 'Application-2'
    modules = {
        'testapp': Module(
            name='Test Module2-1',
            template_name='enre/erp/core/test_module.js',
            script_class='TestModule'
        ),
        'testapp2': Module(
            name='Test Module2-2',
            template_name='enre/erp/core/test_module.js',
            script_class='TestModule'
        )
    }


class AppView3(ApplicationView):
    name = 'Application-3'


class AppView4(ApplicationView):
    name = 'Application-4'


class AppView5(ApplicationView):
    name = 'Application-5'