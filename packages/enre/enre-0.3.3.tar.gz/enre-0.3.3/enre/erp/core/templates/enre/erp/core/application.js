{% load url from future %}
{% load i18n %}

{% if module_content %}
    {{ module_content }}
{% endif %}

qx.Class.define('enre.erp.Application', {
    extend:qx.application.Standalone,
    include:[qx.locale.MTranslation],

    properties: {
        container: {nullable: true, init: null}
    },

    members:{

        main:function () {
            this.base(arguments);
            {% if current_module.color %}
            enre.erp.theme.Util.shiftColor('{{ current_module.color }}');
            {% else %}
            qx.theme.manager.Meta.getInstance().setTheme(enre.erp.theme.Theme);
            {% endif %}
            var container = new qx.ui.container.Composite(new qx.ui.layout.Dock());
            var appbar = new enre.erp.ui.appbar.Bar();
            var btn;
            {% for app in apps_list %}
            btn = new enre.erp.ui.appbar.Button('{% trans app.name %}', '{% url app.view_name '' %}');
            appbar.add(btn);
            {% endfor %}
            appbar.addSpacer();
            {% get_current_language as LANGUAGE_CODE %}
            {% get_language_info for LANGUAGE_CODE as lang %}
            {% get_available_languages as LANGUAGES %}
            var langButton = new enre.erp.ui.appbar.Button('{{ lang.name_local }}');
            appbar.add(langButton);
            var langMenu = new qx.ui.menu.Menu();
            {% for lang_code, lang_name in LANGUAGES %}
                btn = new qx.ui.menu.Button('{{ lang_name }}');
                btn.addListener('execute', function(e) {this.setLocale('{{ lang_code }}')}, this);
                langMenu.add(btn);
            {% endfor %}
            langButton.setMenu(langMenu);

            var logoutButton = new enre.erp.ui.appbar.Button(this.tr('Logout'));
            logoutButton.addListener('execute', function (e) {
                enre.ui.dialog.Dialog.warning('Logout ?', 'yes-no').show().addListener('yes', function (e) {
                    var rpc = new enre.remote.Rpc('enre.qx.services.AuthService');
                    try {
                        rpc.callSync('logout');
                        location.reload();
                    } catch (ex) {
                        enre.ui.dialog.Dialog.error(ex.toString());
                    }
                }, this);
                var rpc = new enre.remote.Rpc('enre.qx.services.AuthService');
            }, this);
            appbar.add(logoutButton);
            container.add(appbar, {edge:'north'});
            {% if modules_list and modules_list|length > 1 %}
                var moduleTab = new enre.erp.ui.moduletab.ModuleTab();
                var page;
                {% for module in modules_list %}
                page = new enre.erp.ui.moduletab.Page('{% trans module.name %}', '{% url app_view_name module.path %}');
                moduleTab.add(page);
                {% if module == current_module %}
                    page.setLayout(new qx.ui.layout.Grow());
                    moduleTab.setSelection([page]);
                    this.setContainer(page);
                {% endif %}
                {% endfor %}
                var _selFlag = false;
                moduleTab.addListener('changeSelection', function(e) {
                    if (_selFlag)
                        return;
                    _selFlag = true;
                    location.href = moduleTab.getSelection()[0].getUrl();
                    moduleTab.setSelection([this.getContainer()]);
                }, this);
                container.add(moduleTab, {edge:'center'});
            {% else %}
                this.setContainer(new qx.ui.container.Composite(new qx.ui.layout.Grow()));
                container.add(this.getContainer(), {edge: 'center'});
            {% endif %}
            {% if current_module %}
            var module = new {{ current_module.script_class }}(this);
            this.getContainer().add(module);
            {% endif %}
            this.getRoot().add(container, {edge:0});
        },

        setLocale: function(lang) {
            var rpc = new enre.remote.Rpc('enre.qx.services.LanguageService');
            try {
                rpc.callSync('set_language', lang);
                location.reload();
            } catch (ex) {
                enre.ui.dialog.Dialog.error(ex.toString()).show();
            }
        }

    }

});

