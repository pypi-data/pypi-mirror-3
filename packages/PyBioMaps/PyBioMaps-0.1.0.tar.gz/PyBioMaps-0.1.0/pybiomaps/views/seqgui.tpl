<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>

    <script src="./jquery/jquery-1.3.2.min.js" type="text/javascript"></script>
    <script src="./jquery/jquery.query.js" type="text/javascript"></script>
    <script src="./js/jquery.selector.js" type="text/javascript"></script>
    <link type="text/css" href="./css/main.css" rel="stylesheet" />
    <link type="text/css" href="./css/lucullus.css" rel="stylesheet" />

    % extjs = '/js/ext-3.3.1'
    <link rel="stylesheet" type="text/css" href="{{extjs}}/resources/css/ext-all.css" />
    <script type="text/javascript" src="{{extjs}}/adapter/ext/ext-base-debug.js"></script>
    <script type="text/javascript" src="{{extjs}}/ext-all-debug.js"></script>

    % extui = '/js/ext.ui'
    <script type="text/javascript" src="{{extui}}/FileUploadField.js"></script>
    <link   type="text/css"       href="{{extui}}/FileUploadField.css" rel="stylesheet" />

    % lucjs = '/js/lucullus'
    % for pkg in ('base','maps','gui'):
        <script type="text/javascript" src="{{lucjs}}/{{pkg}}.js"></script>
    % end

    <style type="text/css">
        .icon-document{ background: url('/img/icons/16x16/actions/document-open.png') 0px center no-repeat !important; }
        .icon-config{ background: url('/img/icons/16x16/categories/preferences-system.png') 0px center no-repeat !important; }
        .ext-gecko .x-window-body .x-form-item {
            overflow:hidden !important; /* scrollbar bug if checkbox is in window */
        }
    </style>
    <title>Lucullus Test Page</title>
</head>
<body>
    <div align="center">
        <table border="0" cellspacing="0" cellpadding="0">
            <tr>
                <td colspan="2">
                    <div id="header"><img src="img/layout/lucullus_logo.png" alt="lucullus" /></div>
                    <ul id="menu">  
                        <li style="background-color: #999999"><a href="index.html">Home</a></li>
                        <li><a href="docu.html">Documentation</a></li>
                        <li><a href="contact.html">Contact</a></li>
                    </ul>
                </td>
            </tr>

            <tr>
                <td width="750px">
                    <div id="headline"><div><div>&#160;</div></div></div>
                </td>
                <td width="150px">
                </td>
            </tr>
            <tr>
                <td class="leftrow">
                    <div id="content">
                        <h2>Demo</h2><p style="padding: 0px 5px 20px 10px;">
                            <button id='new_ext_window'>New Ext Window</button>
                            <button id='call_test_code'>dev</button>
                        </p>
                        <h2>Systems Biology</h2><p style="padding: 0px 5px 20px 10px;">Biology is currently experiencing a paradigm shift - from studying individual genes and proteins towards analysing the structure and function of gene and protein networks. We are interested in understanding motor protein mediated processes in eukaryotic cells that are essential for muscle function, neuronal transport, cell division and others, at a systems level. Over the past few years, we have developed experimental methodologies to gain insight into the function of the dynein/dynactin motor protein complex at atomic resolution, and computational methods to determine the motor protein content of the eukaryotes.</p>
                        <h2>Bioinformatics</h2><p style="padding: 0px 5px 20px 10px;">The basis for the understanding of intracellular transport in eukaryotes at a cellular or organismal level is the determination of the motor protein content of the genomes. In this respect we highly profit from the continuously increasing amount of finished genome sequences. However, the process of genome annotation still lags considerably behind that of genome data generation. But it is the annotation that connects the sequence to the biology of the organism. Thus, we manually annotate the motor proteins using the possibilities of comparative genomics and multiple sequence alignments. To cope with the exponentially increasing amount of data we develop database and gene determination tools.</p>
                        <h2>Biochemistry / Structural Biology</h2><p style="padding: 0px 5px 20px 5px;">To understand the function of the motor proteins at atomic resolution we need precise models. A few kinesin and myosin crystal structures are available, but high-resolution data for the dynein/dynactin complex is still missing. Therefore, we are developing methods for the production of difficult-to-express proteins. For this purpose we are mainly using the lower eukaryote <i>Dictyostelium discoideum</i>.</p>
                    </div>
                </td>
                <td id="rightrow">
                    <div><a href="http://www.motorprotein.de" target="motorprotein"><img src="img/layout/motorprotein_link.png" alt="Motorprotein.de" /></a></div>
                    <div style="padding-top: 5px"><a href="http://www.diark.org" target="diark"><img src="img/layout/diark_link.png" alt="link to diark" /></a></div>
                    <div style="padding-top: 5px"><a href="http://www.cymobase.org" target="cymobase"><img src="img/layout/cymobase_link.png" alt="link to cymobase" /></a></div>
                    <div style="padding-top: 5px"><a href="http://www.webscipio.org" target="scipio"><img src="img/layout/scipio_link.png" alt="link to scipio" /></a></div>
                    <div style="padding-top: 20px"><a href="http://www.mpg.de" target="mpg"><img src="img/layout/mpg.png" alt="MPG" /></a></div>
                    <div style="padding-top: 5px"><a href="http://www.mpibpc.mpg.de" target="mpibpc"><img src="img/layout/mpibpc.png" alt="MPI for biophysical chemistry" /></a></div>
                </td>
            </tr>
            <tr>
                <td>
                    <div id="baseline"><div><div>&#160;</div></div></div>
                </td>
                <td />
            </tr>
            <tr>
                <td>
                    <div id="footer">&#169; Motorprotein.de 2010 | <a class="external" href="http://www.mpibpc.gwdg.de/metanavi/impressum/index.html" target="foobar">Impressum</a>
                    <a href="http://www.mozilla.org/products/firefox" target="foobar"><img src="img/layout/firefox2b.gif" alt="" /></a></div>
                </td>
                <td />
            </tr>
        </table>
    </div>

    <script type="text/javascript">
        // var server - 'http://fab8:8080/api'
        var server = document.location.protocol + '//' + document.location.host + document.location.pathname + 'api/'
        var api = new Lucullus.ThingFactory({server: server, apikey: 'test'})
        var getVars = Ext.urlDecode(window.location.search.substring(1));
        var app;
        
        getIndexedTwinMap = function(view) {
            var index = api.create('IndexView')
            // Map index resources to data resources
            view.on('change', function(res) {
              index.query('setup', {source: res.id})
            })
            var imap = new Lucullus.maps.MapPanel({
              width: 100, view: index, controlConfig: {scaleX: 0, scaleY: 0},
              autoclip: false
            })
            var vmap = new Lucullus.maps.MapPanel({
              flex: 1, view: view, controlConfig: {scaleX: 1, scaleY: 0},
              autoclip: false
            })
            var twin = new Lucullus.maps.TwinMapPanel({
                slaveMap: imap, masterMap: vmap, slaveScaleX: 0
            })
        }
        
        
        Ext.onReady(function(){
            Ext.get('call_test_code').on('click', function(){
                // Create resources
                var viewTL = api.create('IndexView')
                var viewTR = api.create('SequenceResource')
                var viewBL = api.create('IndexView')
                var viewBR = api.create('SequenceResource')
                var viewRR = api.create('RulerView')

                // Map index resources to data resources
                viewTR.on('change', function(res) {
                  viewTL.query('setup', {source: res.id})
                })
                viewBR.on('change', function(res) {
                  viewBL.query('setup', {source: res.id})
                })

                // Load data
                viewBR.query('load', {source:'http://fab8:8080/test/test.seq'})
                viewBR.wait(function(){
                    viewTR.query('copy', {source: viewBR.id, index:2})
                })

                // Create base MapPanels
                var mapRR = new Lucullus.maps.MapPanel({
                  flex: 1, view: viewRR
                })
                var mapTL = new Lucullus.maps.MapPanel({
                  width: 100, view: viewTL, controlConfig: {scaleX: 0, scaleY: 0},
                  autoclip: false
                })
                var mapTR = new Lucullus.maps.MapPanel({
                  flex: 1, view: viewTR, controlConfig: {scaleX: 1, scaleY: 0},
                  autoclip: false
                })
                var mapBL = new Lucullus.maps.MapPanel({
                  width: 100, view: viewBL, controlConfig: {scaleX: 0, scaleY: 5},
                  autoclip: false
                })
                var mapBR = new Lucullus.maps.MapPanel({
                  flex: 1, view: viewBR
                })

                // Create top and bottom twinmap
                var twinT = new Lucullus.maps.TwinMapPanel({
                    slaveMap: mapTL, masterMap: mapTR, height: 15, slaveScaleX: 0
                })
                var twinB = new Lucullus.maps.TwinMapPanel({
                    slaveMap: mapBL, masterMap: mapBR, flex:1, slaveScaleX: 0
                })



                // Create main twinmap
                var twin = new Lucullus.maps.TwinMapPanel({
                    slaveMap: twinT, masterMap: twinB, slavePosition: 'top',
                    slaveScaleY: 0, flex:1
                })

                var twin_final = new Lucullus.maps.TwinMapPanel({
                    slaveMap: twinR, masterMap: twin, slavePosition: 'top',
                    slaveScaleY: 0
                })

                twin_final.initCtrl()
                /*var*/ win = new Ext.Window({width:400, height:300, layout:'fit', shadow:false})
                win.add(twin_final)
                win.show()
            });

            Ext.get('new_ext_window').on('click', function(){
                luc = new Lucullus.gui.AppWindow({api: api})
                luc.show()
                if(getVars['maximize'])
                    luc.gui.root.maximize()
            
                if( getVars && getVars['url']) {
                    var source = getVars['url']
                    var format = getVars['format'] || 'fasta'
                    var name = getVars['name'] || 'FastaFile'

                    // This is a global for easy debugging
                    //var app
                    if( format == 'fasta' ) {
                        app = new Lucullus.gui.FastaApp({
                            name: name,
                            source: source
                        })
                    } else {
                        Ext.Msg.alert('Error', 'Currently only fasta files are supported.');
                        return
                    }
                }
                if(app) luc.addApp(app);
            });
        });
    </script>
</body>
</html>

