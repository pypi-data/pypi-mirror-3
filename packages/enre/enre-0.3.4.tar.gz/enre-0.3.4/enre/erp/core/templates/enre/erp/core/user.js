{% load i18n %}


qx.Mixin.define('enre.erp.core.MUserForm', {
    extend: enre.ui.view.MEditContainer,

    construct: function(parent) {
        this.setServiceName('enre.erp.core.services.UserService');
        if (parent) {
            this.setParent(parent);
        }
    },

    members:{
        _initUserForm:function () {
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


qx.Class.define('enre.erp.core.UserEditPanel', {
    extend:enre.ui.view.EditPanel,
    include: [enre.erp.core.MUserForm],

    members: {
        _initControls: function() {
            this.base(arguments);
            this._initUserForm();
        }
    }
});


qx.Class.define('enre.erp.core.UserWindow', {
    extend:enre.ui.view.EditWindow,
    include: [enre.erp.core.MUserForm],

    members: {
        _initControls: function() {
            this.base(arguments);
            this.setWidth(950);
            this.setHeight(500);
            this.setCaption('{% trans 'User' %}');
            this._initUserForm();
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
