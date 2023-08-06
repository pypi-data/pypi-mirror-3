<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>

    <script src="./jquery/jquery-1.3.2.min.js" type="text/javascript"></script>
    <script src="./jquery/jquery.query.js" type="text/javascript"></script>
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
</head>
<body style='overflow: hidden'>
    <table border="0" cellpadding="0" cellspacing="0">
        <tr>
            <td></td>
            <td><div id='map_t' style=''></div></td>
            <td></td>
        </tr>
        <tr>
            <td><div id='map_l' style=''></div></td>
            <td><div id='map' style=''></div></td>
            <td><div id='map_r' style=''></div></td>
        </tr>
        <tr>
            <td></td>
            <td><div id='map_b' style=''></div></td>
            <td></td>
        </tr>
    </table></body>
</html>
<script type="text/javascript">
    // var server - 'http://fab8:8080/api'
    
    $(window).resize(function(){
        var w = $(window).width()
        var h = $(window).height()
        $('#map').width(w-30).height(h-30)
        $('#map_t,#map_b').width(w-30).height(15)
        $('#map_l,#map_r').width(15).height(h-30)
    })
    $(window).resize()
    
    var server = document.location.protocol + '//' + document.location.host + '/api/';
    var api = new Lucullus.ThingFactory({server: server, apikey: 'test'});
    var getVars = Ext.urlDecode(window.location.search.substring(1));

    var map = new Lucullus.maps.Map('#map', {});
    var mapt = new Lucullus.maps.Map('#map_t', {});
    var mapl = new Lucullus.maps.Map('#map_l', {});
    var mapb = new Lucullus.maps.Map('#map_b', {});
    var mapr = new Lucullus.maps.Map('#map_r', {});
    var points;
    var res;

    function start() {
        res = api.create('LevelResource');
        res.query('setup', {level: 1750, data_color: '#ff8000'});
        res.query('load_local', {data:getVars.data, procs:getVars.procs, proc2s:getVars.proc2s, poi:getVars.poi});
        map.addLayer(new Lucullus.maps.ViewLayer({view: res, buffer:1}));
        points = map.addLayer(new Lucullus.maps.PointLayer());
        map.addLayer(new Lucullus.maps.ControlLayer());
        map.addLayer(new Lucullus.maps.MoveBridgeLayer({
            target: mapt, scaleY:0}));
        map.addLayer(new Lucullus.maps.MoveBridgeLayer({
            target: mapr, scaleX:0}));
        map.addLayer(new Lucullus.maps.MoveBridgeLayer({
            target: mapb, scaleY:0}));
        map.addLayer(new Lucullus.maps.MoveBridgeLayer({
            target: mapl, scaleX:0}));

        mapt.addLayer(new Lucullus.maps.ViewLayer({
            view: api.create('RulerView'), buffer:1, channel:'top'}))
        mapr.addLayer(new Lucullus.maps.ViewLayer({
            view: api.create('RulerView'), buffer:1, channel:'right'}))
        mapb.addLayer(new Lucullus.maps.ViewLayer({
            view: mapt.base.view, buffer:1, channel:'bottom'}))
        mapl.addLayer(new Lucullus.maps.ViewLayer({
            view: mapr.base.view, buffer:1, channel:'left'}))

        res.on('change', function() {
            if(!res.state.ppm_resolution) return;
            mapt.base.view.query('setup', {
                scale: -res.state.ppm_resolution[0],
                nullvalue: res.state.ppm_max[0]
            })
            mapr.base.view.query('setup', {
                scale: res.state.ppm_resolution[1],
                nullvalue: res.state.ppm_max[1]
            })
        })
        res.query('get_points', {}, function(result) {
            if(!result.result.points) return
            jQuery.each(result.result.points, function(i, p) {
                points.addPoint(p)
            })
            map.show(); mapt.show(); mapr.show(); mapb.show(); mapl.show();
        });


        /*
        var layer = new Lucullus.maps.SpriteLayer({images: [
            {url:'http://jquery.org/wp-content/uploads/2010/01/JQuery_logo_color_onwhite-300x74.png', top:10, left:10}
            ]})
        layer.is_hud = true;
        map.addLayer(layer);

        layer = new Lucullus.maps.SpriteLayer({images: [
            {url:'http://jquery.org/wp-content/uploads/2010/01/JQuery_logo_color_onwhite-300x74.png', top:80, left:200}
            ], animate:true})
        map.addLayer(layer);
        */



    }

    start();
</script>