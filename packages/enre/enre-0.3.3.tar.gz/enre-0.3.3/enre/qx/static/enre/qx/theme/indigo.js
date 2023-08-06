qx.Theme.define('enre.theme.indigo.Color', {
    extend:qx.theme.indigo.Color,

    colors:{
    }
});


qx.Theme.define('enre.theme.indigo.Decoration', {
    extend:qx.theme.indigo.Decoration,

    decorations:{

        'collapsepanel':{
            decorator:[
                qx.ui.decoration.MDoubleBorder,
                qx.ui.decoration.MBackgroundColor
            ],

            style:{
                width:1,
                color:'window-border',
                innerWidth:1,
                innerColor:'window-border-inner',
                backgroundColor:'background'
            }
        },

        'collapsepanel-caption':{
            decorator : [
                qx.ui.decoration.MBorderRadius,
                qx.ui.decoration.MSingleBorder
            ],

            style :
            {
                radius: [3, 3, 0, 0],
                color: "window-border",
                widthBottom: 1
            }
        },


        'button-box-right-bordersimple':{
            include:'button-box',

            style:{
                radius:0,
                width:[1, 1, 1, 0]
            }
        },

        'button-box-hovered-right-bordersimple':{
            include:'button-box-hovered',

            style:{
                radius:0,
                width:[1, 1, 1, 0]
            }
        },

        'button-box-pressed-hovered-right-bordersimple':{
            include:'button-box-pressed-hovered',

            style:{
                radius:0,
                width:[1, 1, 1, 0]
            }
        },

        'button-box-pressed-right-bordersimple':{
            include:"button-box-pressed",

            style:{
                radius:0,
                width:[1, 1, 1, 0]
            }
        }

    }
});


qx.Theme.define('enre.theme.indigo.Font', {
    extend:qx.theme.indigo.Font,

    fonts:{
    }
});


qx.Theme.define('enre.theme.indigo.Appearance', {
    extend:qx.theme.indigo.Appearance,

    appearances:{

        'tabview/pane':{
            style:function (states) {
                return {
                    backgroundColor:'background',
                    decorator:'main',
                    padding:4
                };
            }
        },

        'modelselect':'combobox',

        'modelselect/button':{
            alias:'button-frame',
            include:'button-frame',

            style:function (states) {
                var decorator = 'button-box-right-bordersimple';

                if (states.hovered && !states.pressed && !states.checked) {
                    decorator = 'button-box-hovered-right-bordersimple';
                } else if (states.hovered && (states.pressed || states.checked)) {
                    decorator = 'button-box-pressed-hovered-right-bordersimple';
                } else if (states.pressed || states.checked) {
                    decorator = 'button-box-pressed-right-bordersimple';
                }

                return {
                    icon:enre.utils.Theme.getIconUrl() + '/16/apps/utilities-text-editor.png',
                    decorator:decorator,
                    padding:0,
                    width:19
                };
            }
        },

        'modelselect/clearbutton':{
            alias:'button-frame',
            include:'button-frame',

            style:function (states) {
                var decorator = 'button-box-right-borderless';

                if (states.hovered && !states.pressed && !states.checked) {
                    decorator = 'button-box-hovered-right-borderless';
                } else if (states.hovered && (states.pressed || states.checked)) {
                    decorator = 'button-box-pressed-hovered-right-borderless';
                } else if (states.pressed || states.checked) {
                    decorator = 'button-box-pressed-right-borderless';
                }

                return {
                    icon:enre.utils.Theme.getIconUrl() + '/16/actions/edit-clear.png',
                    decorator:decorator,
                    padding:0,
                    width:19
                };
            }
        },

        'collapsepanel':{
            style:function (states) {
                return {
                    contentPadding:[ 4, 4, 4, 4 ],
                    backgroundColor:states.maximized ? "background" : undefined,
                    decorator:states.maximized ? undefined : states.active ? "window-active" : "window"
                };
            }
        },

        'collapsepanel/pane':{},

        'collapsepanel/title':{
            style:function (states) {
                return {
                    cursor:"default",
                    font:"default",
                    marginRight:20,
                    alignY:"middle"
                };
            }
        },


        'collapsepanel/captionbar':{
            style : function(states)
            {
                var active = states.active && !states.disabled;
                return {
                    padding : [3, 8, active ? 1 : 3, 8],
                    textColor: active ? "highlight" : "font",
                    decorator: active ? "window-caption-active" : "window-caption"
                };
            }
        },

        'collapsepanel/button':{
            alias:'button',

            style:function (states) {
                return {
                    marginLeft:2,
                    icon:states.minimized ? qx.theme.simple.Image.URLS['arrow-down'] : qx.theme.simple.Image.URLS['arrow-up'],
                    padding:[ 1, 2 ],
                    cursor:states.disabled ? undefined : 'pointer'
                };
            }
        }

    }
});


qx.Theme.define('enre.theme.Indigo', {
    meta:{
        color:enre.theme.indigo.Color,
        decoration:enre.theme.indigo.Decoration,
        font:enre.theme.indigo.Font,
        icon:qx.theme.icon.Tango,
        appearance:enre.theme.indigo.Appearance
    }
});
