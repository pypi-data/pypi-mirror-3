{% load i18n %}
{% load erp_party %}

qx.Class.define('enre.erp.party.AbstractContactInfoWindow', {
    extend:enre.ui.view.EditWindow,
    type:'abstract',

    construct:function (serviceName, contactInfoTypeId, parent) {
        this.base(arguments, serviceName, parent);
        this.setContactInfoTypeId(contactInfoTypeId);
    },

    properties:{
        contactInfoTypeId:{
            init:null
        }
    },

    members:{
        _addFooter:function (form) {
            var checkForm = new enre.ui.form.Form();
            var active = new qx.ui.form.CheckBox('{% trans 'active' %}');
            checkForm.add(active, '', null, 'is_active');
            var solicitation = new qx.ui.form.CheckBox('{% trans 'allow solicitation' %}');
            checkForm.add(solicitation, '', null, 'is_solicitation');
            this.bindForm(checkForm);
            form.add(new enre.ui.form.Container(new enre.ui.form.HBoxRenderer(checkForm, false), true), '');
            var description = new qx.ui.form.TextArea().set({wrap:false});
            form.add(description, '{% trans 'Description' %}', null, 'description');
        },

        save:function (closeOnSave) {
            this._model.set('party', this.getParent().getPartyId());
            this._model.set('contact_info_type', this.getContactInfoTypeId());
            return this.base(arguments, closeOnSave);
        }
    }

});


qx.Class.define('enre.erp.party.ContactInfoWindow', {
    extend:enre.erp.party.AbstractContactInfoWindow,

    construct:function (contactInfoTypeId, parent) {
        this.base(arguments, 'enre.erp.party.services.ContactInfoService', contactInfoTypeId, parent);
    },

    members:{
        _initControls:function () {
            this.base(arguments);
            this.setCaption('{% trans 'Contact info' %}');
            this.setWidth(430);
            var form = new enre.ui.form.Form();
            var info = new qx.ui.form.TextField().set({required:true, maxLength:255});
            form.add(info, '{% trans 'Address' %}', null, 'info');
            this._addFooter(form);
            this.bindForm(form);
            this.addWidget(new enre.ui.form.SingleRenderer(form));
        }
    }
});


qx.Class.define('enre.erp.party.PostallAddressWindow', {
    extend:enre.erp.party.AbstractContactInfoWindow,

    construct:function (contactInfoTypeId, parent) {
        this.base(arguments, 'enre.erp.party.services.PostalAddressService', contactInfoTypeId, parent);
    },

    members:{
        _initControls:function () {
            this.base(arguments);
            this.setWidth(500);
            this.setCaption('{% trans 'Postal address' %}');
            var form = new enre.ui.form.Form();
            var toName = new qx.ui.form.TextField().set({maxLength:150});
            form.add(toName, '{% trans 'To name' %}', null, 'to_name');
            var address = new qx.ui.form.TextField().set({required:true, maxLength:255});
            form.add(address, '{% trans 'Address1' %}', null, 'address');
            var address2 = new qx.ui.form.TextField().set({maxLength:255});
            form.add(address2, '{% trans 'Address2' %}', null, 'address2');
            var city = new qx.ui.form.TextField().set({required:true, maxLength:50});
            form.add(city, '{% trans 'City' %}', null, 'city');
            var postalCode = new qx.ui.form.TextField().set({maxLength:50});
            form.add(postalCode, '{% trans 'Postal code' %}', null, 'postal_code');
            var country = new enre.ui.model.Select('enre/geo/stores/CountryStore',
                    '{% trans 'Select country' %}',
                    '{% trans 'Country' %}');
            country.addListener('changeValue', function (e) {
                region.setValue(null);
                region.setFilter({country:country.getValue()});
            }, this);
            form.add(country, '{% trans 'Country' %}', null, 'country');
            var region = new enre.ui.model.Select('enre/geo/stores/RegionStore',
                    '{% trans 'Select region' %}',
                    '{% trans 'Region' %}');
            form.add(region, '{% trans 'Region' %}', null, 'region');

            var dlg = new enre.ui.view.RelationSelect('enre/erp/party/stores/PostalAddressTypeStore', 'postaladdress',
                    '{% trans 'Select addrress type' %}', '{% trans 'Name' %}'
            );
            var addrTypes = new enre.ui.view.RelationPanel(
                    'enre/erp/party/stores/PostalAddressStore',
                    [
                        ['{% trans 'Name' %}'],
                        ['name'],
                        'id'
                    ],
                    'enre.erp.party.services.PostalAddressService',
                    'postal_address_types',
                    dlg,
                    null,
                    this
            ).set({height:126, statusBarVisible:false});

            form.add(new enre.ui.form.Container(addrTypes, true), '{% trans 'Postal address types' %}');

            this._addFooter(form);
            this.bindForm(form);
            this.addWidget(new enre.ui.form.SingleRenderer(form));
        }
    }
});


qx.Class.define('enre.erp.party.ContactInfoRelationPanel', {
    extend:enre.ui.view.RelationPanel,

    construct:function (modelUrl, serviceName, relation, parent) {
        this.base(arguments, modelUrl,
                [
                    ['{% trans 'Contact info type' %}', '{% trans 'Contact info' %}', 'contact_info_type__id', 'contact_info_type__codename'],
                    ['contact_info_type__name', 'info', 'contact_info_type__id', 'contact_info_type__codename']
                ],
                serviceName,
                relation,
                null,
                ' '
        );
        this._setFilter();
        this._table.setHiddenColumns(['contact_info_type__id', 'contact_info_type__codename']);
        this._table.setColumnWidth(3, '20%');
        this.setHeight(146);
        this.setStatusBarVisible(false);
        if (parent) {
            this.setParent(parent);
        }
    },

    members:{
        _showInactive:null,

        _initControls:function () {
            this.base(arguments);
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
                    var menuButton
                {% get_contact_info_types as contact_info_types %}
                {% for contact_info in contact_info_types %}
                    menuButton = new qx.ui.menu.Button('{% trans contact_info.codename %}');
                    menuButton.addListener('execute', function (e) {
                        this._onCreateButton('{{ contact_info.codename }}', '{{ contact_info.id }}');
                    }, this);
                    menu.add(menuButton);
                {% endfor %}
                    this._createButton.setMenu(menu);
                    this._toolbar.add(this._createButton);
                    this._createButton.setVisibility('excluded');
                    break;
                default:
                    this.base(arguments, name);
            }
        },

        _initPanel:function (type, id) {
            switch (type) {
                case 'postal_address':
                    this.setCreatePanel(new enre.erp.party.PostallAddressWindow(id));
                    break;
                default :
                    this.setCreatePanel(new enre.erp.party.ContactInfoWindow(id));
            }
        },

        _onCreateButton:function (type, id) {
            this._initPanel(type, id);
            this.base(arguments);
        },

        _onView:function (e) {
            this._initPanel(
                    this.getTable().getValueById('contact_info_type__codename', this.getTable().getFocusedRow()),
                    this.getTable().getValueById('contact_info_type__id', this.getTable().getFocusedRow())
            );
            this.base(arguments, e);
        },

        _onEdit:function (e) {
            this._initPanel(
                    this.getTable().getValueById('contact_info_type__codename', this.getTable().getFocusedRow()),
                    this.getTable().getValueById('contact_info_type__id', this.getTable().getFocusedRow())
            );
            this.base(arguments, e);
        },

        getPartyId:function () {
            return this.getParent().getPk();
        }
    }
});