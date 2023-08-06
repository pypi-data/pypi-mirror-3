import os, os.path
import re
import time
import cgi
import rfc822
import bottle
from bottle import HTTPResponse, HTTPError, route, validate, abort
import logging
import pybiomaps.render
import pybiomaps.render.geometry
import pybiomaps.resource
import tempfile

log = logging.getLogger(__name__)

###############################################################################
## Configuration ###############################################################
###############################################################################

cfg = dict()
cfg['path.base'] = os.path.abspath(os.path.dirname(__file__))
cfg['path.views'] = os.path.join(cfg['path.base'], 'views')
cfg['path.db'] = '/tmp/pybiomaps'
cfg['path.static'] = [os.path.join(cfg['path.base'], 'static')]
cfg['api.strip'] = ''
cfg['api.keys'] = ['test']
cfg['debug'] = False

def add_static_dir(path):
    cfg['path.static'].append(os.path.abspath(path))

rdb = pybiomaps.resource.Pool(cfg['path.db'])

def config(**config):
    for key in config:
        if '_' in key:
            config[key.replace('_','.')] = config[key]
            del config[key]
    cfg.update(config)
    if 'path.db' in config:
        if not os.path.exists(cfg['path.db']):
            os.makedirs(cfg['path.db'])
        rdb.savepath = cfg['path.db']
        log.debug("Ressource path: %s", rdb.savepath)
    if 'api.strip' in config:
        app.rootpath = cfg['api.strip']
    if 'path.views' in config:
        bottle.TEMPLATE_PATH.insert(0, cfg['path.views'])
        log.debug("Template path: %s", bottle.TEMPLATE_PATH)
    if 'debug' in config:
        bottle.debug(True)

bottle.TEMPLATE_PATH.insert(0, cfg['path.views'])

err = dict()
err['no key'] = 'You have to provide a valid api key'
err['unknown type'] = 'The requestet resource type is not available.'
err['no resource'] = 'The requested resource could not been found.'
err['setup error'] = 'Resource setup failed'
err['query error'] = 'Resource query failed'

app = bottle.Bottle()

def is_python_name(name):
    return bool(re.match('^[a-zA-Z_]\w*$', name))

def load_plugin(path):
    rdb.install_module(path)

def start(*a, **k):
    log.info("Starting server: %s", repr((a, k)))
    try:
        bottle.run(app=app, *a, **k)
    finally:
        rdb.cleanup(-1)

def apierr(code, **args):
    args['error'] = code
    if 'detail' not in args:
        args['detail'] = err.get(code, 'Undocmented error')
    log.warning("API error: %s" % repr(args))
    return args

def needs_apikey(func):
    def wrapper(*a, **ka):
        key = bottle.request.POST.get('apikey', None)
        if key not in cfg['api.keys']:
            return apierr('no key')
        del bottle.request.POST['apikey']
        return func(*a, **ka)
    return wrapper

def needs_ressource(func):
    def wrapper(*a, **ka):
        rid = int(ka.pop('rid', -1))
        r = rdb.fetch(int(rid))
        if not r:
            return apierr('no resource', id=int(rid))
        return func(*a, ressource=r, **ka)
    return wrapper

class ExtJSFramePlugin(object):
    ''' Extjs iframe hack needs special json handling '''
    def apply(self, func, context):
        def wrapper(*a, **ka):
            rv = func(*a, **ka)
            if '_extjs_frame' in bottle.request.forms:
                return cgi.escape(bottle.json_dumps(rv))
            else:
                return rv
        return wrapper

app.install(ExtJSFramePlugin())

def api_response(ressource):
    return {"id": ressource.id,
            "type": ressource.__class__.__name__,
            "state": ressource.getstate(),
            "methods": ressource.getapi()}


@app.post('/api/create', apply=[needs_apikey])
def create():
    rdb.cleanup(60*60)
    options = {}
    for key in bottle.request.POST:
        if not is_python_name(key): continue
        values = bottle.request.forms.getall(key)
        options[key] = values[0] if len(values) == 1 else values
    log.debug('CREATE %r', options)
    try:
        r = rdb.create(options.pop('type', '<unknown>'))
        if options: r.setup(**options)
    except pybiomaps.resource.ResourceTypeNotFound:
        return apierr('unknown type', types=rdb.plugins.keys())
    except pybiomaps.resource.ResourceSetupError, e:
        return apierr('setup error', id=rid, detail=e.args[0])
    return api_response(r)


@app.post('/api/r:rid#[0-9]+#/setup', apply=[needs_apikey, needs_ressource])
def setup(ressource):
    """ Accesses the resource configuration and functions """
    options = {}
    for key in bottle.request.POST:
        if not is_python_name(key): continue
        values = bottle.request.forms.getall(key)
        options[key] = values[0] if len(values) == 1 else values
    log.debug('SETUP %r', options)
    try:
        ressource.setup(**options)
        return api_response(ressource)
    except pybiomaps.resource.ResourceSetupError, e:
        return apierr('setup error', id=ressource.id, detail=e.args[0])


@app.post('/api/r:rid#[0-9]+#/:query#[a-z_]+#',
          apply=[needs_apikey, needs_ressource])
def query(ressource, query):
    """ Accesses the resource configuration and functions """
    options = dict(bottle.request.POST.dict)
    for key in options:
        if len(options[key]) == 1:
            options[key] = options[key][0]
    response = {'request': query, 'options': options}
    try:
        response['result'] = ressource.query(query, **options)
    except pybiomaps.resource.ResourceQueryError, e:
        response['id'] = ressource.id
        response['detail'] = e.args[0]
        return apierr('query error', **response)
    response.update(api_response(ressource))
    return response


@app.route('/api/r:rid#[0-9]+#/help/:query#[a-z_]+#', apply=[needs_ressource])
def help(ressource, query=None):
    api = ressource.getapi()
    if query in api:
        doc = getattr(ressource, "api_%s"%s).__doc__ or 'Undocumented'
        return dict(id=ressource.id, query=query, help=doc)
    else:
        return apierr('query error', id=ressource.id, detail='Undefined')


@app.route('/api/r:rid#[0-9]+#', apply=[needs_ressource])
def info(ressource):
    return api_response(ressource)


@app.route('/api/r:rid#[0-9]+#/tiles/:w#[0-9]+#x:h#[0-9]+#/:x#-?[0-9]+#/:y#-?[0-9]+#/:z#-?[0-9]+#/:channel.:format#.*#')
def render_tiles(rid, channel, x, y, z, w, h, format):
    return render(rid, channel, int(x)*int(w), int(y)*int(h), int(z)*10, w, h, format)


@app.route('/api/r:rid#[0-9]+#/:channel#[a-z]+#-x:x#-?[0-9]+#y:y#-?[0-9]+#z:z#-?[0-9]+#w:w#[0-9]+#h:h#[0-9]+#.:format#.*#')
def render(rid, channel, x, y, z, w, h, format):
    r = rdb.fetch(int(rid))
    if not r:
        return HTTPError(404, 'Resource not found')
    if not isinstance(r, pybiomaps.resource.BaseView):
        return HTTPError(404, "This resource has no visuals")
    x,y,z,w,h = [int(n) if n else 0 for n in (x,y,z,w,h)]
    z = float(z)
    if w == h == 0:
        w, h = r.size()
        if z != 1.0:
            w /= 2**(-z/10)
            h /= 2**(-z/10)
    if w < 16 or h < 16: 
        return HTTPError(500, "Image size to small")
    elif w > 10240 or h > 10240:
        return HTTPError(500, "Image size to big")
    if format not in ('png', 'pdf', 'svg'):
        return HTTPError(500, "Image format not supported.")
    # Send cached file to client
    fdict = dict(rid=rid, channel=channel, mtime=r.mtime,
                 x=x, y=y, z=z, w=w, h=h, ext=format)
    fname = '%(rid)s.images/%(channel)s-%(mtime)d/x%(x)dy%(y)dz%(z)dw%(w)dh%(h)d.%(ext)s'
    filename = os.path.join(cfg['path.db'], fname % fdict)
    
    if not os.path.exists(filename) or cfg['debug']:
        try: os.makedirs(os.path.dirname(filename))
        except OSError: pass
        try:
            area = pybiomaps.render.geometry.Area(left=x, top=y, width=w, height=h)
            rc = pybiomaps.render.Target(area=area, format=format, target=filename,
                                        scale=2**(-z/10), channel=channel)
            r.render(rc)
            rc.save()
        except (IOError,OSError):
            log.exception("Could not create cache image file %s", filename)
            raise
        except Exception, e:
            log.exception("Rendering failed!")
            raise
    bottle.response.headers['X-Copyright'] = "Max Planck Institut (MPIBPC Goettingen) Marcel Hellkamp"
    bottle.response.headers['Expires'] = rfc822.formatdate(time.time() + 60*60*24)
    return bottle.static_file(filename=os.path.basename(filename), root=os.path.dirname(filename))


@app.route('/')
def index():
    return bottle.template('seqgui')


@app.route('/tpl_:name')
def named_index(name):
    return bottle.template(name)


@app.route('/clean')
def cleanup():
    rdb.cleanup(10)
    return "done"


@app.route('/:filename#.+#')
def static(filename):
    for path in cfg['path.static']:
        if os.path.exists(os.path.join(path, filename)):
            return bottle.static_file(filename=filename, root=path)
    abort(404, "File not found")
