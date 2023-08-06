{% load i18n %}
{% include 'enre/erp/party/party.js' %}


qx.Class.define('enre.erp.party.OwnOrganizationEditPanel', {
    extend:enre.erp.party.OrganizationEditPanel,

    members:{
        _initPanels:function () {
            this.setIsOwnVisible(false);
            this.base(arguments);
        },

        save:function (closeOnSave) {
            this._model.set('is_own', true);
            this.base(arguments, closeOnSave);
        }

    }
});


qx.Class.define('enre.erp.party.OwnPersonEditPanel', {
    extend:enre.erp.party.PersonEditPanel,

    members:{
        _initPanels:function () {
            this.setIsOwnVisible(false);
            this.base(arguments);
        },

        _initModel:function (closeOnSave) {
            this.base(arguments, closeOnSave);
            this._model.set('is_business_owner', true);
            this._codePanel.getChildControl('legend').setEnabled(false);
        },

        save:function (closeOnSave) {
            this._model.set('is_own', true);
            this.base(arguments, closeOnSave);
        }

    }
});


qx.Class.define('enre.erp.party.OwnPariesToolBar', {
    extend:enre.ui.view.ToolBar,

    members:{
        _initControls:function () {
            this._toolbarButton('view');
            this._buttonsPart.add(new qx.ui.toolbar.Separator());
            this._toolbarButton('add');
            this._buttonsPart.add(new qx.ui.toolbar.Separator());
            this._toolbarButton('create');
            this._toolbarButton('edit');
            this._toolbarButton('delete');
            this.addSpacer();
            this._toolbarButton('refresh');
        },

        _toolbarButton:function (name) {
            switch (name) {
                case 'add':
                    var addButton = new qx.ui.toolbar.Button(this.tr('btn_add'), this._getIconPath() + 'list-add.png');
                    addButton.addListener('execute', function (e) {
                        this.getParent().fireEvent('add');
                    }, this);
                    this._buttonsPart.add(addButton);
                    break;
                case 'create':
                    var createButton = new qx.ui.toolbar.MenuButton(this.tr('btn_create'), this._getIconPath() + 'document-new.png');
                    var menu = new qx.ui.menu.Menu();
                    var organizationButton = new qx.ui.menu.Button('{% trans 'Organization' %}');
                    organizationButton.addListener('execute', function (e) {
                        this.getParent().fireDataEvent('create', 'organization');
                    }, this);
                    menu.add(organizationButton);
                    var personButton = new qx.ui.menu.Button('{% trans 'Person' %}');
                    personButton.addListener('execute', function (e) {
                        this.getParent().fireDataEvent('create', 'person');
                    }, this);
                    menu.add(personButton);
                    createButton.setMenu(menu);
                    this._buttonsPart.add(createButton);
                    break;
                default:
                    this.base(arguments, name);
            }
        },

        _controlState:function () {
            this._setEnabledPart(true);
            this._setEnabledButtons(false);
        }
    }
});


qx.Class.define('enre.erp.party.OwnPartiesView', {
    extend:enre.erp.party.PartiesView,

    construct:function () {
        this.base(arguments, 'enre/erp/party/stores/PartyStore/own_parties');
        this.setOrganizationEditPanel(enre.erp.party.OwnOrganizationEditPanel);
        this.setPersonEditPanel(enre.erp.party.OwnPersonEditPanel);
        this.addListener('add', this._onAdd, this);
    },

    events:{
        'add':'ex.event.type.Event'
    },

    members:{
        _initControls:function () {
            this.base(arguments);
            this.setToolBar(new enre.erp.party.OwnPariesToolBar(this));
        },

        _onDelete:function () {
            this._initParty();
            if (!this.isRecord()) {
                return;
            }
            new enre.ui.dialog.Dialog.warning(this.tr('msg_delrec'), 'yes-no').show().addListener('yes', function () {
                try {
                    this.getService().callSync('set_is_own', this.getTable().getFocusedPk(), false);
                    this.getTable().getTableModel().reloadData();
                } catch (ex) {
                    enre.ui.dialog.Dialog.error(ex.toString()).show();
                }
            }, this);
        },

        _onAdd:function (e) {
            var dlg = new enre.ui.model.SelectDialog('enre/erp/party/stores/PartyStore',
                    '{% trans 'Select party' %}', '{% trans 'Name' %}'
            ).set({width:500, textField:'display_name'});
            dlg.setFilter({is_own:false});
            dlg.addListener('rowSelect', function (e) {
                if (!e.getData()) {
                    return;
                }
                try {
                    var service = new enre.remote.Rpc('enre.erp.party.services.PartyService');
                    service.callSync('set_is_own', e.getData()[0], true);
                    this.getTable().getTableModel().reloadData();
                } catch (ex) {
                    enre.ui.dialog.Dialog.error(ex.toString()).show();
                }
            }, this);
            dlg.show();
        }

    }
});

qx.Class.define('enre.erp.party.OwnParties', {
    extend:enre.erp.Module,

    members:{
        _initControls:function () {
            this.setLayout(new qx.ui.layout.Grow());
            this.add(new enre.erp.party.OwnPartiesView());
        }
    }
});
