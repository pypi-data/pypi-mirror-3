/**
 * Lucullus Namespace
 */

var Lucullus = new Object();

Lucullus.DEBUG = false
Lucullus.log = function(){} // no-op

Lucullus.debug = function() {
    /* This is debugging code and only works with Firefox FireBug installed and active */
    if(console && console.log && Ext) {
        Lucullus.log = console.log
        Ext.util.Observable.prototype.fireEvent = Ext.util.Observable.prototype.fireEvent.createInterceptor(function() {
            console.log(arguments);
            return true;
        });
    } else {
        alert("Could not find ExtJS or a console to log to. Debug mode requires FireBug or a similar addon.")
    }
}

Lucullus.dom = {}
Lucullus.dom.getPageOffset = function(obj) {
    var curleft = curtop = 0;
    while (obj = obj.offsetParent) {
        curleft += obj.offsetLeft;
        curtop += obj.offsetTop;
    };
    return {left: curleft, top: curtop};
}

Lucullus.dom.getInnerSize = function(obj) {
    var el = Ext.get(obj)
    return {width: el.getWidth(true), height: el.getHeight(true)}
}




/* Lucullus.Thing is a RESTful API to create, change and query remote objects.
It is a mixture between an online data store and an RPC client. */

Lucullus.Thing = Ext.extend(Ext.util.Observable, {
    constructor: function(type, config) {
        /* Create a new remote resource.
           Required options:
             - apikey: A valid API key
             - server: The server URL
           If you specify an 'id', the resource is not created, but fetched.
        */
        if (!(this instanceof arguments.callee))
             throw new Error("Constructor called as a function");
        this.id = null      // Reaource ID
        this.actions = []   // RPC methods
        this.result = {}    // Result of last query call
        this.state = {}     // Current state of the resource
        this.errors = []    // Stack of errors
        this.type = type    // Resource class name.
        this.queue = []     // Request queue.
        this.apikey = 'guest'
        this.server = 'http://example.com/'
        
        this.addEvents('create', // Fired after successfull remote object creation
                       'change', // Fired on each change to the remote state (newer mtime)
                       'answer', // Fired on an answer to a query
                       'result', // Fired if the answer contains a 'result' field 
                       'done',   // Fired if requst queue is empty.
                       'error')  // Fired on errors
        Ext.apply(this, config)
        Lucullus.Thing.superclass.constructor.call(this);
        // Create new or fetch existing resource
        if(!this.id) {
            this.query('create', {type: this.type})
            this.id = 'ID_UNKNOWN'
        } else if(!this.state.mtime) {
            this.update() // Get current state
        }
    },
    addListener: function(eventName, fn, scope, o) {
        var rv = Lucullus.Resouce.superclass.addListener.call(this, eventName, fn, scope, o)
        this.tick()
        return rv
    },
    query: function(action, options, callback, scope) {
        /* Call an action on a remote resource. The returned object fires
           events related to this query.
           To enable form submission, add a 'form' key to the options.
           */
        // Build URL
        var uri = this.server
        if(this.id && action) uri = uri + 'r' + this.id + '/' + action
        else if(this.id)  uri = uri + 'r' + this.id
        else if(action) uri = uri + action

        // Create and preconfigure query object
        var q = new Ext.data.Connection({url: uri, method: action?'POST':'GET'})
        q.tosend = {params: options||{}} // Custom atribute. Used in this.tick()
        q.tosend.params.apikey = this.apikey
        // Special-case form uploads
        if(q.tosend.params.form) {
            q.tosend.form = q.tosend.params.form;
            delete q.tosend.params.form;
        }
        // Extend q with new events
        q.addEvents('create', 'change', 'answer', 'result', 'error')
        // Fire new 'answer' and 'error' events from standard events
        q.on('requestcomplete', function(self, resp) {
            var data = Ext.decode(resp.responseText);
            if(!data) data = {error: 'No Data'}
            if(data.error) q.fireEvent('error', this, data);  
            else q.fireEvent('answer', this, data);
        }, this)
        q.on('requestexception', function() {
            q.fireEvent('error', this, {error: 'Request failed (the hard way).'});
        }, this)
        // Use 'error' and 'answer' events to update $this.
        // These are called first. Other callbacks will see an updated $this.
        q.on('error', function(self, data) {
            this.errors.push({query: this.queue.shift(), data:data})
            this.tick()
        }, this)
        q.on('answer', function(self, data) {
            var old_mtime = this.state.mtime || 0
            var old_id = this.id
            if(data.id) this.id = data.id
            if(data.type) this.type = data.type
            if(data.actions) this.actions = data.methods
            if(data.state) this.state = data.state
            if(data.result) this.result = data.result
            // Fire more specific events
            if(old_id != this.id) q.fireEvent('create', this)
            if(old_mtime < this.state.mtime) q.fireEvent('change', this)
            if(data.result) q.fireEvent('result', this, data.result)
            this.queue.shift()
            this.tick()
        }, this)
        // Repair queries that were issued too early
        q.on('create',function() {
            Ext.each(this.queue, function(n) {
                n.url = n.url.replace('ID_UNKNOWN',''+this.id)
            }, this)
        }, this)
        // Relay events from q to $this.
        this.relayEvents(q, ['create', 'change', 'answer', 'result', 'error',
                             'beforerequest', 'requestcomplete',
                             'requestexception'])
        // Add specified callback if present
        if(callback) this.on('answer', callback, scope)
        // Continue with next query
        this.queue.push(q)
        this.tick()
        return q
    },
    update: function(callback, scope) {
        // Get current state from server
        return this.query(null, null, callback, scope)
    },
    tick: function() {
        /* Send next query, but only of no other query is running. */
        if(this.queue.length == 0) {
            this.fireEvent('done', this);
            return;
        }
        if(this.queue[0].isLoading()) return;
        this.queue[0].request(this.queue[0].tosend)
    },
    wait: function(callback, scope, options) {
        /* Similar to this.on('done', callback[, scope]), but:
           - fires immediately if no queries are in the queue and the Thing
             is created already.
           - fires only once per callback. */
        options = options || {single: true};
        if(this.queue.length > 0 || ! this.state.mtime)
            this.on('done', callback, scope, options);
        else if(scope)
            callback.call(scope, this);
        else
            callback(this);
    },
    image: function(channel, x, y, z, w, h, format) {
        if(x === undefined) x = 0
        if(y === undefined) y = 0
        if(z === undefined) z = 0
        if(w === undefined) w = 256
        if(h === undefined) h = 256
        if(format === undefined) format = 'png'
        if(w === 'full') w = Math.ceil(this.state.size[0] * Math.pow(2, z/10))
        if(h === 'full') h = Math.ceil(this.state.size[1] * Math.pow(2, z/10))
        if(z === 'fit') {
            var z1 = Math.log(Math.pow(w/this.state.size[0], 10)) / Math.LN2
            var z2 = Math.log(Math.pow(h/this.state.size[1], 10)) / Math.LN2
            z = Math.ceil(Math.min(z1, z2))
        }
        if(z === NaN || w === NaN || h === NaN) return

        return self.server+'r'+this.id+'/'+channel+'-x'+x+'y'+y+'z'+z+
               'w'+w+'h'+h+'.'+format+'?mtime='+this.state.mtime
    }
})

/* Helper to create multiple Things with similar options (e.g. apikey and
   server). Usage:
   
   var api = Lucullus.ThingFactory({apikey:'...', server:'...'})
   var res1 = api.create('ResourceType')
   var res2 = api.create('ResourceType', {additional:'options'})
*/

Lucullus.ThingFactory = function(options) {
    this.options = options || {}
    this.create = function(type, options, callback, scope) {
        options = options || {}
        options.server = options.server || this.options.server
        options.apikey = options.apikey || this.options.apikey
        return new Lucullus.Thing(type, options, callback, scope)
    }
    return this
}
