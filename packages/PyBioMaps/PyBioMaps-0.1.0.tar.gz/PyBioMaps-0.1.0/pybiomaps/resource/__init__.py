import pickle as pickle
import inspect
import time
import os.path
import sys
import logging
import threading

log = logging.getLogger(__name__)

class ResourceError(Exception): pass
class ResourceNotFound(ResourceError): pass
class ResourceTypeNotFound(ResourceError): pass
class ResourceSetupError(ResourceError): pass
class ResourceQueryError(ResourceError): pass

class Pool(object):
    """ Factory to create, store and manage resource instances."""
    def __init__(self, savepath):
        self.savepath = savepath
        self.plugins = dict() # Classes
        self.db = dict() # Instances
        self.depts = {} # rid->[rid, rid, ...] mapping
        self.savelock = threading.Lock()

    def install(self, cls):
        ''' Install a plugin '''
        if not isinstance(cls, type):
            raise TypeError('Plugin must be a class.')
        if not issubclass(cls, BaseResource):
            raise TypeError('Plugin must implement BaseResource.')
        if cls.__name__ in self.plugins:
            if cls != self.plugins[cls.__name__]:
                raise TypeError('Plugin name not unique.')
            return
        log.info("Loaded plugin %s.", repr(cls))
        self.plugins[cls.__name__] = cls

    def install_module(self, module):
        ''' Install all plugins from a module '''
        if not inspect.ismodule(module):
            __import__(module)
            module = sys.modules[module]
        for name, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, BaseResource):
                self.install(cls)

    def get_savepath(self, rid):
        return os.path.join(self.savepath, "%d.res" % rid)

    def create(self, plugin):
        ''' Create a new resource '''
        if plugin not in self.plugins:
            raise ResourceTypeNotFound('Plugin %s not available' % plugin)
        res = self.plugins[plugin](self)
        rid = id(res)
        while rid in self.db or os.path.exists(self.get_savepath(rid)):
            rid += 1
        self.db[rid] = res
        res.id = rid
        res.prepare()
        res.touch()
        return res

    def cleanup(self, timeout=60*60):
        ''' Save resources older than timeout in seconds. '''
        for rid, res in self.db.items():
            if res.atime < time.time() - timeout:
                self.save(rid)

    def save(self, rid):
        ''' Save a resource to disk. '''
        with self.savelock:
            res = self.db.pop(rid, None)
            fname = self.get_savepath(rid)
            if res:
                res.touch()
                res.sleep()
                with open(fname, 'wb') as fp:
                    pickle.dump(res, fp, -1)
        return fname

    def fetch(self, rid):
        ''' Load a resource (from disk if necessary). '''
        with self.savelock:
            if rid not in self.db:
                fname = self.get_savepath(rid)
                if not os.path.exists(fname):
                    return None
                with open(fname, 'rb') as fp:
                    res = pickle.load(fp)
                    res.pool = self
                    res.id = rid
                    res.wakeup()
                    res.touch()
                    self.db[rid] = res
            return self.db[rid]






class BaseResource(object):
    """ An empty cache-, pick- and saveable data container bound to a session. """

    def __init__(self, pool):
        self.mtime = time.time()
        self.atime = time.time()
        self.id = -1
        self.pool = pool

    def touch(self, mtime = True):
        """ Mark the resource as accessed or modified """
        if mtime:
            self.mtime = time.time()
        self.atime = time.time()

    def getapi(self):
        return [c[4:] for c in dir(self) if c.startswith('api_') and callable(getattr(self, c))]
        #TODO use inspect

    def __getstate__(self):
        self.sleep()
        dct = self.__dict__.copy()
        for key in ['pool']:
            del dct[key]
        return dct

    def getstate(self):
        """ Should return a dict with some infos about this resource """
        return {'mtime':self.mtime, 'atime':self.atime, 'methods':self.getapi(), 'id':self.id}

    def sleep(self):
        """ Called just before the resource is pickled. """
        pass

    def wakeup(self):
        """ Called just after the resource is unpickled. """
        pass

    def prepare(self):
        """ Called on resource creation """
        pass

    def setup(self, **options):
        ''' May change the resources state but does not return anything '''
        pass

    def query(self, name, **options):
        ''' May change the resources state and returns a result dict '''
        try:
            c = getattr(self, "api_" + name)
        except (AttributeError), e:
            raise ResourceQueryError("Resource %s does not implement %s()" % (self.__class__.__name__, name))
        # Parameter testing
        provided = set(options.keys())
        available, onestar, twostar, defaults = inspect.getargspec(c)
        available.remove('self')
        if not defaults:
            requied = set(available)
        else:
            requied = set(available[0:-len(defaults)])
        available = set(available)
        missing = requied - provided
        if missing:
            raise ResourceQueryError('Missing arguments: %s' % ','.join(missing))
        unknown = provided - available
        if unknown and not twostar:
            raise ResourceQueryError('Unknown arguments: %s' % ','.join(unknown))
        self.touch(False)
        return c(**options)






class BaseView(BaseResource):
    def size(self):
        """ Should return the absolute size of the drawable area in pixel. """
        return (0,0)

    def offset(self):
        """ Should return the (x,y) offset of the drawable area in pixel. """
        return (0,0)

    def getstate(self):
        state = super(BaseView, self).getstate()
        w, h = self.size()
        ox, oy = self.offset()
        state.update({'offset':[ox, oy], 'size':[w, h]})
        return state

    def render(self, ra):
        """ Renders into a RenderArea cairo context. """
        pass







class TextResource(BaseResource):
    def prepare(self):
        self.source = None
        self.ctype = 'text/plain'
        self.coding = 'utf8'
        self.data = None
    
    def setup(self, **options):
        self.source = self.options.get('source', self.source)
        self.ctype = self.options.get('content_type', self.ctype)
        self.coding = self.options.get('coding', self.coding)
        if self.source: self.load(self.source)

    def load(self, source):
        if source.startswith("http://"):
            try:
                self.data = urllib2.urlopen(source, None).read()
            except (urllib2.URLError, urllib2.HTTPError), e:
                raise ResourceQueryError('Faild do open URI: %s' % source)
        else:
            raise ResourceQueryError('Unsupported protocol or uri syntax: %s' % source)
        return {'size': self.size}

        