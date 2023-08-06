{% load i18n %}
{% load erp_accounting %}


qx.Class.define('enre.erp.accounting.AbstractPaymentMethodWindow', {
    extend:enre.ui.view.EditWindow,
    type:'abstract',

    construct:function (serviceName, paymentMethodTypeId, parent) {
        this.base(arguments, serviceName, parent);
        this.setPaymentMethodTypeId(paymentMethodTypeId);
    },

    properties:{
        paymentMethodTypeId:{
            init:null
        }
    },

    members:{
        _addFooter:function (form) {
            var active = new qx.ui.form.CheckBox('{% trans 'active' %}');
            form.add(active, '', null, 'is_active');
            var description = new qx.ui.form.TextArea().set({wrap:false});
            form.add(description, '{% trans 'Description' %}', null, 'description');
        },

        save:function (closeOnSave) {
            this._model.set('party', this.getParent().getPartyId());
            this._model.set('payment_method_type', this.getPaymentMethodTypeId());
            return this.base(arguments, closeOnSave);
        }
    }

});


qx.Class.define('enre.erp.accounting.BankAccountWindow', {
    extend:enre.erp.accounting.AbstractPaymentMethodWindow,

    construct:function (paymentMethodTypeId, parent) {
        this.base(arguments, 'enre.erp.accounting.services.BankAccountService', paymentMethodTypeId, parent);
    },

    members:{
        _initControls:function () {
            this.base(arguments);
            this.setCaption('{% trans 'Bank account' %}');
            this.setWidth(400);
            var form = new enre.ui.form.Form();
            var bankName = new qx.ui.form.TextField().set({required:true, maxLength:100});
            form.add(bankName, '{% trans 'Bank name' %}', null, 'bank_name');
            var accountNumber = new qx.ui.form.TextField().set({required:true, maxLength:100});
            form.add(accountNumber, '{% trans 'Bank account' %}', null, 'account');
            var loroAccount = new qx.ui.form.TextField().set({maxLength:100});
            form.add(loroAccount, '{% trans 'Corr. account' %}', null, 'corr_account');
            var bankCode = new qx.ui.form.TextField().set({maxLength:9});
            form.add(bankCode, '{% trans 'Bank code' %}', null, 'bank_code');
            this._addFooter(form);
            this.bindForm(form);
            this.addWidget(new enre.ui.form.SingleRenderer(form));
        }
    }

});


qx.Class.define('enre.erp.accounting.CreditCardWindow', {
    extend:enre.erp.accounting.AbstractPaymentMethodWindow,

    construct:function (paymentMethodTypeId, parent) {
        this.base(arguments, 'enre.erp.accounting.services.CreditCardService', paymentMethodTypeId, parent);
    },

    members:{
        _initControls:function () {
            this.base(arguments);
            this.setCaption('{% trans 'Credit card' %}');
            this.setWidth(400);
            var form = new enre.ui.form.Form();
            var firstName = new qx.ui.form.TextField().set({required:true, maxLength:50});
            form.add(firstName, '{% trans 'First name' %}', null, 'first_name');
            var lastName = new qx.ui.form.TextField().set({required:true, maxLength:50});
            form.add(lastName, '{% trans 'Last name' %}', null, 'last_name');
            var cardType = new enre.ui.model.SelectBox('enre/erp/accounting/stores/CreditCardTypeStore').set({required:true});
            form.add(cardType, '{% trans 'Card type' %}', null, 'credit_card_type');
            var cardNumber = new qx.ui.form.TextField().set({required:true, maxLength:100});
            form.add(cardNumber, '{% trans 'Number' %}', null, 'number');

            var expireDate = new qx.ui.form.DateField().set({required:true});
            form.add(expireDate, '{% trans 'Expire date' %}', null, 'expire_date');
            this._addFooter(form);
            this.bindForm(form);
            this.addWidget(new enre.ui.form.SingleRenderer(form));
        }
    }

});


qx.Class.define('enre.erp.accounting.PaymentMethodRelationPanel', {
    extend:enre.ui.view.RelationPanel,

    construct:function (modelUrl, serviceName, relation, parent) {
        this.base(arguments, modelUrl,
                [
                    ['{% trans 'Payment method type' %}', '{% trans 'Payment method' %}', 'payment_method_type__id', 'payment_method_type__codename'],
                    ['payment_method_type__name', 'method', 'payment_method_type__id', 'payment_method_type__codename']
                ],
                serviceName,
                relation,
                null,
                ' ',
                parent
        );
        this.setHiddenColumns(['payment_method_type__id', 'payment_method_type__codename']);
        this._table.setColumnWidth(3, '20%');
        this._setFilter();
    },

    members:{

        _showInactive:null,

        _initControls:function () {
            this.base(arguments);
            this.setHeight(146);
            this.setStatusBarVisible(false);
            this._showInactive = new qx.ui.form.CheckBox('{% trans 'Show inactive' %}').set({margin:[0, 15]});
            this._showInactive.addListener('changeValue', function (e) {
                this._setFilter();
            }, this);
            this._toolbar.add(this._showInactive);
        },

        _setFilter:function () {
            if (this._showInactive.getValue()) {
                this._model.setFilter(null);
            } else {
                this._model.setFilter({is_active:true});
            }
            this.reloadData();
        },

        _toolbarButton:function (name) {
            switch (name) {
                case 'create':
                    this._createButton = new qx.ui.form.MenuButton(this.tr('btn_create'),
                            this._getIconPath() + 'document-new.png'
                    ).set({margin:0});
                    var menu = new qx.ui.menu.Menu();
                {% get_payment_method_types as payment_method_types %}
                {% for payment_method_type in payment_method_types %}
                    var menuButton = new qx.ui.menu.Button('{% trans  payment_method_type.codename %}');
                    menuButton.addListener('execute', function (e) {
                        this._onCreateButton('{{ payment_method_type.codename }}', '{{ payment_method_type.id }}');
                    }, this);
                    menu.add(menuButton);
                {% endfor %}
                    this._createButton.setMenu(menu);
                    this._toolbar.add(this._createButton);
                    this._createButton.setVisibility('excluded');
                    break;
                default :
                    this.base(arguments, name);
            }
        },

        _initPanel:function (type, id) {
            switch (type) {
                case 'bank_account':
                    this.setCreatePanel(new enre.erp.accounting.BankAccountWindow(id));
                    break;
                case 'credit_card':
                    this.setCreatePanel(new enre.erp.accounting.CreditCardWindow(id));
                    break;
                default :
                    throw new Error('Bad payment method type')
            }
        },

        _onCreateButton:function (type, id) {
            this._initPanel(type, id);
            this.base(arguments);
        },

        _onView: function(e) {
            this._initPanel(
                    this.getTable().getValueById('payment_method_type__codename', this.getTable().getFocusedRow()),
                    this.getTable().getValueById('payment_method_type__id', this.getTable().getFocusedRow())
            );
            this.base(arguments, e);
        },

        _onEdit: function(e) {
            this._initPanel(
                    this.getTable().getValueById('payment_method_type__codename', this.getTable().getFocusedRow()),
                    this.getTable().getValueById('payment_method_type__id', this.getTable().getFocusedRow())
            );
            this.base(arguments, e);
        },

        getPartyId:function () {
            return this.getParent().getPk();
        }
    }

});
