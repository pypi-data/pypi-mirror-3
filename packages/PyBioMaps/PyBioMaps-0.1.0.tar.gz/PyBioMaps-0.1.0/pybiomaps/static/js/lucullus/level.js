Ext.namespace('Lucullus.gui.level')

Lucullus.gui.level.App = Ext.extend(Ext.util.Observable, {
    constructor: function(config) {
        config = config || {}
        Ext.applyIf(config, {
            api: null,
            level: 1750,
            data_color: '#ffa554'
        })
        this.api = config.api
        this.config = config
        // Call our superclass constructor to complete construction process.
        Lucullus.gui.level.App.superclass.constructor.call(this, config)
    },
    init: function() {
        Ext.MessageBox.wait('Loading Application...')
        this.res = this.api.create('LevelResource');
        this.res.on('error', function(self, data) {
            Ext.MessageBox.alert(data.error, data.detail)
        })
        this.res.query('setup', {level: this.config.level, data_color: this.config.data_color})
        // prepare ruler views
        this.ruler_h = api.create('RulerView');
        this.ruler_v = api.create('RulerView');
        this.panel = new Lucullus.maps.TwinMapPanel({
            slavePosition: 'top',
            slaveScaleY: 0,
            slave: {view: this.ruler_h, height: 15, channel:'top', bodyStyle:{padding: '0 15px'}},
            master: {
                xtype: 'twinmap',
                slavePosition: 'bottom',
                slaveScaleY: 0,
                slave: {view: this.ruler_h, height: 15, channel:'bottom', bodyStyle:{padding: '0 15px'}},
                master: {
                    xtype: 'twinmap',
                    slavePosition: 'left',
                    slaveScaleX: 0,
                    slave: {view: this.ruler_v, width: 15, channel:'left'},
                    master: {
                        xtype: 'twinmap',
                        slavePosition: 'right',
                        slaveScaleX: 0,
                        slave: {view: this.ruler_v, width: 15, channel:'right'},
                        master: {view: this.res}
                    }
                }
            }
        });
        this.panel.initCtrl()
        var self = this
        this.res.wait(function(){
            Ext.MessageBox.hide()
            self.ruler_h.query('setup', {
                scale: -self.res.state.ppm_resolution[0],
                nullvalue: self.res.state.ppm_max[0]
            })
            self.ruler_h.query('setup', {
                scale: self.res.state.ppm_resolution[1],
                nullvalue: self.res.state.ppm_min[1]
            })
        })
    },
    load: function(data, procs, proc2s, poi) {
        if(!this.res) this.init()
        var config = {
            data: data,
            procs: procs,
            proc2s: proc2s
        }
        if(poi) config.poi = getVars.poi
        Ext.MessageBox.wait('Loading Data...')
        this.res.query('load_local', config)
        this.res.wait(function(){Ext.MessageBox.hide()})
    }
})
