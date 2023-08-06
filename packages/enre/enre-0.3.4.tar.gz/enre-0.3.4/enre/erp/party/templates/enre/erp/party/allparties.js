{% load i18n %}
{% include 'enre/erp/party/party.js' %}


qx.Class.define('enre.erp.party.AllPariesToolBar', {
    extend:enre.ui.view.ToolBar,

    members:{
        _toolbarButton:function (name) {
            switch (name) {
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


qx.Class.define('enre.erp.party.AllPartiesView', {
    extend:enre.erp.party.PartiesView,

    members: {
        _initControls: function() {
            this.base(arguments);
            this.setToolBar(new enre.erp.party.AllPariesToolBar(this));
        }
    }


});


qx.Class.define('enre.erp.party.AllParties', {
    extend:enre.erp.Module,

    members:{
        _initControls:function () {
            this.setLayout(new qx.ui.layout.Grow());
            this.add(new enre.erp.party.AllPartiesView());
        }
    }
});
