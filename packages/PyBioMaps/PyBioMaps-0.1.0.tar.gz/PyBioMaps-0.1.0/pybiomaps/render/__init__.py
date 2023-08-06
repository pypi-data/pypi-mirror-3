import cairo
import math
from pybiomaps.render.geometry import Area
from pybiomaps.render.color import pick as colorpick
from cStringIO import StringIO

class Target(object):
    """
        Represents a single render area (AOI: Area of Interest) and provides
        georemtry and cairo helper methods. This is passed to plugins on a
        BaseView.render() call.
    """
    def __init__(self, area, format='png', scale=1.0, channel='default', target=None):
        assert isinstance(area, Area)
        self.area = area
        self.scale = scale
        self.channel = channel
        if scale <> 1.0:
            self.area.scale(scale, scale)
        self.format = format.lower()
        self.target = target
        self._surface = None
        self._context = None

    @property
    def surface(self):
        """ A cairo surface """
        if not self._surface:
            w = int(self.area.width / self.scale)
            h = int(self.area.height / self.scale)
            if self.format in ('png'):
                self._surface = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
            elif self.format in ('pdf'):
                self._surface = cairo.PDFSurface(self.target, w, h)
            elif self.format in ('svg'):
                self._surface = cairo.SVGSurface(self.target, w, h)
            else:
                raise NotImplementedError("Format %s is not supported." % self.format)
        return self._surface

    @property
    def context(self):
        """ A cairo context translated to the AOI position """
        if not self._context:
            self._context = cairo.Context(self.surface)
            self._context.scale(1.0/self.scale, 1.0/self.scale)
            self._context.translate(-self.area.left, -self.area.top)
        return self._context

    def save(self):
        """ Renderes image to a byte stream """
        if self.format == 'png':
            self.surface.write_to_png(self.target)
        elif self.format in ('pdf', 'svg'):
            self.surface.finish()
        else:
            raise NotImplementedError("Format %s is not supported." %
                                      self.format)

    def clear(self, color='white'):
        """ Clears the image (color fill) """
        self.set_color(color)
        self.context.paint()

    def set_color(self, color):
        """ Clears the image (color fill) """
        c = colorpick(color)
        if c:
            self.context.set_source_rgba(*c)

    def draw_stripes(self, width=100, c1='white', c2='gray'):
        '''Rendert einen gestreiften Hintergrund'''
        context = self.context
        area = self.area
        # Compute start color
        c = (c1, c2)
        ci = int(math.floor(float(area.left) / width))
        offset = - (area.left % width)
        while offset < area.width:
            self.set_color(c[ci%2])
            context.rectangle(area.left+offset, area.top, width, area.height)
            context.fill()
            offset += width
            ci += 1
