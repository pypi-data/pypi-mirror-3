qx.Class.define('TestModule', {
    extend: qx.ui.container.Composite,

    construct: function() {
        this.base(arguments);
        this.setLayout(new qx.ui.layout.Basic());
        this.setPadding(4);
        var btn = new qx.ui.form.Button('Module');
        this.add(btn);
    }
});