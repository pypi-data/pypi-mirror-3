{% load url from future %}

qx.Class.define('enre.erp.core.References', {
    extend:enre.erp.Module,

    members:{
        _initControls:function () {
            this.setLayout(new qx.ui.layout.Grow());
            var pane = new qx.ui.splitpane.Pane();

            var list = new enre.ui.widget.GroupListPanel('name', 'group', 'enre/erp/core/stores/ReferenceStore');
            list.setWidth(200);
            list.addListener('changeSelection', function (e) {
                var item = e.getData().getItem(0);
                if (!item || !item.get('url')) {
                    return;
                }
                container.load(item.get('url'), item.get('class_name'));
            });
            pane.add(list, 0);

            var container = new enre.ui.container.Script();
            pane.add(container, 1);
            this.add(pane);
        }

    }
});
