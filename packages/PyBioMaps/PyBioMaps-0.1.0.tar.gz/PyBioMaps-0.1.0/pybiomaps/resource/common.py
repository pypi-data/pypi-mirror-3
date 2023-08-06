from pybiomaps.resource import BaseView
import cairo
import math

class IndexView(BaseView):
    def prepare(self):
        self.blocksize = 12
        self.fontcolor = 'black'
        self.source = None
        self.names = []

    def size(self):
        w = max([len(i) for i in self.names] + [0]) * self.blocksize
        h = len(self.names) * self.blocksize
        return (w, h)

    def getstate(self):
        s = super(IndexView, self).getstate()
        s['rows'] = len(self.names)
        return s

    def sleep(self):
        self.names = []

    def wakeup(self):
        if self.source is not None:
            self.names = self.pool.fetch(self.source).get_index()

    def setup(self, **options):
        self.blocksize = int(options.get('blocksize', self.blocksize))
        if 'source' in options and options['source'].isdigit():
            self.source = int(options.get('source'))
            self.names = self.pool.fetch(self.source).get_index()

    def render(self, rc):
        # Shortcuts
        c = rc.context

        # The font should look the same regardless of scale factor
        blocksize = rc.scale * self.blocksize
        # For high zoom levels this means we have to skip some lines.
        skip = int(math.ceil(blocksize/self.blocksize))-1

        # Rows to consider
        row_first = int(math.floor(float(rc.area.top) / self.blocksize))
        row_first -= row_first % (skip+1)
        row_last  = int(math.ceil(float(rc.area.bottom) / self.blocksize))
        row_last += row_last % (skip+1)
        row_last  = min(row_last, len(self.names)-1)
        
        # Configuration
        c.select_font_face("mono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        options = cairo.FontOptions()
        #fo.set_hint_metrics(cairo.HINT_METRICS_ON)
        #fo.set_hint_style(cairo.HINT_STYLE_NONE)
        options.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        c.set_font_options(options)
        c.set_font_size(blocksize * 0.9)
        real_lineheight = c.font_extents()[1]

        # Fill the background with #ffffff
        rc.clear(color='white')
        rc.set_color(self.fontcolor)
        font_extends = c.font_extents()
        for row in range(row_first, row_last+1, skip+1):
            name = self.names[row] + (' ...' if skip > 1 else '')
            y  = self.blocksize * row # upper edge of line
            y += float(self.blocksize*(skip+1)) / 2 # middle if line
            y += blocksize/2
            x = 0
            c.move_to(x, y)
            c.show_text(name)
        return self


class RulerView(BaseView):
    ''' TODO: dublictate in plugins/ruler'''
    def prepare(self):
        self.mode       = 't'
        self.nullvalue  = 0
        self.scale      = 1
        self.fontsize   = 10
        self.fontcolor  = 'black'
        self.width      = 15
        self.digits     = 0

    def setup(self, **options):
        self.mode       = options.get('mode', self.mode)[0]
        for name in ('nullvalue', 'scale'):
            if name not in options: continue
            value = options[name]
            value = float(value) if '.' in value else int(value)
            setattr(self, name, value) 
        self.touch()

    def size(self):
        return (2**32, 2**32)

    def offset(self):
        return (-2**31, -2**31)

    def render(self, rc):
        c = rc.context
        fontsize = self.fontsize * rc.scale
        scale = rc.scale
        px = scale # size of a real pixel
        grid = 10 * max(1, int(px)) # size of grid step in pixel
        width = self.width
        flip = False

        # Calculate minimum and maximum pixel values (along the axis)
        if rc.channel in ('top', 'default'):
            px_min, px_max = rc.area.left, rc.area.right
            if rc.area.top > self.width*px: return
        elif rc.channel == 'right':
            px_min, px_max = rc.area.top, rc.area.bottom
            if rc.area.left > self.width*px: return
            rc.context.rotate(0.5 * math.pi)
            rc.context.translate(0,-self.width*px)
        elif rc.channel == 'bottom':
            px_min, px_max = rc.area.left, rc.area.right
            if rc.area.top > self.width*px: return
            flip = True
        elif rc.channel == 'left':
            px_min, px_max = rc.area.top, rc.area.bottom
            if rc.area.left > self.width*px: return
            rc.context.rotate(0.5 * math.pi)
            rc.context.translate(0,-self.width*px)
            flip = True

        rc.clear('white')
        # Ths visible grid is between first and last
        # Both first and last are in the grid lines
        first = int(px_min - px_min % grid)
        last = int(px_max + grid - px_max % grid)

        rc.set_color(self.fontcolor)

        # xargs is limited to int but we may have long here.
        mark = first-grid
        while mark < last+grid:
            if mark % (grid*10) == 0:
                if flip: c.rectangle(mark-px, 0, 3*px, 4*px)
                else: c.rectangle(mark-px, width*px-4*px, 3*px, 4*px)
            else:
                if flip: c.rectangle(mark, 0, 1*px, 2*px)
                else: c.rectangle(mark, width*px-2*px, 1*px, 2*px)
            mark += grid
        c.fill()

        fo = cairo.FontOptions()
        fo.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        c.set_font_options(fo)
        c.set_font_size(fontsize)
        font_extends = c.font_extents()
        font_height = font_extends[3]

        grid *= 10
        first = px_min
        first -= first % grid
        last = px_max
        last += grid - last % grid

        # Calculate minimum number of fractional digits to show per 10-grid
        digits = 1
        while -1 < grid*self.scale*10**digits < 1:
            digits += 1

        mask = '%%.%df' % digits if digits else '%d'
        fname = mask % (self.nullvalue+first*self.scale)
        lname = mask % (self.nullvalue+last*self.scale)
        overlap = 0.5 * max(c.text_extents(name)[2] for name in (fname, lname))
        # To big numbers...
        if overlap*2 > grid: return
        # Roud up to grid
        overlap += grid - overlap % grid
        # xargs is limited to int but we may have long here.
        mark = first - overlap
        while mark < last + overlap:
            value = self.nullvalue + mark * self.scale
            if not digits: value = round(value)
            name = mask % value
            text_width, text_height = c.text_extents(name)[2:4]
            if flip: c.move_to(mark - text_width/2.0, width*px-px)
            else: c.move_to(mark - text_width/2.0, text_height+px)
            c.show_text(name)
            mark += grid
        return self
