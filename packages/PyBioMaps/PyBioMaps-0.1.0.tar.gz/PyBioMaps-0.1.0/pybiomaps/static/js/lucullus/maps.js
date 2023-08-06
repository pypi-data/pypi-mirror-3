/* 
Eine MAP besteht aus mehreren LAYERn, die alle in einem einzigen container-div
als position:relative untergebracht werden. Bei Bewegungen wird das
container-div bewegt. Alles enthaltene bewegt sich dann mit.

LAYER koennen ihrerseits container-divs haben. Das steht ihnen frei.

Alle x Millisekungen werden alle Layer neu gezeichnet. Sie haben selbst dafuer
zu sorgen, das das effizient geschiet. Was genau sie darstellen muessen,
entnehmen sie dem viewport der MAP.
*/

/** Lucullus.maps.Map represents a scrollable map with multiple layers. All
layers are moved. */

Lucullus = Lucullus || {}

Lucullus.extend = function(baseclass, override) {
    /* Creates a new class with values from $override mixed into the prototype
       of $baseclass. */
    
    // Override the constructor, if requested.
    var constructor = baseclass
    if(override.constructor && override.constructor !== ({}).constructor)
        constructor = override.constructor

    // Create a new constructor function that calls the old one.
    var cls = function(){
        constructor.apply(this, arguments);
    };
    
    // Clone the baseclass prototype.
    var dummy = function(){}
    dummy.prototype = baseclass.prototype;
    cls.prototype = new dummy();

    // Copy (and overwrite) new prototype values.
    for (var name in override) {
        if(name === 'constructor') continue;
        cls.prototype[name] = override[name];
    }

    return cls;
}



Lucullus.maps = Lucullus.maps || {}

Lucullus.maps.Map = function(node, config) {
    // The root DOM node for all map related nodes.
    this.dom = jQuery(node);
    this.dom.css({overflow:'hidden', position:'relative', top:'0px', left:'0px', padding:'0px'})
    this.dom.empty()

    // Container for map layers
    this.mapdiv = jQuery('<div />');
    this.mapdiv.css({position:'absolute', top:'0px', left:'0px', width:'1px', height:'1px'});
    this.dom.append(this.mapdiv);

    // Container for HUD layers (these don't move)
    this.huddiv = this.mapdiv.clone();
    this.dom.append(this.huddiv);

    // Lists of map and hud layer objects
    this.maps = [];
    this.huds = [];

    // Base map layer (used for clipping and other stuff)
    this.base = null;

    /** A viewport defines the area of the map the user is able to see.
        It is a plain object with the following attributes:

        top: The X value of the top-most pixel row.
        left: The Y value of the left-most pixel column.
        width: The number of pixels in Y direction.
        height: The number of pixels in X direction.
        bottom: top+height
        right: left+width
        zoom: The zoom factor as specified by the user.
    */

    this.viewport = {top:    0, left:   0,
                     width:  0, height: 0,
                     bottom: 0, right:  0,
                     zoom:   0}

    // handle for the draw interval
    this._draw_interval = null;
    
    /*
     * Configuration 
     */

    this.autoclip = config.autoclip || true;
    this.draw_interval = config.draw_interval || 200;
    this.zindex = config.zindex || 100;
}





Lucullus.maps.Map.prototype = {
    start: function() {
        // Layout all layers and start the draw interval.
        if(this._draw_interval !== null) return
        this.layout()
        var self = this;
        this._draw_interval = window.setInterval(function(){
            self.draw();
        }, this.draw_interval)
    },
    stop: function() {
        // Clear the draw interval.
        if(this._draw_interval === null) return
        window.clearInterval(this._draw_interval);
        this._draw_interval = null;
    },
    show: function() {
        // Show the primary dom node and start rendering.
        this.dom.show();
        this.start();
    },
    hide: function() {
        // Hide the primary dom node and stop rendering.
        this.dom.hide();
        this.stop();
    },

    draw: function() {
        /* Draw each layer and check for a resized viewport.
            This method is called every draw_interval milliseconds and on
            events that drastically change the viewport (e.g. zoom).
        */
        var vp = this.viewport, dom = this.dom;
        var w = vp.width, h = vp.height;
        if(w != dom.innerWidth() || h != dom.innerHeight()) {
            vp.width  = dom.innerWidth();
            vp.height = dom.innerHeight();
            vp.bottom = vp.top + vp.height;
            vp.right  = vp.left + vp.width;
            this.huddiv.width(vp.width).height(vp.height)
            jQuery.each(this.maps, function(){ this.onResize(vp) });
            jQuery.each(this.huds, function(){ this.onResize(vp) });
        }
        jQuery.each(this.maps, function(){ this.onDraw(vp) })
        jQuery.each(this.huds, function(){ this.onDraw(vp) })
    },
    layout: function() {
        /* Create HTML nodes for all layers. */
        
        var mapdiv = this.mapdiv,
            huddiv = this.huddiv,
            zindex = this.zindex;

        // Do not layout an inactive map.
        if(this._draw_interval !== null) return;

        mapdiv.empty();
        jQuery.each(this.maps, function() {
            this.dom.css('z-index', zindex).empty();
            zindex += 1 + (this.onLayout(zindex) || 0);
            mapdiv.append(this.dom)
        })

        huddiv.empty();
        jQuery.each(this.huds, function() {
            this.dom.css('z-index', zindex).empty();
            zindex += 1 + (this.onLayout(zindex) || 0);
            huddiv.append(this.dom)
        })
        this.max_zindex = zindex;
    },
    addLayer: function(layer, base) {
        // Add a new layer object. If the second parameter is true, the layer
        // is used as the new base layer.
        layer.map = this
        if(layer.is_hud) {
            this.huds.push(layer);
        } else if(base || layer.is_base || !this.base) {
            if(this.base) this.base.is_base = false;
            layer.is_base = true;
            this.base = layer;
            this.maps.unshift(layer);
        } else {
            this.maps.push(layer);
        }
        this.layout();
        return layer
    },

    
    moveTo: function(x, y) {
        /*  Move the top-left corner viewport to a specific position. If
            either x or y are null, they default to the current position.
            
            Map movements are measured in browser pixels. The Map object has
            no knowlege about the scale or ratio of the data. Example: If each
            pixel represents n data units, and you want to move x data units
            to the left, you actually need to move x*n pixels to the left.
        */
        if(!this.base) return;
        var view = this.viewport;

        // Default to current position
        if(typeof x != 'number') x = view.left;
        if(typeof y != 'number') y = view.top;

        // Clip movements based on the current base-layer extent
        if(this.autoclip) {
            var box = this.base.getExtent(view.zoom);
            x = Math.max(box.left, Math.min(box.right-view.width, x));
            y = Math.max(box.top, Math.min(box.bottom-view.height, y));
        }

        // Calculate movement vector
        x = Math.round(x);
        y = Math.round(y);
        var dx = x - view.left;
        var dy = y - view.top;

        // No movement -> nothing to di.
        if(!dx && !dy) return;

        // Update viewport
        view.left   += dx;
        view.right  += dx;
        view.top    += dy;
        view.bottom += dy;

        // Trigger onMove callbacks for all maps.
        jQuery.each(this.maps, function(){ this.onMove(view) });
        jQuery.each(this.huds, function(){ this.onMove(view) });

        // Actually move the primaty dom node.
        this.mapdiv.css({left: -x+'px', top: -y+'px'});
    },
    moveBy: function(dx, dy) {
        // Move the viewport by a specific (pixel) distance.
        this.moveTo(this.viewport.left + dx, this.viewport.top + dy, absolute);
    },
    zoom: function(level) {
        // Change the zoom level but keep the focus on the same spot.
        // e.g. If the extent of the base layer changes, the map is moved to
        // the new position. This usually triggers a redraw.

        var view = this.viewport
        var old = view.zoom
        view.zoom = level

        // Trigger onZoom callbacks for all maps.
        jQuery.each(this.maps, function(){ this.onZoom(view) });
        jQuery.each(this.huds, function(){ this.onZoom(view) });

        // Get old and new extend
        var obox = this.base.getExtend(old)
        var nbox = this.base.getExtend(level)

        // Calculate center of current viewport in old extend
        var cx = view.left + view.width  / 2;
        var cy = view.top  + view.height / 2;

        // Calculate relative position of center within old extend
        var ox = (obox.right  - obox.left) / (cx - obox.left)
        var oy = (obox.bottom - obox.top)  / (cy - obox.top)

        // Calculate position of center in new extend
        var nx = nbox.left + ox * (obox.right  - obox.left)
        var ny = nbox.top  + oy * (obox.bottom - obox.top)

        // Move to new center and redraw.
        this.moveTo(nx - view.width/2, ny - view.height/2)
        this.draw()

        return old
    }
}





/* A Layer object renders one layer of data. */

Lucullus.maps.Layer = function(config) {
    this.config = config || {}
    this.dom = jQuery('<div />')
    this.dom.css({ position: 'absolute', top: '0px', left: '0px',
                   width: '1px', height: '1px' })
    this.map = null;
    this.init(config||{})
}

Lucullus.maps.Layer.prototype = {
    is_base: false,
    init: function(config) {
        /* Called by the constructor. */
    },
    getExtent: function(zoom) {
        /* Called by the Map to get the extend of the base layer. The extent
           is an object with the following attributes:
           
           top: Minimum x value.
           left: Minimum y value.
           bottom: Maximum x value.
           right: Maximum y value.
           
           The extend should be calculated according to the specified zoom
           level. If a zoom level is not supported, return null. The returned
           object must not change at runtime.
        */
        return {top:0, left:0, right:0, bottom:0};
    },
    onLayout: function(zIndex) {
        // Called by the Map as soon as the layer is is added to the dom tree
        //  and on subsequent Map.layout() calls. This should create all
        //  dom nodes required to display the data and add them to this.dom.
        // @param zIndex CSS z-index of this.dom.
        // @return The number of additional z-indices used by this Layer.
        return 0
    },
    onDraw: function(viewport) {
        /* Called every Map.draw_interval milliseconds, even if the viewport
         * did not change. Should update visuals according to new viewport.
         */
    },
    onResize: function(viewport) {
        /* Called on viewport resize events, just before the draw() call.
         * @param viewport Current viewport.
        */
    },
    onZoom: function(viewport) {
        /* Called on zoom events.
         * @param viewport Current viewport.
        */
    },
    onMove: function(viewport) {
        /* Called on every single move event. Do only fast calculations here.
         */
    }
}

/* This layer does not draw anything, but relays movements to a different map.
   It is used to synchronize two or more maps.
*/
Lucullus.maps.MoveBridgeLayer = Lucullus.extend(Lucullus.maps.Layer, {
    init: function(config) {
        this.target = config.target
        this.scaleX = typeof config.scaleX == 'number' ? config.scaleX : 1;
        this.scaleY = typeof config.scaleY == 'number' ? config.scaleY : 1;
        this.offsetX = config.offsetX || 0;
        this.offsetY = config.offsetY || 0;
    },
    onMove: function(vp) {
        this.target.moveTo(this.offsetX + this.scaleX * vp.left,
                           this.offsetY + this.scaleY * vp.top)
    },
    onZoom: function(vp) {
        this.target.zoom(vp.zoom)
    }
})

/* Draw labeled points and show the label if the mouse is near the point. */

Lucullus.maps.PointLayer = Lucullus.extend(Lucullus.maps.Layer, {
    init: function(config) {
        // Position and number of currently displayed tiles
        this.points = [];
        if(config.points) {
            var self = this
            jQuery.each(config.points, function(index, p) {
                self.addPoint(p);
            });
        }
        this.needs_refresh = true;
        this.extent = {top:0, bottom:0, left:0, right:0}
    },
    addPoint: function(p) {
        this.extent.top = Math.min(this.extent.top, p.x);
        this.extent.bottom = Math.max(this.extent.bottom, p.x);
        this.extent.left = Math.min(this.extent.left, p.y);
        this.extent.right = Math.max(this.extent.right, p.y);
        this.points.push(p);
        this.needs_refresh = true;
    },
    onLayout: function(zindex) {
        self.label_zindex = zindex+1;
        return 1
    },
    onDraw: function(vp) {
        if(! this.points) return;
        if(! this.needs_refresh) return;
        var html = '';
        var lz = this.label_zindex;
        jQuery.each(this.points, function(index, p) {
            var name = p.name.replace(/&/g, "&amp;")
                             .replace(/</g, "&lt;")
                             .replace(/>/g, "&gt;");
            html += '<span style="position: absolute; width:1px; height:1px;'+
                    ' top: '+(p.y-1)+'px; left: '+(p.x-1)+'px;'+
                    ' border: 1px solid '+p.color+';">'+
                        '<span style="z-index: '+lz+'; display:none;'+
                        ' position: relative; top:5px; left:5px; width: 200px">'+
                            name+
                        '</span>'+
                    '</span>'
        })
        this.dom.html(html);
        this.dom.find('span span').parent().hover(function(){
            jQuery(this).children().show()
        }, function(){
            jQuery(this).children().hide()
        })
        this.needs_refresh = false;
    }
})



Lucullus.maps.TileLayer = Lucullus.extend(Lucullus.maps.Layer, {
    constructor: function(config) {
        // Position and number of currently displayed tiles
        Lucullus.maps.Layer.call(this, config);
        config = config || {}
        this.covered = {top:0, left:0, bottom:0, right:0}
        this.tilesize = config.tilesize || 256;
        this.offset = config.offset || {top:0, left:0}
        // Number of tiles to draw in advance
        this.buffer = config.buffer || 0;
        if(typeof config.url == 'string') {
            var url = config.url
            config.url = function(x, y, z, ts) {
                return url.replace(/\{x\*size\}/g, x*ts)
                          .replace(/\{y\*size\}/g, y*ts)
                          .replace(/\{x\}/g, x)
                          .replace(/\{y\}/g, y)
                          .replace(/\{z\}/g, z)
                          .replace(/\{size\}/g, ts);
            }
        }
        if(typeof config.url == 'function')
            this.url = config.url;
        
    },
    onDraw: function(vp) {
        if(!this.url) return;

        var view = vp;
        var cov = this.covered;
        var ts = this.tilesize;
        var ext = this.getExtent();
        var off = this.offset;

        // Calculate visible tiles (including border)
        var vtop    = Math.floor(view.top    / ts) - this.buffer;
        var vleft   = Math.floor(view.left   / ts) - this.buffer;
        var vbottom = Math.ceil( view.bottom / ts) + this.buffer;
        var vright  = Math.ceil( view.right  / ts) + this.buffer;
        // Clip visible tiles on extent
        vtop    = Math.max(vtop,    Math.floor(ext.top    / ts));
        vleft   = Math.max(vleft,   Math.floor(ext.left   / ts));
        vbottom = Math.min(vbottom, Math.ceil(ext.bottom / ts));
        vright  = Math.min(vright,  Math.ceil(ext.right  / ts));
        
        if(vtop == vbottom || vleft == vright) return;
        if(cov.top != vtop || cov.left != vleft || cov.bottom != vbottom || cov.right != vright) {
            var html = '';
            for(var x=vleft; x<vright; x++) {
                for(var y=vtop; y<vbottom; y++) {
                    html += '<img src="'+this.url(x,y,0,ts)+'" alt="pos: ['+x+' '+y+' '+0+']"'+
                            ' style="position: absolute;'+
                            ' width:'+ts+'px; height:'+ts+'px;'+
                            ' top:'+(y*ts)+'px; left:'+(x*ts)+'px" />';
                }
            }
            this.dom.html(html);
            cov.top = vtop;
            cov.left = vleft;
            cov.right = vright;
            cov.bottom = vbottom;
        }
    },
    onLayout: function() {
        this.covered = {top:0, left:0, bottom:0, right:0}
    }
})


Lucullus.maps.ViewLayer = Lucullus.extend(Lucullus.maps.TileLayer, {
    constructor: function(config) {
        var self = this;
        config = config || {}
        config.url = function(x, y, z, ts) {
            return self.view.image(self.channel, x*ts, y*ts, z, ts, ts, 'png')
        }
        Lucullus.maps.TileLayer.call(this, config);

        this.channel = config.channel || 'default'
        this.view = config.view;
        this.view.on('change', function(view) {
            var ext = self.getExtent()
            if(view.state && view.state.offset) {
                ext.top = view.state.offset[1];
                ext.left = view.state.offset[0];
            }
            if(view.state && view.state.size) {
                ext.bottom = ext.top + view.state.size[1];
                ext.right = ext.left + view.state.size[0];
            }
            this.covered = {top:0, left:0, bottom:0, right:0};
            if(this.map) this.map.moveBy(0,0);
        }, this)
    }
})




Lucullus.maps.RulerLayer = Lucullus.extend(Lucullus.maps.Layer, {
    is_hud: true,
    constructor: function(config) {
        var self = this;
        config = config || {};
        Lucullus.maps.Layer.call(this, config);
        this.position = config.position || 'top'
        this.api = config.api;
        this.ruler = this.api.create('RulerView')
        this.ruler.on('change', function(view) {
            var ext = self.getExtent()
            if(view.state) {
                if(view.state.offset) {
                    ext.top = view.state.offset[1];
                    ext.left = view.state.offset[0];
                }
                if(view.state.size) {
                    ext.bottom = ext.top + view.state.size[1];
                    ext.right = ext.left + view.state.size[0];
                }
            }
            if(this.map) this.map.moveBy(0,0);
        }, this)
    },
    onLayout: function(zindex) {
        if(!this.subdom) {
            this.subdom = jQuery('<div>')
            this.subdom.appendTo(this.dom)
            this.submap = new Lucullus.maps.Map(this.subdom, {})
            this.sublayer = new Lucullus.maps.ViewLayer({
                view: this.ruler, buffer:1, channel:this.position
            })
            this.submap.addLayer(this.sublayer)
        }
        this.dom.append(this.subdom)
        this.submap.zindex = zindex+1
        this.submap.layout()
        this.onResize(this.map.viewport)
        return this.submap.max_zindex-zindex;
    },
    onResize: function(vp) {
        this.dom.width(vp.width).height(vp.height)
        if(this.position == 'top')
            this.subdom.height(15).width(vp.width-30)
                .css({top:'0px', left:'15px'})
        else if (this.position == 'bottom')
            this.subdom.height(15).width(vp.width-30)
                .css({top:vp.height-15+'px', left:'15px'})
        else if (this.position == 'left')
            this.subdom.height(vp.height-30).width(15)
                .css({top:'15px', left:'0px'})
        else if (this.position == 'right')
            this.subdom.height(vp.height-30).width(15)
                .css({top:'15px', left:vp.width-15+'px'})
    },
    onMove: function(vp) {
        if(this.position == 'top' || this.position == 'bottom')
            this.submap.moveTo(vp.left, 0)
        else
            this.submap.moveTo(0, vp.top)
    }
})



Lucullus.maps.SpriteLayer = Lucullus.extend(Lucullus.maps.Layer, {
    constructor: function(config) {
        // Position and number of currently displayed tiles
        config = config || {}
        Lucullus.maps.Layer.call(this, config);
        this.images = config.images;
        this.animate = config.animate;
    },
    onLayout: function() {
        var self = this;
        jQuery.each(this.images, function(){
            var i = jQuery('<img src="'+this.url+'" />');
            i.css({position: 'absolute', top:this.top+'px', left:this.left+'px'})
             .appendTo(self.dom);
            if(self.animate) {
                var c = this;
                bla = function() {
                    i.animate({left:c.left+200+'px'})
                    .animate({top:c.top+200+'px'})
                    .animate({left:c.left+'px'})
                    .animate({top:c.top+'px'})
                };
                window.setInterval(bla, 5000);
            }
        });
    }
}); 






Lucullus.maps.ControlLayer = Lucullus.extend(Lucullus.maps.Layer, {
    is_hud: true,
    constructor: function(config) {
        // Position and number of currently displayed tiles
        var self = this;
        Lucullus.maps.Layer.call(this, config);
        this.config = config || {}
        this.status = jQuery('<span />').css({
            position: 'absolute', width: '1px'
        }).appendTo(this.dom)
    },
    onLayout: function(zindex) {
        var map = this.map;
        this.control = new Lucullus.maps.MapMouseControl()
        this.control.init(map.dom[0], null, {})
        this.control.onMovement = function(dx, dy) {
            map.moveBy(-dx, -dy);
        }
        this.joystick = jQuery('<div />').css({
            'background-image': 'url(/img/joystick.png)',
            'background-position': 'center center',
            position: 'absolute',
            top: '10px',
            left: '10px',
            width:'40px',
            height:'40px'});//.appendTo(this.dom)
        this.status.css({top: '5px', left: (map.viewport.width-50)+'px'})
        return 0;
    },
    onResize: function(vp) {
        this.status.css({top: '5px', left: (vp.width-50)+'px'})
    },
    onMove: function(vp) {
        this.status.html('x:'+vp.left+' y:'+vp.top)
    }
});



















/**
 * ViewMap displays a matrix of images tiles and allows the user to browse the
 * matrix with the mouse. If the matrix is bigger than the visible area, only
 * the visible image tiles are loaded. This way it is possible to display very
 * large maps or data visualized in realtime in a browser.
 * @constructor
 */




Lucullus.maps.ViewMap = function(config) {
    /* Shows a view in an element using a movable tile map */
    this.view = config.view
    this.root = config.root
    this.root.innerHTML = '<div style="overflow: hidden; position: relative">'
    this.node = this.root.firstChild
    this.autoclip = config.autoclip
    this.channel = config.channel

    /* Default values */
    this.clipping = [0, 0, 0, 0]    // minimum and maximum pixel to show
    this.tilesize = [256, 256]      // Size of a tile in pixel
    this.tiles    = [0, 0]          // Number of tiles
    this.offset   = [0, 0]          // Current offset (negative position of the upper left corner relative to the data area)
    this.zoom     = 0

    this.map =  null
    this.buffer = null

    // Some caches for faster processing
    this.mapsize = [0,0]                // Size of viewable area
    this.mapoffset = [0,0]              // Position of map
    this.bufferoffset = [0,0]           // Position of buffer
    
    this.refresh_speed = 500            // Interval for map<->buffer swaps
    this.refresh_interval = null
    this.refresh_please = true
    this.overlap = 0
    this.stopped = true
    
    // Setup
    var s = Lucullus.dom.getInnerSize(this.root)
    this.setWindowSize(s.width, s.height)

    // Start refresh loop when ready.
    var self = this
    this.view.wait(function() {
        self.start()
    })
    // Refresh again on each change
    this.view.on('change', function() {
        this.refresh_please = true
    }, this)
}

/**
 * Start the refresh interval.
 */

Lucullus.maps.ViewMap.prototype.start = function() {
    if(this.stopped) {
        this.stopped = false
        this.refresh_please = true
        var self = this
        this.refresh_interval = window.setInterval(function() {
            self.refresh()
        }, this.refresh_speed)
    }
}

/**
 * Stop the refresh interval. The map is paused, but not destroyed.
 */

Lucullus.maps.ViewMap.prototype.stop = function() {
    if(!this.stopped) {
        this.stopped = true
        window.clearInterval(this.refresh_interval)
    }
}

/**
 * Pause the refresh interval and then destroy all DOM-nodes or references
 * created by this instance. The ViewMap is unusable after calling this method.
 */

Lucullus.maps.ViewMap.prototype.destroy = function() {
    this.stop()
    this.root.empty()
    delete this.node, this.map, this.buffer
}

/**
 * Redraw the map. 
 * @param {bool} now If true, do not wait for the refresh loop. Do it now.
 */

Lucullus.maps.ViewMap.prototype.redraw = function(now) {
    this.refresh_please = true
    if(now) this.refresh()
}

/**
 * Move the map by (dx, dy) pixel. Clipping is applied.
 * @param {int} dx Number of Pixel to move in x direction.
 * @param {int} dy Number of Pixel to move in y direction.
 * @param {bool} virtual If true, do not actually move but only return clipped movement.
 * @returns A (dx, dy) tuple with the actual movement after clipping.
 */

Lucullus.maps.ViewMap.prototype.move = function(dx, dy, virtual) {
    if(!this.map) return [0, 0];

    // Normalise movement (clipping)
    if(!dx) dx=0;
    if(!dy) dy=0;
    if(this.autoclip) {
        dx = Math.min(- this.clipping[0], Math.max(this.mapsize[0] - this.clipping[2], this.offset[0] + Math.round(dx))) - this.offset[0]
        dy = Math.min(- this.clipping[1], Math.max(this.mapsize[1] - this.clipping[3], this.offset[1] + Math.round(dy))) - this.offset[1]
    }
    if(virtual) return [dx, dy]
    if(dx == 0 && dy == 0) return [0, 0];

    // Update offset
    this.offset[0] += dx
    this.offset[1] += dy

    // move map (and buffer, if available)
    this.mapoffset[0] += dx
    this.mapoffset[1] += dy
    if(this.map) {
        this.map.style.top = this.mapoffset[1] + 'px'
        this.map.style.left = this.mapoffset[0] + 'px'
    }
    
    if(this.buffer) {
        this.bufferoffset[0] += dx
        this.bufferoffset[1] += dy
        this.buffer.style.top = this.bufferoffset[1] + 'px'
        this.buffer.style.left = this.bufferoffset[0] + 'px'
    }
    return [dx, dy]
}

/**
 * Get the size of the viewport.
 * @returns (w, h) tuple.
 */

Lucullus.maps.ViewMap.prototype.getWindowSize = function() {
    return this.mapsize.slice()
}

/**
 * Resize the viewport.
 * @param {int} w Width of the viewport.
 * @param {int} h Height of the viewport.
 */

Lucullus.maps.ViewMap.prototype.setWindowSize = function(w, h) {
    w = typeof w == 'number' ? w : 0
    h = typeof h == 'number' ? h : 0
    this.node.style.width = w+'px'
    this.node.style.height = h+'px'
    var tiles_x = Math.ceil(w / this.tilesize[0] ) + 1 + this.overlap * 2
    var tiles_y = Math.ceil(h / this.tilesize[1] ) + 1 + this.overlap * 2
    this.mapsize = [w, h]
    this.tiles = [tiles_x, tiles_y]
    this.redraw()
}


/**
 * Return the clipping area.
 * @returns (minX, minY, maxX, maxY).
 */

Lucullus.maps.ViewMap.prototype.getClipping = function() {
    return this.clipping.slice()
}

/**
 * Limit the viewable area of the map.
 * @param {int} minX Position of the upper edge.
 * @param {int} minY Position of the left edge.
 * @param {int} maxX Position of the lower edge.
 * @param {int} maxY Position of the right edge.
 */

Lucullus.maps.ViewMap.prototype.setClipping = function(minX, minY, maxX, maxY) {
    if(typeof minX == 'number') this.clipping[0] = minX
    if(typeof minY == 'number') this.clipping[1] = minY
    if(typeof maxX == 'number') this.clipping[2] = maxX
    if(typeof maxY == 'number') this.clipping[3] = maxY
    this.move(0, 0) // Immediately move to viewable area.
}

/**
 * Get the width and height of the viewable area of the map.
 * @returns (w, h) tuple.
 */

Lucullus.maps.ViewMap.prototype.getSize = function() {
    return [this.clipping[2] - this.clipping[0], this.clipping[3] - this.clipping[1]]
}

/**
 * Changes the width and height of the viewable area of the map. This moves
 * the bottom right corner of the clipping area but does not change the upper
 * left corner.
 * @param {int} w New width of the clipping area.
 * @param {int} h New height of the clipping area.
 */

Lucullus.maps.ViewMap.prototype.setSize = function(w, h) {
    if(typeof w == 'number') this.clipping[2] = this.clipping[0] + w
    if(typeof h == 'number') this.clipping[3] = this.clipping[1] + h
    this.move(0, 0) // Immediately move to viewable area.
}

/**
 * Get the position of the upper left corner of the viewport relative to the
 * map coordinates. In other words: Get the coordinates of the pixel that is
 * visible in the upper left corner.
 * @returns (x, y) tuple.
 */

Lucullus.maps.ViewMap.prototype.getPosition = function() {
    return [-this.offset[0], -this.offset[1]]
}

/**
 * Move the upper left corner of the viewport to this position.
 * @param {int} x If this is a number, move to this position.
 * @param {int} y If this is a number, move to this position.
 * @returns (x, y) tuple with the new coordinates (may differ due to clipping).
 */

Lucullus.maps.ViewMap.prototype.setPosition = function(x, y) {
    x = typeof x == 'number' ? -(this.offset[0]+x) : 0
    y = typeof y == 'number' ? -(this.offset[1]+y) : 0
    this.move(x, y)
    return this.getPosition()
}

/**
 * Get the normalized coordinates for a given position. This is (0.0, 0.0) for
 * the top- and leftmost position and (1.0, 1.0) for the bottom- and rightmost
 * position. The size of the viewport is calculated in, so that "right"
 * actually means "right aligned".
 * @param {int} x x-coordinate.
 * @param {int} y y-coordinate.
 * @returns (normX, normY) tuple.
 */

Lucullus.maps.ViewMap.prototype.normalizePosition = function(x, y) {
    var width = this.clipping[2] - this.clipping[0] - this.mapsize[0]
    var height = this.clipping[2] - this.clipping[0] - this.mapsize[1]
    var posX = x - this.clipping[0]
    var posY = y - this.clipping[1]
    return [posX / width, posY / height]
}

/**
 * The reverse of normalizeCoordinates()
 * @see #normalizeCoordinates
 */

Lucullus.maps.ViewMap.prototype.denormalizePosition = function(nx, ny) {
    var width = this.clipping[2] - this.clipping[0] - this.mapsize[0]
    var height = this.clipping[2] - this.clipping[0] - this.mapsize[1]
    var minX = this.clipping[0]
    var minY = this.clipping[1]
    return [Math.round(width * nx) + minX, Math.round(height * ny) + minY]

}

/**
 * Get the current normalized position of the viewport.
 * @returns (scrollX, scrollY) tuple.
 */

Lucullus.maps.ViewMap.prototype.getScrollPosition = function() {
    return this.normalizePosition(-this.offset[0], -this.offset[1])
}

/**
 * Move to a position using normalized (0.0-1.0) coordinates.
 * @param {float} sx If this is a number, move to this (normalized) position.
 * @param {float} sy If this is a number, move to this (normalized) position.
 * @returns (x, y) tuple with the new (normalized) coordinates.
 */

Lucullus.maps.ViewMap.prototype.setScrollPosition = function(sx, sy) {
    var spos = this.getScrollPosition();
    if(typeof sx != 'number') sx = spos[0];
    if(typeof sy != 'number') sy = spos[1];
    var npos = this.denormalizePosition(sx, sy);
    return this.setPosition(npos[0], npos[1]);
}

/**
 * Get the current zoom level.
 * @returns Zoom level.
 */

Lucullus.maps.ViewMap.prototype.getZoom = function() {
    return this.zoom;
}

/**
 * Change the zoom level. This moves the map and triggers a redraw.
 * @param {int} Zoom level.
 */

Lucullus.maps.ViewMap.prototype.setZoom = function(level) {
    if(this.buffer) Ext.get(this.buffer).remove();
    if(this.map) Ext.get(this.map).remove();
    var oldPos = this.getScrollPosition();
    var oldZoom = this.getZoom()
    this.zoom = Math.round(level);
    var scaleDiff = Math.pow(2, -(oldZoom-this.zoom)/10) // TODO: reversed?
    this.clipping[0] = this.clipping[0] * scaleDiff
    this.clipping[1] = this.clipping[1] * scaleDiff
    this.clipping[2] = this.clipping[2] * scaleDiff
    this.clipping[3] = this.clipping[3] * scaleDiff
    this.setScrollPosition(oldPos[0], oldPos[1])
    this.redraw()
}

/**
 * Return the position of a mouse click relative to the map area.
 * @param {int} x Absolute x position (relative to document)
 * @param {int} y Absolute y position (relative to document)
 * @ returns (x, y) tuple relative to map coordinates.
*/

Lucullus.maps.ViewMap.prototype.getClickPosition = function(x, y) {
    var nodeOffset = Lucullus.dom.getPageOffset(this.node)
    x = x - nodeOffset.left - this.offset[0]
    y = y - nodeOffset.top - this.offset[1]
    return [x, y]
}

/**
 * Redraw the map area (if necessary) and make sure that all visible tiles are
 * loaded.
 * @private
 */

Lucullus.maps.ViewMap.prototype.refresh = function() {
    if(this.stopped) return
    // Do nothing if map is within scope. refresh_please forces a refresh.

    var outofscope = (
        this.mapoffset[0] > 0 || this.mapoffset[1] > 0
        || this.mapoffset[0] + this.tiles[0]*this.tilesize[0] < this.mapsize[0]
        || this.mapoffset[1] + this.tiles[1]*this.tilesize[1] < this.mapsize[1]
    )
    if(!outofscope && !this.refresh_please) return;
    this.refresh_please = false

    var self = this
    var scale = Math.pow(2, -this.zoom/10)
    // React on changed view parameter
    if(!this.view) {
        this.node.empty()
        return
    }
    if(this.view.state && this.view.state.size && this.view.state.offset) {
        var width = this.view.state.size[0]
        var height = this.view.state.size[1]
        var ox = this.view.state.offset[0]
        var oy = this.view.state.offset[1]
        this.clipping = [ ox / scale, oy / scale, (width+ox) / scale, (height+oy) / scale ]
    } else {
        this.clipping = [0, 0, 0, 0]
    }
    // If the map is not visible, we don't have to do anything
    if(this.mapsize[0] == 0 || this.mapsize[1] == 0) return
    // Index number of top left tile
    var nx = Math.floor(-this.offset[0] / this.tilesize[0]) - this.overlap
    var ny = Math.floor(-this.offset[1] / this.tilesize[1]) - this.overlap
    // Total offset of top left tile
    var ox = nx * this.tilesize[0] 
    var oy = ny * this.tilesize[1] 
    // Offset of top left tile relative to visible area
    var vox = ox+this.offset[0]
    var voy = oy+this.offset[1]

    if(this.buffer) {
        Ext.get(this.buffer).remove()
    }

    if(this.map){
        this.buffer = this.map
        this.bufferoffset = this.mapoffset
    }

    this.map = document.createElement('div')
    this.map.setAttribute('style', 'position: absolute; left: '+vox+'px; top: '+voy+'px; width: '+(this.mapsize[0])+'px; height: '+(this.mapsize[1])+'px')
    this.mapoffset = [vox, voy]
    this.map.innerHTML = this.imagetiles(nx, ny)
    this.node.appendChild(this.map)
}

Lucullus.maps.ViewMap.prototype.imagetiles = function(nx, ny) {
    /* Fills the current map with images using (nx,ny) as number of top left
       tile and (cx,cy) as number of tiles to show */
    var tx = this.tilesize[0]
    var ty = this.tilesize[1]
    var cx = this.tiles[0]
    var cy = this.tiles[1]
    var images = []
    var zoom = this.zoom, channel = this.channel
    for(var y=0; y<cy; y++) {
        for(var x=0; x<cx; x++) {
            // Image URL
            var url = this.view.image(channel, (x+nx)*tx, (y+ny)*ty, zoom, tx, ty, 'png')
            // Offset within our map in pixel
            var ox = x * tx
            var oy = y * ty
            // Total offset of data area in pixel
            var tox = (x+nx) * tx
            var toy = (y+ny) * ty
            
            if(this.autoclip || tox < this.clipping[2] && toy < this.clipping[3] && (tox + tx) > this.clipping[0] && (toy + ty) > this.clipping[1]) {
                images.push('<img src="'+url+'" style="position:absolute; width:'+tx+'px; height:'+ty+'px; left:'+ox+'px; top:'+oy+'px;" />')
            } else {
                images.push('<div style="position:absolute; width:'+tx+'px; height:'+ty+'px; left:'+ox+'px; top:'+oy+'px; background: grey;">no data</div>')
            }
        }
    }
    return images.join("\n")
}



Lucullus.maps.ViewMap.prototype.delta = function(x, y) {
    // Calculates the movement required to reach position (x,y)
    return [-this.offset[0] - x, -this.offset[1] - y]
}


Lucullus.maps.ViewMap.prototype.get_center = function() {
    /** returns the current focus (center) of the map */
    var pos = this.get_position()
    var size = this.get_size()
    return [pos[0] + size[0] / 2, pos[1] + size[1] / 2]
}

Lucullus.maps.ViewMap.prototype.get_position_by_absolute = function(x,y) {
    x = x - this.node.offset().left - this.offset[0]
    y = y - this.node.offset().top - this.offset[1]
    return [x,y].slice()
}













/** This is an Ext.Panel which holds a single Lucullus.maps.ViewMap.
    @class Lucullus.gui.MapPanel
    New events: mapReady, mapMove, mapMoved
    New config: controls {}
*/

Lucullus.maps.MapPanel = Ext.extend(Ext.Panel, {
    constructor: function(config) {
        var self = this
        config = config || {}
        Ext.applyIf(config, {
            view: null, // Lucullus.Thing
            map: null,  // Lucullus.maps.ViewMap
            control: {}, // control config
            layout: "fit",
            autoclip: true,
            border: false,
            channel:'default',
        })

        // Initiate the Panel
        Lucullus.maps.MapPanel.superclass.constructor.call(this, config)

        // New events
        this.addEvents(
            "mapReady", // Fired as soon as the map is available
            "mapMoved",
            "mapZoom",
            // Control events (mouse control)
            "ctrlClick", // Parameter: affected map, x, y
            "ctrlDClick", // Parameter: affected map, x, y
            "ctrlMove", // Parameter: affected map, dx, dy
            "ctrlWheel" // Parameter: affected map, wheel delta
        );

        // A mouse control handler. Move only this panel per default.
        this.control = new Lucullus.maps.MapMouseControl()

        // Create the map object as soon as possible
        this.on('render', function() { // Wait for this.body
            if(!this.view) return
            this.view.wait(function() { // Wait for this.view
                this.map = new Lucullus.maps.ViewMap({
                    root: this.body.dom,
                    view: this.view,
                    autoclip: this.autoclip,
                    channel: this.channel
                    })
                this.fireEvent('mapReady', this.map)
            }, this)
        }, this)

        // Start/stop map rendering when panel is shown/hidden
        this.on('hide', function() {
            if(this.map) this.map.stop()
        }, this)
        this.on('show', function() {
            if(this.map) this.map.start()
        }, this)
        this.on('destroy'), function() {
            if(this.map) {
                this.map.destroy()
                this.map = null
            }
        }

        // Initialize mouse controls
        this.on('mapReady', function() {
            this.control.init(this.body, null, this.controlConfig)
            this.control.onMovement = function(dx, dy) {
                self.fireEvent("ctrlMove", self.map, dx, dy)
            }
            this.control.onClick = function(x, y) {
                self.fireEvent('ctrlClick', self.map, x, y)
            }
            this.control.onDClick = function(x, y) {
                self.fireEvent('ctrlDClick', self.map, x, y)
            }
            this.control.onWheel = function(delta) {
                self.fireEvent('ctrlWheel', self.map, delta)
            }
        }, this)

        // Resize the ViewMaps along with the panel 
        this.on('bodyresize', function(){
            if(this.map) {
                var h = this.body.getHeight(true)
                var w = this.body.getWidth(true)
                this.map.setWindowSize(w, h)
            }
        }, this)
    },
    initCtrl: function() {
        // Connect ctrl* events with move and zoom actions.
        this.on('ctrlMove', function(map, x, y) {
            this.move(x, y)
        }, this)
        this.on('ctrlWheel', function(map, delta) {
            if(delta < 0) {
                this.setZoom(this.getZoom() - 1)
            } else if (delta > 0) {
                this.setZoom(this.getZoom() + 1)
            }
        }, this)
    },
    move: function(x, y, noevent) {
        var m = this.map.move(x,y)
        if(!m[0] && !m[1]) return m
        if(!noevent) this.fireEvent('mapMoved', m[0], m[1]);
        return m
    },
    getZoom: function() {
        if(!this.map) return 0
        return this.map.getZoom()
    },
    setZoom: function(level, noevent) {
        if(!this.map) return
        this.map.setZoom(level)
        if(!noevent) this.fireEvent("mapZoom", level)
    },
    // These should move to ViewMap at some pointe
    getPos: function() {
        if(!this.map) return [0, 0]
        return this.map.getPosition()
    },
    setPos: function(x, y, noevent) {
        if(!this.map) return [0, 0]
        var delta = this.map.delta(x, y)
        return this.move(delta[0], delta[1], noevent)
    },
    getSize: function() {
        if(!this.map) return [0, 0]
        return this.map.getSize()
    },
    getMinPos: function() {
        if(!this.map) return [0, 0]
        return [this.map.clipping[0], this.map.clipping[1]]
    },
    getMaxPos: function() {
        if(!this.map) return [0, 0]
        return [this.map.clipping[2], this.map.clipping[3]]
    },
    getWindowSize: function() {
        if(!this.map) return [0, 0]
        return this.map.getWindowSize()
    }
});

Ext.reg('map', Lucullus.maps.MapPanel);

/*
Example for a 2x2 map grid:

// Create resources
var viewTL = api.create('IndexView')
var viewTR = api.create('SequenceResource')
var viewBL = api.create('IndexView')
var viewBR = api.create('SequenceResource')

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
var mapTL = new Lucullus.maps.MapPanel({
  width: 100, view: viewTL, controlConfig: {scaleX: 0, scaleY: 5}
})
var mapTR = new Lucullus.maps.MapPanel({
  flex: 1, view: viewTR, controlConfig: {scaleX: 1, scaleY: 0}
})
var mapBL = new Lucullus.maps.MapPanel({
  width: 100, view: viewBL, controlConfig: {scaleX: 0, scaleY: 0}
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
    slaveMap: twinT, masterMap: twinB, slavePosition: 'top', slaveScaleY: 0
})

twin.initCtrl()
var win = new Ext.Window({width:400, height:300, layout:'fit'})
win.add(twin)
win.show()

*/

/* This panel combines two MapPanels into one (hBox or vBox layout).
   - Mouse controls are redirected from the slave to the master panel.
   - Method calls are reldirected to the master panel.
   - Events of the master panel are repeated.
   - On each move or zoom event, the slave is synced with the master using
     absolute positions and zoom levels.
   In the end, this Panel should behave like a single MapPanel and the slave
   should be invisible. Do not call methods on the slave directly. Calling
   methods on the master should be save.

  Options:
  masterMap: Lucullus.maps.MapPanel.
  slaveMap: Lucullus.maps.MapPanel.
  slavePosition: One of 'left', 'right', 'top' or 'bottom' (default: left)
*/

Lucullus.maps.TwinMapPanel = Ext.extend(Ext.Panel, {
    constructor: function(config) {
        config = config || {}
        Ext.applyIf(config, {
            border: false,
            layoutConfig: { align : 'stretch' },
            slavePosition: 'left',
            slaveScaleX: 1,
            slaveScaleY: 1,
            defaultType: 'map',
            items: []
        })

        if(config.master) config.items[0] = config.master
        if(config.slave) config.items[1] = config.slave

        // Add map objects to hBox layout
        if(config.slavePosition == 'left') {
            config.items = [config.items[1], config.items[0]];
            config.layout = 'hBox'
        } else if(config.slavePosition == 'right') {
            config.layout = 'hBox'
        } else if(config.slavePosition == 'top') {
            config.items = [config.items[1], config.items[0]];
            config.layout = 'vBox'
        } else if(config.slavePosition == 'bottom') {
            config.layout = 'vBox'
        }

        Ext.each(config.items, function() {
            if(!this.width && !this.height && !this.flex) this.flex = 1
        })

        // Initiate the Panel
        Lucullus.maps.TwinMapPanel.superclass.constructor.call(this, config)

        if(config.slavePosition == 'left') {
            this.master = this.items.items[1]
            this.slave  = this.items.items[0]
        } else if(config.slavePosition == 'right') {
            this.master = this.items.items[0]
            this.slave  = this.items.items[1]
        } else if(config.slavePosition == 'top') {
            this.master = this.items.items[1]
            this.slave  = this.items.items[0]
        } else if(config.slavePosition == 'bottom') {
            this.master = this.items.items[0]
            this.slave  = this.items.items[1]
        }



        // Relay control events from child maps to $this.
        this.relayEvents(this.master, ["ctrlClick", "ctrlDClick",
                                          "ctrlMove", "ctrlWheel"])
        this.relayEvents(this.slave,  ["ctrlClick", "ctrlDClick",
                                          "ctrlMove", "ctrlWheel"])
        // Relay action events from data map to $this.
        this.relayEvents(this.master, ["mapReady", "mapMoved", "mapZoom"])

        // Sync index with data map using absolute positions.
        this.on('mapMoved', function() {
            var pos = this.master.getPos()
            this.slave.setPos(pos[0]*this.slaveScaleX,
                              pos[1]*this.slaveScaleY,
                              true) // Do not emit events
        }, this)
        this.on('mapZoom', function(z) {
            this.slave.setZoom(z, true) // Do not emit events
        }, this)

        // Deligate MapPanel API to data map.
        Ext.each(['move', 'getZoom', 'setZoom', 'getPos', 'setPos'], function(name){
            this[name] = this.master[name].createDelegate(this.master)
        }, this)

        // Resize remaining panels on show/hide events.
        this.master.on('show', this.syncSize, this)
        this.master.on('hide', this.syncSize, this)
        this.slave.on('show', this.syncSize, this)
        this.slave.on('hide', this.syncSize, this)

    }, initCtrl: function() {
        // Connect ctrl* events with move and zoom actions.
        // Info: ctrl* events come from both master and slave.
        //       Move actions go to master child only, but slave is synched
        //       anyway.
        this.on('ctrlMove', function(map, x, y) {
            this.move(x, y)
        }, this)
        this.on('ctrlWheel', function(map, delta) {
            if(delta < 0) {
                this.setZoom(this.getZoom() - 1)
            } else if (delta > 0) {
                this.setZoom(this.getZoom() + 1)
            }
        }, this)
    }, resizeChild: function(w, h) {
        /* Resize the non-flexed child.  */
        var child = this.master.flex ? this.slave : this.master;
        if(typeof w == 'number') {
            child.setWidth(w);
            child.width = w; // ExjJS Bug: Required by some layouts
        }
        if(typeof h == 'number') {
            child.setHeight(h);
            child.height = h; // ExjJS Bug: Required by some layouts
        }
        this.syncSize();
    }
})

Ext.reg('twinmap', Lucullus.maps.TwinMapPanel);









/* This object recognizes drag-move-drop gestures starting from a specific
   HTML node. By default, every mousemove event during the gesture triggers
   the abstract onMovement() event handler. By using setInterval() with a
   number greater than 0, the onMovement() method is called independently from
   actual mouse movements.
   
   Movements can be scaled. To disable left-right movement on a vertical
   control, use scale factors of (0.0, 1.0).
   
   getMovement() returns the movement relative to the last call of that
   method. getMovement(true) does not reset the value. getDistance() returns
   the position of the mouse pointer relative to the starting point.
   Before a drag and after a drop, both methods return [0,0].
  */

Lucullus.maps.MapMouseControl = Ext.extend(Ext.dd.DragDrop, {
    lastX: 0,
    lastY: 0,
    currentX: 0,
    currentY: 0,
    dragging: false,
    cframe: null,
    scaleX: 1,
    scaleY: 1,
    applyConfig: function() {
        Lucullus.maps.MapMouseControl.superclass.applyConfig.call(this);
        if(typeof this.config.scaleX == 'number') this.scaleX = this.config.scaleX;
        if(typeof this.config.scaleY == 'number') this.scaleY = this.config.scaleY;
        if(typeof this.config.interval == 'number') this.interval = this.config.interval;
    },
    onAvailable: function() {
        Ext.EventManager.on(this.id, "click", function(e, node) {
            var xy = e.getXY()
            this.onClick(xy[0], xy[1])
            e.stopEvent()
        }, this);
        Ext.EventManager.on(this.id, "dblclick", function(e, node) {
            var xy = e.getXY()
            this.onDClick(xy[0], xy[1])
            e.stopEvent()
        }, this);
        Ext.EventManager.on(this.id, 'mousewheel', function(e, node){
            this.onWheel(e.getWheelDelta())
            e.stopEvent()
        }, this)

    },
    startDrag: function(x, y) {
        this.dragging = true;
        this.lastX = x;
        this.lastY = y;
        this.currentX = x;
        this.currentY = y;
        if(!this.cframe) {
            this.cframe = document.createElement("div");
            this.cframe.style.position   = "absolute";
            this.cframe.style.visibility = "hidden";
            this.cframe.style.width      = '100%'
            this.cframe.style.height     = '100%'
            this.cframe.style.zIndex     = 99999;
            document.body.insertBefore(this.cframe, document.body.firstChild);
        }
        /*
        if(!this.task) {
            // Trigger onMovement() every X ms and stop after the drag
            this.task = {
                run: function() {
                    this.onMovement();
                    if(!this.dragging) {
                        Ext.TaskMgr.stop(this.task);
                    }
                },
                interval: this.interval,
                scope: this
            }
        }
        if(this.interval) {
            Ext.TaskMgr.start(this.task);
        }*/
        this.cframe.style.cursor     = "move";
        this.cframe.style.visibility = "visible";
    },
    onDrag: function(e) {
        this.currentX = e.getPageX();
        this.currentY = e.getPageY();
        if(!this.interval) // Without an interval, we use real time tracking
        var xy = this.getMovement()
        this.onMovement(xy[0], xy[1])
    },
    endDrag: function(e) {
        this.dragging = false;
        this.cframe.style.cursor     = "";
        this.cframe.style.visibility = "hidden";
        //if(this.interval) Ext.TaskMgr.stop(this.task);
    },
    onMovement: function(x, y) {
        // Override this
    },
    onClick: function(x, y) {
        // Override this
    },
    onDClick: function(x, y) {
        // Override this
    },
    onWheel: function(delta) {
        // overwrite this
    },
    getMovement: function(noreset) {
        /* Return the movement since the last call of thie method. */
        if(!this.dragging) return [0,0];
        var x = (this.currentX-this.lastX) * this.scaleX
        var y = (this.currentY-this.lastY) * this.scaleY
        if(!noreset) {
            this.lastX = this.currentX;
            this.lastY = this.currentY;
        }
        return [x, y]
    },
    getDistance: function() {
        /* Return the distance from the start position. */
        if(!this.dragging) return [0,0];
        var x = (this.currentX-this.startX) * this.scaleX
        var y = (this.currentY-this.startY) * this.scaleY
        return [x, y]
    },
    setInterval: function(n) {this.interval = n} //TODO: No Effect!
})
