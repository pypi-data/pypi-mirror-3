/**
 * UTILS
 */
qx.Class.define('enre.utils.Http', {

    statics:{

        CSRF_TOKEN_NAME:'csrfmiddlewaretoken',
        CSRF_COOKIE_NAME:'csrftoken',

        getCsrf:function () {
            return qx.bom.Cookie.get(this.CSRF_COOKIE_NAME);
        }

    }

});



qx.Class.define('enre.utils.Theme', {

    statics:{
        getIconUrl:function () {
            return qx.util.AliasManager.getInstance().getAliases()['icon'];
        }
    }

});

qx.Class.define('enre.utils.Locale', {

    statics:{

        addTranslations:function (translations) {
            var lmgr = qx.locale.Manager.getInstance();
            for (var locale in translations) {
                lmgr.addTranslation(locale, translations[locale]);
            }
        }

    }
});


qx.Class.define('enre.utils.Misc', {
    statics:{
        urlToClass:function (url) {
            var url = url.split('/').join('.');
            if (url[0] == '.') {
                url = url.substring(1)
            }
            if (url[url.length - 1] == '.') {
                url = url.substring(0, url.length - 1);
            }
            return url;
        }
    }
});


qx.Class.define('enre.utils.Serializer', {
    extend:qx.util.Serializer,

    statics:{

        toJson:function (object, qxSerializer, dateFormat) {
            var result = "";

            // null or undefined
            if (object == null) {
                return "null";
            }

            // data array
            if (qx.data && qx.data.IListData && qx.Class.hasInterface(object.constructor, qx.data.IListData)) {
                result += "[";
                for (var i = 0; i < object.getLength(); i++) {
                    result += enre.utils.Serializer.toJson(object.getItem(i), qxSerializer, dateFormat) + ",";
                }
                if (result != "[") {
                    result = result.substring(0, result.length - 1);
                }
                return result + "]";
            }

            // other arrays
            if (qx.lang.Type.isArray(object)) {
                result += "[";
                for (var i = 0; i < object.length; i++) {
                    result += enre.utils.Serializer.toJson(object[i], qxSerializer, dateFormat) + ",";
                }
                if (result != "[") {
                    result = result.substring(0, result.length - 1);
                }
                return result + "]";
            }

            // qooxdoo object
            if (object instanceof qx.core.Object) {
                if (qxSerializer != null) {
                    var returnValue = qxSerializer(object);
                    // if we have something returned, ruturn that
                    if (returnValue != undefined) {
                        return '"' + returnValue + '"';
                    }
                    // continue otherwise
                }
                result += "{";
                var properties = qx.util.PropertyUtil.getAllProperties(object.constructor);
                for (var name in properties) {
                    // ignore property groups
                    if (properties[name].group != undefined) {
                        continue;
                    }
                    var value = object["get" + qx.lang.String.firstUp(name)]();
                    result += '"' + name + '":' + enre.utils.Serializer.toJson(value, qxSerializer, dateFormat) + ",";
                }
                if (result != "{") {
                    result = result.substring(0, result.length - 1);
                }
                return result + "}";
            }

            // localized strings
            if (object instanceof qx.locale.LocalizedString) {
                object = object.toString();
                // no return here because we want to have the string checks as well!
            }

            // date objects with formater
            if (qx.lang.Type.isDate(object) && dateFormat != null) {
                return '"' + dateFormat.format(object) + '"';
            } else if (qx.lang.Type.isDate(object)) {
                return '"new Date(Date.UTC('
                        + object.getUTCFullYear() + ','
                        + object.getUTCMonth() + ','
                        + object.getUTCDate() + ','
                        + object.getUTCHours() + ','
                        + object.getUTCMinutes() + ','
                        + object.getUTCSeconds() + ','
                        + object.getUTCMilliseconds()
                        + '))"';
            }

            // javascript objects
            if (qx.lang.Type.isObject(object)) {
                result += "{";
                for (var key in object) {
                    result += '"' + key + '":' +
                            enre.utils.Serializer.toJson(object[key], qxSerializer, dateFormat) + ",";
                }
                if (result != "{") {
                    result = result.substring(0, result.length - 1);
                }
                return result + "}";
            }

            // strings
            if (qx.lang.Type.isString(object)) {
                // escape
                object = object.replace(/([\\])/g, '\\\\');
                object = object.replace(/(["])/g, '\\"');
                object = object.replace(/([\r])/g, '\\r');
                object = object.replace(/([\f])/g, '\\f');
                object = object.replace(/([\n])/g, '\\n');
                object = object.replace(/([\t])/g, '\\t');
                object = object.replace(/([\b])/g, '\\b');

                return '"' + object + '"';
            }

            // Date and RegExp
            if (qx.lang.Type.isDate(object) || qx.lang.Type.isRegExp(object)) {
                return '"' + object + '"';
            }

            // all other stuff
            return object + "";
        }

    }

});

/**
 * UI.MODEL
 */
qx.Mixin.define('enre.ui.model.MModelService', {

    properties:{
        serviceName:{
            nullable:true,
            apply:'_applyServiceName'
        }
    },

    members:{
        _service:null,

        _applyServiceName:function (value, old_value) {
            this._service = new enre.remote.ModelService(value);
        },

        getService:function () {
            return this._service;
        }
    },

    destruct:function () {
        this._service = null;
    }
});

qx.Interface.define('enre.ui.model.IModelSelect', {

    members:{

        setPk:function (value) {
        },

        getPk:function () {
        }
    }
});


qx.Class.define('enre.ui.model.SelectBox', {
    extend:qx.ui.form.SelectBox,
    implement:[enre.ui.model.IModelSelect],

    construct:function (url, textField, pkField, nullRow) {
        this.base(arguments);
        this._controller = new qx.data.controller.List(null, this);
        this._store = new enre.remote.Store();
        this._store.addListener('loaded', this._onStoreLoaded, this);
        if (url) {
            this.setUrl(url);
        }
        if (textField) {
            this.setTextField(textField);
        }
        if (pkField) {
            this.setPkField(pkField);
        } else if (textField) {
            this.setPkField(textField);
        }
        if (!textField && !pkField) {
            this._delegate();
        }
        if (nullRow) {
            this.setNullRow(nullRow);
        }
    },

    events:{
        'dataLoaded':'qx.event.type.Data'
    },


    properties:{
        url:{
            init:null,
            apply:'_applyUrl'
        },
        pkField:{
            init:'id',
            apply:'_applyDelegate'
        },
        textField:{
            init:'name',
            apply:'_applyDelegate'
        },
        nullRow:{
            init:null
        },
        filter:{
            init:null,
            apply:'_applyFilter'
        },
        exclude:{
            init:null,
            apply:'_applyExclude'
        }
    },

    members:{
        _controller:null,
        _store:null,

        _applyUrl:function (value, oldValue) {
            if (value == oldValue) {
                return;
            }
            this._store.setUrl(value);
        },

        _applyFilter:function (value, oldValue) {
            this._store.setFilter(value);
        },

        _applyExclude:function (value, oldValue) {
            this._store.setExclude(value);
        },

        _delegate:function () {
            this._controller.setDelegate({
                textField:this.getTextField(),
                pkField:this.getPkField(),
                bindItem:function (controller, item, id) {
                    controller.bindProperty(this.textField, "label", null, item, id);
                    controller.bindProperty(this.pkField, "model", null, item, id);
                }
            });
        },

        _applyDelegate:function (value, old_value) {
            this._delegate();
        },

        _onStoreLoaded:function (e) {
            var model = this._store.getModel();
            if (this.getNullRow()) {
                var row = {};
                row[this.getPkField()] = '_null_value_';
                row[this.getTextField()] = this.getNullRow();
                model.insertAt(0, qx.data.marshal.Json.createModel(row));
            }
            this._controller.setModel(model);
            this.fireDataEvent('dataLoaded', e.getData());
        },

        getPk:function () {
            if (this.getSelection().length == 0) {
                return null;
            }
            var pk = this.getSelection()[0].getModel();
            if (pk == '_null_value_') {
                pk = null;
            }
            return pk;
        },

        setPk:function (value) {
            var pk = value;
            if (!pk) {
                pk = '_null_value_';
            }
            var items = this.getChildren();
            for (var i = 0; i < items.length; i++) {
                if (items[i].getModel() == pk) {
                    this.setSelection([items[i]]);
                    break;
                }
            }
        },

        reloadData:function () {
            this._store.reload();
        }

    },

    destruct:function () {
        this._controller = this._store = null;
    }

});


qx.Class.define('enre.ui.model.SelectDialog', {
    extend:qx.ui.window.Window,
    include:[qx.locale.MTranslation],

    construct:function (url, dialogCaption, columnCaption, icon, pkField, textField) {
        this.base(arguments, dialogCaption, icon);
        if (url) this.setUrl(url);
        if (columnCaption) this.setColumnCaption(columnCaption);
        if (pkField) this.setPkField(pkField);
        if (textField) this.setTextField(textField);
        var iconPath = enre.utils.Theme.getIconUrl();
        this.setLayout(new qx.ui.layout.Dock());
        this.setModal(true);
        this.setShowMinimize(false);
        this.setWidth(350);
        this.setHeight(430);
        this.setContentPadding(0);
        this.addListener('keypress', this._onKeyPress, this);
        var container = new qx.ui.container.Composite(new qx.ui.layout.Dock());
        this._findText = new qx.ui.form.TextField();
        this._findText.addListener('keypress', this._findKeyPress, this);
        this._findText.addListener('input', this._onInput, this);
        container.add(this._findText, {edge:'center'});
        var findButton = new qx.ui.form.Button(null, iconPath + '/16/actions/system-search.png').set({
            focusable:false,
            padding:0
        });
        findButton.addListener('execute', this._onFindButton, this);
        container.add(findButton, {edge:'east'});
        this.add(container, {edge:'north'});
        this.add(container, {edge:'north'});
        this._table = new enre.ui.model.Table();
        this._table.setStatusBarVisible(false);
        this._table.setColumnVisibilityButtonVisible(false);
        this._table.addListener('keypress', this._tableKeyPress, this);
        this.add(this._table, {edge:'center'});
        var form = new qx.ui.form.Form();
        var okButton = new qx.ui.form.Button(this.tr('btn_select'), iconPath + '/16/actions/dialog-apply.png').set({
            focusable:false
        });
        okButton.addListener('execute', this._onOkButton, this);
        form.addButton(okButton);
        var cancelButton = new qx.ui.form.Button(this.tr('btn_cancel'), iconPath + '/16/actions/dialog-close.png').set({
            focusable:false
        });
        cancelButton.addListener('execute', this._onCancelButton, this);
        form.addButton(cancelButton);
        var renderer = new qx.ui.form.renderer.Single(form);
        renderer.setPadding(6);
        this.add(renderer, {edge:'south'});
        this._table.focus();
        this._timer = new qx.event.Timer(200);
        this._timer.addListener('interval', this._onTimer, this);
    },

    events:{
        'rowSelect':'qx.event.type.Data'
    },

    properties:{
        url:{nullable:false},
        filter:{init:null},
        exclude:{init:null},
        columnCaption:{init:null},
        pkField:{init:'id'},
        textField:{init:'name'}
    },

    members:{
        _model:null,
        _table:null,
        _findText:null,
        _timer:null,

        _onKeyPress:function (e) {
            var id = e.getKeyIdentifier();
            if (id == 'Escape') {
                this._onCancelButton();
            }
            if (id == "PageDown" || id == "PageUp") {
                this._table.focus();

            }
        },

        _findKeyPress:function (e) {
            if (e.getKeyIdentifier() == 'Enter') {
                this._onFindButton();
            }
        },

        _tableKeyPress:function (e) {
            if (e.getKeyIdentifier() == 'Enter') {
                this._onOkButton();
            }
        },

        _onOkButton:function () {
            if (this._table.getFocusedRow() == null || this._table.getFocusedRow() == undefined) {
                return;
            }
            this.fireDataEvent('rowSelect', [
                this._table.getFocusedPk(), this._model.getValue(0, this._table.getFocusedRow())
            ]);
            this.close();
        },

        _onCancelButton:function () {
            this.fireDataEvent('rowSelect', null);
            this.close();
        },

        _onFindButton:function () {
            var txt = this._findText.getValue();
            if ((!txt || txt.length == 0) && !this.getFilter()) {
                this._model.setFilter(null);
            } else {
                var filter = this.getFilter() ? this.getFilter() : {};
                filter[this.getTextField() + '__icontains'] = txt;
                this._model.setFilter(filter);
            }
            this._model.reloadData();
        },

        _onTimer:function (e) {
            this._onFindButton();
            this._timer.stop();
        },

        _onInput:function () {
            this._timer.stop();
            this._timer.start();
        },

        _initModel:function () {
            this._model = new enre.remote.TableModel(this.getUrl());
            if (!this.getColumnCaption()) {
                this.setColumnCaption(this.getTextField());
            }
            this._model.setColumns([this.getColumnCaption()], [this.getTextField()], this.getPkField());
            this._model.setFilter(this.getFilter());
            this._model.setExclude(this.getExclude());
        },

        show:function () {
            this.center();
            this._initModel();
            this._table.setTableModel(this._model);
            this.base(arguments);
        }

    },

    destruct:function () {
        this._model = this._table = this._findText = null;
    }

});


qx.Class.define('enre.ui.model.Select', {
    extend:qx.ui.core.Widget,
    include:[
        qx.ui.form.MForm
    ],
    implement:[
        qx.ui.form.IForm,
        qx.ui.form.IStringForm
    ],

    construct:function (url, dialogCaption, columnCaption, icon, pkField, textField) {
        this.base(arguments);
        if (url) this.setUrl(url);
        if (dialogCaption) this.setDialogCaption(dialogCaption);
        if (columnCaption) this.setColumnCaption(columnCaption);
        if (icon) this.setDialogIcon(icon);
        if (pkField) this.setPkField(pkField);
        if (textField) this.setTextField(textField);
        var layout = new qx.ui.layout.HBox();
        layout.setAlignY("middle");
        this._setLayout(layout);
        this.addListener('keypress', this._onKeyPress, this);
        this._createChildControl("textfield");
        this._createChildControl('button');
        this._createChildControl('clearbutton');
    },


    properties:{
        appearance:{
            refine:true,
            init:"modelselect"
        },

        focusable:{
            refine:true,
            init:true
        },

        value:{
            init:null,
            apply:'_applyValue'
        },
        url:{init:null},
        filter:{init:null},
        exclude:{init:null},
        pkField:{init:'id'},
        textField:{init:'name'},
        columnCaption:{init:null},
        dialogCaption:{init:'Select'},
        dialogIcon:{init:null},
        dialogWidth:{init:350},
        dialogHeight:{init:450}
    },

    events:{
        changeValue:'qx.event.type.Data',
        dataLoaded:'qx.event.type.Data'
    },

    members:{

        _createChildControlImpl:function (id, hash) {
            var control;
            switch (id) {
                case 'textfield':
                    control = new qx.ui.form.TextField();
                    control.setFocusable(false);
                    control.addState('inner');
                    control.setReadOnly(true);
                    control.addListener('blur', this.close, this);
                    this._add(control, {flex:1});
                    break;
                case 'button':
                    control = new qx.ui.form.Button();
                    control.setFocusable(false);
                    control.setKeepActive(true);
                    control.addState('inner');
                    control.addListener('execute', this._onButtonClick, this);
                    this._add(control);
                    break;
                case 'clearbutton':
                    control = new qx.ui.form.Button();
                    control.setFocusable(false);
                    control.setKeepActive(true);
                    control.addState('inner');
                    control.addListener('execute', this._onClearButtonClick, this);
                    this._add(control);
            }
            return control || this.base(arguments, id);
        },

        _forwardStates:{
            focused:true,
            invalid:true
        },

        _setTextValue:function () {
            if (this.getValue && this.getUrl()) {
                var filter = {};
                filter[this.getPkField()] = this.getValue();
                var store = new enre.remote.Store(this.getUrl(), filter);
                store.addListener('loaded', function (e) {
                    var text = null;
                    var model = e.getData();
                    if (model && model.length > 0) {
                        text = model.getItem(0).get(this.getTextField());
                    }
                    this.getChildControl('textfield').setValue(text);
                    this.fireDataEvent('dataLoaded', model ? model.getItem(0) : null);
                }, this);
            } else {
                this.getChildControl('textfield').setValue(null);
            }
        },

        _applyValue:function (value, old_value) {
            if (value != old_value) {
                this._setTextValue();
            }
            this.fireDataEvent('changeValue', value);
        },

        _onButtonClick:function () {
            if (!this.getUrl() || !this.getChildControl('button').getEnabled()) {
                return;
            }
            var win = new enre.ui.model.SelectDialog(this.getUrl(), this.getDialogCaption(), this.getColumnCaption(),
                    this.getDialogIcon(), this.getPkField(), this.getTextField());
            win.addListener('rowSelect', function (e) {
                this.focus();
                var msg = e.getData();
                if (!msg) {
                    return;
                }
                this.setValue(msg[0]);
                this.getChildControl('textfield').setValue(msg[1]);
            }, this);
            win.setFilter(this.getFilter());
            win.setExclude(this.getExclude());
            win.show();
        },

        _onClearButtonClick:function () {
            this.setValue(null);
            this.getChildControl('textfield').setValue(null);
        },

        _onKeyPress:function (e) {
            var id = e.getKeyIdentifier();
            if (id == 'Enter' || id == 'Space') {
                this._onButtonClick();
            } else if (id == 'Escape') {
                this._onClearButtonClick();
            }
        },

        tabFocus:function () {
            var field = this.getChildControl("textfield");
            field.getFocusElement().focus();
            field.selectAllText();
        },

        focus:function () {
            this.base(arguments);
            this.getChildControl("textfield").getFocusElement().focus();
        },

        setReadOnly:function (value) {
            this.getChildControl('button').setEnabled(!value);
            this.getChildControl('clearbutton').setEnabled(!value);
        }

    }

});


qx.Class.define('enre.ui.model.Table', {
    extend:qx.ui.table.Table,

    construct:function (tableModel, custom) {
        var _custom = {};
        if (custom) {
            _custom = custom;
        }
        if (!_custom['tableColumnModel']) {
            _custom['tableColumnModel'] = function (obj) {
                return new qx.ui.table.columnmodel.Resize(obj);
            }
        }
        this.base(arguments, tableModel, _custom);
    },

    properties:{
        initFirstRow:{
            init:true
        },
        hiddenColumns:{
            init:null,
            apply:'_applyHiddenColumns'
        }
    },

    members:{

        _onDataLoaded:function () {
            if (this.getInitFirstRow() && !this.getFocusedRow() && this.getTableModel().getRowCount() > 0) {
                this.setFocusedCell(0, 0);
                this.getSelectionModel().setSelectionInterval(0, 0);
            }
        },

        _applyTableModel:function (value, old) {
            this.base(arguments, value, old);
            var emptyClass = eval(this.getEmptyTableModel().classname);
            var tableModel = this.getTableModel();
            if (!(tableModel instanceof emptyClass)) {
                if (this.getPkField() && this.getTableModel().isPkHidden()) {
                    this.getTableColumnModel().setColumnVisible(this.getTableModel().getColumnIndexById(this.getPkField()), false);
                }
                tableModel.addListener('dataLoaded', this._onDataLoaded, this);
                tableModel.addListener('changePkHidden', function () {
                    this._applyTableModel(tableModel);
                }, this);
            }
        },

        _applyHiddenColumns:function (value, old_value) {
            if (old_value) {
                this.setColumnsVisible(old_value, true);
            }
            this.setColumnsVisible(value, false);
        },

        _removeColumnMenuItem:function (menu, columnId) {
            var label = this.getTableModel().getColumnName(this.getTableModel().getColumnIndexById(columnId));
            var buttons = menu.getChildren();
            for (var i = 0; i < buttons.length; i++) {
                if (!(buttons[i] instanceof qx.ui.table.columnmenu.MenuItem)) {
                    continue;
                }
                if (buttons[i].getLabel() == label) {
                    menu.remove(buttons[i]);
                    break;
                }
            }
        },

        _initColumnMenu:function () {
            this.base(arguments);
            var menu = this.getChildControl("column-button").getMenu();
            if (this.getTableModel().isPkHidden()) {
                this._removeColumnMenuItem(menu, this.getPkField());
            }
            if (this.getHiddenColumns()) {
                var columns = this.getHiddenColumns();
                for (var i = 0; i < columns.length; i++) {
                    this._removeColumnMenuItem(menu, columns[i]);
                }
            }
        },

        setColumnsVisible:function (columns, visible) {
            for (var i = 0; i < columns.length; i++) {
                this.getTableColumnModel().setColumnVisible(this.getTableModel().getColumnIndexById(columns[i]), visible);
            }
        },

        isColumnHidden:function (column) {
            var columns = this.getHiddenColumns();
            for (var i = 0; i < columns.length; i++) {
                if (columns[i] == column) {
                    return true;
                }
            }
            return false;
        },

        getPkField:function () {
            return this.getTableModel().getPkField();
        },

        getSelectionPks:function () {
            var pkField = this.getPkField();
            var tableModel = this.getTableModel();
            var ids = [];
            var ranges = this.getSelectionModel().getSelectedRanges();
            for (var i = 0; i < ranges.length; i++) {
                var range = ranges[i];
                for (var row = range.minIndex; row <= range.maxIndex; row++) {
                    ids[ids.length] = tableModel.getPk(row)
                }
            }
            if (ids.length > 0 && !ids[0]) {
                return [];
            }
            return ids;
        },

        getFocusedPk:function () {
            if (this.getFocusedRow() == null) {
                return null;
            }
            return this.getTableModel().getPk(this.getFocusedRow());
        },

        setColumnWidth:function (col, width, flex) {
            var resizeBehavior = this.getTableColumnModel().getBehavior();
            resizeBehavior.setWidth(col, width, flex);
        },

        getValueById:function (columnId, rowIndex) {
            return this.getTableModel().getValueById(columnId, rowIndex);
        },

        getValue:function (columnIndex, rowIndex) {
            return this.getTableModel().getValue(columnIndex, rowIndex);
        }

    }
});


qx.Class.define('enre.ui.model.ActionTable', {
    extend:enre.ui.model.Table,
    include:[qx.locale.MTranslation],

    construct:function (url) {
        this.base(arguments, url);
        this.setInitFirstRow(false);
        this.addListener('changeTableModel', this._onChangeTableModel, this);
        this.addListener('cellClick', this._checkActionClick, this);
    },

    properties:{
        iconSize:{
            init:16,
            check:function (value) {
                var valid = ['16', '22', '32', '48', '64', '128'];
                return qx.lang.Array.contains(valid, value.toString());
            }
        }
    },

    events:{
        'view':'qx.event.type.Data',
        'edit':'qx.event.type.Data',
        'delete':'qx.event.type.Data'
    },

    members:{

        _fireActionEvent:function (event) {
            if (!this.getFocusedPk) {
                return;
            }
            this.fireDataEvent(event, this.getFocusedPk());
        },

        _checkActionClick:function (e) {
            var id = this.getTableModel().getColumnId(e.getColumn());
            switch (id) {
                case '_view_action_':
                    this._fireActionEvent('view');
                    break;
                case '_edit_action_':
                    this._fireActionEvent('edit');
                    break;
                case '_delete_action_':
                    this._fireActionEvent('delete');
                    break;
            }
        },

        _setActionColumn:function (action, image, tooltip) {
            var col = this.getTableModel().getColumnIndexById(action);
            var iconPath = enre.utils.Theme.getIconUrl() + '/' + this.getIconSize().toString() + '/actions/';
            var renderer = new enre.ui.table.ActionCellRenderer(iconPath + image, tooltip,
                    parseInt(this.getIconSize()),
                    parseInt(this.getIconSize())
            );
            this.getTableColumnModel().setDataCellRenderer(col, renderer);
            this.getTableModel().setColumnSortable(col, false);
            this.setColumnWidth(col, parseInt(this.getIconSize()) + 10);
        },

        _onChangeTableModel:function () {
            var tableModel = this.getTableModel();
            var iconPath = enre.utils.Theme.getIconUrl() + '/16/actions/';
            this._setActionColumn('_view_action_', 'edit-find.png', this.tr('btn_view'));
            this._setActionColumn('_edit_action_', 'edit-select-all.png', this.tr('btn_edit'));
            this._setActionColumn('_delete_action_', 'edit-delete.png', this.tr('btn_delete'));
        },

        _initColumnMenu:function () {
            this.base(arguments);
            for (var i = 0; i < this.getTableModel().getActionsCount(); i++) {
                this.getChildControl("column-button").getMenu().removeAt(0);
            }
        },

        setActionVisible:function (action, visible) {
            var col = this.getTableModel().getColumnIndexById(action);
            this.getTableColumnModel().setColumnVisible(col, visible);
        }
    }
});


/**
 * UI.CONTAINER
 */
qx.Class.define('enre.ui.container.Panel', {
    extend:qx.ui.container.Composite,

    construct:function (layout) {
        this.base(arguments, layout);
        if (!layout) {
            this.setLayout(new qx.ui.layout.Grow());
        }
    },

    properties:{
        appearance:{
            refine:true,
            init:'panel'
        }
    }
});

qx.Class.define('enre.ui.container.CollapsePanel', {

    extend:qx.ui.core.Widget,

    include:[
        qx.ui.core.MRemoteChildrenHandling,
        qx.ui.core.MRemoteLayoutHandling,
        qx.ui.core.MContentPadding
    ],

    construct:function (caption, icon, minimize) {
        this.base(arguments);
        this._setLayout(new qx.ui.layout.VBox());
        this._createChildControl('captionbar');
        this._createChildControl('pane');
        this._createChildControl('button');
        this.addListener('focusin', this._onFocusIn, this);
        this.addListener('focusout', this._onFocusOut, this);
        this.addListener('keypress', this._onKeyPress, this);
        if (caption) {
            this.setCaption(caption);
        }
        if (icon) {
            this.setIcon(icon);
        }
        if (minimize) {
            this.setMinimize(true);
        }
        this.initVisibility();

        this._updateCaptionBar();

    },

    events:{

    },

    properties:{

        appearance:{
            refine:true,
            init:'collapsepanel'
        },

        focusable:{
            refine:true,
            init:true
        },

        icon:{
            check:'String',
            nullable:true,
            apply:'_applyCaptionBarChange',
            event:'changeIcon',
            themeable:true
        },

        caption:{
            apply:'_applyCaptionBarChange',
            event:'changeCaption',
            nullable:true
        },

        minimize:{
            init:false,
            check:'Boolean',
            event:'changeState',
            apply:'_applyStateChange'
        }

    },

    members:{
        _forwardStates:{
            active:true,
            minimized:true
        },

        _createChildControlImpl:function (id, hash) {
            var control;

            switch (id) {
                case 'pane':
                    control = new qx.ui.container.Composite();
                    this._add(control, {flex:1});
                    break;

                case 'captionbar':
                    var layout = new qx.ui.layout.Grid();
                    layout.setRowFlex(0, 1);
                    layout.setColumnFlex(1, 1);
                    control = new qx.ui.container.Composite(layout);
                    control.addListener('dblclick', this._onButtonClick, this);
                    this._add(control);
                    break;

                case 'icon':
                    control = new qx.ui.basic.Image(this.getIcon());
                    this.getChildControl('captionbar').add(control, {row:0, column:0});
                    break;

                case 'title':
                    control = new qx.ui.basic.Label(this.getCaption());
                    control.setWidth(0);
                    control.setAllowGrowX(true);
                    var captionBar = this.getChildControl('captionbar');
                    captionBar.add(control, {row:0, column:1});
                    break;

                case 'button':
                    control = new qx.ui.form.Button();
                    control.setFocusable(false);
                    control.addListener('execute', this._onButtonClick, this);

                    this.getChildControl('captionbar').add(control, {row:0, column:2});
                    break;
            }
            return control || this.base(arguments, id);
        },

        getChildrenContainer:function () {
            return this.getChildControl('pane');
        },

        _getContentPaddingTarget:function () {
            return this.getChildControl('pane');
        },

        _updateCaptionBar:function () {
            var icon = this.getIcon();
            if (icon) {
                this.getChildControl('icon').setSource(icon);
                this._showChildControl('icon');
            } else {
                this._excludeChildControl('icon');
            }

            var caption = this.getCaption();
            if (caption) {
                this.getChildControl('title').setValue(caption);
                this._showChildControl('title');
            } else {
                this._excludeChildControl('title');
            }

        },

        _applyCaptionBarChange:function (value, old_value) {
            this._updateCaptionBar();
        },


        _applyStateChange:function (minimize) {
            if (minimize) {
                this._excludeChildControl('pane');
                this.addState('minimized');
            } else {
                this._showChildControl('pane');
                this.removeState('minimized');
            }
        },

        _onButtonClick:function (e) {
            this.setMinimize(!this.getMinimize());
        },

        _onFocusIn:function (e) {
            this.addState('active');
        },

        _onFocusOut:function (e) {
            this.removeState('active');
        },

        _onKeyPress:function (e) {
            var id = e.getKeyIdentifier();
            if (id == 'PageUp') {
                this._applyStateChange(true);
            } else if (id == 'PageDown') {
                this._applyStateChange(false);
            }
        }

    }

});

qx.Class.define('enre.ui.container.Script', {
    extend:qx.ui.container.Composite,

    construct:function () {
        this.base(arguments);
        this.setLayout(new qx.ui.layout.Grow());
        this._loader = new enre.remote.Script();
    },

    events:{
        'load':'qx.event.type.Data'
    },

    members:{
        _loader:null,
        _class:null,
        _className:null,

        load:function (url, cls) {
            var cls = cls;
            if (!cls) {
                cls = enre.utils.Misc.urlToClass(url);
            }
            if (this._className == cls) {
                return;
            }
            this._loader.load(enre.utils.Django.ajaxUrl + url, function () {
                if (this._class) {
                    this.remove(this._class);
                    this._class.dispose();
                }
                this._className = cls;
                var script = eval(cls);
                this._class = new script();
                this.add(this._class);
                this.fireDataEvent('load', script);
            }, this);
        }
    },

    destruct:function () {
        this._loader = this._class = this._className = null;
    }

});

/**
 * UI.DIALOG
 */
qx.Class.define('enre.ui.dialog.DialogWindow', {
    extend:qx.ui.window.Window,
    include:[qx.locale.MTranslation],

    construct:function (message, image, buttons) {
        this.base(arguments, this.tr('dlg_simple'));
        this.setLayout(new qx.ui.layout.Dock());
        this.setModal(true);
        this.setAllowMaximize(false);
        this.setShowMaximize(false);
        this.setShowMinimize(false);
        this.setResizable(false);
        this.addListener('keypress', this._onKeyPress, this);
        this._message = new qx.ui.basic.Label().set({alignY:'middle', rich:true});
        this.add(this._message, {edge:'center'});
        if (message) {
            this.setMessage(message);
        }
        if (buttons) {
            for (var i = 0; i < buttons.length; i++) {
                this.addButton(buttons[i]);
            }
        }
        if (image) {
            this.setImage(image);
        }
    },

    properties:{

        image:{
            check:'String',
            nullable:true,
            event:'changeImage',
            apply:'_applyImage'
        },

        message:{
            check:'String',
            nullable:true,
            event:'changeMessage',
            apply:'_applyMessage'
        },

        defaultButton:{
            nullable:true
        },

        cancelButton:{
            nullable:true
        }
    },

    members:{
        _form:null,
        _renderer:null,
        _image:null,
        _message:null,

        _applyImage:function (value, old_value) {
            if (!value && !old_value) {
                return;
            } else if (!value && old_value) {
                this.setIcon(null);
                this.remove(this._image);
                this._image = null;
                return;
            }
            var iconPath = enre.utils.Theme.getIconUrl();
            this.setIcon(iconPath + '/16' + value);
            if (!this._image) {
                this._image = new qx.ui.basic.Image().set({alignY:'middle', margin:[0, 15, 0, 0]});
                this.add(this._image, {edge:'west'});
            }
            this._image.setSource(iconPath + '/48' + value);
        },

        _applyMessage:function (value, old_value) {
            this._message.setValue(value.replace(new RegExp('\n', 'g'), '<br>'));
        },

        _onKeyPress:function (e) {
            var id = e.getKeyIdentifier();
            if (id == 'Escape') {
                if (this.getCancelButton()) {
                    this.getCancelButton().fireEvent('execute');
                } else {
                    this.close();
                }
            }
        },

        show:function () {
            this.base(arguments);
            if (this._image && this._renderer) {
                this._image.setMargin([0, 15, 30, 0]);
            }
            if (this.getDefaultButton()) {
                this.getDefaultButton().focus();
            } else {
                this.focus();
            }
            this.center();
        },

        addButton:function (button) {
            if (!this._form) {
                this._form = new qx.ui.form.Form();
                this._renderer = new qx.ui.form.renderer.Single(this._form).set({margin:[6, 0, 0, 0]});
                this.add(this._renderer, {edge:'south'});
            }
            button.addListener('execute', function (e) {
                this.close();
            }, this);
            this._renderer.addButton(button);
        },

        resetButtons:function () {
            if (!this._renderer) {
                return;
            }
            this.remove(this._renderer);
            this._renderer = null;
            this._form = null;
        }

    },

    destruct:function () {
        this._renderer = this._form = this._message = this._image = null;
    }

});


qx.Class.define('enre.ui.dialog.Dialog', {
    extend:qx.core.Object,
    include:[qx.locale.MTranslation],

    construct:function (message, buttons, type, caption) {
        this.base(arguments);
        this._window = new enre.ui.dialog.DialogWindow();
        if (message) {
            this.setMessage(message);
        }
        if (type) {
            this.setType(type);
        }
        if (buttons) {
            this.setButtons(buttons);
        }
        if (caption) {
            this.setCaption(caption);
        }
    },

    statics:{

        SIMPLE:'simple',
        ERROR:'error',
        INFORMATION:'information',
        WARNING:'warning',

        OK:'ok',
        OK_CANCEL:'ok-cancel',
        YES_NO:'yes-no',
        YES_NO_CANCEL:'yes-no-cancel',

        simple:function (message, buttons, caption) {
            return new enre.ui.dialog.Dialog(message, buttons, 'simple', caption);
        },

        error:function (message, buttons, caption) {
            return new enre.ui.dialog.Dialog(message, buttons, 'error', caption);
        },

        information:function (message, buttons, caption) {
            return new enre.ui.dialog.Dialog(message, buttons, 'information', caption);
        },

        warning:function (message, buttons, caption) {
            return new enre.ui.dialog.Dialog(message, buttons, 'warning', caption);
        }

    },

    properties:{

        type:{
            check:'String',
            init:'simple',
            apply:'_applyType'
        },

        buttons:{
            check:'String',
            nullable:true,
            apply:'_applyButtons'
        }

    },

    events:{
        'ok':'qx.event.type.Event',
        'cancel':'qx.event.type.Event',
        'yes':'qx.event.type.Event',
        'no':'qx.event.type.Event'
    },

    members:{

        _window:null,

        _addButton:function (label, icon, event) {
            var btn = new qx.ui.form.Button(label, icon);
            btn.addListener('execute', function (e) {
                this.fireEvent(event);
            }, this);
            this._window.addButton(btn);
            return btn;
        },

        _applyType:function (value, old_value) {
            var dlg = enre.ui.dialog.Dialog;
            if (value != dlg.SIMPLE && value != dlg.ERROR && value != dlg.INFORMATION && value != dlg.WARNING) {
                throw new Error('Bad dialog type');
            }
            switch (value) {
                case dlg.SIMPLE:
                    this._window.setCaption(this.tr('dlg_simple'));
                    this._window.setImage(null);
                    break;
                case dlg.ERROR:
                    this._window.setCaption(this.tr('dlg_error'));
                    this._window.setImage('/status/dialog-error.png');
                    break;
                case dlg.INFORMATION:
                    this._window.setCaption(this.tr('dlg_information'));
                    this._window.setImage('/status/dialog-information.png');
                    break;
                case dlg.WARNING:
                    this._window.setCaption(this.tr('dlg_warning'));
                    this._window.setImage('/status/dialog-warning.png');
                    break;
            }
        },

        _applyButtons:function (buttons, old_buttons) {
            var iconPath = enre.utils.Theme.getIconUrl();
            var dlg = enre.ui.dialog.Dialog;
            if (buttons != dlg.OK && buttons != dlg.OK_CANCEL && buttons != dlg.YES_NO && buttons != dlg.YES_NO_CANCEL) {
                throw new Error('Bad buttons type');
            }
            if (old_buttons) {
                this.resetButtons();
            }
            if (buttons.indexOf(dlg.OK) == 0) {
                this._window.setDefaultButton(this._addButton(this.tr('btn_ok'), iconPath + '/16/actions/dialog-ok.png', 'ok'));
            }
            if (buttons.indexOf(dlg.YES_NO) == 0) {
                this._window.setDefaultButton(
                        this._addButton(this.tr('btn_yes'), iconPath + '/16/actions/dialog-apply.png', 'yes')
                );
                var btn = this._addButton(this.tr('btn_no'), iconPath + '/16/actions/dialog-close.png', 'no');
                if (buttons == dlg.YES_NO) {
                    this._window.setCancelButton(btn);
                }
            }
            if (buttons == dlg.OK_CANCEL || buttons == dlg.YES_NO_CANCEL) {
                this._window.setCancelButton(
                        this._addButton(this.tr('btn_cancel'), iconPath + '/16/actions/dialog-cancel.png', 'cancel')
                );
            }
        },

        resetButtons:function () {
            this._window.resetButtons();
        },

        _applyMessage:function (value, old_value) {
            this._window.setMessage(value);
        },

        setMessage:function (message) {
            this._window.setMessage(message);
        },

        getMessage:function () {
            return this._window.getMessage();
        },

        setCaption:function (caption) {
            this._window.setCaption(caption);
        },

        getCaption:function () {
            return this._window.getCaption();
        },

        show:function () {
            if (!this.getButtons()) {
                this.setButtons(enre.ui.dialog.Dialog.OK);
            }
            this._window.show();
            return this
        }

    }

});


/**
 * UI.FORM
 */
qx.Class.define('enre.ui.form.ValidationManager', {
    extend:qx.ui.form.validation.Manager,

    members:{

        validate:function () {
            var valid = this.base(arguments);
            var items = this.getItems();
            for (var i = 0; i < items.length; i++) {
                var item = items[i];
                if (qx.Class.hasInterface(item.constructor, qx.ui.core.ISingleSelection) && item.getRequired()
                        && item.getSelection().length > 0 && item.getSelection()[0].getModel() == '_null_value_') {
                    item.setValid(false);
                    return false;
                }
            }
            return valid;
        }

    }

});

qx.Class.define('enre.ui.form.Form', {
    extend:qx.ui.form.Form,

    construct:function () {
        this.base(arguments);
        this._validationManager = new enre.ui.form.ValidationManager();
    }

});

qx.Class.define('enre.ui.form.DateField', {
    extend:qx.ui.form.DateField,

    properties:{
        readOnly:{
            init:false,
            apply:'_applyReadOnly'
        }
    },

    members:{
        _applyReadOnly:function (value, old_value) {
            this.getChildControl('textfield').setReadOnly(value);
            this.getChildControl('button').setEnabled(!value);
            this.getChildControl('popup').setEnabled(!value);
        }
    }
});


qx.Interface.define('enre.ui.form.IContainer', {
    extend:qx.ui.form.IStringForm
});


qx.Class.define('enre.ui.form.Container', {
    extend:qx.ui.core.Widget,
    include:[ qx.ui.form.MForm],
    implement:[qx.ui.form.IForm, enre.ui.form.IContainer],

    construct:function (renderer, showLabel) {
        this.base(arguments);
        this.setLayout(new qx.ui.layout.Grow());
        if (renderer) {
            this.setRenderer(renderer);
        }
        if (showLabel) {
            this.setShowLabel(showLabel);
        }
    },

    properties:{
        value:{ init:null },
        valid:{init:null},
        required:{init:false},
        showLabel:{init:false},
        renderer:{
            init:null,
            apply:'_applyRenderer'
        }
    },

    members:{

        _applyRenderer:function (value, old_value) {
            if (old_value) {
                this._remove(old_value);
            }
            this._add(value);
        },

        isValid:function () {
            return true;
        },

        setEnabled:function (value) {

        },

        setLayout:function (layout) {
            this._setLayout(layout);
        }

    }

});


qx.Class.define('enre.ui.form.SingleRenderer', {
    extend:qx.ui.form.renderer.Single,

    construct:function (form) {
        this.base(arguments, form);
        this.addListener('changeLocale', this._setLocaleAlign, this);
        this.getLayout().setColumnFlex(0, 0);
        this._setLocaleAlign();
    },

    members:{

        _setLocaleAlign:function () {
            var locale = qx.locale.Manager.getInstance().getLocale();
            if (locale == 'ru') {
                this.getLayout().setColumnAlign(0, 'left', 'top');
            } else {
                this.getLayout().setColumnAlign(0, 'right', 'top');
            }
        },

        addItems:function (items, names, title) {
            if (title != null) {
                this._add(this._createHeader(title), {row:this._row, column:0, colSpan:2});
                this.getLayout().setColumnFlex(this._row + 1, 1);
                this._row++;
            }
            for (var i = 0; i < items.length; i++) {
                if (qx.Class.hasInterface(items[i].constructor, enre.ui.form.IContainer) && !items[i].getShowLabel()) {
                    this._add(items[i], {row:this._row, column:0, colSpan:2});
                    this.getLayout().setColumnFlex(this._row + 1, 1);
                } else {
                    var label = this._createLabel(names[i], items[i]);
                    this._add(label, {row:this._row, column:0});
                    var item = items[i];
                    label.setBuddy(item);
                    this._add(item, {row:this._row, column:1});
                    this.getLayout().setColumnFlex(this._row + 1, 2);
                    if (!qx.Class.hasInterface(items[i].constructor, enre.ui.form.IContainer)) {
                        this._connectVisibility(item, label);
                    }
                }
                this._row++;
                if (qx.core.Environment.get("qx.dynlocale")) {
                    this._names.push({name:names[i], label:label, item:items[i]});
                }
            }
        }

    }
});

qx.Class.define('enre.ui.form.HBoxRenderer', {
    extend:qx.ui.form.renderer.Single,

    construct:function (form, flexible) {
        if (flexible != undefined) {
            this.setFlexible(flexible);
        }
        this.base(arguments, form);
        this._setLayout(new qx.ui.layout.HBox(10));
        this.setPadding(0);

    },

    properties:{
        flexible:{
            init:true
        }
    },

    members:{

        addItems:function (items, names, title) {
            if (title != null) {
                this._add(this._createHeader(title), {row:this._row, column:0, colSpan:2});
                this._row++;
            }
            for (var i = 0; i < items.length; i++) {
                var container = new qx.ui.container.Composite(new qx.ui.layout.Dock(5));
                var label = this._createLabel(names[i], items[i]);
                if (label.getValue().length > 0) {
                    container.add(label, {edge:'west'});
                }
                var item = items[i];
                if (item instanceof qx.ui.form.AbstractField) {
                    container.setPadding([1, 0, 0, 0]);
                }
                label.setBuddy(item);
                container.add(item, {edge:'center'});
                if (this.getFlexible()) {
                    this._add(container, {width:'100%', flex:1});
                } else {
                    this._add(container);
                }
                this._row++;
                this._connectVisibility(item, label);
                if (qx.core.Environment.get("qx.dynlocale")) {
                    this._names.push({name:names[i], label:label, item:items[i]});
                }
            }
        }

    }

});


/**
 * UI.TABLE
 */
qx.Class.define('enre.ui.table.ActionCellRenderer', {
    extend:qx.ui.table.cellrenderer.Image,

    construct:function (url, tooltip, width, height) {
        this.base(arguments, width, height);
        var clazz = this.self(arguments);
        clazz.stylesheet = qx.bom.Stylesheet.createElement(
                ".qooxdoo-table-cell-icon {" +
                        "  text-align:center;" +
                        "  padding-top:1px;" +
                        "  cursor:pointer" +
                        "}"
        );
        if (url) {
            this.setUrl(url);
        }
        if (tooltip) {
            this.setTooltip(tooltip);
        }
    },

    properties:{
        url:{ nullable:true },
        tooltip:{nullable:true}
    },

    members:{

        _getImageInfos:function (cellInfo) {
            var imageData = this.base(arguments, cellInfo);
            imageData.url = this.getUrl();
            imageData.tooltip = this.getTooltip();
            return imageData;
        }
    }

});


/**
 * UI.VIEW
 */
qx.Interface.define('enre.ui.view.IEditContainer', {

    members:{
        _initControls:function () {
        },

        getPk:function () {
        }
    }

});

qx.Mixin.define('enre.ui.view.MEditContainer', {
    include:[enre.ui.model.MModelService, qx.locale.MTranslation],

    construct:function (serviceName, parent) {
        this.setLayout(new qx.ui.layout.Dock());
        if (serviceName) {
            this.setServiceName(serviceName);
        }
        if (parent) {
            this.setParent(parent);
        }
        var scroll = new qx.ui.container.Scroll().set({height:null});
        this._container = new qx.ui.container.Composite(new qx.ui.layout.VBox(10));
        this._container.setPadding(10);
        scroll.add(this._container);
        this.add(scroll, {edge:'center'});
        this._forms = new qx.type.Array();
        this._initControls();
    },

    properties:{
        parent:{
            nullable:false
        },

        pkField:{
            nullable:true
        }
    },

    events:{
        'dataLoaded':'qx.event.type.Data',
        'refresh':'qx.event.type.Event'
    },

    members:{
        _model:null,
        _forms:null,
        _container:null,
        _saveButton:null,
        _backButton:null,
        _pk:null,
        _displayMode:null,

        _onBackButton:function (e) {
            this.close();
        },

        _onSaveButton:function (e) {
            this.save(true);
        },

        _onRefreshButton:function (e) {
            this.reloadData();
            this.fireEvent('refresh');
        },

        _initForm:function () {
            for (var i = 0; i < this._forms.length; i++) {
                this._forms[i].reset();
                var items = this._forms[i].getItems();
                for (var name in items) {
                    if (this._displayMode == 'view') {
                        this._setFieldReadOnly(items[name], true);
                    } else {
                        this._setFieldReadOnly(items[name], false);
                    }
                }
            }
        },

        _setFieldReadOnly:function (field, value) {
            if (field instanceof qx.ui.form.AbstractField || field instanceof enre.ui.model.Select
                    || field instanceof enre.ui.form.DateField) {
                field.setReadOnly(value);
            } else {
                field.setEnabled(!value);
            }
        },

        _show:function (mode, pk) {
            this._pk = pk;
            this._displayMode = mode;
            this._initForm();
            this.reloadData();
            if (this._displayMode != 'view') {
                this._saveButton.setEnabled(true);
            } else {
                this._saveButton.setEnabled(false);
            }
        },

        getPk:function () {
            return this._pk;
        },

        getDisplayMode:function () {
            return this._displayMode;
        },

        close:function () {
            this.getParent().fireEvent('closeEdit');
            this.hide();
        },

        getModel:function () {
            return this._model;
        },

        getContainer:function () {
            return this._container;
        },

        bindForm:function (form) {
            var items = form.getItems();
            for (var name in items) {
                if (qx.Class.hasInterface(items[name].constructor, enre.ui.model.IModelSelect)) {
                    items[name].setNullRow(this.tr('_none_'));
                }
            }
            this._forms.append([form]);
        },

        unbindForm:function (form) {
            this._form.remove(form);
        },

        bindForms:function (forms) {
            for (var i = 0; i < forms.length; i++) {
                this.bindForm(forms[i]);
            }
        },

        getForms:function () {
            return this._forms;
        },

        addWidget:function (widget, options) {
            this._container.add(widget, options);
        },

        removeWidget:function (widget) {
            this._container.remove(widget);
        },

        _initModel:function (model) {
            this._model = model;
            var mdl = this._model.clone();
            for (var i = 0; i < this._forms.length; i++) {
                var form = this._forms[i];
                form.reset();
                var controller = new qx.data.controller.Form(this._model, form);
                var items = form.getItems();
                for (var name in items) {
                    if (name.length > 0 && qx.Class.hasInterface(items[name].constructor, enre.ui.model.IModelSelect)) {
                        var itemName = name.toString();
                        items[name].addListener('dataLoaded', function (e) {
                            this._model.set(itemName, mdl.get(itemName));
                        }, this);
                    }
                }
            }
            this.fireDataEvent('dataLoaded', this._model);
        },

        reloadData:function () {
            this._initModel(this.getService().getRecord(this._pk));
        },

        save:function (closeOnSave) {
            for (var i = 0; i < this._forms.length; i++) {
                if (!this._forms[i].validate()) {
                    return false;
                }
            }
            try {
                this._initModel(this.getService().saveRecord(this._model));
                this._pk = this._model.get(this.getPkField());
                if (closeOnSave) {
                    this.close();
                    this.getParent().fireDataEvent('saveEdit', this._pk);
                } else {
                    this._model.set(this.getPkField(), this._pk);
                    this.getParent().fireEvent('refresh');
                }
                return true;
            } catch (ex) {
                enre.ui.dialog.Dialog.error(ex.toString()).show();
                return false;
            }
        }

    }

});

qx.Class.define('enre.ui.view.EditPanel', {
    extend:qx.ui.container.Composite,
    include:[enre.ui.view.MEditContainer],
    implement:[enre.ui.view.IEditContainer],
    type:'abstract',

    properties:{

        toolbar:{
            nullable:false
        }

    },

    events:{
        'close':'qx.event.type.Event'
    },

    members:{
        _buttonsPart:null,
        _refreshButton:null,

        _initControls:function () {
            var iconPath = enre.utils.Theme.getIconUrl() + '/22/actions/';

            var toolbar = new qx.ui.toolbar.ToolBar();
            this._buttonsPart = new qx.ui.toolbar.Part();

            this._backButton = new qx.ui.toolbar.Button(this.tr('btn_back'), iconPath + 'go-previous.png');
            this._backButton.addListener('execute', this._onBackButton, this);
            this._buttonsPart.add(this._backButton);

            this._buttonsPart.add(new qx.ui.toolbar.Separator());

            this._saveButton = new qx.ui.toolbar.Button(this.tr('btn_save'), iconPath + 'document-save.png');
            this._saveButton.addListener('execute', this._onSaveButton, this);
            this._buttonsPart.add(this._saveButton);

            toolbar.add(this._buttonsPart);
            this.add(toolbar, {edge:'north'});
            this.setToolbar(toolbar);

            this._refreshButton = new qx.ui.toolbar.Button(this.tr('btn_refresh'), iconPath + 'view-refresh.png');
            this._refreshButton.addListener('execute', this._onRefreshButton, this);
            toolbar.addSpacer();
            toolbar.add(this._refreshButton);
        },

        show:function (mode, pk) {
            this._show(mode, pk)
            this.base(arguments);
        }

    }

});


qx.Class.define('enre.ui.view.EditWindow', {
    extend:qx.ui.window.Window,
    include:[enre.ui.view.MEditContainer],
    implement:[enre.ui.view.IEditContainer],
    type:'abstract',

    members:{

        _initControls:function () {
            this.setContentPadding(0);
            var iconPath = enre.utils.Theme.getIconUrl() + '/16/actions/';
            this.setModal(true);
            this.setAllowMinimize(false);
            this.setShowMinimize(false);
            this._saveButton = new qx.ui.toolbar.Button(this.tr('btn_save'), iconPath + 'document-save.png');
            this._saveButton.addListener('execute', this._onSaveButton, this);
            this._backButton = new qx.ui.toolbar.Button(this.tr('btn_close'), iconPath + 'dialog-close.png');
            this._backButton.addListener('execute', this._onBackButton, this);
            var layout = new qx.ui.layout.Grid(10, 0);
            layout.setColumnFlex(0, 1);
            var container = new qx.ui.container.Composite(layout);
            container.setPadding([0, 10, 10, 10]);
            container.add(this._saveButton, {row:0, column:2});
            this._saveButton.setMargin(0);
            container.add(this._backButton, {row:0, column:3});
            this._backButton.setMargin(0);
            this.add(container, {edge:'south'});
        },

        show:function (mode, pk) {
            this._show(mode, pk)
            this.base(arguments);
            this.center();
        }

    }

});


qx.Mixin.define('enre.ui.view.MFilterPanel', {

    properties:{
        parent:{
            nullable:false
        }
    }

});


qx.Class.define('enre.ui.view.FilterPanel', {
    extend:qx.ui.container.Composite,
    include:[enre.ui.view.MFilterPanel, qx.locale.MTranslation],

    construct:function (parent) {
        this.base(arguments);
        this.setLayout(new qx.ui.layout.Dock());
        this.setPadding(4);
        if (parent) {
            this.setParent(parent);
        }
        var iconPath = enre.utils.Theme.getIconUrl() + '/16/actions/';

        var clearButton = new qx.ui.form.Button(null, iconPath + 'edit-clear.png').set({padding:2, margin:[0, 0, 0, 2]});
        clearButton.addListener('execute', this._onClearButton, this);
        this.add(clearButton, {edge:'east'});
        this._timer = new qx.event.Timer(200);
        this._timer.addListener('interval', this._onTimer, this);
    },

    properties:{
        parent:{
            nullable:false
        },

        form:{
            nullable:false,
            apply:'_applyForm'
        }
    },

    members:{
        _renderer:null,
        _timer:null,

        _onClearButton:function () {
            if (!this.getForm()) {
                return;
            }
            this.getForm().reset();
            this.getParent().fireEvent('filter');
        },

        _applyForm:function (value, old_value) {
            if (this._renderer) {
                this.remove(this._renderer);
            }
            var items = value.getItems();
            for (var name in items) {
                if (qx.Class.hasInterface(items[name].constructor, enre.ui.model.IModelSelect)) {
                    items[name].setNullRow(this.tr('_all_'));
                }
                if (qx.Class.hasInterface(items[name].constructor, qx.ui.core.ISingleSelection)) {
                    qx.util.PropertyUtil.setUserValue(items[name], '_firstChange', true);
                    items[name].addListener('changeSelection', this._onChangeSelection, this);
                } else if (qx.Class.hasInterface(items[name].constructor, qx.ui.form.IStringForm)) {
                    items[name].addListener('input', this._onInput, this);
                }
            }
            this._renderer = new enre.ui.form.HBoxRenderer(value);
            this.add(this._renderer);
        },

        _onChangeSelection:function (e) {
            if (!this.getForm()) {
                return;
            }
            var items = this.getForm().getItems();
            for (var name in items) {
                if (!qx.Class.hasInterface(items[name].constructor, qx.ui.core.ISingleSelection)) {
                    continue;
                }
                if (items[name].getSelection()[0] == e.getData()[0] && qx.util.PropertyUtil.getUserValue(items[name], '_firstChange')) {
                    qx.util.PropertyUtil.setUserValue(items[name], '_firstChange', false);
                    return;
                }
            }
            this.getParent().fireEvent('filter');
        },

        _onTimer:function (e) {
            this.getParent().fireEvent('filter');
            this._timer.stop();
        },

        _onInput:function () {
            this._timer.stop();
            this._timer.start();
        },

        getFilter:function () {
            var filter = new qx.type.Array();
            var controller = new qx.data.controller.Form(null, this.getForm());
            var items = this.getForm().getItems();
            for (var name in items) {
                var value;
                if (qx.Class.hasInterface(items[name].constructor, qx.ui.core.ISingleSelection)) {
                    value = items[name].getSelection()[0].getModel();
                    if (value == '_null_value_') {
                        value = null;
                    }
                } else {
                    value = items[name].getValue();
                }
                if (!value) continue;
                var flt = {};
                flt[name] = value;
                filter.append([flt, 'and']);
            }
            if (filter.length > 0) {
                filter.removeAt(filter.length - 1);
            }
            return filter;
        }
    }

});

qx.Class.define('enre.ui.view.CollapseFilterPanel', {
    extend:enre.ui.container.CollapsePanel,
    include:[enre.ui.view.MFilterPanel],

    construct:function (parent) {
        this.base(arguments);
        if (parent) {
            this.setParent(parent);
        }
        this.setMinimize(true);
    }

});

qx.Class.define('enre.ui.view.ToolBar', {
    extend:qx.ui.toolbar.ToolBar,
    include:[qx.locale.MTranslation],

    construct:function (parent) {
        this.base(arguments);
        this.setSpacing(5);
        this._buttonsPart = new qx.ui.toolbar.Part();
        this.add(this._buttonsPart);
        this._initControls();
        if (parent) {
            this.setParent(parent);
        }
        this._initEvents();
        this._controlState();
    },

    properties:{
        parent:{
            nullable:true,
            apply:'_applyParent'
        }
    },

    members:{
        _buttonsPart:null,
        _editButton:null,
        _delButton:null,

        _initControls:function () {
            this._toolbarButton('view');
            this._buttonsPart.add(new qx.ui.toolbar.Separator());
            this._toolbarButton('create');
            this._toolbarButton('edit');
            this._toolbarButton('delete');
            this.addSpacer();
            this._toolbarButton('refresh');
        },

        _getIconPath:function () {
            return enre.utils.Theme.getIconUrl() + '/22/actions/';
        },

        _toolbarButton:function (name) {
            switch (name) {
                case 'view':
                    this._viewButton = new qx.ui.toolbar.Button(this.tr('btn_view'), this._getIconPath() + 'edit-find.png');
                    this._viewButton.addListener('execute', function (e) {
                        this.getParent().fireEvent('view');
                    }, this);
                    this._buttonsPart.add(this._viewButton);
                    break;
                case 'create':
                    var createButton = new qx.ui.toolbar.Button(this.tr('btn_create'), this._getIconPath() + 'document-new.png');
                    createButton.addListener('execute', function (e) {
                        this.getParent().fireEvent('create');
                    }, this);
                    this._buttonsPart.add(createButton);
                    break;
                case 'edit':
                    this._editButton = new qx.ui.toolbar.Button(this.tr('btn_edit'), this._getIconPath() + 'edit-select-all.png');
                    this._editButton.addListener('execute', function (e) {
                        this.getParent().fireEvent('edit');
                    }, this);
                    this._buttonsPart.add(this._editButton);
                    break;
                case 'delete':
                    this._deleteButton = new qx.ui.toolbar.Button(this.tr('btn_delete'), this._getIconPath() + 'edit-delete.png');
                    this._deleteButton.addListener('execute', function (e) {
                        this.getParent().fireEvent('delete');
                    }, this);
                    this._buttonsPart.add(this._deleteButton);
                    break;
                case 'refresh':
                    var refreshButton = new qx.ui.toolbar.Button(this.tr('btn_refresh'), this._getIconPath() + 'view-refresh.png');
                    refreshButton.addListener('execute', function (e) {
                        this.getParent().fireEvent('refresh');
                    }, this);
                    this.add(refreshButton);
                    break;
                default:
                    throw new Error("Button '" + name + "' not found");
            }
        },

        _initEvents:function () {
            if (!this.getParent() || !this.getParent().getTable()) {
                return;
            }
            this.getParent().getTable().addListener('changeTableModel', function (e) {
                this._initEvents();
            }, this);
            this.getParent().addListener('dataChanged', function (e) {
                this._checkEnabledButtons();
            }, this);
        },

        _setEnabledPart:function (enabled) {
            this._buttonsPart.setEnabled(enabled);
        },

        _setEnabledButtons:function (enabled) {
            this._viewButton.setEnabled(enabled);
            this._editButton.setEnabled(enabled);
            this._deleteButton.setEnabled(enabled);
        },

        _checkEnabledButtons:function () {
            if (this.getParent().getTable().getTableModel().getRowCount() == 0 || !this.getParent().getEditPanel()) {
                this._setEnabledButtons(false);
            } else {
                this._setEnabledButtons(true);
            }
        },

        _controlState:function () {
            if (!this.getParent() || !this.getParent().getEditPanel()) {
                this._setEnabledPart(false)
            } else {
                this._setEnabledPart(true);
                this._setEnabledButtons(false);
            }
        },

        _onChangeEditPanel:function (e) {
            this._controlState();
            this._checkEnabledButtons();
        },

        _applyParent:function (value, old_value) {
            if (old_value) {
                old_value.removeListener('changeEditPanel', this._onChangeEditPanel, this);
            }
            this.getParent().addListener('changeEditPanel', this._onChangeEditPanel, this);
            this._controlState();
            this._initEvents();
        }
    }

});


qx.Class.define('enre.ui.view.ViewPanel', {
    extend:qx.ui.container.Composite,
    include:[enre.ui.model.MModelService, qx.locale.MTranslation],

    construct:function (modelUrl, columns, serviceName, editPanel) {
        this.base(arguments);
        this.setLayout(new qx.ui.layout.Grow());
        this._initControls();
        if (modelUrl) {
            this.setModelUrl(modelUrl);
        }
        if (columns) {
            this.setColumns(columns[0], columns[1], columns[2]);
        }
        if (serviceName) {
            this.setServiceName(serviceName);
        }
        if (editPanel) {
            this.setEditPanel(editPanel);
        }
        this.addListener('view', this._onView, this);
        this.addListener('create', this._onCreate, this);
        this.addListener('edit', this._onEdit, this);
        this.addListener('delete', this._onDelete, this);
        this.addListener('refresh', this._onRefresh, this);
        this.addListener('closeEdit', this._onCloseEdit, this);
        this.addListener('saveEdit', this._onSaveEdit, this);
        this.addListener('filter', this._onFilter, this);
    },

    properties:{

        toolBar:{
            nullable:false,
            apply:'_applyToolBar'
        },

        modelUrl:{
            nullable:true,
            apply:'_applyModelUrl'
        },

        editPanel:{
            nullable:true,
            apply:'_applyEditPanel'
        },

        filterPanel:{
            nullable:true,
            apply:'_applyFilterPanel'
        },

        displayMode:{
            init:'list'
        }

    },

    events:{
        'view':'qx.event.type.Event',
        'create':'qx.event.type.Event',
        'edit':'qx.event.type.Event',
        'delete':'qx.event.type.Event',
        'refresh':'qx.event.type.Event',
        'closeEdit':'qx.event.type.Event',
        'saveEdit':'qx.event.type.Data',
        'filter':'qx.event.type.Event',
        'dataChanged':'qx.event.type.Data',
        'changeEditPanel':'qx.event.type.Data',
        'changeSelection':'qx.event.type.Event',
        'dataLoaded':'qx.event.type.Data'
    },

    members:{
        _gridPanel:null,
        _table:null,
        _columns:null,
        _editPanel:null,

        _initControls:function () {
            this._gridPanel = new qx.ui.container.Composite(new qx.ui.layout.Dock());
            this._table = new enre.ui.model.Table();
            this._table.getSelectionModel().addListener('changeSelection', function (e) {
                this.fireEvent('changeSelection');
            }, this);
            var toolbar = new enre.ui.view.ToolBar();
            this.setToolBar(toolbar);
            this._gridPanel.add(this._table, {edge:'center'});
            this.add(this._gridPanel);
        },

        _initModel:function () {
            if (this.getModelUrl() && this._columns) {
                var model = new enre.remote.TableModel(this.getModelUrl());
                model.setColumns(this._columns[0], this._columns[1], this._columns[2]);
                model.addListener('dataChanged', function (e) {
                    this.fireDataEvent('dataChanged', e.getData());
                }, this);
                model.addListener('dataLoaded', function (e) {
                    this.fireDataEvent('dataLoaded', this._table.getTableModel());
                }, this);
                this.getTable().setTableModel(model);
            }
        },

        _applyToolBar:function (value, oldValue) {
            if (oldValue) {
                this._gridPanel.remove(oldValue);
            }
            this._gridPanel.add(value, {edge:'north'});
            value.setParent(this);
        },

        _applyModelUrl:function (value, old_value) {
            this._initModel();
        },

        _applyFilterPanel:function (value, old_value) {
            if (old_value) {
                this._gridPanel.remove(old_value);
            }
            value.setParent(this);
            this._gridPanel.add(value, {edge:'north'});
        },

        _applyEditPanel:function (value, old_value) {
            if (this._editPanel) {
                this.remove(this._editPanel);
                this._editPanel = null;
            }
            if (typeof value == 'object') {
                value.hide();
            }
            this.fireEvent('changeEditPanel', this._editPanel);
        },

        _dispEditForm:function (mode) {
            if (!this.getEditPanel() || (mode != 'create' && !this.isRecord())) {
                return;
            }
            if (!this._editPanel) {
                var obj = this.getEditPanel();
                if (typeof obj == 'object') {
                    this._editPanel = obj;
                } else {
                    this._editPanel = new obj();
                }
            }
            this._editPanel.setParent(this);
            if (!this._editPanel.getService()) {
                this._editPanel.setServiceName(this.getServiceName());
            }
            if (this._editPanel instanceof enre.ui.view.EditPanel) {
                this.add(this._editPanel);
                this._gridPanel.hide();
            }
            this._editPanel.setVisibility(true);
            var pk = this.getTable().getFocusedPk();
            if (mode == 'create') {
                pk = null;
            }
            this._editPanel.setPkField(this.getTable().getPkField());
            this._editPanel.show(mode, pk);
        },

        _onView:function () {
            this._dispEditForm('view');
        },

        _onCreate:function () {
            this._dispEditForm('create');
        },

        _onEdit:function () {
            this._dispEditForm('edit');
        },

        _onDelete:function () {
            if (!this.isRecord()) {
                return;
            }
            new enre.ui.dialog.Dialog.warning(this.tr('msg_delrec'), 'yes-no').show().addListener('yes', function () {
                try {
                    this.getService().deleteRecord(this.getTable().getFocusedPk());
                    this.getTable().getTableModel().reloadData();
                } catch (ex) {
                    enre.ui.dialog.Dialog.error(ex.toString()).show();
                }
            }, this);
        },

        _onRefresh:function () {
            if (!this.getTable()) {
                return;
            }
            this.getTable().getTableModel().reloadData();
        },

        _onCloseEdit:function () {
            this._gridPanel.show();
        },

        _onSaveEdit:function () {
            this.getTable().getTableModel().reloadData();
        },

        _onFilter:function () {
            if (!this.getFilterPanel()) {
                return;
            }
            var filter = this.getFilterPanel().getFilter();
            this._table.getTableModel().setFilter(filter);
            this._table.getTableModel().reloadData();
        },

        getTable:function () {
            return this._table;
        },

        isRecord:function () {
            if (this.getTable() && this.getTable().getTableModel().getRowCount() > 0 && this.getTable().getFocusedPk()) {
                return true;
            }
            new enre.ui.dialog.Dialog.warning(this.tr('msg_please_selrec')).show();
            return false;
        },

        setColumns:function (columnNameArr, columnIdArr, pkField) {
            this._columns = [null, null, null];
            if (columnNameArr) this._columns[0] = columnNameArr;
            if (columnIdArr) this._columns[1] = columnIdArr;
            if (pkField) this._columns[2] = pkField;
            this._initModel();
        },

        setColumnWidth:function (column, width) {
            this.getTable().setColumnWidth(column, width);
        },

        setHiddenColumns:function (columns) {
            this.getTable().setHiddenColumns(columns);
        },

        setDataCellRenderer:function (column, renderer) {
            this.getTable().getTableColumnModel().setDataCellRenderer(column, renderer);
        },

        getGridPanel:function () {
            return this._gridPanel;
        },

        getPk:function () {
            return this._table.getFocusedPk();
        },

        sortByColumn:function (columnIndex, ascending) {
            if (this._table) {
                var asc = ascending ? ascending : true;
                this._table.getTableModel().sortByColumn(columnIndex, asc);
            }
        }

    },

    destruct:function () {
        this._disposeObjects(['_editPanel', '_table', '_service', '_gridPanel']);
        this._gridPanel = this._table = this._columns = this._service = this._editPanel = null;
    }

});


qx.Class.define('enre.ui.view.RelationSelect', {
    extend:enre.ui.model.SelectDialog,

    construct:function (url, relationField, dialogCaption, columnCaption, icon, pkField, textField) {
        this.base(arguments, url, dialogCaption, columnCaption, icon, pkField, textField);
        if (relationField) {
            this.setRelationField(relationField);
        }
    },

    events:{
        'select':'qx.event.type.Data'
    },

    properties:{
        relationField:{init:null}
    },

    members:{
        _pk:null,

        _onOkButton:function () {
            this.fireDataEvent('select', this._table.getFocusedPk());
            this.close();
        },

        _onCancelButton:function (e) {
            this.fireDataEvent('select', null);
            this.close();
        },

        _initModel:function () {
            this.base(arguments);
            if (this.getRelationField()) {
                var exclude = {};
                exclude[this.getRelationField() + '__in'] = [this._pk];
                this._model.setExclude(exclude);
            }
        },

        show:function (pk) {
            this._pk = pk;
            this.base(arguments)
        }
    }
});


qx.Class.define('enre.ui.view.RelationPanel', {
    extend:qx.ui.container.Composite,
    include:[enre.ui.model.MModelService, qx.locale.MTranslation],

    construct:function (modelUrl, columns, serviceName, relation, addPanel, createPanel, parent) {
        this.base(arguments);
        this.setLayout(new qx.ui.layout.Dock());
        this._initControls();
        if (modelUrl) {
            this.setModelUrl(modelUrl);
        }
        if (columns) {
            this.setColumns(columns[0], columns[1], columns[2]);
        }
        if (serviceName) {
            this.setServiceName(serviceName);
        }
        if (relation) {
            this.setRelation(relation);
        }
        if (addPanel) {
            this.setAddPanel(addPanel);
        }
        if (createPanel) {
            this.setCreatePanel(createPanel);
        }
        if (parent) {
            this.setParent(parent);
        }
        this.addListener('appear', this._onAppear, this);
        this.addListener('saveEdit', this._onSaveEdit, this);
        this.addListener('closeEdit', this._onCloseEdit, this);
    },

    properties:{
        parent:{
            nullable:true,
            apply:'_applyParent'
        },

        modelUrl:{
            nullable:true,
            apply:'_applyModelUrl'
        },

        relation:{
            nullable:true,
            apply:'_applyRelation'
        },

        addPanel:{
            nullable:true,
            apply:'_applyAddPanel'
        },

        createPanel:{
            nullable:true,
            apply:'_applyCreatePanel'
        },

        deleteMode:{
            init:'default',
            check:function (value) {
                var valid = ['default', 'relation', 'record'];
                return qx.lang.Array.contains(valid, value.toString());
            }
        },

        visibleView:{
            init:true
        },

        visibleEdit:{
            init:true
        },

        visibleDelete:{
            init:true
        }
    },

    events:{
        'saveEdit':'qx.event.type.Data',
        'closeEdit':'qx.event.type.Event'
    },

    members:{
        _model:null,
        _table:null,
        _columns:null,
        _toolbar:null,
        _addPanel:null,
        _createPanel:null,
        _addButton:null,
        _createButton:null,
        _createPanelMode:null,

        _initControls:function () {
            this._toolbar = new qx.ui.container.Composite(new qx.ui.layout.HBox(5));
            this._toolbar.setAppearance('relationpanel/toolbar');
            this.add(this._toolbar, {edge:'north'});
            this._table = new enre.ui.model.ActionTable();
            this._table.addListener('view', this._onView, this);
            this._table.addListener('edit', this._onEdit, this);
            this._table.addListener('delete', this._onDelete, this);
            this.add(this._table, {edge:'center'});
            this._toolbarButton('add');
            this._toolbarButton('create');

        },

        _getIconPath:function () {
            return enre.utils.Theme.getIconUrl() + '/16/actions/';
        },

        _toolbarButton:function (name) {
            switch (name) {
                case 'add':
                    this._addButton = new qx.ui.form.Button(this.tr('btn_add'), this._getIconPath() + 'list-add.png');
                    this._addButton.addListener('execute', this._onAddButton, this);
                    this._toolbar.add(this._addButton);
                    this._addButton.setVisibility('excluded');
                    break;
                case 'create':
                    this._createButton = new qx.ui.form.Button(this.tr('btn_create'), this._getIconPath() + 'document-new.png');
                    this._createButton.addListener('execute', this._onCreateButton, this);
                    this._toolbar.add(this._createButton);
                    this._createButton.setVisibility('excluded');
                    break;
            }
        },

        _initModel:function () {
            if (this.getModelUrl() && this._columns && this.getRelation()) {
                if (!this._model) {
                    this._model = new enre.remote.ActionTableModel();
                }
                this._model.setColumns(this._columns[0], this._columns[1], this._columns[2]);
                this.getTable().setTableModel(this._model);
            }
        },

        _applyParent:function (value, old_value) {
            if (old_value) {
                old_value.removeListener('changeSelection', this._onParentChangeSelection, this);
                old_value.removeListener('refresh', this._onParentRefresh, this);
            }
            value.addListener('changeSelection', this._onParentChangeSelection, this);
            value.addListener('refresh', this._onParentRefresh, this);
        },

        _isParentSaved:function () {
            if (!this.getParent().getPk()) {
                return this.getParent().save(false);
            }
            return true;
        },

        _applyModelUrl:function (value, old_value) {
            this._initModel();
        },

        _applyRelation:function (value, old_value) {
            this._initModel();
        },

        _applyAddPanel:function (value, old_value) {
            if (this._addPanel) {
                this._addPanel = null;
            }
            if (value && !old_value) {
                this._addButton.setVisibility('visible');
            } else if (!value && old_value) {
                this._addButton.setVisibility('excluded');
            }
        },

        _applyCreatePanel:function (value, old_value) {
            if (this._createPanel) {
                this._createPanel = null;
            }
            if (value && !old_value) {
                this._createButton.setVisibility('visible');
            } else if (!value && old_value) {
                this._createButton.setVisibility('excluded');
            }
        },

        _onParentChangeSelection:function () {
            this.reloadData();
        },

        _onParentRefresh:function (e) {
            var id = this.getParent().addListener('dataLoaded', function (e) {
                this.getParent().removeListenerById(id);
                this.reloadData();
            }, this);
        },

        _onView:function (e) {
            this._showCreatePanel('view', e.getData());
        },

        _onEdit:function (e) {
            this._showCreatePanel('edit', e.getData());
        },

        _getDeleteMode:function () {
            if (this.getDeleteMode() != 'default') {
                return mode;
            }
            if (this._addButton.getVisibility() != 'visible') {
                return 'record';
            }
            return 'relation'
        },

        _onDelete:function (e) {
            var pk = e.getData();
            new enre.ui.dialog.Dialog.warning(this.tr('msg_delrec'), 'yes-no').show().addListener('yes', function () {
                try {
                    this.getService().deleteRelation(this.getRelation(), this._getDeleteMode(), this.getParent().getPk(), pk);
                    this.reloadData();
                } catch (ex) {
                    enre.ui.dialog.Dialog.error(ex.toString()).show();
                }
            }, this);
        },

        _createRelation:function (pk) {
            if (pk) {
                try {
                    this.getService().createRelation(this.getRelation(), this.getParent().getPk(), pk);
                    this.reloadData();
                } catch (ex) {
                    enre.ui.dialog.Dialog.error(ex.toString()).show();
                }
            }
        },

        _setParentModal:function (mode) {
            if (this.getParent() instanceof enre.ui.view.EditWindow) {
                this.getParent().setModal(mode);
            }
        },

        _onAddButton:function (e) {
            if (!this._isParentSaved()) {
                return;
            }
            if (!this._addPanel) {
                this._addPanel = this._getPanel(this.getAddPanel());
                this._addPanel.addListener('select', this._onSelect, this);
            }
            this._setParentModal(false);
            this._addPanel.show(this.getParent().getPk());
        },


        _onSelect:function (e) {
            this._setParentModal(true);
            this._createRelation(e.getData());
        },

        _showCreatePanel:function (mode, pk) {
            if (!this._createPanel) {
                this._createPanel = this._getPanel(this.getCreatePanel());
                this._createPanel.setParent(this);
                this._createPanel.setPkField(this._table.getPkField());
            }
            this._setParentModal(false);
            this._createPanelMode = mode;
            this._createPanel.show(mode, pk);
        },

        _onCreateButton:function (e) {
            if (!this._isParentSaved()) {
                return;
            }
            this._showCreatePanel('create', null);
        },

        _onSaveEdit:function (e) {
            if (this._createPanelMode == 'create') {
                this._createRelation(e.getData());
            } else {
                this.reloadData();
            }
            this._setParentModal(true);
        },

        _onCloseEdit:function (e) {
            this._setParentModal(true);
        },

        _getPanel:function (panel) {
            var obj = panel;
            if (typeof obj == 'object') {
                return  obj;
            }
            return new obj();
        },

        _setVisiblyToolbar:function () {
            if (this._addButton.getVisibility() == 'visible' || this._createButton.getVisibility() == 'visible') {
                this._toolbar.setVisibility('visible');
            } else {
                this._toolbar.setVisibility('exclude');
            }
        },

        _onAppear:function (e) {
            if (this._addButton) {
                if (this.getParent().getDisplayMode() == 'view') {
                    this._addButton.setEnabled(false);
                } else {
                    this._addButton.setEnabled(true);
                }
            }
            if (this._createButton) {
                if (this.getParent().getDisplayMode() == 'view') {
                    this._createButton.setEnabled(false);
                } else {
                    this._createButton.setEnabled(true);
                }
            }
            this._table.setActionVisible('_view_action_', false);
            this._table.setActionVisible('_edit_action_', false);
            this._table.setActionVisible('_delete_action_', false);
            if ((this._addButton.getVisibility() == 'visible' || this._createButton.getVisibility() == 'visible')
                    && this.getParent().getDisplayMode() != 'view' && this.getVisibleDelete()) {
                this._table.setActionVisible('_delete_action_', true);
            }
            if (this._createButton.getVisibility() == 'visible' && this.getParent().getDisplayMode() != 'view') {
                if (this.getVisibleView()) {
                    this._table.setActionVisible('_view_action_', true);
                }
                if (this.getVisibleEdit()) {
                    this._table.setActionVisible('_edit_action_', true);
                }
            }
            this._setVisiblyToolbar();
            if (!(this.getParent() instanceof enre.ui.view.ViewPanel)) {
                this.reloadData();
            }
        },

        getTable:function () {
            return this._table;
        },

        getToolbar:function () {
            return this._toolbar;
        },

        setColumns:function (columnNameArr, columnIdArr, pkField) {
            this._columns = [null, null, null];
            if (columnNameArr) this._columns[0] = columnNameArr;
            if (columnIdArr) this._columns[1] = columnIdArr;
            if (pkField) this._columns[2] = pkField;
            this._initModel();
        },

        sortByColumn:function (columnIndex, ascending) {
            var asc = ascending ? ascending : true;
            this._model.sortByColumn(columnIndex, asc);

        },

        reloadData:function () {
            if (!this.getParent() || !this.getModelUrl() || !this.getRelation()) {
                return;
            }
            var url = this.getModelUrl();
            if (url.charAt(url.length - 1) != '/') {
                url += '/';
            }
            url += 'relation/' + this.getRelation() + '/' + this.getParent().getPk();
            this._model.setUrl(url);
            this._model.reloadData();
        },

        setColumnWidth:function (column, width) {
            this.getTable().setColumnWidth(column, width);
        },

        setHiddenColumns:function (columns) {
            this._table.setHiddenColumns(columns);
        },

        setStatusBarVisible:function (value) {
            this._table.setStatusBarVisible(value);
        }
    },

    destruct:function () {
        this._model = this._table = this._columns = this._toolbar = this._addPanel = this._createPanel
                = this._addButton = this._createButton = null;
    }

});


qx.Class.define('enre.ui.view.ManyToManySelect', {
    extend:qx.ui.container.Composite,
    include:[enre.ui.model.MModelService, qx.locale.MTranslation],

    construct:function (modelUrl, columns, relation, serviceName, serviceRelation, parent) {
        this.base(arguments);
        this._initControls();
        if (modelUrl) {
            this.setModelUrl(modelUrl);
        }
        if (columns) {
            this.setColumns(columns[0], columns[1], columns[2]);
        }
        if (relation) {
            this.setRelation(relation);
        }
        if (serviceName) {
            this.setServiceName(serviceName);
        }
        if (serviceRelation) {
            this.setServiceRelation(serviceRelation);
        }
        if (parent) {
            this.setParent(parent);
        }
        this.addListener('appear', this._onAppear, this);
    },

    properties:{

        modelUrl:{
            nullable:true,
            apply:'_applyModelUrl'
        },

        relation:{
            init:null,
            apply:'_applyRelation'
        },

        parent:{
            init:null,
            apply:'_applyParent'
        },

        serviceRelation:{
            init:null
        },

        selectionMode:{
            init:null,
            apply:'_applySelectionMode'
        },

        unselectCaption:{
            init:null,
            apply:'_applyLabels'
        },

        selectCaption:{
            init:null,
            apply:'_applyLabels'
        }

    },

    members:{
        _unselectPanel:null,
        _selectPanel:null,
        _unselectLabel:null,
        _selectLabel:null,
        _unselectTable:null,
        _selectTable:null,
        _unselectModel:null,
        _selectModel:null,
        _columns:null,
        _addButton:null,
        _delButton:null,

        _initControls:function () {
            var iconPath = enre.utils.Theme.getIconUrl() + '/16/actions/';
            this.setLayout(new qx.ui.layout.HBox());
            this._unselectPanel = new qx.ui.container.Composite(new qx.ui.layout.Dock());
            this._unselectLabel = new qx.ui.basic.Label();
            this._unselectLabel.setAppearance('manytomanyrelation/label');
            this._unselectPanel.add(this._unselectLabel, {edge:'north'});
            this._unselectTable = new enre.ui.model.Table();
            this._unselectTable.setInitFirstRow(false);
            this._unselectPanel.add(this._unselectTable, {edge:'center'});
            this.add(this._unselectPanel, {width:'50%', flex:1});
            var panel = new qx.ui.container.Composite();
            panel.setAppearance('manytomanyrelation/buttonpanel');
            panel.setLayout(new qx.ui.layout.VBox(10, 'middle'));
            this._addButton = new qx.ui.form.Button(null, iconPath + 'go-next.png');
            this._addButton.addListener('execute', this._onAddButton, this);
            panel.add(this._addButton);
            this._delButton = new qx.ui.form.Button(null, iconPath + 'go-previous.png');
            this._delButton.addListener('execute', this._onDelButton, this);
            panel.add(this._delButton);
            this.add(panel);
            this._selectPanel = new qx.ui.container.Composite(new qx.ui.layout.Dock());
            this._selectLabel = new qx.ui.basic.Label();
            this._selectLabel.setAppearance('manytomanyrelation/label');
            this._selectPanel.add(this._selectLabel, {edge:'north'});
            this._selectTable = new enre.ui.model.Table();
            this._selectTable.setInitFirstRow(false);
            this._selectPanel.add(this._selectTable, {edge:'center'});
            this.setSelectionMode(qx.ui.table.selection.Model.MULTIPLE_INTERVAL_SELECTION);
            this.add(this._selectPanel, {width:'50%', flex:1});
            this._checkLabels();
        },

        _initModels:function () {
            if (this.getModelUrl() && this._columns && this.getRelation()) {
                if (!this._unselectModel) {
                    this._unselectModel = new enre.remote.TableModel();
                    this._unselectModel.addListener('dataLoaded', this._onDataLoaded, this);
                    this._selectModel = new enre.remote.TableModel();
                    this._selectModel.addListener('dataLoaded', this._onDataLoaded, this);
                }
                this._unselectModel.setColumns(this._columns[0], this._columns[1], this._columns[2]);
                this._selectModel.setColumns(this._columns[0], this._columns[1], this._columns[2]);
                this._selectModel.setPkHidden(this._unselectModel.getPkHidden());
                this._unselectTable.setTableModel(this._unselectModel);
                this._unselectTable.setColumnWidth(0, '30%');
                this._selectTable.setTableModel(this._selectModel);
                this._selectTable.setColumnWidth(0, '30%');
            }
        },

        _applyModelUrl:function (value, oldValue) {
            this._initModels();
        },

        _applyRelation:function (value, oldValue) {
            this._initModels();
        },

        _applyParent:function (value, old_value) {
            if (old_value) {
                old_value.removeListener('changeSelection', this._onParentChangeSelection, this);
                old_value.removeListener('refresh', this._onParentRefresh, this);
            }
            value.addListener('changeSelection', this._onParentChangeSelection, this);
            value.addListener('refresh', this._onParentRefresh, this);
            this._checkSelection();
        },

        _onDataLoaded:function (e) {
            this._checkSelection();
        },

        _applySelectionMode:function (value, old_value) {
            if (old_value) {
                this._unselectTable.getSelectionModel().removeListener('changeSelection', this._onChangeSelection, this);
                this._selectTable.getSelectionModel().removeListener('changeSelection', this._onChangeSelection, this);
            }
            this._unselectTable.getSelectionModel().setSelectionMode(value);
            this._unselectTable.getSelectionModel().addListener('changeSelection', this._onChangeSelection, this);
            this._selectTable.getSelectionModel().setSelectionMode(value);
            this._selectTable.getSelectionModel().addListener('changeSelection', this._onChangeSelection, this);
        },

        _applyLabels:function (value, old_value) {
            this._checkLabels();
        },

        _onParentChangeSelection:function () {
            this._unselectTable.resetSelection();
            this._unselectTable.resetCellFocus();
            this._selectTable.resetSelection();
            this._selectTable.resetCellFocus();
            this.reloadData();
        },

        _onParentRefresh:function (e) {
            var id = this.getParent().addListener('dataLoaded', function (e) {
                this.getParent().removeListenerById(id);
                this.reloadData();
            }, this);
        },

        _onAddButton:function (e) {
            if (!this._isParentSaved()) {
                return;
            }
            try {
                this.getService().createRelations(this.getServiceRelation(), this.getParent().getPk(), this._unselectTable.getSelectionPks());
                if (this._unselectTable.getSelectionPks().length > 1) {
                    this._unselectTable.resetSelection();
                    this._unselectTable.resetCellFocus();
                }
                this.reloadData();
            } catch (ex) {
                enre.ui.dialog.Dialog.error(ex.toString()).show();
            }
        },

        _onDelButton:function (e) {
            try {
                this.getService().deleteRelations(this.getServiceRelation(), 'relation', this.getParent().getPk(), this._selectTable.getSelectionPks());
                if (this._selectTable.getSelectionPks().length > 1) {
                    this._selectTable.resetSelection();
                    this._selectTable.resetCellFocus();
                }
                this.reloadData();
            } catch (ex) {
                enre.ui.dialog.Dialog.error(ex.toString()).show();
            }
        },

        _onChangeSelection:function (value, old_value) {
            this._checkSelection();
        },

        _checkLabels:function () {
            if (!this.getUnselectCaption() && !this.getSelectCaption()) {
                this._unselectLabel.setVisibility('excluded');
                this._selectLabel.setVisibility('excluded');
            } else {
                this._unselectLabel.setValue(this.getUnselectCaption());
                this._unselectLabel.setVisibility('visible');
                this._selectLabel.setValue(this.getSelectCaption());
                this._selectLabel.setVisibility('visible');
            }
        },

        _checkSelection:function () {
            this._addButton.setEnabled(false);
            this._delButton.setEnabled(false);
            if (this.getParent().getDisplayMode() == 'view') {
                return;
            }
            if (this._unselectTable.getSelectionPks().length > 0) {
                this._addButton.setEnabled(true);
            }
            if (this._selectTable.getSelectionPks().length > 0) {
                this._delButton.setEnabled(true);
            }
        },

        _isParentSaved:function () {
            if (!this.getParent().getPk()) {
                return this.getParent().save(false);
            }
            return true;
        },

        _onAppear:function () {
            if (!(this.getParent() instanceof enre.ui.view.ViewPanel)) {
                this.reloadData();
            }
        },

        setColumns:function (columnNameArr, columnIdArr, pkField) {
            this._columns = [null, null, null];
            if (columnNameArr) this._columns[0] = columnNameArr;
            if (columnIdArr) this._columns[1] = columnIdArr;
            if (pkField) this._columns[2] = pkField;
            this._initModels();
        },

        setColumnWidth:function (column, width) {
            this._unselectTable.setColumnWidth(column, width);
            this._selectTable.setColumnWidth(column, width);
        },

        sortByColumn:function (columnIndex, ascending) {
            var asc = ascending ? ascending : true;
            this._unselectModel.sortByColumn(columnIndex, asc);
            this._selectModel.sortByColumn(columnIndex, asc);
        },

        setStatusBarVisible:function (value) {
            this._unselectTable.setStatusBarVisible(value);
            this._selectTable.setStatusBarVisible(value);
        },

        reloadData:function () {
            if (!this.getParent() || !this.getModelUrl() || !this.getRelation()) {
                return;
            }
            this._unselectModel.setUrl(this.getModelUrl());
            var _in = {};
            _in[this.getRelation() + '__in'] = [this.getParent().getPk()];
            this._unselectModel.setExclude(_in);
            this._unselectModel.reloadData();
            this._selectModel.setUrl(this.getModelUrl());
            this._selectModel.setFilter(_in);
            this._selectModel.setDistinct([this._selectModel.getPkField()]);
            this._selectModel.reloadData();
        }
    },

    destruct:function () {
        this._selectPanel = this._unselectPanel = this._selectLabel = this._unselectLabel
                = this._unselectTable = this._selectTable = this._selectModel = this._unselectModel
                = this._addButton, this._delButton = null;
    }
});


/**
 * UI.WIDGET
 */
qx.Class.define('enre.ui.widget.GroupListPanel', {
    extend:qx.ui.list.List,

    construct:function (labelField, groupField, store) {
        this.base(arguments)
        if (store) {
            if (store instanceof qx.core.Object) {
                this.setStore(store);
            } else {
                var _store = new enre.remote.Store(store);
                this.setStore(_store);
            }
        }
        if (labelField) {
            this.setLabelField(labelField);
        }
        if (groupField) {
            this.setGroupField(groupField);
        }
        if (!groupField) {
            this._setDelegate();
        }
    },

    properties:{
        appearance:{
            refine:true,
            init:'grouplistpanel'
        },

        labelField:{
            init:null,
            apply:'_applyLabelField'
        },

        groupField:{
            init:null,
            apply:'_applyGroupField'
        },

        store:{
            init:null,
            apply:'_applyStore'
        }
    },

    members:{

        _setDelegate:function () {
            var delegate = {

                _groupField:this.getGroupField(),

                group:function (model) {
                    return model.get(this._groupField) ? model.get(this._groupField) : null;
                },

                createGroupItem:function () {
                    return new qx.ui.form.ListItem();
                },

                configureGroupItem:function (item) {
                    item.setAppearance('grouplistpanel/groupitem');
                },

                configureItem:function (item) {
                    item.setAppearance('grouplistpanel/item');
                },

                bindGroupItem:function (controller, item, id) {
                    controller.bindProperty(null, 'label', null, item, id);
                }
            };
            this.setDelegate(delegate);
        },

        _applyLabelField:function (value, old_value) {
            this.setLabelPath(value);
        },

        _applyGroupField:function (value, old_value) {
            this._setDelegate();
        },

        _applyStore:function (value, old_value) {
            if (old_value) {
                old_value.removeListener('loaded', this._onDataLoaded, this);
                old_value.dispose();
                old_value = null;
            }
            value.bind('model', this, 'model');
            value.addListener('loaded', this._onDataLoaded, this);
        },

        _onDataLoaded:function (e) {
            if (e.getData().length > 0) {
                var selection = new qx.data.Array();
                selection.push(e.getData().getItem(0));
                this.setSelection(selection);
                this.getSelection().addListener('change', function (e) {
                    this.fireDataEvent('changeSelection', this.getSelection());
                }, this)
            }
        }

    }

});

/**
 * REMOTE
 */
qx.Class.define('enre.remote.Rpc', {

    extend:qx.io.remote.Rpc,

    construct:function (service) {
        qx.io.remote.Rpc.CONVERT_DATES = true;
        qx.io.remote.Rpc.RESPONSE_JSON = true;
        this.base(arguments, enre.utils.Django.rpcUrl, service)
    },

    members:{

        createRequest:function () {
            var request = this.base(arguments);
            request.setRequestHeader('X-CSRFToken', enre.utils.Http.getCsrf());
            return request;
        }

    }

});


qx.Class.define('enre.remote.ModelService', {
    extend:enre.remote.Rpc,

    members:{

        getRecord:function (pk) {
            var json = this.callSync('get', pk);
            return qx.data.marshal.Json.createModel(json);
        },

        saveRecord:function (model) {
            var json = enre.utils.Serializer.toJson(model);
            return qx.data.marshal.Json.createModel(this.callSync('save', json));
        },

        deleteRecord:function (pk) {
            return this.callSync('delete', pk);
        },

        createRelation:function (relation, modelPk, relationPk) {
            return this.callSync('create_relation', relation, modelPk, relationPk);
        },

        deleteRelation:function (relation, mode, modelPk, relationPk) {
            return this.callSync('delete_relation', relation, mode, modelPk, relationPk);
        },

        createRelations:function (relation, modelPk, relationsPks) {
            return this.callSync('create_relations', relation, modelPk, enre.utils.Serializer.toJson(relationsPks));
        },

        deleteRelations:function (relation, mode, modelPk, relationsPks) {
            return this.callSync('delete_relations', relation, mode, modelPk, enre.utils.Serializer.toJson(relationsPks));
        }
    }
});


qx.Class.define('enre.remote.Store', {

    extend:qx.data.store.Json,

    construct:function (url, filter, delegate) {
        if (filter) {
            this.setFilter(filter);
        }
        this.base(arguments, url, delegate);
    },

    properties:{
        filter:{init:null},
        exclude:{init:null},
        distinct:{init:null}
    },

    members:{

        _createRequest:function (url) {
            if (this._request) {
                this._request.dispose();
                this._request = null;
            }
            var _url = enre.utils.Django.storeUrl + url + '?';
            if (this.getFilter()) {
                _url = _url + '_filter=' + enre.utils.Serializer.toJson(this.getFilter());
            }
            if (this.getExclude()) {
                _url = _url + '&_exclude=' + enre.utils.Serializer.toJson(this.getExclude());
            }
            if (this.getDistinct()) {
                _url = _url + '&_distinct=' + enre.utils.Serializer.toJson(this.getDistinct());
            }
            var req = new qx.io.request.Xhr(_url);
            this._setRequest(req);
            req.setAccept('application/json');
            req.setParser('json');
            req.setCache(false);
            req.setRequestHeader('Pragma', 'no-cache');
            req.setRequestHeader('Cache-Control', 'no-cache');
            req.addListener('success', this._onSuccess, this);
            var del = this._delegate;
            if (del && qx.lang.Type.isFunction(del.configureRequest)) {
                this._delegate.configureRequest(req);
            }
            req.addListener('changePhase', this._onChangePhase, this);
            req.addListener('fail', this._onFail, this);
            req.send();
        }

    }

});


qx.Class.define('enre.remote.TableModel', {

    extend:qx.ui.table.model.Remote,

    construct:function (url) {
        this.base(arguments);
        if (url) {
            this.setUrl(url);
        }
    },

    events:{
        'dataLoaded':'qx.event.type.Event',
        'changePkHidden':'qx.event.type.Event'
    },

    properties:{
        url:{ nullable:true },
        filter:{ init:null },
        exclude:{init:null},
        distinct:{init:null},
        defaultSortColumnIndex:{init:0}
    },

    members:{

        _pkField:'id',
        _pkFieldHidden:true,

        _createRequest:function (url) {
            var req = new qx.io.remote.Request(enre.utils.Django.storeUrl + url, 'POST', "application/json");
            req.setRequestHeader('Content-Type', 'application/json');
            req.setRequestHeader('X-CSRFToken', enre.utils.Http.getCsrf());
            return req;
        },

        _queryParams:function () {
            var data = {};
            if (this.getFilter() != null) {
                data['_filter'] = enre.utils.Serializer.toJson(this.getFilter());
            }
            if (this.getExclude() != null) {
                data['_exclude'] = enre.utils.Serializer.toJson(this.getExclude());
            }
            if (this.getDistinct() != null) {
                data['_distinct'] = enre.utils.Serializer.toJson(this.getDistinct());
            }
            return data;
        },

        _loadRowCount:function () {
            if (!this.getUrl()) {
                return;
            }
            var url = this.getUrl();
            if (!url) {
                url = '/';
            } else if (url.length == 0 || url.charAt(url.length - 1) != '/') {
                url += '/'
            }
            url += 'row_count';
            var req = this._createRequest(url);
            req.addListener("completed", this._onRowCountCompleted, this);
            var data = this._queryParams();
            req.setData(enre.utils.Serializer.toJson(data));
            req.send();
        },

        _onRowCountCompleted:function (response) {
            var result = response.getContent();
            if (result != null) {
                this._onRowCountLoaded(result);
            }
        },

        _loadRowData:function (firstRow, lastRow) {
            if (!this.getUrl()) {
                return;
            }
            var req = this._createRequest(this.getUrl());
            var data = this._queryParams();
            data['_from'] = firstRow;
            data['_to'] = lastRow;
            if (this.getSortColumnIndex() >= 0) {
                var order = this.getColumnId(this.getSortColumnIndex());
                if (!this.isSortAscending()) {
                    order = '-' + order;
                }
                data['_order'] = enre.utils.Serializer.toJson([order]);
            }
            req.setData(enre.utils.Serializer.toJson(data));
            req.addListener("completed", this._onLoadRowDataCompleted, this);
            req.send();
        },

        _onLoadRowDataCompleted:function (response) {
            var result = response.getContent();
            if (result != null) {
                this._onRowDataLoaded(result);
            }
            this.fireEvent("dataLoaded");
        },

        getPkField:function () {
            return this._pkField
        },

        isPkHidden:function () {
            return this._pkFieldHidden;
        },

        setPkHidden:function (hidden) {
            this._pkFieldHidden = hidden;
            this.fireEvent('changePkHidden');
        },

        getPkHidden:function () {
            return this._pkFieldHidden;
        },

        setColumns:function (columnNameArr, columnIdArr, pkField) {

            function checkId(arr, id) {
                for (var i = 0; i < arr.length; i++) {
                    if (arr[i] == id) {
                        return true;
                    }
                }
                return false;
            }

            if (pkField) {
                this._pkField = pkField;
            }

            if (columnNameArr && this._pkField) {
                if (columnIdArr) {
                    if (checkId(columnIdArr, this._pkField)) {
                        this.setPkHidden(false);
                    } else {
                        this.setPkHidden(true);
                        columnIdArr[columnIdArr.length] = this._pkField;
                        columnNameArr[columnNameArr.length] = this._pkField;
                    }
                } else {
                    if (checkId(columnNameArr, this._pkField)) {
                        this.setPkHidden(false);
                    } else {
                        this.setPkHidden(true);
                        columnNameArr[columnNameArr.length] = this._pkField;
                    }
                }
            }
            if (this.getSortColumnIndex() < 0) {
                this.sortByColumn(this.getDefaultSortColumnIndex(), true);
            }
            this.base(arguments, columnNameArr, columnIdArr);
        },

        getPk:function (row) {
            if (this.getPkField() == null) {
                throw new Error("The property is not defined 'pkField'");
            }
            return this.getValueById(this.getPkField(), row);
        }

    },

    destruct:function () {
        this._pkField = this._pkFieldHidden = null;
    }

});


qx.Class.define('enre.remote.ActionTableModel', {
    extend:enre.remote.TableModel,

    construct:function (url) {
        this.base(arguments, url);
        this.setDefaultSortColumnIndex(3);
    },

    properties:{
        actionsCount:{ init:3}
    },

    members:{
        setColumns:function (columnNameArr, columnIdArr, pkField) {
            var columnNameArr = columnNameArr;
            var columnIdArr = columnIdArr;
            if (!columnIdArr) {
                columnIdArr = columnNameArr;
            }
            columnNameArr.unshift(' ');
            columnIdArr.unshift('_delete_action_');
            columnNameArr.unshift(' ');
            columnIdArr.unshift('_edit_action_');
            columnNameArr.unshift(' ');
            columnIdArr.unshift('_view_action_');
            this.base(arguments, columnNameArr, columnIdArr, pkField);
        }
    }
});


qx.Class.define('enre.remote.Script', {

    extend:qx.core.Object,

    events:{
        'load':'qx.event.type.Data',
        'loadend':'qx.event.type.Event',
        'abort':'qx.event.type.Event',
        'error':'qx.event.type.Event',
        'timeout':'qx.event.type.Event',
        'readystatechange':'qx.event.type.Data'
    },

    members:{
        _request:null,
        __callback:null,
        __context:null,

        _fireEvent:function (event, data) {
            if (data) {
                this.fireDataEvent(event, data);
            } else {
                this.fireEvent(event);
            }
        },

        load:function (url, callback, context) {
            if (this._request) {
                this.reset();
            }
            this._request = new qx.bom.request.Script();
            this._request.context = this;
            this._request.onload = function (context) {
                if (this.context.__callback) {
                    this.context.__callback.call(this.context.__context || window);
                }
                this.context._fireEvent('load', this);
            }
            this._request.onloadend = function () {
                this.context._fireEvent('loadend');
            }
            this._request.onabort = function () {
                this.context._fireEvent('abort');
            }
            this._request.onerror = function () {
                this.context._fireEvent('error');
            }
            this._request.ontimeout = function () {
                this.context._fireEvent('timeout');
            }
            this._request.onreadystatechange = function (e) {
                this.context._fireEvent('readystatechange', this);
            }
            this._request.open("GET", url);
            this._request.send();
            this.__callback = callback;
            this.__context = context || window;
        },

        reset:function () {
            if (this._request) {
                this._request.dispose();
                this._request = this.__callback = this.__context = null;
            }
        }
    },

    destruct:function () {
        this.reset();
    }

});