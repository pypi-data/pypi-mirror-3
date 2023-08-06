qx.Theme.define('enre.erp.theme.Color', {
    extend:enre.theme.simple.Color,

    colors:{
        'background':'#F6F6F6',

        'menubar-link':'#24B',
        'moduletab-unselected':'#DCDCDC',
        'moduletab-button-border':'#000000',
        'moduletab-button-text-select':'#FFFFFF',
        'moduletab-button-text-unselect':'#000000'
    }
});


qx.Theme.define('enre.erp.theme.Decoration', {
    extend:enre.theme.simple.Decoration,

    decorations:{

        "white-box":{
            decorator:[
                qx.ui.decoration.MSingleBorder,
                qx.ui.decoration.MBackgroundColor
            ],

            style:{
                width:1,
                color:"white-box-border",
                backgroundColor:"white"
            }
        },

        'moduletab-border':{
            decorator:qx.ui.decoration.Uniform,

            style:{
                width:[6, 0, 2, 0],
                color:'background-selected'
            }
        },

        'moduletab-page-button-top-bottom':{
            decorator:qx.ui.decoration.Single,

            style:{
                width:[0, 1],
                color:'moduletab-button-border'
            }
        },

        'moduletab-page-button-top-bottom-first':{
            include:'moduletab-page-button-top-bottom',

            style:{
                color:[
                    'moduletab-button-border', 'moduletab-button-border',
                    'moduletab-button-border', 'moduletab-unselected'
                ]
            }
        },

        'moduletab-page-button-top-bottom-last':{
            include:'moduletab-page-button-top-bottom',

            style:{
                color:[
                    'moduletab-button-border', 'moduletab-unselected',
                    'moduletab-button-border', 'moduletab-button-border'
                ]
            }
        },

        'moduletab-page-button-right-left':{
            decorator:qx.ui.decoration.Single,

            style:{
                width:[1, 0],
                color:'moduletab-button-border'
            }
        },

        'moduletab-page-button-right-left-first':{
            include:'moduletab-page-button-right-left',

            style:{
                color:[
                    'moduletab-unselected', 'moduletab-button-border',
                    'moduletab-button-border', 'moduletab-button-border'
                ]
            }
        },

        "moduletab-page-button-right-left-last":{
            include:'moduletab-page-button-right-left',

            style:{
                color:[
                    'moduletab-button-border', 'moduletab-button-border',
                    'moduletab-unselected', 'moduletab-button-border'
                ]
            }
        }
    }
});


qx.Theme.define('enre.erp.theme.Font', {
    extend:enre.theme.simple.Font,

    fonts:{
    }
});


qx.Theme.define('enre.erp.theme.Appearance', {
    extend:enre.theme.simple.Appearance,

    appearances:{

        "table":{
            style:function (states) {
                return {
                    backgroundColor:'white'
                }
            }
        },


        "groupbox":{},

        "groupbox/legend":{
            alias:"atom",

            style:function (states) {
                return {
                    textColor:states.invalid ? "invalid" : undefined,
                    padding:[0, 0, 0, 5],
                    margin:0,
                    font:"bold"
                };
            }
        },


        "groupbox/frame":{
            style:function (states) {
                return {
                    backgroundColor:"background",
                    padding:[6, 9],
                    margin:[10, 0, 0, 0],
                    decorator:"white-box"
                };
            }
        },

        "check-groupbox" : "groupbox",

        "check-groupbox/legend" :
        {
            alias : "checkbox",
            include : "checkbox",

            style: function(states) {
                return {
                    textColor : states.invalid ? "invalid" : undefined,
                    padding:[0, 0, 0, 5],
                    font: "bold"
                }
            }
        },

        "menu" :
        {
            style : function(states)
            {
                var result =
                {
                    backgroundColor : "white",
                    decorator : "main",
                    spacingX : 6,
                    spacingY : 1,
                    iconColumnWidth : 16,
                    arrowColumnWidth : 4,
                    padding : 1,
                    placementModeY : states.submenu || states.contextmenu ? "best-fit" : "keep-align"
                };

                if (states.submenu)
                {
                    result.position = "right-top";
                    result.offset = [-2, -3];
                }

                if (states.contextmenu) {
                    result.offset = 4;
                }

                return result;
            }
        },

        'appbar':{
            style:function (states) {
                return {
                    backgroundColor:'white',
                    padding:[2, 2]
                };
            }
        },

        'appbar-button':{
            style:function (states) {
                var decorator;
                var padding = [2, 6];
                if (!states.disabled) {
                    if (states.pressed) {
                        decorator = 'menubar-button-pressed';
                        padding = [1, 5, 2, 5];
                    } else if (states.hovered) {
                        decorator = 'menubar-button-hovered';
                        padding = [1, 5];
                    }
                }

                return {
                    padding:padding,
                    cursor:states.disabled ? undefined : 'pointer',
                    textColor:'menubar-link',
                    decorator:decorator
                };
            }
        },

        'moduletab': {
            alias: 'tabview',

            style: function(states) {
                return {
                    backgroundColor: 'white'
                }
            }
        },

        'moduletab/pane':{
            style:function (states) {
                return {
                    backgroundColor:'background',
                    decorator:'moduletab-border',
                    padding:0
                };
            }
        },

        'moduletab-page':'tabview-page',

        'moduletab-page/button':{
            style:function (states) {
                var decorator;
                var marginTop = 0, marginRight = 0, marginBottom = 0, marginLeft = 0;

                if (states.barTop || states.barBottom) {
                    var paddingTop = 5, paddingBottom = 5, paddingLeft = 9, paddingRight = 9;
                } else {
                    var paddingTop = 8, paddingBottom = 8, paddingLeft = 4, paddingRight = 4;
                }

                if (states.barTop || states.barBottom) {
                    decorator = 'moduletab-page-button-top-bottom';
                } else if (states.barRight || states.barLeft) {
                    decorator = 'moduletab-page-button-right-left';
                }

                if (states.checked) {
                    if (states.barTop) {
                        paddingLeft += 1;
                        paddingRight += 1;
                        paddingTop += 4;
                    } else if (states.barBottom) {
                        paddingLeft += 1;
                        paddingRight += 1;
                        paddingTop += 2;
                    } else if (states.barLeft) {
                        paddingTop += 1;
                        paddingBottom += 1;
                        paddingLeft += 4;
                        paddingRight += 2;
                    } else if (states.barRight) {
                        paddingTop += 1;
                        paddingBottom += 1;
                        paddingLeft += 2;
                        paddingRight += 4;
                    }
                } else {
                    if (states.barTop) {
                        marginBottom += 2;
                        marginTop += 4;
                    } else if (states.barBottom) {
                        marginBottom += 4;
                        marginTop += 2;
                    } else if (states.barLeft) {
                        marginRight += 2;
                        marginLeft += 4;
                    } else if (states.barRight) {
                        marginRight += 4;
                        marginLeft += 2;
                    }
                }

                if (states.firstTab && !states.checked) {
                    decorator += "-first";
                } else if (states.lastTab && !states.checked) {
                    decorator += "-last";
                }

                return {
                    zIndex:states.checked ? 10 : 5,
                    decorator:states.checked ? undefined : decorator,
                    backgroundColor:states.checked ? "background-selected" : 'moduletab-unselected',
                    //textColor : states.disabled ? states.checked ? "tabview-label-active-disabled" : "text-disabled" : 'black',
                    textColor:states.checked ? 'moduletab-button-text-select' : 'moduletab-button-text-unselect',
                    font:'bold',
                    cursor:states.disabled ? undefined : "pointer",
                    padding:[ paddingTop, paddingRight, paddingBottom, paddingLeft ],
                    margin:[ marginTop, marginRight, marginBottom, marginLeft ]
                };
            }
        }

    }
});


qx.Theme.define('enre.erp.theme.Theme', {
    meta:{
        color:enre.erp.theme.Color,
        decoration:enre.erp.theme.Decoration,
        font:enre.erp.theme.Font,
        icon:qx.theme.icon.Tango,
        appearance:enre.erp.theme.Appearance
    }
});


qx.Class.define('enre.erp.theme.Util', {

    statics:{
        _shift_etalon:'background-selected',

        _shift_names:[
            'background-selected-dark',
            'background-pane',
            'light-background',
            'tabview-unselected',
            'tabview-button-border',
            'table-focus-indicator',
            'table-row-background-focused-selected',
            'table-row-background-focused',
            'table-row-background-selected',
            'window-border',
            'window-border-inner',
            'border-main',
            'link'
        ],

        getColor:function (name) {
            return enre.erp.theme.Color.colors[name];
        },

        setColor:function (name, color) {
            enre.erp.theme.Color.colors[name] = color;
        },

        shiftColorByName:function (name, shift) {
            var rgb = this.getColor(name);
            if (typeof(rgb) == 'string') {
                rgb = qx.util.ColorUtil.stringToRgb(this.getColor(name));
            }
            var _rgb = [];
            for (var i = 0; i < 3; i++) {
                var c = rgb[i] + shift[i];
                if (c < 0) {
                    c = 0;
                } else if (c > 255) {
                    c = 255;
                }
                _rgb[i] = c;
            }
            this.setColor(name, qx.util.ColorUtil.rgbToHexString(_rgb));
        },

        shiftColor:function (color) {
            //alert(qx.theme.manager.Meta.getInstance().getTheme());
            var rgb = color;
            if (typeof(color) == 'string') {
                rgb = qx.util.ColorUtil.stringToRgb(color);
            }
            var _ergb = qx.util.ColorUtil.stringToRgb(this.getColor(this._shift_etalon));
            var _rgb = [rgb[0] - _ergb[0],
                rgb[1] - _ergb[1],
                rgb[2] - _ergb[2]];
            this.shiftColorByName(this._shift_etalon, _rgb);
            for (var i = 0; i < this._shift_names.length; i++) {
                this.shiftColorByName(this._shift_names[i], _rgb);
            }
            qx.theme.manager.Meta.getInstance().setTheme(enre.erp.theme.Theme);
        }
    }

});

qx.Class.define('enre.erp.Module', {
    extend:qx.ui.container.Composite,
    include:[qx.locale.MTranslation],

    construct:function (parent, layout) {
        this.base(arguments, layout);
        this.setPadding(2);
        this.setParent(parent);
        this._initControls();
    },

    properties:{
        parent:{nullable:false}
    },

    members:{
        _initControls:function () {

        }
    }

});

/**
 * APPLICATION BAR
 */
qx.Class.define('enre.erp.ui.appbar.Bar', {

    extend:qx.ui.menubar.MenuBar,

    properties:{

        appearance:{
            refine:true,
            init:"appbar"
        }

    }

});


qx.Class.define('enre.erp.ui.menu.BrowserMenu', {
    extend:qx.ui.menu.Menu,

    construct:function (url) {
        this.base(arguments);
        if (url) {
            this.setUrl(url);
        }
        var winButton = new qx.ui.menu.Button('Open in new window');
        winButton.addListener('execute', function (e) {
            if (!this.getUrl()) {
                return
            }
            window.open(this.getUrl(), '_blank');
        }, this);
        this.add(winButton);
    },

    properties:{
        url:{
            nullable:true,
            check:'String'
        }
    }

});


qx.Class.define('enre.erp.ui.appbar.Button', {

    extend:qx.ui.menubar.Button,

    construct:function (label, url, icon, command, menu) {
        this.base(arguments, label, icon, command, menu);
        if (url) {
            this.setUrl(url);
        }
        this.addListener('execute', this._onExecute, this);
    },

    properties:{
        url:{
            nullable:true,
            apply:'_applyUrl'
        },

        appearance:{
            refine:true,
            init:"appbar-button"
        }
    },

    members:{

        _applyUrl:function (url, old_url) {
            this.setContextMenu(new enre.erp.ui.menu.BrowserMenu(url));
        },

        _onExecute:function (e) {
            if (this.getUrl()) {
                document.location.href = this.getUrl();
            }
        }

    }

});


qx.Class.define('enre.erp.ui.moduletab.ModuleTab', {
    extend:qx.ui.tabview.TabView,

    properties:{
        appearance:{
            refine:true,
            init:'moduletab'
        }
    }

});


qx.Class.define('enre.erp.ui.moduletab.Page', {
    extend:qx.ui.tabview.Page,

    construct:function (label, url, icon) {
        this.base(arguments, label, icon);
        if (url) {
            this.setUrl(url);
        }
    },

    properties:{

        appearance:{
            refine:true,
            init:'moduletab-page'
        },

        url:{
            nullable:true,
            apply:'_applyUrl'
        }
    },

    members:{
        _applyUrl:function (url, old_url) {
            this.getButton().setContextMenu(new enre.erp.ui.menu.BrowserMenu(url));
        }
    }

});
