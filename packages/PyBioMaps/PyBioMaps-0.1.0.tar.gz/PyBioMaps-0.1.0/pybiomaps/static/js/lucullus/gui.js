Ext.namespace('Lucullus.gui')

Lucullus.gui.AppWindow = function(options) {
    /* This creates/opens a window holding multiple workspaces  */
    this.gui = {}
    this.apps = []
    var self = this
    Ext.apply(this, options)

    this.gui.root = new Ext.Window({
        title: 'Lucullus Workspace',
        closable: true,
        maximizable: true,
        hidden: true,
        width: 600,
        height: 350,
        //border:false,
        plain: true,
        layout: 'fit',
        tbar: {xtype:'toolbar'},
        bbar: {xtype:'toolbar'}
    });

    this.gui.toolbar = this.gui.root.getTopToolbar()
    this.gui.toolbar.add(
        new Ext.Button({
            text: 'New',
            icon: '/img/icons/16x16/actions/document-new.png',
            menu: new Ext.menu.Menu({items:[
                {
                    text: 'Open URL...',
                    handler: this.do_load, scope: this,
                    icon: '/img/icons/16x16/categories/applications-internet.png'
                }, {
                    text: 'Load test tree',
                    handler: function(){
                        var a = new Lucullus.gui.NewickApp({
                            api: self.api, name: 'TestApp', source:'http://fab8:8080/test/test.phb'
                        })
                        self.addApp(a)
                    },
                    icon: '/img/icons/16x16/categories/applications-internet.png'
                }, {
                    text: 'Load test sequence',
                    handler: function(){
                        var a = new Lucullus.gui.FastaApp({
                            api: self.api, name: 'TestApp', source:'http://fab8:8080/test/myosin.seq'
                        })
                        self.addApp(a)
                    },
                    icon: '/img/icons/16x16/categories/applications-internet.png'
                }, {
                    text: 'Open file...',
                    handler: this.do_load, scope: this,
                    disabled: true,
                    icon: '/img/icons/16x16/actions/document-open.png'
                }, {
                    text: 'Export',
                    handler: this.do_export, scope: this,
                    disabled: true,
                    icon: '/img/icons/16x16/actions/document-save.png'
                } 
            ]})
        })
    )
    this.gui.toolbar.add('-')
    this.gui.statusbar = this.gui.root.getBottomToolbar()

    /* Tab area */
    this.gui.tabpanel = new Ext.TabPanel({
        resizeTabs: true, // turn on tab resizing
        minTabWidth: 150,
        tabWidth: 200,
        enableTabScroll: true, //<-- displays a scroll for the tabs
        border: false,
    });
    this.gui.root.add(this.gui.tabpanel)
}

Lucullus.gui.AppWindow.prototype.show = function() {
    if(this.gui.root.hidden) this.gui.root.show()
}

Lucullus.gui.AppWindow.prototype.hide = function() {
    if(!this.gui.root.hidden) this.gui.root.hide()
}

Lucullus.gui.AppWindow.prototype.close = function() {
    this.hide()
    this.gui.root.close()
    this.gui.root.destroy()
}

Lucullus.gui.AppWindow.prototype.do_load = function() {
    var self = this
    new Lucullus.gui.ImportWindow({
        api: this.api,
        app_window: this
    });
}

/**
     * Adds a new app panel to the window.
     * @param {Object}   app The application object to add.
     
     The app object must define a panel object in app.gui.root and may define
     toolbar objects in app.gui.toolbar and app.gui.statusbar. These toolbars
     get merged with the bars in the main wondow.
     */

Lucullus.gui.AppWindow.prototype.addApp = function(app) {
    // Add new app to app list
    var id = app.gui.root.getId()
    this.apps[id] = app // TODO: Was passiert bei doppelt eingefuegten apps?
    this.gui.tabpanel.add(app.gui.root)

    /* This function adds $items to $toolbar and listens on $root events
       to hide or remove them. This way we can dynamically change the
       tool- and statusbar on each tab-change or tab-close. */
    function mergebars(container, toolbar, root) {
        toolbar.add(container)
        root.on({
            activate: function(){
                container.show()
                toolbar.doLayout()
            },
            deactivate: function(){
                container.hide()
                toolbar.doLayout()
            },
            close: function(){
                container.hide()
                toolbar.remove(container)
                toolbar.doLayout()
            },
        })
    }
    
    // Merge toolbars (if present)
    if(app.gui.toolbar && app.gui.toolbar.items &&
       app.gui.toolbar.items.getCount()) {
        mergebars(app.gui.toolbar, this.gui.toolbar, app.gui.root)
    }
    
    // Merge statusbars  (if present)
    if(app.gui.statusbar && app.gui.statusbar.items &&
       app.gui.statusbar.items.getCount()) {
        mergebars(app.gui.statusbar, this.gui.statusbar, app.gui.root)
    }

    // Remove app on a close event (tab is closed)
    app.gui.root.on('close', function(){
        this.apps.remove(id)
    }, this)
    
    // Install and activate new tab
    this.gui.tabpanel.activate(app.gui.root)
}










Lucullus.gui.ImportWindow = function(options) {
    this.options = {onsubmit: alert}
    jQuery.extend(this.options, options)
    var self = this
    this.gui = {}

    var dataType = {
        xtype: 'radiogroup',
        fieldLabel: 'Type',
        anchor: '95%',
        items: [
            {boxLabel: 'Sequence Alignment', name: 'type',
             inputValue: 'SeqApp', checked: true},
            {boxLabel: 'Newick Tree', name: 'type',
             inputValue: 'NewickApp'},
        ]
    }

    var nameField = {
        xtype: 'textfield',
        fieldLabel: 'Project Name',
        name: 'name',
        emptyText: 'Unnamed'
    }

    var urlField = {
        xtype: 'textfield',
        emptyText: 'http://',
        value: 'http://',
        fieldLabel: 'URL',
        name: 'url',
    }

    var uploadField = {
        xtype: 'fileuploadfield',
        emptyText: 'Select data file',
        name: 'upload',
        fieldLabel: 'Disk'
    };

    var hiddenField = {
        xtype: 'hidden',
        value: options.apikey,
        name: 'apikey'
    };

    /* Layout hacky */
    this.gui.form = new Ext.FormPanel({
        bodyStyle: 'padding:0 10px 0;',
        frame: true,
        fileUpload: true,
        baseParams: {'_extjs_frame': 1,
                    'apikey': this.options.api.key},
        method: 'POST',
        labelWidth: 100,
        border: false,
        plain: true,
        items: [{
            xtype: 'fieldset',
            title: 'Data Settings',
            items: [dataType, nameField]
        },{
            xtype: 'fieldset',
            title: 'Data Source (choose one)',
            defaults: {
                anchor: '95%',
            },
            items: [urlField, uploadField]
        }]
    });

    this.gui.root = new Ext.Window({
        title: 'Data Import Form',
        modal: true,
        width: 500,
        minWidth: 300,
        border: false,
        //layout: 'fit',
        items: [this.gui.form],
        buttons: [{text: 'Load'}, {text: 'Cancel'}]
    });

    this.gui.root.show()
    this.gui.root.buttons[0].on("click", this.onClick, this)
    this.gui.root.buttons[1].on("click", this.onAbort, this)

    /* This hack allows submitting the form with enter key. It works by adding
       an invisible submit button to the form and catch its click event.
    */
    var enter_hack = this.gui.form.getForm().el.createChild({
        tag: 'input',
        type: 'submit',
        style: { position: 'absolute', top: '-10000px', left: '-10000px' },
        tabIndex: -1 // Exclude this button from tab-focus
    });
    enter_hack.on("click", this.onClick, this);
}

Lucullus.gui.ImportWindow.prototype.onClick = function() {
    this.gui.form.getForm().submit({
        url: this.optons.api.server + '/create',
        waitMsg: 'Uploading your data ...',
        success: function(fp, o) {
            msg('Success', 'Processed file "'+o.result.file+'" on the server');
        },
        error: function(fp, o) {
            msg('Success', 'Processed file "'+o.result.file+'" on the server');
        }
    }, this);
    return false
}

Lucullus.gui.ImportWindow.prototype.onAbort = function() {
    this.gui.root.destroy()
}








/** Base Application suitable to be used by the AppWindow class.
    @class Lucullus.gui.BaseApp
    This class is used as a base class for all Lucllus application plugins.
    It creates an Ext.Panel in this.gui.root and relays most of ths events.
*/

Lucullus.gui.BaseApp = Ext.extend(Ext.util.Observable, {
    constructor: function(config){
        // Call our superclass constructor to complete construction process.
        Lucullus.gui.BaseApp.superclass.constructor.call(this)
        // Configuration
        this.conf = config
        // Apply defaults
        Ext.applyIf(this.conf, {
            name: "Unnamed",
            type: "BaseApp"
        })

        // Create basic gui elements
        this.gui = {}
        this.gui.toolbar = new Ext.Container({layout: 'toolbar'})
        this.gui.statusbar = new Ext.Container({layout: 'toolbar'})
        this.gui.status = new Ext.Toolbar.TextItem({text:'Loading...'})
        this.gui.statusbar.add(this.gui.status)
        this.gui.root = new Ext.Panel({
            title: this.conf.name + " (" + this.conf.type + ")",
            iconCls: 'icon-document',
            closable: true,
            layout: 'fit',
            border: false,
        })
        
        // Namespace for resources
        this.res = {}
        this.maps = {}
        this.controls = {}

        /* Relay common events from this.gui.root to this.
           This allows others (e.g. the main window) to register event
           listeners to this object instead of this.gui.root for important
           events. */
        this.relayEvents(this.gui.root, [
            'activate', 'deactivate', 'show', 'hide', 'close', 'resize', 'render', 'destroy', 'enable','disable'
        ])

        // Learn some custom events
        this.addEvents(
            "appFailed", // Fired on a critical non-reversable error
            "appReady" // Fired as soon as the app is usable
        );
        
        // Add callbacks to common events
        this.on('appFailed', this.gui.root.disable, this.gui.root)
    },
    destroy: function() {
        this.gui.toolbar.destroy()
        this.gui.root.destroy()
        Ext.iterate(this.maps, function(map){
            this.maps[map].destroy()
        }, this)
    },
    setStatus: function(text) {
        this.gui.status.setText(text)
    }
});










Lucullus.gui.FastaApp = Ext.extend(Lucullus.gui.BaseApp, {
    constructor: function(config){
        // Initialize BaseApp
        var self = this
        config.type = 'Fasta'
        Lucullus.gui.FastaApp.superclass.constructor.call(this, config)

        // Apply defaults
        Ext.applyIf(this.conf, {})

        this.prepare_maps();
        this.prepare_table();
        this.prepare_toolbar();
        this.gui.root.add(this.gui.table)

        // Create data structures client and server side
        this.res.seq = this.conf.api.create('SequenceResource')
        this.maps.seq.setView(this.res.seq)
        this.res.seq.on('create', function(res) {
            this.res.index = this.conf.api.create('IndexView', {'source': res.id})
            this.maps.index.setView(this.res.index)
        }, this)
        /* Update Index on Sequence change */
        this.res.seq.on('change', function(ref, state) {
            this.res.index.query('setup', {'source': ref.id })
        }, this)

        // Create data structures client and server side
        this.res.refseq = this.conf.api.create('SequenceResource')
        this.maps.refseq.setView(this.res.refseq)
        this.res.refseq.on('create', function(res) {
            this.res.refidx = this.conf.api.create('IndexView', {'source': res.id})
            this.maps.refidx.setView(this.res.refidx)
        }, this)
        /* Update Index on Sequence change */
        this.res.refseq.on('change', function(ref, state) {
            this.res.refidx.query('setup', {'source': ref.id })
        }, this)

        if(this.conf.source) this.load(this.conf.source)
        this.update()
    },
    prepare_maps: function() {
        if(this.maps.seq) return

        /* The seq map displays the data (middle-middle). */
        this.maps.seq = new Lucullus.maps.MapPanel({
            border: false,
            controls: {scaleX: 2,
                       scaleY: 2}
        })

        /* The Index is displayed middle-left */
        this.maps.index = new Lucullus.maps.MapPanel({
            border: false,
            split: true,
            width: 100
        })

        this.maps.refseq = new Lucullus.maps.MapPanel({
            border: false
        })

        this.maps.refidx = new Lucullus.maps.MapPanel({
            border: false,
            width: 100
        })

        this.controls.hslider = new Ext.Slider({maxValue: 100*1000,
                                                animate: false})
        this.controls.vslider = new Ext.Slider({maxValue: 100*1000,
                                                animate: false,
                                                vertical: true,
                                                value:    100*1000})

        // Move main map on slider change
        this.controls.hslider.on("change", function(foo, value) {
            var hv = this.controls.hslider.getValue() / 100000
            var vv = 1 - this.controls.vslider.getValue() / 100000
            var p = this.maps.seq.getPosByScroll(hv, vv)
            this.maps.seq.setPos(p[0], p[1])
        }, this)

        // Move main map on slider change
        this.controls.vslider.on("change", function(foo, value) {
            var hv = this.controls.hslider.getValue() / 100000
            var vv = 1 - this.controls.vslider.getValue() / 100000
            var p = this.maps.seq.getPosByScroll(hv, vv)
            this.maps.seq.setPos(p[0], p[1])
        }, this)

        // Zoom all maps on main map zoom event
        this.maps.seq.on('mapZoom', function(level) {
            this.maps.index.setZoom(level)
            this.maps.refseq.setZoom(level)
            this.maps.refidx.setZoom(level)
            this.update()
        }, this)

        // Move all maps on main map move event (and update slider)
        this.maps.seq.on('mapMoved', function(dx, dy) {
            var p = this.maps.seq.getPos()
            this.maps.index.setPos(0, p[1])
            this.maps.refseq.setPos(p[0], 0)
            this.maps.refidx.setPos(0, p[1])
            // Sync sliders but do not fire events to prevent recursion.
            var pos = this.maps.seq.getScrollPos();
            this.controls.hslider.suspendEvents()
            this.controls.hslider.setValue(100*1000*pos[0])
            this.controls.hslider.resumeEvents()
            this.controls.vslider.suspendEvents()
            this.controls.vslider.setValue(100*1000*(1-pos[1]))
            this.controls.vslider.resumeEvents()
        }, this)

        this.maps.index.on('mapDClick', function(x, y) {
            var h = this.maps.seq.getSize()[1]
            var rows = this.res.seq.state.rows
            var index = Math.floor(y / (h / rows))
            this.setSelection(index)
        }, this)
    },
    prepare_table: function() {
        if(this.gui.table) return
        this.prepare_maps()
        this.gui.table = new Ext.Panel({
            layout: 'table',
            region: 'center',
            width: 'auto',
            border: false,
            layoutConfig: {
                columns: 3,
                tableAttrs: {
                    style: {
                        width: '100%',
                        height: '100%'
                    }
                }
            }
        });

        this.gui.table.add({'html':'logo'});
        this.gui.table.add({'html':'ruler'});
        this.gui.table.add({'html':'x'});
        this.gui.table.add(this.maps.refidx);
        this.gui.table.add(this.maps.refseq);
        this.gui.table.add({'html':'x'});
        this.gui.table.add(this.maps.index);
        this.gui.table.add(this.maps.seq);
        this.gui.table.add(this.controls.vslider);
        this.gui.table.add({'html':'y'});
        this.gui.table.add(this.controls.hslider);
        this.gui.table.add({'html':'z'});
        this.gui.table.on('resize', function() {this.update()}, this)
    },
    prepare_toolbar: function() {
        if(this.gui.toolbar.items) return
        this.prepare_maps()
        this.gui.toolbar.add({
            tooltip: 'Zoom in',
            xtype: 'button',
            icon: '/img/icons/16x16/actions/zoom-in.png',
            handler: function() {
                this.maps.seq.setZoom(this.maps.seq.getZoom() + 1)
            },
            scope: this
        })
        this.gui.toolbar.add({
            tooltip: 'Zoom 1:1',
            xtype: 'button',
            icon: '/img/icons/16x16/actions/zoom-original.png',
            handler: function() {
                this.maps.seq.setZoom(0)
            },
            scope: this
        })
        this.gui.toolbar.add({
            tooltip: 'Zoom out',
            xtype: 'button',
            icon: '/img/icons/16x16/actions/zoom-out.png',
            handler: function() {
                this.maps.seq.setZoom(this.maps.seq.getZoom() + 1)
            },
            scope: this
        })
        this.gui.toolbar.add({
            tooltip: 'Search for a sequence.',
            xtype: 'button',
            icon: '/img/icons/16x16/actions/edit-find.png',
            handler: function() {
                var callback = function(button, text) {
                    if(button == 'ok') {
                        this.jumpTo(text)
                    }
                }
                Ext.MessageBox.prompt('Search', 'Enter a sequence name:', callback, this);
            },
            scope: this
        })
        this.gui.refButton = this.gui.toolbar.add({
            tooltip: 'Add a sequence to the reference view.',
            xtype: 'button',
            disabled: true,
            icon: '/img/icons/16x16/categories/applications-accessories.png',
            handler: this.setRefSeqs,
            scope: this
        })
    },
    update: function() {
        // Update table dimensions
        this.maps.refseq.updateMap()
        var table = this.gui.table
        el = table.getEl()
        if(!el) return
        var tw = el.getComputedWidth()
        var th = el.getComputedHeight()
        var iw = 100 // Index width
        var rh = 20 // Ruler height
        var refh = this.maps.refseq.getSize()[1] // Reference height
        x = this.maps.refseq
        var ss = 20 // Scrollbar size
        var w = [iw, tw-iw-ss, ss]
        var h = [rh, refh, th-rh-refh-ss, ss]
        for(var row=0; row<h.length; row++) {
            for(var col=0; col<w.length; col++) {
                table.items.items[row*w.length+col].setSize({
                    width: w[col],
                    height: h[row]
                })
            }
        }
        // Update maps
        this.maps.seq.updateMap()
        this.maps.index.updateMap()
        this.maps.refseq.updateMap()
        this.maps.refidx.updateMap()
    },
    load: function(source) {
        var self = this
        Ext.MessageBox.wait('Loading...')
        this.res.seq.wait(function(){
            var seq_update = this.res.seq.query('load', {'source': source})
            seq_update.on('answer', function() {
                var index_update = self.res.index.query('setup', {'source': this.res.seq.id })
                index_update.on('answer', function() {
                    self.update()
                    Ext.MessageBox.hide()
                    self.setStatus('Alignment loaded. Doubleclick on a sequence name to select it.')
                }, this)
                index_update.on('error', function(self, data) {
                    Ext.MessageBox.alert("Index failed: " + data.error)
                }, this)
            }, this)
            seq_update.on('error', function(self, data) {
                Ext.MessageBox.alert("Upload failed: " + data.error)
            }, this)
        }, this)

    },
    jumpTo: function(seq, offset) {
        Ext.MessageBox.wait('Searching, please wait...')
        var query = this.maps.seq.view.query('search', {'query':seq, 'limit':100})
        offset = offset | 0
        query.on('result', function(res, result) {
            Ext.MessageBox.hide()
            if(!result.matches){
                Ext.MessageBox.alert('Search failed.', 'Cold not find a sequence with name: '+ seq);
            } else if (offset >= result.matches.length) {
                Ext.MessageBox.alert('Search failed.', 'Not enough matches for: '+ seq);
            } else {
                var index = result.matches[offset].index
                var height_per_index = this.maps.seq.getSize()[1] / result.count
                var target = index * height_per_index
                //target -= self.maps.seq.getWindowSize()[1] / 2
                this.maps.seq.setPos(this.maps.seq.getPos()[0], Math.floor(target))
            }
        }, this)
        query.on('error', function(res, data) {
            Ext.MessageBox.alert("Search failed: " + data.error)
        })
    },
    setRefSeqs: function() {
        /* Add the selected sequence to the reference alignment. */
        Ext.MessageBox.wait('Loading reference sequence, please wait...')
        var index = this.selected
        if(index === null) {
            Ext.MessageBox.alert('Error', 'You need to select a sequence first (doubleclick).');
            return
        }
        var query = this.maps.refseq.view.query('copy', {
            'source': this.maps.seq.view.id, 'index':index})
        query.on('answer', function(res, data) {
            this.update()
            Ext.MessageBox.hide()
        }, this)
    }, setSelection: function(index) {
        this.selected = index
        this.setStatus('Selected: '+ this.selected)
        this.gui.refButton.setDisabled(false)
    }
});










Lucullus.gui.NewickApp = function(options) {
    this.options = {
      api: Lucullus.current,
      fontsize: 10,
      source: '/test/test.seq',
      name: 'Unnamed Tree'
    }
    jQuery.extend(this.options, options)
    var self = this
    this.api = this.options.api
    this.data = {}
    this.gui = {}

    this.gui.toolbar = new Ext.Toolbar({
        items:[{text: this.options.name}]
    });

    this.gui.root = new Ext.Panel({
        title: self.options.name + " (Newick Tree)",
        iconCls: 'icon-document',
        closable: true,
        layout: 'border',
        border: false,
    })
    
    this.gui.root.on('activate', function(){
        self.sync_size()
    })
    this.gui.root.on('destroy', function(){
        for ( var i in this.gui.toolbar_items ) {
            if(this.gui.toolbar_items[i].destroy)
                this.gui.toolbar_items[i].destroy();
        }
    }, this)


    /* Toolbar area */

    this.gui.index_panel = new Ext.Panel({
        //title: 'Index',
        border: false,
        region: 'west',
        split: true,
        disabled: true,
        width: 100,
    })
    this.gui.root.add(this.gui.index_panel);

    this.gui.map_panel = new Ext.Panel({
        //title: 'Phylogenetic Tree',
        region: 'center',
        disabled: true,
        border: false
    })
    this.gui.root.add(this.gui.map_panel);

    this.gui.ruler_panel = new Ext.Panel({
        //title: 'Phylogenetic Tree',
        region: 'north',
        collapsible: false,
        border: false,
        height: 25
    })
    //this.gui.root.add(this.gui.ruler_panel);


    // Create data structures client and server side
    this.data.tree = this.api.create('NewickResource', {
        fontsize: this.options.fontsize
    })
    this.data.index = this.api.create('IndexView', {
        fontsize: this.options.fontsize
    })

    // Create a mouse-event hub to syncronize the different panels
    this.ml = new Lucullus.MoveListenerFactory()

    // Create ViewMaps as soon as the map and index panel doms are available
    this.gui.map_panel.on('render', function(){
        if(!self.gui.map_view) {
            self.gui.map_view = new Lucullus.ViewMap(
                          self.gui.map_panel.body.dom,
                          self.data.tree)
            // The whole map is a mouse control
            self.ml.addMap(self.gui.map_view,1,1)
            self.ml.addLinear(self.gui.map_view.node,1,1)
        }
    })

    this.gui.index_panel.on('render', function(){
        if(!self.gui.index_view) {
            self.gui.index_view = new Lucullus.ViewMap(
                          self.gui.index_panel.body.dom,
                          self.data.index)
            // The whole index map is a mouse control, but limited to the y axis
            self.ml.addMap(self.gui.index_view, 0, 1)
            self.ml.addJoystick(self.gui.index_view.node, 0, 1)
        }
    })

    // Resize the ViewMaps along wih the panel 
    this.gui.map_panel.on('resize', this.sync_size, this)
    this.gui.index_panel.on('resize', this.sync_size, this)
    this.gui.map_panel.on('enable', this.sync_size, this)
    this.gui.index_panel.on('enable', this.sync_size, this)

    // As soon as the initialisation finishes, configure the index map
    this.data.tree.wait(function(){
        var upreq = self.data.tree.load({'source':self.options.source})
        upreq.wait(function(){
            self.data.index.wait(function(){
                if(upreq.result.keys) {
                    self.gui.root.items.items[1].enable()
                    self.sync_size()
                    self.data.index.setup({
                        'keys': upreq.result.keys
                    }).wait(function(){
                        self.gui.root.items.items[0].enable()
                        self.sync_size()
                    })
                    return
                }
                if(upreq.error) {
                    alert("Upload failed: " + upreq.result.detail)
                }
                self.close()
            })
        })
    })
}

Lucullus.gui.NewickApp.prototype.sync_size = function() {
    if(this.gui.map_view) {
        var h = this.gui.map_panel.body.getHeight(true)
        var w = this.gui.map_panel.getWidth(true)
        this.gui.map_view.resize(w, h)
    }
    if(this.gui.index_view) {
        var h = this.gui.index_panel.body.getHeight(true)
        var w = this.gui.index_panel.getWidth(true)
        this.gui.index_view.resize(w, h)
    }
}

Lucullus.gui.NewickApp.prototype.close = function() {
    this.gui.root.destroy()
}















Lucullus.gui.FastaApp = Ext.extend(Lucullus.gui.BaseApp, {
    constructor: function(config){
        config.type = 'Fasta'
        Lucullus.gui.FastaApp.superclass.constructor.call(this, config)
        // Apply defaults
        Ext.applyIf(this.conf, {})

        // Prepare resources
        this.res = {}
        this.res.seq = this.conf.api.create('SequenceResource')
        this.res.ref = this.conf.api.create('SequenceResource')
        this.res.seqi = this.conf.api.create('IndexView')
        this.res.refi = this.conf.api.create('IndexView')
        this.res.ruler = this.conf.api.create('RulerView', {height:20})

        // Auto-Sync index with sequence for reference and main sequence
        this.res.seq.on('change', function(res) {
          this.res.seqi.query('setup', {source: res.id})
        }, this)
        this.res.ref.on('change', function(res) {
          this.res.refi.query('setup', {source: res.id})
        }, this)

        this.prepareMaps()

        // Listen to DClicks to select sequences
        this.map.seqi.on('ctrlDClick', function(x, y) {
            var h = this.map.seq.getSize()[1]
            var rows = this.res.seq.state.rows
            var index = Math.floor(y / (h / rows))
            this.setSelection(index)
        }, this)

        if(this.conf.source) this.load(this.conf.source)
        this.map.tall.initCtrl()
    },
    prepareMaps: function() {
        /* This app combines up to 6 (2x3) MapPanels into one, all
            synchronized and fully managed. I could not find an 'easy' way to
            do this, sorry.
            
            The MapPanels are organized as a tree of master/slave pairs:
            
            slave:
                slave:          Dummy Map               1)
                master:         Ruler                   2)
            master:
                slave:
                    slave:      Reference Index         3)
                    master:     Reference Sequence      4)
                master:
                    slave:      Main Index              5)
                    master:     Main Sequence           6)
            
            100px *
            +---+---+
            | 1 | 2 | 20px
            +---+---+
            | 3 | 4 | 15px
            +---+---+
            | 5 | 6 | *
            +---+---+
            
        */

        if(this.map) return

        // Prepare MapPanels and preconfigure size and scaling.
        this.map = {}
        this.map.dummy = new Ext.Panel({html:'x', width:100})
        this.map.ruler = new Lucullus.maps.MapPanel({
          flex:1, view: this.res.ruler, controlConfig: {scaleX: 1, scaleY: 0},
          autoclip: false
        })
        this.map.ref = new Lucullus.maps.MapPanel({
          flex: 1, view: this.res.ref, controlConfig: {scaleX: 1, scaleY: 0},
          autoclip: false
        })
        this.map.refi = new Lucullus.maps.MapPanel({
          width: 100, view: this.res.refi, controlConfig: {scaleX: 0, scaleY: 0},
          autoclip: false
        })
        this.map.seq = new Lucullus.maps.MapPanel({
          flex: 1, view: this.res.seq
        })
        this.map.seqi = new Lucullus.maps.MapPanel({
          width: 100, view: this.res.seqi, controlConfig: {scaleX: 0, scaleY: 1},
          autoclip: false
        })

        // Group sequence maps with their index (and ruler with dummy)
        this.map.trul = new Lucullus.maps.TwinMapPanel({
            slaveMap: this.map.dummy, masterMap: this.map.ruler, height:20
        })
        this.map.tref = new Lucullus.maps.TwinMapPanel({
            slaveMap: this.map.refi, masterMap: this.map.ref,
            slaveScaleX: 0, height: 0
        })
        this.map.tseq = new Lucullus.maps.TwinMapPanel({
            slaveMap: this.map.seqi, masterMap: this.map.seq,
            slaveScaleX: 0, flex: 1
        })

        // Combine bots reference and main sequence into a twin map
        this.map.tboth = new Lucullus.maps.TwinMapPanel({
            slaveMap: this.map.tref, masterMap: this.map.tseq,
            slavePosition: 'top', flex: 1, slaveScaleY: 0
        })

        // Combine the ruler and the combined sequence maps
        this.map.tall = new Lucullus.maps.TwinMapPanel({
            slaveMap: this.map.trul, masterMap: this.map.tboth,
            slavePosition: 'top', slaveScaleY: 0
        })

        this.gui.root.add(this.map.tall)
    },
    load: function(source) {
        // Load a source from an url
        var self = this
        Ext.MessageBox.wait('Loading...')
        var tr = this.res.seq.query('load', {'source': source})
        tr.on('answer', function(){
            Ext.MessageBox.hide()
            self.setStatus('Alignment loaded. Doubleclick on a sequence name to select it.')
        })
        tr.on('error', function(self, data){
            Ext.MessageBox.alert("Upload failed: " + data.error)
        })
    },
    setRefSeqs: function() {
        /* Add the selected sequence to the reference alignment. */
        Ext.MessageBox.wait('Loading reference sequence, please wait...')
        var index = this.selected
        if(index === null) {
            Ext.MessageBox.alert('Error', 'You need to select a sequence first (doubleclick).');
            return
        }
        var query = this.maps.refseq.view.query('copy', {
            'source': this.maps.seq.view.id, 'index':index})
        query.on('answer', function(res, data) {
            this.map.tboth.resizeChild(15)
            Ext.MessageBox.hide()
        }, this)
    }, setSelection: function(index) {
        this.selected = index
        this.setStatus('Selected: '+ this.selected)
        this.gui.refButton.setDisabled(false)
    }
})
