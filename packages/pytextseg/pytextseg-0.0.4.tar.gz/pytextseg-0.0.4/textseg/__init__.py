#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Text segmentation module

The textseg module provides functions fill() and wrap(), Unicode-aware
alternatives for those of textwrap standard module.  It also provides
classes LineBreak and GCStr, lower level interfaces for text segmentation.
"""

# Copyright (C) 2012 Hatuka*nezumi - IKEDA Soji.

__all__ = ['Consts', 'GCStr', 'LineBreak', 'fill', 'fold', 'wrap']

import re
import _textseg
from textseg.Consts import lbcBK, lbcCR, lbcLF, lbcNL, lbcSP, eawN

try:
    unicode, unichr
except NameError:
    unicode = str
    unichr = chr

###
### Function wrap()
###

def wrap(text,
         width = 70,
         initial_indent = "",
         subsequent_indent = "",
         expand_tabs = True,
         replace_whitespace = True,
         fix_sentence_endings = False, # currently no effects
         break_long_words = True,
         **kwds):
    '''\
wrap(text[, options...]) -> [unicode]

Wrap paragraphs of a text then return a list of wrapped lines.

Reformat each paragraph in ``text`` so that it fits in lines of no more than 
``width`` columns if possible, and return a list of wrapped lines.  By 
default, tabs in ``text`` are expanded and all other whitespace characters 
(including newline) are converted to space.'''

    def format(self, action, s):
        if action.startswith('eo'):
            return self.newline
        if action in ('sot', 'sop'):
            return s * 0 + initial_indent + s
        if action == 'sol':
            return s * 0 + subsequent_indent + s
        if action == '':
            if s == initial_indent or s == subsequent_indent:
                return ''
        return None

    if expand_tabs:
        text = GCStr(text).expandtabs()
    if replace_whitespace:
        table = {}
        for c in unicode('\t\n\x0b\x0c\r '):
            table[c] = unicode(' ')
        text = text.translate(table)

    for k, v in list({ 'charmax': 0,
                       'format': format,
                       'newline': '',
                       'urgent': (break_long_words and "FORCE" or None),
                       'width': width,
                     }.items()):
        kwds.setdefault(k, v)
    lb = LineBreak(**kwds)
    return [unicode(s) for s in lb.wrap(text)]

###
### Function fill()
###

def fill(text, **kwds):
    '''\
fill(text[, options...]) -> unicode

Reformat the single paragraph in ``text`` to fit in lines of no more than 
``width`` columns, and return a new string containing the entire wrapped 
paragraph.  Optional named arguments will be passed to wrap() function.'''

    return unicode("\n").join(wrap(text, **kwds))

###
### Function fold()
###

def _fold_FIXED(self, action, s):
    s = GCStr(s)
    if action in ('sot', 'sop'):
        self['_'] = {}
        self['_']['width'] = self.width
        if s.startswith('>'):
            self.width = 0
    elif action == '':
        self['_']['line'] = s
    elif action == 'eol':
        return self.newline
    elif action.startswith('eo'):
        if len(self['_']['line']) and self.width:
            s = self.newline + self.newline
        else:
            s = self.newline
        self.width = self['_']['width']
        del self['_']
        return s
    return None

_prefixRe = re.compile(r'^>+')
def _fold_FLOWED(self, action, s):
    s = GCStr(s)
    if action == 'sol':
        if len(self['_']['prefix']):
            return self['_']['prefix'] + ' ' + s
        elif s.startswith(' ') or s.startswith('From ') or s.startswith('>'):
            return ' ' + s
    elif action.startswith('so'):
        self['_'] = {}
        m = _prefixRe.match(unicode(s))
        if m:
            self['_']['prefix'] = m.group()
        else:
            self['_']['prefix'] = ''
            if s.startswith(' ') or s.startswith('From '):
                return ' ' + s
    elif action == '':
        self['_']['line'] = s
    elif action == 'eol':
        if len(s):
            s = ' '
        return s + ' ' + self.newline
    elif action.startswith('eo'):
        if len(self['_']['line']) and not len(self['_']['prefix']):
            s = ' ' + self.newline + self.newline
        else:
            s = self.newline
        del self['_']
        return s
    return None

def _fold_PLAIN(self, action, s):
    if action.startswith('eo'):
        return self.newline
    return None

_fold_funcs = {'flowed': _fold_FLOWED,
               'fixed': _fold_FIXED,
               'plain': _fold_PLAIN,
               }

_specialBreakRe = re.compile('([' + unichr(0xB) + unichr(0xC) +
                             unichr(0x85) + unichr(0x2028) + unichr(0x2029) +
                             '])', re.S)

def fold(string, method = 'plain', tabsize = 8, **kwds):
    """\
Folds lines of string *string* and returns it.

Surplus SPACEs and horizontal tabs at end of line are removed,
newline sequences are replaced by that specified by optional newline
argument and newline is appended at end of text if it does not exist.
Horizontal tabs are treated as tab stops according to tabsize argument.

Following options may be specified for ``method`` argument.

``"fixed"``
    Lines preceded by ">" won't be folded.
    Paragraphs are separated by empty line.
``"flowed"``
    "Format=Flowed; DelSp=Yes" formatting defined by RFC 3676.
``"plain"``
    Default method.  All lines are folded.
"""
    def sizing(self, cols, pre, spc, s):
        spcstr = spc + s
        i = 0
        for c in spcstr:
            if c.lbc != lbcSP:
                cols += spcstr[i:].cols
                break
            if c == "\t":
                if 0 < tabsize:
                    cols += tabsize - (cols % tabsize)
            else:
                cols += c.cols
            i = i + 1
        return cols

    if string is None or not len(string):
        return ''
    if not isinstance(string, unicode):
        string = unicode(string)

    kwds.update({'format': _fold_funcs.get(method.lower(), _fold_PLAIN),
                 'sizing': sizing,
                 })
    lb = LineBreak(**kwds)
    lbc = lb.lbc
    lbc[ord("\t")] = lbcSP
    lb.lbc = lbc

    result = ''
    for s in _specialBreakRe.split(string):
        if not len(s):
            continue
        elif _specialBreakRe.match(s):
            result += s
        else:
            result += ''.join([unicode(l) for l in lb.wrap(s)])
    return result

###
### Class for Line breaking
###

class LineBreak(_textseg.LineBreak):
    '''\
LineBreak class performs Line Breaking Algorithm described in Unicode 
Standards Annex #14 [UAX14]_. East_Asian_Width informative properties 
defined by Annex #11 [UAX11]_ will be concerned to determine breaking 
positions.
'''

    MANDATORY = 4
    DIRECT = 3
    INDIRECT = 2
    PROHIBITED = 1

    DEFAULTS = {
        'width': 70,
        'minwidth': 0,
        'charmax': 998,
        'eastasian_context': False,
        'eaw': None,
        'format': 'SIMPLE',
        'hangul_as_al': False,
        'lbc': None,
        'legacy_cm': True,
        'newline': "\n",
        'prep': None,
        'sizing': "UAX11",
        'urgent': None,
        'virama_as_joiner': True,
    }

    def __init__(self, **kwds):
        '''\
LineBreak([options...]) -> LineBreak

Create new LineBreak object.  Optional named arguments may specify 
initial property values.  See documentations of each properties.'''
        for k, v in list(self.DEFAULTS.items()):
            kwds.setdefault(k, v)
        _textseg.LineBreak.__init__(self, **kwds)

###
### Class for Grapheme cluster string
###

class GCStr(_textseg.GCStr):
    '''\
GCStr class treats Unicode string as a sequence of 
*extended grapheme clusters* defined by Unicode Standard Annex #29 
[UAX29]_.

**Grapheme cluster** is a sequence of Unicode character(s) that consists 
of one **grapheme base** and optional **grapheme extender** and/or 
**"prepend" character**.  It is close in that people consider as 
*character*.'''

    PROHIBIT_BEFORE = 1
    ALLOW_BEFORE = 2

    def __new__(cls, string, lb = None):
        '''\
GCStr(string[, lb]) -> GCStr

Create new grapheme cluster string (GCStr object) from Unicode string
``string``.

Optional LineBreak object ``lb`` controls breaking features.  Following
properties of LineBreak object affect new GCStr object.

    - eastasian_context
    - eaw
    - lbc
    - legacy_cm
    - virama_as_joiner
'''

        if lb is None:
            lb = LineBreak()
        return _textseg.GCStr.__new__(cls, string, lb=lb)

    '''
    def center(self, width, fillchar=' '):
        """\
S.center(width[, fillchar]) -> GCStr

Return S centered in a string of width columns. Padding is
done using the specified fill character (default is a space)"""

        fillchar = self * 0 + fillchar
        if width < self.cols + fillchar.cols:
            return self

        marg = (width - self.cols) // fillchar.cols
        right = marg // 2 + (marg & (width // fillchar.cols) & 1)
        return fillchar * (marg - right) + self + fillchar * right
    '''

    def endswith(self, suffix, start = 0, end = None):
        '''\
S.endswith(suffix[, start[, end]]) -> bool

Return True if S ends with the specified suffix, False otherwise.
With optional start, test S beginning at that position.
With optional end, stop comparing S at that position.
suffix can also be a tuple of strings to try.'''
        if isinstance(suffix, tuple):
            pass
        elif not isinstance(suffix, unicode):
            prefix = unicode(suffix)

        if end is None:
            return unicode(self[start:]).endswith(suffix)
        else:
            return unicode(self[start:end]).endswith(suffix)

    def expandtabs(self, tabsize=8):
        '''\
S.expandtabs([tabsize]) -> GCStr

Return a copy of S where all tab characters are expanded using spaces.
If *tabsize* is not given, a tab size of 8 columns is assumed.'''

        ret = self * 0
        j = 0
        for c in self:
            if c.lbc in (lbcBK, lbcCR, lbcLF, lbcNL):
                ret += c
                j = 0
            elif c == unicode('\t'):
                if 0 < tabsize:
                    incr = tabsize - (j % tabsize)
                    ret += unicode(' ') * incr
                    j += incr
            else:
                ret += c
                j += c.cols
        return ret

    def ljust(self, width, fillchar=' '):
        """\
S.ljust(width[, fillchar]) -> GCStr

Return S left-justified in a grapheme cluster string of width columns.
Padding is done using the specified fill character (default is a space)."""

        fillchar = self * 0 + fillchar
        if width < self.cols + fillchar.cols:
            return self
        return self + fillchar * ((width - self.cols) // fillchar.cols)

    def rjust(self, width, fillchar=' '):
        """\
S.rjust(width[, fillchar]) -> GCStr

Return S right-justified in a string of width columns. Padding is\n\
done using the specified fill character (default is a space)."""

        fillchar = self * 0 + fillchar
        if width < self.cols + fillchar.cols:
            return self
        return fillchar * ((width - self.cols) // fillchar.cols) + self

    def startswith(self, prefix, start = 0, end = None):
        '''\
S.startswith(prefix[, start[, end]]) -> bool

Return True if S starts with the specified prefix, False otherwise.
With optional start, test S beginning at that position.
With optional end, stop comparing S at that position.
prefix can also be a tuple of strings to try.'''
        if isinstance(prefix, tuple):
            pass
        elif not isinstance(prefix, unicode):
            prefix = unicode(prefix)

        if end is None:
            return unicode(self[start:]).startswith(prefix)
        else:
            return unicode(self[start:end]).startswith(prefix)

    def translate(self, table):
        '''\
S.translate(table) -> GCStr

Return a copy of the GCStr object S, where all characters have been mapped
through the given translation table, which must be a mapping of
Unicode ordinals to Unicode ordinals, strings, or None.
Unmapped characters are left untouched. Characters mapped to None
are deleted.'''
        return self * 0 + unicode(self).translate(table)

