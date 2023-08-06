qx.Theme.define('enre.theme.simple.Color', {
    extend:qx.theme.simple.Color,

    colors:{
    }
});


qx.Theme.define('enre.theme.simple.Decoration', {
    extend:qx.theme.simple.Decoration,

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
            decorator:qx.ui.decoration.Single,

            style:{
                width:[0, 0, 1, 0],
                color:'window-border-inner'
            }
        },

        'collapsepanel-caption-minimized':{
            decorator:qx.ui.decoration.Single,

            style:{
                width:0
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
        },


        'panel-box':{
            decorator:[
                qx.ui.decoration.MSingleBorder,
                qx.ui.decoration.MBackgroundColor
            ],

            style:{
                width:1,
                color:'white-box-border',
                backgroundColor:'white'
            }
        }
    }
});


qx.Theme.define('enre.theme.simple.Font', {
    extend:qx.theme.simple.Font,

    fonts:{
        "grouplistitem":{
            size:14,
            family:["arial", "sans-serif"],
            bold:true,
            italic:true,
            decoration:["underline"]
        }
    }
});


qx.Theme.define('enre.theme.simple.Appearance', {
    extend:qx.theme.simple.Appearance,

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

        'panel':{
            style:function (states) {
                return {
                    backgroundColor:'background',
                    padding:[6, 9],
                    decorator:'panel-box'
                };
            }
        },

        'collapsepanel':{
            style:function (states) {
                return {
                    contentPadding:[ 4, 4, 4, 4 ],
                    backgroundColor:'background',
                    decorator:'collapsepanel'
                };
            }
        },

        'collapsepanel/pane':{},

        'collapsepanel/title':{
            style:function (states) {
                return {
                    cursor:'default',
                    font:'bold',
                    marginRight:20,
                    alignY:'middle'
                };
            }
        },

        'collapsepanel/captionbar':{
            style:function (states) {
                return {
                    backgroundColor:states.active ? 'light-background' : 'background-disabled',
                    padding:4,
                    font:'bold',
                    decorator:states.minimized ? 'collapsepanel-caption-minimized' : 'collapsepanel-caption'
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
        },

        'grouplistpanel':{
            alias:'scrollarea',

            style:function (states) {
                return {
                    padding:2,
                    backgroundColor:'light-background'
                }
            }
        },


        'grouplistpanel/item':{
            alias:'atom',

            style:function (states) {
                var padding = [3, 5, 3, 15];
                if (states.lead) {
                    padding = [ 2, 4 , 2, 14];
                }
                if (states.dragover) {
                    padding[2] -= 2;
                }

                var backgroundColor;
                if (states.selected) {
                    backgroundColor = 'background-selected'
                    if (states.disabled) {
                        backgroundColor += '-disabled';
                    }
                }
                return {
                    gap:4,
                    padding:padding,
                    cursor:'pointer',
                    backgroundColor:backgroundColor,
                    textColor:states.selected ? 'text-selected' : undefined,
                    decorator:states.lead ? "lead-item" : states.dragover ? 'dragover' : undefined
                };
            }
        },


        'grouplistpanel/groupitem':{
            alias:'atom',

            style:function (states) {
                return {
                    gap:4,
                    padding:[3, 5, 3, 5],
                    backgroundColor:'light-background',
                    textColor:'black',
                    font:'grouplistitem',
                    decorator:states.lead ? 'lead-item' : states.dragover ? 'dragover' : undefined
                };
            }
        },

        'relationpanel':{},

        'relationpanel/toolbar':{
            style:function (states) {
                return {padding:[0, 0, 2, 0]}
            }
        },

        'manytomanyrelation': {},

        'manytomanyrelation/buttonpanel': {
            style:function (states) {
                return {
                    padding: 10
                }
            }
        },

        'manytomanyrelation/label': {
            include : "label",
            alias : "label",

            style: function(states) {
                return {
                    font: 'bold',
                    padding:[3, 5, 3, 5]
                }
            }
        }
    }
});


qx.Theme.define('enre.theme.Simple', {
    meta:{
        color:enre.theme.simple.Color,
        decoration:enre.theme.simple.Decoration,
        font:enre.theme.simple.Font,
        icon:qx.theme.icon.Tango,
        appearance:enre.theme.simple.Appearance
    }
});