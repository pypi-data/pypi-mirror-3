{% load i18n %}
{% load enre %}
{% include 'enre/erp/party/contactinfo.js' %}
{% if 'enre.erp.accounting'|is_application %}{% include 'enre/erp/accounting/paymentmethod.js' %}{% endif %}
{% if user.is_superuser %}{% include 'enre/erp/core/user.js' %}{% endif %}

qx.Class.define('enre.erp.party.PartyRelationshipWindow', {
    extend:enre.ui.view.EditWindow,

    construct:function (parent) {
        this.base(arguments, 'enre.erp.party.services.PartyRelationshipService', parent);
        this.setWidth(500);
        this.setCaption('{% trans 'Party relation' %}');
        var form = new enre.ui.form.Form();
        this._relatedParty = new enre.ui.model.Select('enre/erp/party/stores/PartyStore',
                '{% trans 'Select party' %}',
                '{% trans 'Party' %}',
                null,
                'id',
                'display_name').set({required:true});
        this._relatedParty.addListener('dataLoaded', function (e) {
            if (!this.isVisible()) {
                return;
            }
            role.setFilter({'party_types__in':[e.getData() ? e.getData().get('party_type') : 0]});
            role.setExclude({partyrelationship__related_party:this._relatedParty.getValue()});
            if (!role.getUrl()) {
                role.setUrl('enre/erp/party/stores/PartyRoleStore');
            } else {
                role.reloadData();
            }
        }, this);
        form.add(this._relatedParty, '{% trans 'Related party' %}', null, 'related_party');
        var role = new enre.ui.model.SelectBox().set({required:true});
        form.add(role, '{% trans 'Party role' %}', null, 'related_party_role');
        this.bindForm(form);
        this.addWidget(new enre.ui.form.SingleRenderer(form));
    },

    members:{
        _parentPartyId:null,
        _relatedParty:null,

        _show:function (mode, pk) {
            this._parentPartyId = this.getParent().getParent().getPk();
            this._relatedParty.setExclude({'id__in':[this._parentPartyId]})
            this.base(arguments, mode, pk);
        },

        save:function (closeOnSave) {
            this._model.set('parent_party', this._parentPartyId);
            return this.base(arguments, closeOnSave);
        }
    }

});


qx.Class.define('enre.erp.party.PartyEditPanel', {
    extend:enre.ui.view.EditPanel,
    type:'abstract',

    properties:{
        isOwnVisible: {
            init: false
        }
    },

    members:{

        _initPanels:function () {
            this._contactInfoPanel();
            this._paymentMethodPanel();
            this._relationPanel();
        },

        _contactInfoPanel:function () {
            var contactInfoGroup = new qx.ui.groupbox.GroupBox('{% trans 'Contact info' %}').set({layout:new qx.ui.layout.Grow()});
            contactInfoGroup.add(new enre.erp.party.ContactInfoRelationPanel(
                    'enre/erp/party/stores/PartyStore',
                    'enre.erp.party.services.PartyService',
                    'contactinfo_set',
                    this
            ));
            this.addWidget(contactInfoGroup);
        },

        _paymentMethodPanel:function () {
            {% if 'enre.erp.accounting'|is_application %}
            var paymentMethodGroup = new qx.ui.groupbox.GroupBox('{% trans 'Payment methods' %}').set({layout:new qx.ui.layout.Grow()});
            paymentMethodGroup.add(new enre.erp.accounting.PaymentMethodRelationPanel(
                    'enre/erp/party/stores/PartyStore',
                    'enre.erp.party.services.PartyService',
                    'paymentmethod_set',
                    this
            ));
            this.addWidget(paymentMethodGroup);
            {% endif %}
        },

        _relationPanel:function () {
            var relationPanel = new qx.ui.container.Composite(new qx.ui.layout.HBox(5));
            var partyRelationshipGroup = new qx.ui.groupbox.GroupBox('{% trans 'Party relationships' %}').set({layout:new qx.ui.layout.Grow()});
            var partyRelationship = new enre.ui.view.RelationPanel(
                    'enre/erp/party/stores/PartyStore',
                    [
                        ['{% trans 'Party' %}', '{% trans 'Party role' %}'],
                        ['related_party__display_name', 'related_party_role__name'],
                        'id'
                    ],
                    'enre.erp.party.services.PartyService',
                    'parent_party',
                    null,
                    enre.erp.party.PartyRelationshipWindow,
                    this
            ).set({height:146, statusBarVisible:false, visibleView:false, visibleEdit:false});
            partyRelationship.setColumnWidth(4, '20%');
            partyRelationshipGroup.add(partyRelationship);
            relationPanel.add(partyRelationshipGroup, {flex:1});
            var dlg = new enre.ui.view.RelationSelect('enre/erp/core/stores/UserStore', 'party',
                    '{% trans 'Select user' %}', '{% trans 'Party user' %}', null, 'id', 'username'
            );
            {% if user.is_superuser %}
            var usersGroup = new qx.ui.groupbox.GroupBox('{% trans 'Users' %}').set({layout:new qx.ui.layout.Grow()});
            var users = new enre.ui.view.RelationPanel(
                    'enre/erp/party/stores/PartyStore',
                    [
                        ['{% trans 'Username' %}', '{% trans 'First name' %}', '{% trans 'Last name' %}'],
                        ['username', 'first_name', 'last_name']
                    ],
                    'enre.erp.party.services.PartyService',
                    'users',
                    dlg,
                    new enre.erp.core.UserWindow(),
                    this
            ).set({height:146, statusBarVisible:false});
            usersGroup.add(users);
            relationPanel.add(usersGroup, {flex:1});
            {% endif %}
            this.addWidget(relationPanel);
        }
    }

});


qx.Class.define('enre.erp.party.OrganizationEditPanel', {
    extend:enre.erp.party.PartyEditPanel,

    members:{
        _initControls:function () {
            this.base(arguments);
            var panel = new enre.ui.container.Panel();
            var form = new enre.ui.form.Form();
            var name = new qx.ui.form.TextField().set({required:true, maxLength:100});
            form.add(name, '{% trans 'Name' %}', null, 'name');
            var shortName = new qx.ui.form.TextField().set({maxLength:50});
            form.add(shortName, '{% trans 'Short name' %}', null, 'short_name');
            this.bindForm(form);
            panel.add(new enre.ui.form.HBoxRenderer(form));
            this.addWidget(panel);
            this.setIsOwnVisible(true);
            this._initPanels();
        },

        _initPanels:function () {
            this._codesPanel(true);
            this.base(arguments);
        },

        _codesPanel:function () {
            var codePanel = new enre.ui.container.Panel();
            var codeForm = new enre.ui.form.Form();
            var inn = new qx.ui.form.TextField().set({maxLength:10});
            codeForm.add(inn, '{% trans 'INN' %}', null, 'inn');
            var kpp = new qx.ui.form.TextField().set({maxLength:9});
            codeForm.add(kpp, '{% trans 'KPP' %}', null, 'kpp');
            var ogrn = new qx.ui.form.TextField().set({maxLength:13});
            codeForm.add(ogrn, '{% trans 'OGRN' %}', null, 'ogrn');
            var okpo = new qx.ui.form.TextField().set({maxLength:11});
            codeForm.add(okpo, '{% trans 'OKPO' %}', null, 'okpo');
            var okato = new qx.ui.form.TextField().set({maxLength:11});
            codeForm.add(okato, '{% trans 'OKATO' %}', null, 'okato');
            if (this.getIsOwnVisible()) {
                var isOwn = new qx.ui.form.CheckBox('{% trans 'own organization'%}');
                codeForm.add(isOwn, '', null, 'is_own');
            }
            this.bindForm(codeForm);
            codePanel.add(new enre.ui.form.HBoxRenderer(codeForm));
            this.addWidget(codePanel);
        }
    }
});


qx.Class.define('enre.erp.party.PersonEditPanel', {
    extend:enre.erp.party.PartyEditPanel,

    members:{
        _initControls:function () {
            this.base(arguments);
            var panel = new enre.ui.container.Panel();
            var form = new enre.ui.form.Form();
            var firstName = new qx.ui.form.TextField().set({required:true, maxLength:50});
            var lastName = new qx.ui.form.TextField().set({required:true, maxLength:50});
            var middleName = new qx.ui.form.TextField().set({maxLength:50});
            form.add(firstName, '{% trans 'First name' %}', null, 'first_name');
            form.add(lastName, '{% trans 'Last name' %}', null, 'last_name');
            form.add(middleName, '{% trans 'Middle name' %}', null, 'middle_name');
            this.bindForm(form);
            panel.add(new enre.ui.form.HBoxRenderer(form));
            this.addWidget(panel);
            this.setIsOwnVisible(true);
            this._initPanels();
        },

        _codesPanel: function() {
            this._codePanel = new qx.ui.groupbox.CheckGroupBox('{% trans 'Business owner' %}').set({layout:new qx.ui.layout.Grow()});
            var codeForm = new enre.ui.form.Form();
            var inn = new qx.ui.form.TextField().set({maxLength:10});
            codeForm.add(inn, '{% trans 'INN' %}', null, 'inn');
            var ogrn = new qx.ui.form.TextField().set({maxLength:13});
            codeForm.add(ogrn, '{% trans 'OGRNIP' %}', null, 'ogrn');
            var okpo = new qx.ui.form.TextField().set({maxLength:11});
            codeForm.add(okpo, '{% trans 'OKPO' %}', null, 'okpo');
            var okato = new qx.ui.form.TextField().set({maxLength:11});
            codeForm.add(okato, '{% trans 'OKATO' %}', null, 'okato');
            if (this.getIsOwnVisible()) {
                var isOwn = new qx.ui.form.CheckBox('{% trans 'own person'%}');
                codeForm.add(isOwn, '', null, 'is_own');
            }
            this.bindForm(codeForm);
            this._codePanel.add(new enre.ui.form.HBoxRenderer(codeForm));
            this.addWidget(this._codePanel);

        },

        _initPanels: function() {
            this._codesPanel();
            this.base(arguments);
        },

        _initModel:function (model) {
            this.base(arguments, model);
            var legend = this._codePanel.getChildControl('legend');
            var controller = new qx.data.controller.Object(this._model);
            controller.addTarget(legend, 'value', 'is_business_owner', true);
        }
    },

    destruct:function () {
        this._codePanel = null;
    }
});


qx.Class.define('enre.erp.party.PartiesView', {
    extend:enre.ui.view.ViewPanel,
    type: 'abstract',

    construct:function (storeUrl) {
        var url = storeUrl ? storeUrl : 'enre/erp/party/stores/PartyStore';
        this.base(arguments, url,
                [
                    ['{% trans 'Party name' %}', '{% trans 'Party type' %}', 'party_type__codename'],
                    ['display_name', 'party_type__name', 'party_type__codename']
                ],
                'enre.erp.party.services.OrganizationService',
                enre.erp.party.OrganizationEditPanel
        );
        this.setHiddenColumns(['party_type__codename']);
        this.setColumnWidth(1, '20%');
        var filter = new enre.ui.view.FilterPanel();
        var filterForm = new qx.ui.form.Form();
        var partyTypeSelect = new enre.ui.model.SelectBox('enre/erp/party/stores/PartyTypeStore');
        filterForm.add(partyTypeSelect, '{% trans 'Party type' %}', null, 'party_type__id');
        var nameField = new qx.ui.form.TextField();
        filterForm.add(nameField, '{% trans 'Party name' %}', null, 'display_name__icontains');
        filter.setForm(filterForm);
        this.setFilterPanel(filter);
    },

    events:{
        'create':'qx.event.type.Data'
    },

    properties: {
        organizationEditPanel: {
            init: enre.erp.party.OrganizationEditPanel
        },
        organizationService: {
            init: 'enre.erp.party.services.OrganizationService'
        },
        personEditPanel: {
            init: enre.erp.party.PersonEditPanel
        },
        personService: {
            init: 'enre.erp.party.services.PersonService'
        }
    },

    members:{

        _initParty:function (partyType) {
            var partyType = partyType ? partyType : this.getTable().getTableModel().getValueById('party_type__codename', this.getTable().getFocusedRow());
            if (partyType == 'organization') {
                this.setServiceName(this.getOrganizationService());
                this.setEditPanel(this.getOrganizationEditPanel());
            } else if (partyType == 'person') {
                this.setServiceName(this.getPersonService());
                this.setEditPanel(this.getPersonEditPanel());
            } else {
                throw new Error("Bad party type '" + partyType + "'");
            }
        },

        _onView:function () {
            this._initParty();
            this.base(arguments);
        },

        _onCreate:function (e) {
            this._initParty(e.getData());
            this.base(arguments);
        },

        _onEdit:function () {
            this._initParty();
            this.base(arguments);
        },

        _onDelete:function () {
            this._initParty();
            this.base(arguments);
        }

    }

});
