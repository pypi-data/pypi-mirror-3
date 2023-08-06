<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.js"></script>

    <link rel="stylesheet" type="text/css" href="/js/ext-3.3.1/resources/css/ext-all.css" />
    <script type="text/javascript" src="/js/ext-3.3.1/adapter/ext/ext-base.js"></script>
    <script type="text/javascript" src="/js/ext-3.3.1/ext-all.js"></script>

    <link type="text/css" href="./css/main.css" rel="stylesheet" />
    <link type="text/css" href="./css/lucullus.css" rel="stylesheet" />

    % lucjs = '/js/lucullus'
    % for pkg in ('base','maps','gui', 'level'):
        <script type="text/javascript" src="{{lucjs}}/{{pkg}}.js"></script>
    % end
    <script type="text/javascript" src="/js/mlayer.js"></script>
	<!-- <script type="text/javascript" src="https://github.com/flot/flot/raw/master/jquery.flot.js"></script> -->
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

    var server = document.location.protocol + '//' + document.location.host + '/api/';
    var api = new Lucullus.ThingFactory({server: server, apikey: 'test'});
    var getVars = Ext.urlDecode(window.location.search.substring(1));

    var points;
    var res, map;


    /* CrossDomain communication if this page is emdedded in an iframe. */

    var xsChannel;
    var xsOrigin;
    var xsDebug = false;
    var xsCache = [];

    function xsend(msg) {
        if(xsChannel) {
            xsChannel.postMessage(msg, xsOrigin);
        } else {
            xsCache.push(msg);
        }
    }

    window.addEventListener("message", function(event) {  
      if(xsDebug || event.data.debug)
        console.log('Got message:', event.data);

      if(!xsChannel && event.data.action === 'connect') {
        xsChannel = event.source;
        xsOrigin = event.origin;
        xsDebug = event.data.debug;
        xsend({action: 'connect', status:'OK'});
        while(xsCache.length > 0) {
            xsend(xsCache.shift());
        }
      }

      if (event.origin !== xsOrigin) return

      if (event.data.action === 'PING') {
        xsend({action: 'PONG'});
      }

      if (event.data.action === 'get_position') {
        xsend({action: 'get_position', viewport: map.viewport});
      }

      if (event.data.action === 'update') {
        d = event.data;
        if(d.level)
          res.query('setup', {level: d.level});
        if(d.x && d.y) {
          zoomTo(d.x.min, d.x.max, d.y.min, d.y.max);
        }
      }
    }, false);

    function logb(b, r) {
        return Math.log(r) / Math.log(b);
    }

    function zoomTo(xmin, xmax, ymin, ymax) {
        var ppm = res.state.ppm_resolution;
        var ppmmin = res.state.ppm_min;
        var ppmmax = res.state.ppm_max;
        // [0.16142578124999998, 0.16142578124999998]
        // [13.8, 13.8]
        // [179.1, 179.1]

        var x_offset = (ppmmax[0] - xmax) / ppm[0];
        var x_width  = (xmax - xmin) / ppm[0];

        var y_offset = (ymin - ppmmin[1]) / ppm[1];
        var y_width  = (ymax - ymin) / ppm[1];

        // Domain knowlege: calculate best zoom level
        var vp = map.viewport;
        var x_zoom = Math.floor(10 * logb(2, vp.width/x_width));
        var y_zoom = Math.floor(10 * logb(2, vp.height/y_width));
        var zoom = Math.min(x_zoom, y_zoom);
        map.zoom(zoom);
        var scale = Math.pow(2, -zoom/10)
        console.log(zoom, scale, x_offset, x_offset/scale)
        map.moveTo(x_offset/scale, y_offset/scale);
    }





    function start() {
        // Create 5 maps, one for each table field.
        map = new mlayer.Map('#map', {});
        var mapt = new mlayer.Map('#map_t', {});
        var mapl = new mlayer.Map('#map_l', {});
        var mapb = new mlayer.Map('#map_b', {});
        var mapr = new mlayer.Map('#map_r', {});

        // Make sure that the table fills the whole screen.
        jQuery(window).resize(function(){
            var w = jQuery(window).width()
            var h = jQuery(window).height()
            var ruler = 15;
            jQuery('#map').width(w-ruler-ruler).height(h-ruler-ruler)
            jQuery('#map_t,#map_b').width(w-ruler-ruler).height(ruler)
            jQuery('#map_l,#map_r').width(ruler).height(h-ruler-ruler)
            if(map) {
                map.resize();
                mapt.resize();
                mapl.resize();
                mapb.resize();
                mapr.resize();
            }
        })
        jQuery(window).resize()

        // Create the main server-side resource
        res = api.create('LevelResource');
        res.query('setup', {level: 0.01, data_color: '#ff8000'});
        res.query('load_local', {
            data:   getVars.data,
            procs:  getVars.procs,
            proc2s: getVars.proc2s,
            poi:    getVars.poi}
        );

        // Add a level view to the center map and rulers to the border maps.
        map.addLayer(new mlayer.layer.LucullusView({view: res, buffer:1}));
        mapt.addLayer(new mlayer.layer.LucullusView({
            view: api.create('Ruler2View'), buffer:1, channel:'top'}))
        mapr.addLayer(new mlayer.layer.LucullusView({
            view: api.create('Ruler2View'), buffer:1, channel:'right'}))
        mapb.addLayer(new mlayer.layer.LucullusView({
            view: mapt.base.view, buffer:1, channel:'bottom'}))
        mapl.addLayer(new mlayer.layer.LucullusView({
            view: mapr.base.view, buffer:1, channel:'left'}))

        // Add move bridges so center map movements affect all maps
        map.addLayer(new mlayer.layer.MoveBridge({target: mapt, scaleY:0}));
        map.addLayer(new mlayer.layer.MoveBridge({target: mapr, scaleX:0}));
        map.addLayer(new mlayer.layer.MoveBridge({target: mapb, scaleY:0}));
        map.addLayer(new mlayer.layer.MoveBridge({target: mapl, scaleX:0}));

        // Add a point layer to the center map.
        points = map.addLayer(new mlayer.layer.Points());
        //canvas = map.addLayer(new mlayer.layer.Canvas());

        // Add a mouse control to the center map.
        var ctrl = new mlayer.layer.Controls()
        map.addLayer(ctrl);

        // Make sure that the rulers are always up to date.
        res.on('change', function() {
            if(!res.state.ppm_resolution) return;
            xsend({action: 'update', resource: res.state});
            var ppm = res.state.ppm_resolution;
            var ppmmax = res.state.ppm_max;
            var ppmmin = res.state.ppm_min;
            map.moveTo(9999999,0);
            mapt.base.view.query('setup', {
                unit: -ppm[0],
                unit_offset: res.state.ppm_max[0]
            });
            mapr.base.view.query('setup', {
                unit: ppm[1],
                unit_offset: res.state.ppm_min[1]
            });
        });

        // Fill the points layer with data.
        res.query('get_points', {}, function(result) {
            if(!result.result.points) return
            var dim = res.state.resolution;
            var ppm = res.state.ppm_resolution;
            var ppmmin = res.state.ppm_min;
            jQuery.each(result.result.points, function(i, p) {
                p.name = p.name + ' [' + p.y + ', ' + p.x + ']'; 
                p.x = dim[0] - (p.x - ppmmin[0]) / ppm[0];
                p.y = (p.y - ppmmin[1]) / ppm[1];
                points.addPoint(p);
                //canvas.addPoint(p);
            });
        });

        map.show(); mapt.show(); mapr.show(); mapb.show(); mapl.show();

        // Install keyboard controls.
    	jQuery(document).keypress(function(e){
    		var step = 10
    		if     (e.which == 43) map.zoomIn(5)            // +
    		else if(e.which == 45) map.zoomOut(5)           // -
    		else if(e.which == 49) map.moveBy(-step, step)  // NUM 1
    		else if(e.which == 50) map.moveBy(0, step)      // NUM 2
    		else if(e.which == 51) map.moveBy(step, step)   // NUM 3
    		else if(e.which == 52) map.moveBy(-step, 0)     // NUM 4
    		//else if(e.which == 53) map.moveBy(5)
    		else if(e.which == 54) map.moveBy(step, 0)      // NUM 6
    		else if(e.which == 55) map.moveBy(-step, -step) // NUM 7
    		else if(e.which == 56) map.moveBy(0, -step)     // NUM 8
    		else if(e.which == 57) map.moveBy(step, -step)  // NUM 9
    	})
    }

    start();

	/*
	map.dom.dblclick(function(e){
		var x=e.pageX, y=e.pageY
		x -= map.mapdom.offset().left
        y -= map.mapdom.offset().top
		console.log(e.pageX, e.pageY, x, y)
        plot(x, y)
	})

	var sprite = new mlayer.layer.Sprite({offset:[20, 20], size:[400,300]})
	map.addLayer(sprite)

    function plot(x, y) {
		scale = Math.pow(2, map.viewport.zoom/10)
	    res.query('cross', {x:Math.round(x/scale), y:Math.round(y/scale)}, function(result) {
	        var dc = [], dr = [];
	        jQuery.each(result.result.row, function(i, p) {
	            dr.push([i*res.state.ppm_resolution[0]-res.state.ppm_max[0],
					    p*res.state.scale])
	        })
	        jQuery.each(result.result.column, function(i, p) {
	            dc.push([i*res.state.ppm_resolution[1]-res.state.ppm_max[1],
		                 p*res.state.scale])
	        })
		    jQuery.plot(jQuery(sprite.dom), [ {
				label: 'y='+Math.round(y/scale),
		        data: dr,
		        color: "rgb(30, 180, 20)",
		        threshold: { below: 1750, color: "rgb(200, 20, 30)" },
		        lines: { show: true },
		    }, {
				label: 'Column',
		        data: dc,
		        color: "rgb(200, 20, 30)",
		        threshold: { below: 1750, color: "rgb(200, 20, 30)" },
		        lines: { show: true },
		    } ], {
			grid: {
			    backgroundColor: 'white',
			  }
			});
	    });
	}
	*/


</script>
