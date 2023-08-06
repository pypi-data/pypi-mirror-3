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

from pybiomaps.resource import BaseView, ResourceQueryError
from Bio import SeqIO, Seq, SeqRecord


def seq_compress(s, gap='-'):
    """ Take a string with gabs and return two lists of equal length:
        1) The absolute position (0..n-1) of each part.
        2) Each part as a strings.
        These lists are separated to allow faster pickling. A list of
        (pos, data) tuples is quite slow."""
    out = []
    pos = []
    index = 0
    while s:
        slen = len(s)
        s = s.lstrip(gap)
        index += slen - len(s)
        nextgab = s.find(gap)
        if nextgab > 0:
            data, s = s[:nextgab], s[nextgab:]
        else:
            data, s = s, ''
        out.append(data)
        pos.append(index)
        index += len(data)
    return pos, out

def seq_decompress(positions, parts, gap='-', prefix=''):
    ''' Take the output of seq_compress and return the reconstructed sequence.
    '''
    for pos, part in izip(positions, parts):
        gaplen = pos - len(prefix)
        if gaplen:
            prefix += '-' * gaplen
        prefix += part
    return prefix

class SequenceResource(BaseView):
    def prepare(self):
        #: A list of three-tuples (name, positions, parts) see seq_compress()
        self.sequences = []
        #: The maximum length of all sequences
        self.columns = 0
        #: The size of each field in pixel
        self.blocksize = 12

    def setup(self, **options):
        self.blocksize = int(options.get('blocksize') or self.blocksize)
        if 'source' in options:
            self.api_load(options['source'],
                          options.get('format','fasta'),
                          options.get('append', False))

    def size(self):
        return (self.columns*self.blocksize, len(self.sequences)*self.blocksize)

    def getstate(self):
        s = super(SequenceResource, self).getstate()
        s['blocksize'] = self.blocksize
        s['rows'] = len(self.sequences)
        s['columns'] = self.columns
        return s
    
    def get_index(self):
        return [s[0] for s in self.sequences]

    def add_seq(self, name, seq):
        positions, parts = seq_compress(seq.upper())
        self.sequences.append((name, positions, parts))
        self.columns = max(self.columns, len(seq))
        self.touch()

    def api_load(self, source, format='fasta', append=False):
        if format not in ('fasta'):
            raise ResourceQueryError('Unsupported file format.')

        if hasattr(source, "file"):
            data = source.file
        elif source.startswith("http://"):
            try:
                data = urllib2.urlopen(source, None)
            except (urllib2.URLError, urllib2.HTTPError), e:
                raise ResourceQueryError('Faild do open URI.')
        else:
            raise ResourceQueryError('Unsupported protocol or uri syntax.')

        try:
            data = SeqIO.parse(data, format)
        except Exception, e:
            raise ResourceQueryError('Fasta parser error %s: %s' % (e.__class__.__name__, str(e.args)))

        if not append:
            self.columns = 0
            self.sequences = []

        names = []
        for s in data:
            names.append(s.id)
            self.add_seq(s.id, str(s.seq))
        return {'new_sequences':names}

    def api_copy(self, source, index):
        ''' Copy a sequence from an existing resource '''
        res = self.pool.fetch(int(source))
        if not res:
            raise ResourceQueryError('Resource ID not found: %s' % source)
        if not isinstance(index, (list, tuple)):
            index = [index]
        names = []
        for i in map(int, index):
            if i >= len(res.sequences): continue
            name, positions, parts = res.sequences[i]
            self.add_seq(name, seq_decompress(positions, parts))
            names.append(name)
        return {'new_sequences': names}

    def api_search(self, query, limit=1, strict=False):
        ''' Search for a sequence name. The query supports additional syntax:
              '*' match any number of characters
              '?' match single character
              '[abc]' match any character in seq
              '[!seq]' match any character not in seq
        '''
        limit = min(100,max(1, int(limit)))
        matches = []
        query = query.lower().strip()
        for i, seq in enumerate(self.sequences):
            name = seq[0].lower()
            if name==query or not strict and fnmatch(name, query):
                matches.append({"name": seq[0], "index": i})
                if len(matches) == limit:
                    break
        return {'matches': matches, 'query': query, 'limit': limit}

    def api_names(self):
        return {"sequence_names": [seq[0] for seq in self.sequences]}

    def render(self, rc):
        # Shortcuts
        c = rc.context
        area = rc.area
        blocksize = self.blocksize
        fontsize = self.blocksize - 1

        # Do not bother rendering details if scale is to high to see anything
        drawdetails = self.blocksize / rc.scale > 6

        # Configuration
        c.select_font_face("mono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        options = cairo.FontOptions()
        options.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        c.set_font_options(options)
        c.set_font_size(self.blocksize)
        lineheight = c.font_extents()[1]

        # precalculate font extents
        tecache = {}
        for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ-':
            data = c.text_extents(char)
            left_offset = float(float(blocksize) - data[2] - data[0]) / 2
            tecache[char] = left_offset

        # Rows to consider
        row_first = int(math.floor(float(area.top) / blocksize))
        row_last  = int(math.ceil(float(area.bottom) / blocksize))
        row_last  = min(row_last, len(self.sequences))
        col_first = int(math.floor(float(area.left) / blocksize))
        col_last  = int(math.ceil(float(area.right) / blocksize))
        col_last  = min(col_last, self.columns)

        # Draw background
        if drawdetails:
            rc.draw_stripes(blocksize*10, 'bio.amino-section1', 'bio.amino-section2')
        else:
            rc.clear('bio.amino-section1')

        # Draw data
        for rownum in range(row_first, row_last):
            y = (rownum+1) * blocksize - lineheight
            name, positions, parts = self.sequences[rownum]
            lastpos = col_first
            for pos, part in izip(positions, parts):
                datalen = len(part)
                if pos + datalen < col_first: continue
                if lastpos > col_last: break
                if lastpos < pos and drawdetails:
                    rc.set_color('bio.amino--')
                    left_offset = tecache['-']
                    for p in xrange(lastpos, min(pos, col_last)):
                        c.move_to(blocksize * p + left_offset, y)
                        c.show_text('-')
                lastpos = pos + datalen
                if drawdetails:
                    for p in xrange(max(pos, col_first), min(pos+datalen, col_last)):
                        char = part[p-pos]
                        rc.set_color('bio.amino-'+char)
                        c.move_to(blocksize * p + tecache['-'], y)
                        c.show_text(char)
                else:
                    rc.set_color('bio.amino--')
                    c.rectangle(blocksize * pos, y, blocksize*datalen, blocksize)
                    c.fill()
        return self
