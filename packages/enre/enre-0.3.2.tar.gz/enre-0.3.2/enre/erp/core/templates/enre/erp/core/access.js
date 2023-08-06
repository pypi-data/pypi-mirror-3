{% load i18n %}


qx.Class.define('enre.erp.core.UserEditPanel', {
    extend:enre.ui.view.EditPanel,

    members:{
        _initControls:function () {
            this.base(arguments);
            this.getContainer().setLayout(new qx.ui.layout.Dock());
            var panel = new qx.ui.container.Composite(new qx.ui.layout.HBox(10)).set({padding:[0, 0, 5, 0]});
            var loginForm = new enre.ui.form.Form();
            loginForm.addGroupHeader('{% trans 'Login information' %}');
            var username = new qx.ui.form.TextField().set({required:true, maxLength:30});
            loginForm.add(username, '{% trans 'Username' %}', null, 'username');
            var passwdValidator = function (value, item) {
                if (!passwd.getValue() || (passwd.getValue() != passwd2.getValue())) {
                    passwd.setValid(false);
                    passwd2.setValid(false);
                    return false;
                }
                return true;
            }
            var passwd = new qx.ui.form.PasswordField().set({required:true, maxLength:128});
            loginForm.add(passwd, '{%  trans 'Password' %}', passwdValidator, 'password');
            var passwd2 = new qx.ui.form.PasswordField().set({required:true, maxLength:128});
            loginForm.add(passwd2, '{%  trans 'Confirm' %}', passwdValidator);
            var manager = new enre.ui.form.ValidationManager();
            var passwdValidator = function (value, item) {
                alert(this);
            }
            var isActive = new qx.ui.form.CheckBox('{% trans 'active' %}');
            loginForm.add(isActive, '', null, 'is_active');
            var isSuperuser = new qx.ui.form.CheckBox('{% trans 'superuser' %}');
            loginForm.add(isSuperuser, '', null, 'is_superuser');
            var isStaff = new qx.ui.form.CheckBox('{% trans 'staff' %}');
            loginForm.add(isStaff, '', null, 'is_staff');
            this.bindForm(loginForm);
            panel.add(new enre.ui.form.SingleRenderer(loginForm), {width:'50%'});
            var personalForm = new enre.ui.form.Form();
            personalForm.addGroupHeader('{% trans 'Personal information' %}');
            var firstName = new qx.ui.form.TextField().set({maxLength:30});
            personalForm.add(firstName, '{% trans 'First name' %}', null, 'first_name');
            var lastName = new qx.ui.form.TextField().set({maxLength:30});
            personalForm.add(lastName, '{% trans 'Last name' %}', null, 'last_name');
            var email = new qx.ui.form.TextField().set({maxLength:75});
            personalForm.add(email, '{% trans 'e-Mail' %}', null, 'email');
            personalForm.addGroupHeader('{% trans 'Additional information' %}');
            var loginInfoForm = new enre.ui.form.Form();
            var dateJoined = new enre.ui.form.DateField();
            loginInfoForm.add(dateJoined, '{% trans 'Date joined' %}', null, 'date_joined');
            var lastLogin = new enre.ui.form.DateField();
            loginInfoForm.add(lastLogin, '{% trans 'Last login' %}', null, 'last_login');
            this.bindForm(loginInfoForm);

            personalForm.add(new enre.ui.form.Container(new enre.ui.form.HBoxRenderer(loginInfoForm)), '');

            this.bindForm(personalForm);
            panel.add(new enre.ui.form.SingleRenderer(personalForm), {width:'50%'});


            this.addWidget(panel, {edge:'north'});


            var selectPanel = new qx.ui.splitpane.Pane();
            var appsSelect = new enre.ui.view.ManyToManySelect(
                    'enre/erp/core/stores/ApplicationStore',
                    [
                        ['{% trans 'Name' %}'],
                        ['name'],
                        'view_name'
                    ],
                    'user',
                    'enre.erp.core.services.UserService',
                    'erp_applications',
                    this
            );
            appsSelect.setMinWidth(300);
            appsSelect.setColumnWidth(0, '100%');
            appsSelect.setUnselectCaption('{% trans 'Applications' %}');
            appsSelect.setSelectCaption('{% trans 'User applications' %}');
            selectPanel.add(appsSelect);
            var groupSelect = new enre.ui.view.ManyToManySelect(
                    'enre/erp/core/stores/GroupStore',
                    [
                        ['{% trans 'Name' %}'],
                        ['name']
                    ],
                    'user',
                    'enre.erp.core.services.UserService',
                    'groups',
                    this
            );
            groupSelect.setMinWidth(300);
            groupSelect.setColumnWidth(0, '100%');
            groupSelect.setUnselectCaption('{% trans 'Groups' %}');
            groupSelect.setSelectCaption('{% trans 'User groups' %}');
            selectPanel.add(groupSelect);
            this.addWidget(selectPanel, {edge:'center'});

            this.addListener('dataLoaded', function (e) {
                passwd2.setValue(passwd.getValue());
            }, this);
            this.addListener('appear', function (e) {
                dateJoined.setReadOnly(true);
                lastLogin.setReadOnly(true);
            }, this);
        }

    }

});


qx.Class.define('enre.erp.core.UserPanel', {
    extend:enre.ui.view.ViewPanel,

    construct:function () {
        this.base(arguments, 'enre/erp/core/stores/UserStore',
                [
                    [
                        '{% trans 'Username' %}', '{% trans 'First name' %}',
                        '{% trans 'Last name' %}', '{% trans 'Active' %}', '{% trans 'Staff' %}'
                    ],
                    ['username', 'first_name', 'last_name', 'is_active', 'is_staff']
                ],
                'enre.erp.core.services.UserService',
                enre.erp.core.UserEditPanel
        );
        this.setColumnWidth(3, '5%');
        this.setDataCellRenderer(3, new qx.ui.table.cellrenderer.Boolean());
        this.setColumnWidth(4, '5%');
        this.setDataCellRenderer(4, new qx.ui.table.cellrenderer.Boolean());
    }
});


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