{% load i18n %}
{% include 'enre/erp/core/user.js' %}


qx.Class.define('enre.erp.core.GroupWindow', {
    extend:enre.ui.view.EditWindow,

    members:{
        _initControls:function () {
            this.base(arguments);
            this.setWidth(400);
            this.setCaption('{% trans 'Group' %}');
            var form = new enre.ui.form.Form();
            var nameField = new qx.ui.form.TextField().set({required:true, maxLength:80, minWidth:200});
            form.add(nameField, '{% trans 'Name' %}', null, 'name');
            this.bindForm(form);
            this.addWidget(new enre.ui.form.SingleRenderer(form));
        }
    }
});


qx.Class.define('enre.erp.core.GroupPanel', {
    extend:enre.ui.view.ViewPanel,

    construct:function () {
        this.base(arguments, 'enre/erp/core/stores/GroupStore',
                [
                    ['{% trans 'Name' %}'],
                    ['name']
                ],
                'enre.erp.core.services.GroupService',
                enre.erp.core.GroupWindow
        );
    }
});

qx.Class.define('enre.erp.core.PermissionPanel', {
    extend:enre.ui.view.ViewPanel,

    construct:function () {
        this.base(arguments, 'enre/erp/core/stores/PermissionStore',
                [
                    ['{% trans 'Code name' %}', '{% trans 'Content type' %}', '{% trans 'Name' %}'],
                    ['codename', 'content_type__name', 'name']
                ]
        );
        this.setColumnWidth(0, '20%');
    }
});

qx.Class.define('enre.erp.core.ApplicationPanel', {
    extend:enre.ui.view.ViewPanel,

    construct:function () {
        this.base(arguments, 'enre/erp/core/stores/ApplicationStore',
                [
                    ['{% trans 'Name' %}'],
                    ['name'],
                    'view_name'
                ]
        );
    }
});


qx.Class.define('enre.erp.core.Access', {
    extend:enre.erp.Module,

    construct:function (parent) {
        this.base(arguments, parent, new qx.ui.layout.Grow());
        var tabView = new qx.ui.tabview.TabView('left');
        var usersPage = new qx.ui.tabview.Page('{% trans 'Users' %}').set({layout:new qx.ui.layout.Grow()});
        usersPage.addListener('appear', function (e) {
            if (usersPage.getChildren().length == 0) {
                usersPage.add(new enre.erp.core.UserPanel());
            }
        }, this);
        tabView.add(usersPage);
        var groupsPage = new qx.ui.tabview.Page('{% trans 'Groups' %}').set({layout:new qx.ui.layout.Grow()});
        groupsPage.addListener('appear', function (e) {
            if (groupsPage.getChildren().length == 0) {
                var pane = new qx.ui.splitpane.Pane('vertical');
                var groupPanel = new enre.erp.core.GroupPanel();
                pane.add(groupPanel);
                var select = new enre.ui.view.ManyToManySelect(
                        'enre/erp/core/stores/PermissionStore',
                        [
                            ['{% trans 'Content type' %}', '{% trans 'Name' %}'],
                            ['content_type__name', 'name']
                        ],
                        'group',
                        'enre.erp.core.services.GroupService',
                        'permissions',
                        groupPanel
                );
                select.setUnselectCaption('{% trans 'Permissions' %}');
                select.setSelectCaption('{% trans 'Group permissions' %}');
                pane.add(select);
                groupsPage.add(pane);
            }
        }, this);
        tabView.add(groupsPage);
        var permsPage = new qx.ui.tabview.Page('{% trans 'Permissions' %}').set({layout:new qx.ui.layout.Grow()});
        permsPage.addListener('appear', function (e) {
            if (permsPage.getChildren().length == 0) {
                permsPage.add(new enre.erp.core.PermissionPanel());
            }
        }, this);
        tabView.add(permsPage);
        var appsPage = new qx.ui.tabview.Page('{% trans 'Applications' %}').set({layout:new qx.ui.layout.Grow()});
        appsPage.addListener('appear', function (e) {
            if (appsPage.getChildren().length == 0) {
                var pane = new qx.ui.splitpane.Pane('vertical');
                var appsPanel = new enre.erp.core.ApplicationPanel();
                pane.add(appsPanel);
                var select = new enre.ui.view.ManyToManySelect(
                        'enre/erp/core/stores/UserStore',
                        [
                            ['{% trans 'Username' %}', '{% trans 'First name' %}', '{% trans 'Last name' %}'],
                            ['username', 'first_name', 'last_name']
                        ],
                        'erp_applications',
                        'enre.erp.core.services.ApplicationService',
                        'user_set',
                        appsPanel
                );
                select.setUnselectCaption('{% trans 'Users' %}');
                select.setSelectCaption('{% trans 'Application users' %}');
                pane.add(select);
                appsPage.add(pane);
            }

        }, this);
        tabView.add(appsPage);
        this.add(tabView);
    }
});