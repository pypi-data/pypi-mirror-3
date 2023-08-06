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

class Ruler2View(BaseView):
    #: Units per pixel
    unit = 1.0
    #: unit value at pixel 0
    unit_offset = 0.0

    #: Fontsize for grid annotation
    fontsize   = 10
    fontcolor  = 'black'

    #: Height or width of 'b' or 'r' aligned rulers.
    width      = 15

    def prepare(self):
        pass

    def setup(self, **options):
        for name in 'unit unit_offset width'.split():
            if name not in options: continue
            setattr(self, name, float(options[name]))
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
        width = self.width
        flip = False

        # Calculate minimum and maximum visible pixel (along the axis)
        # and translate/rotate the context to match the alignment.
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

        # The grid defaults to one unit in size.
        grid = 1/abs(self.unit)

        # Adjust the grid until it makes sense to the user, but keep nice values.
        while grid/px > 500: grid /= 10
        while grid/px < 50:  grid *= 10

        # Calculate the pixel offset of the 0 point
        offset = self.unit_offset/self.unit

        # Calculate the grid offset in virtual pixel
        offset %= grid

        # Calculate the position of the first and last visible grid
        first = px_min - ((px_min+offset) % grid)
        last  = px_max + ((px_max+offset) % grid)

        # Render the small grid (10 steps per grid)
        mark = first-grid
        while mark < last+grid:
            if flip: c.rectangle(mark, 0, 1*px, 2*px)
            else: c.rectangle(mark, width*px-2*px, 1*px, 2*px)
            mark += grid / 10

        # Render the grid
        mark = first-grid
        while mark < last+grid:
            if flip: c.rectangle(mark-px, 0, 3*px, 4*px)
            else: c.rectangle(mark-px, width*px-4*px, 3*px, 4*px)
            mark += grid

        # Draw the grid
        rc.clear('white')
        rc.set_color(self.fontcolor)
        c.fill()

        # And now render the annotations

        fo = cairo.FontOptions()
        fo.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        c.set_font_options(fo)
        c.set_font_size(fontsize)
        font_extends = c.font_extents()
        font_height = font_extends[3]

        # Calculate minimum number of fractional digits to show per grid
        digits = 0
        while grid*10**digits <= 1:
            digits += 1

        mask = '%%.%df' % digits if digits else '%d'
        fname = mask % (self.unit_offset+first*px)
        lname = mask % (self.unit_offset+last*px)
        overlap = 0.5 * max(c.text_extents(name)[2] for name in (fname, lname))
        # Numbers too big, would overlap ...
        if overlap*2 > grid: return
        # Round up to grid
        overlap += grid - overlap % grid
        mark = first - overlap
        while mark < last + overlap:
            value = (self.unit_offset + mark*self.unit)
            if not digits: value = round(value)
            name = mask % value
            text_width, text_height = c.text_extents(name)[2:4]
            if flip: c.move_to(mark - text_width/2.0, width*px-px)
            else: c.move_to(mark - text_width/2.0, text_height+px)
            c.show_text(name)
            mark += grid
        return self
