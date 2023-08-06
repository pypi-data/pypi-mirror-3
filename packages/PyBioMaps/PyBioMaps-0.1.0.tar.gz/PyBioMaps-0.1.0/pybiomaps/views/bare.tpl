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

    % lucjs = '/js/lucullus'
    % for pkg in ('base','maps','gui', 'level'):
        <script type="text/javascript" src="{{lucjs}}/{{pkg}}.js"></script>
    % end
    <title>Lucullus 3dSpec Viewer</title>

    <script type="text/javascript">
        // var server - 'http://fab8:8080/api'
        var server = document.location.protocol + '//' + document.location.host + '/api/'
        var api = new Lucullus.ThingFactory({server: server, apikey: 'test'})
        var getVars = Ext.urlDecode(window.location.search.substring(1));
        var app, win;
        
        Ext.onReady(function() {    
            app = new Lucullus.gui.level.App({api:api})
            app.load(getVars.data, getVars.procs, getVars.proc2s, getVars.poi)
            win = new Ext.Viewport({
                layout: 'fit',
                items: [app.panel]
            })
            return
        });
    </script>


</head>
<body>
</body>
</html>

