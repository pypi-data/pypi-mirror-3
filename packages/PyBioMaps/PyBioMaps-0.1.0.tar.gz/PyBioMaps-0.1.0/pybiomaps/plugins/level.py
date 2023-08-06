#!/usr/bin/env python
# encoding: utf-8
"""
plugin_seq.py

Created by Marcel Hellkamp on 2009-01-20.
Copyright (c) 2008 Marcel Hellkamp. All rights reserved.
"""

import cairo
import math
import random
import os
import sys
import urllib2
from StringIO import StringIO
from fnmatch import fnmatch
from itertools import izip
import array, struct

from pybiomaps.resource import BaseView, ResourceQueryError
from pybiomaps.render.color import pick as color_picker
from Bio import SeqIO, Seq, SeqRecord

import logging
log = logging.getLogger(__name__)

def calc_digits(f, err=0):
    ''' Return a sane number of digits to display. '''
    d = 0
    while -1 < f*10**d < 1:
        d += 1
    return d


class ProcFile(object):
    def __init__(self, filename):
        self.data = {}
        with open(filename, 'r') as fp:
            for line in fp:
                if not line.startswith('##$'): continue
                key, value = [x.strip() for x in line[3:].split("=", 1)]
                self.data[key] = value
        self.dim = int(self.data['SI'])
        self.scale = 2 ** float(self.data['NC_proc'])
        self.sweep = float(self.data['SW_p'])
        self.sfreq = float(self.data['SF'])
        self.ppm_max = float(self.data['OFFSET'])
        self.ppm_min = self.ppm_max - (self.sweep / self.sfreq)
        self.ppm_width = self.ppm_max - self.ppm_min
        self.ppm_resolution = self.ppm_width / self.dim
        self.byteorder = 'b' if 'BYTORDP' in self.data else 'l'

try:
    import matplotlib._cntr as mplctr
    import numpy
except ImportError:
    mplctr = None


class Contour(object):
    def __init__(self, narray):
        if narray.ndim != 2: raise TypeError("Need 2d array")
        self.data = narray
        self.width, self.height = narray.shape
        self._cntr = None
        self._tcache = {}

    def __getstate__(self):
        d = self.__dict__.copy()
        d.update(_cntr=None, _tcache={})
        return d

    @classmethod
    def load(cls, fname, width, height, format='<i4'):
        with open(fname, "rb") as fp:
            data = numpy.fromfile(fp, format, -1)
            data = numpy.ndarray(shape=(width, height), buffer=data, dtype=format)
            return cls(data)

    def trace(self, level, bbox=None):
        ''' Calculate a contour on a specific level. Return an iterator that
            yields closed paths. Each path is a list of points. Each point is
            a (x, y) tuple. If a bounding box ((minx, miny), (maxx, maxy)) is
            specified, only paths that are within that area are returned. '''
        if not self._cntr:
            if not mplctr: raise ImportError('matplitlib._cntr not found.')
            ax, ay = numpy.meshgrid(numpy.arange(self.width),
                                    numpy.arange(self.height))
            _mask = numpy.ma.getmask(self.data)
            if _mask is numpy.ma.nomask: _mask = None
            self._cntr = mplctr.Cntr(ax, ay, self.data)
        if level not in self._tcache:
            self._tcache[level] = []
            for path in self._cntr.trace(level):
                amin = path.min(axis=0)
                amax = path.max(axis=0)
                self._tcache[level].append((amin, amax, path))
        bmin, bmax = bbox or (None, None)
        for amin, amax, path in self._tcache[level]:
            if bbox and ((amax<bmin).any() or (amin>bmax).any()): continue
            yield path



class LevelResource(BaseView):
    def prepare(self):
        self.data = array.array('i')
        self.level = -99999999999999999999.0
        self.proc_level = 0.01
        self.grid = 10
        self.color = {
            'bg': (1,1,1,1), 'grid': (0,0,0,0.2), 'data': (0,0,0,1),
            'points': (1,0,0,1)
        }
        self.min = 0
        self.max = 0
        self.dim = (0,0)
        self.scale = 1.0
        self.ppm_min = 0, 0
        self.ppm_max = 0, 0
        self.ppm_resolution = 1.0, 1.0
        self.points = []
        self.contour = None

    def setup(self, **options):
        if 'level' in options:
            self.level = float(options.get('level'))
        if 'proc_level' in options:
            self.proc_level = None
            pl = float(options['proc_level'])
            if 0 < pl < 1:
                self.proc_level = pl
                self.fix_level()
                self.touch()
        self.grid = int(options.get('grid') or self.grid)
        for key in options:
            if key.endswith("_color"):
                self.color[key[:-6]] = color_picker(options[key])
        self.touch()

    def get_interpolated(self, x, y):
        pass

    def size(self):
        return self.dim

    def getstate(self):
        s = super(LevelResource, self).getstate()
        s['scale'] = self.scale
        s['level'] = self.level
        s['proc_level'] = self.proc_level
        s['ppm_min'] = self.ppm_min
        s['ppm_max'] = self.ppm_max
        s['ppm_resolution'] = self.ppm_resolution
        s['resolution'] = self.dim
        return s

    def api_load_local(self, data, procs, proc2s, poi=None):
        self.touch()
        data_file = '/tmp/webpeakr/peakr_uploaded_file_%s'

        if procs and proc2s:
            try:
                self.procs  = p1 = ProcFile(data_file % procs)
                self.proc2s = p2 = ProcFile(data_file % proc2s)
            except IOError:
                raise ResourceQueryError('Could not load all procfiles')
            if p1.scale != p2.scale:
                raise ResourceQueryError('Scale values do not match.')
            if p1.byteorder != p2.byteorder:
                raise ResourceQueryError('Byte order does not match.')
            self.dim = p1.dim, p2.dim
            self.scale = p1.scale
            self.ppm_min = (p1.ppm_min, p2.ppm_min)
            self.ppm_max = (p1.ppm_max, p2.ppm_max)
            self.ppm_resolution = (p1.ppm_resolution, p2.ppm_resolution)

        if procs and proc2s and data:
            try:
                with open(data_file % data, 'rb') as fp:
                    self.data.fromfile(fp, p1.dim*p2.dim)
            except IOError, e:
                raise ResourceQueryError('Could not load data file: %r' % data)
            if p1.byteorder != 'b':
                self.data.byteswap()
            self.min = min(self.data)
            self.max = max(self.data)
            self.fix_level()
            self.contour = None

        if poi:
            if not isinstance(poi, list): poi = [poi] if poi else []
            for p in poi:
                color = 'green'
                if ':' in p: p, color = p.split(':')
                try:
                    with open(data_file % p, 'r') as fp:
                        for line in fp:
                            y, x, name = line.split(None, 2)
                            x, y = float(x), float(y)
                            point = dict(x=x, y=y, name=name, color=color)
                            point['ccolor'] = color_picker(color, False)
                            self.points.append(point)
                except IOError:
                    raise ResourceQueryError('Could not load point data: %r' % p)
        
            if not sum(self.dim):
                # We have no resolution data. This scales the points up to 1024px
                self.ppm_min = mi = (min(p['x'] for p in self.points)-1,
                                     min(p['y'] for p in self.points)-1)
                self.ppm_max = ma = (max(p['x'] for p in self.points)+1,
                                     max(p['y'] for p in self.points)+1)
                self.dim = (1024, 1024)
                self.ppm_resolution = (float(ma[0]-mi[0])/1024, float(ma[1]-mi[1])/1024)
                self.scale = 1.0

    def api_get_points(self):
        return {'points': self.points}

    def api_cross(self, x, y):
        data = numpy.flipud(numpy.ndarray(shape=self.dim, buffer=self.data, dtype='<i4'))
        x, y = int(x), int(y)
        column = [int(p) for p in data[x,:]]
        row    = [int(p) for p in data[:,y]]
        return {'row': row, 'column': column, 'value': int(data[x,y])}

    def get_highmap_paths(self, level, bbox):
        if not self.contour:
            data = numpy.ndarray(shape=self.dim, buffer=self.data, dtype='<i4')
            self.contour = Contour(numpy.flipud(data))
        return self.contour.trace(level, bbox)

    def render(self, rc):
        rc.clear(self.color['bg'])
        self.render_levels(rc)
        self.render_grid(rc)
        if 'poi' in rc.channel:
            self.render_points(rc)
            self.render_ruler(rc)
        return self

    def render_points(self, rc):
        dim = self.dim
        ppm = self.ppm_resolution
        ppmmin = self.ppm_min
        px = rc.scale
        c = rc.context
        c.set_line_width(1*px)
        area = rc.area
        for p in self.points:
            x = dim[0] - (p['x'] - ppmmin[0]) / ppm[0]
            y = (p['y'] - ppmmin[1]) / ppm[0]
            c.set_source_rgba(*p['ccolor'])
            c.arc(x-1, y-1, 2.0*px, 0, 2*math.pi);
            c.stroke()

    def calc_grid(self, rc, axis=0):
        ''' Return low boundary and width of visible grid lines. '''
        px = rc.scale

        # The grid defaults to one unit in size.
        grid = abs(1.0/self.ppm_resolution[axis])
        # Adjust the grid until it makes sense to the user, but keep nice values.
        while grid/px > 1000: grid /= 10
        while grid/px < 100:  grid *= 10

        if axis == 0:
            offset = (self.ppm_max[axis]/-self.ppm_resolution[axis]) % grid
        else:
            offset = (self.ppm_min[axis]/self.ppm_resolution[axis]) % grid

        return offset, grid

    def render_ruler(self, rc):
        c = rc.context
        area = rc.area
        px = rc.scale
        fontsize = 10 * rc.scale

        c.set_source_rgba(0,0,0,1)

        offset, width = self.calc_grid(rc, 0)
        left   = area.left - (area.left % width)
        right  = area.right + width - (area.right % width)

        offset2, height = self.calc_grid(rc, 1)
        top     = area.top - (area.top % height)
        bottom  = area.bottom + height - (area.bottom % height)

        width, height = float(width), float(height)

        fo = cairo.FontOptions()
        fo.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        c.set_font_options(fo)
        c.set_font_size(fontsize)
        font_extends = c.font_extents()
        font_height = font_extends[3]

        digits = calc_digits(width)
        format = '%%.%df' % digits if digits else '%.0f'

        mark = left-width-offset
        while mark < right+width:
            value = self.ppm_max[0] + mark * -self.ppm_resolution[0]
            text = format % value
            text_width, text_height = c.text_extents(text)[2:4]
            c.move_to(mark - text_width/2.0, area.top+text_height+px)
            c.show_text(text)
            mark += width

        digits = calc_digits(height)
        format = '%%.%df' % digits if digits else '%.0f'

        mark = top-height-offset2
        while mark < bottom+height:
            value = self.ppm_min[1] + mark * self.ppm_resolution[1]
            text = format % value
            text_width, text_height = c.text_extents(text)[2:4]
            c.move_to(area.left+px, mark+text_height/2)
            c.show_text(text)
            mark += height

    def render_grid(self, rc):
        c = rc.context
        area = rc.area
        px = rc.scale

        offset, width = self.calc_grid(rc, 0)
        left   = area.left - (area.left % width)
        right  = area.right + width - (area.right % width)

        offset2, height = self.calc_grid(rc, 1)
        top     = area.top - (area.top % height)
        bottom  = area.bottom + height - (area.bottom % height)

        c.set_source_rgba(*self.color['grid'])
        c.set_line_width(1*px)
        c.set_dash((1*px,1*px), 1)

        width, height = float(width), float(height)

        mark = left-width-offset
        while mark < right+width:
            c.move_to(mark-px, top)
            c.line_to(mark-px, bottom)
            mark += width/10.0

        mark = top - height-offset2
        while mark < bottom+height:
            c.move_to(left, mark-px)
            c.line_to(right, mark-px)
            mark += height/10.0

        c.stroke()
        c.set_dash((1*px,1*px), 0)

        mark = left-width-offset
        while mark < right+width:
            c.move_to(mark-px, top)
            c.line_to(mark-px, bottom)
            mark += width

        mark = top - height-offset2
        while mark < bottom+height:
            c.move_to(left, mark-px)
            c.line_to(right, mark-px)
            mark += height

        c.stroke()

    def render_rulers(self, rc):
        pass

    def fix_level(self):
        if self.proc_level and self.data:
            sarray = sorted(self.data)
            index = int((len(self.data)-1)*self.proc_level)
            self.level = int(sarray[index] * self.scale)

    def render_levels(self, rc):
        if not self.data: return
        c = rc.context
        area = rc.area
        bbox = area.area[:2], area.area[2:]
        levels = []
        r,g,b,a = self.color['data']
        numlevel = 10
        for i in xrange(numlevel):
            #alpha = float(i)/numlevel
            #alpha = 1-alpha
            color = r,g,b,1#alpha
            level = int((self.level * 2 ** i) / self.scale)
            if level > self.max: break
            levels.append((level, color))

        c.set_line_width(1.0 * rc.scale)
        line_to, move_to, close_path = c.line_to, c.move_to, c.close_path
        for level, color in levels:
            c.set_source_rgba(*color)
            c.new_path()
            for path in self.get_highmap_paths(level, bbox):
                move_to(*path[0])
                [line_to(*point) for point in path[1:]]
                close_path()
            c.stroke()

