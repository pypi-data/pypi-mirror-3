#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Copyright (C) 2012 by Hatuka*nezumi - IKEDA Soji.

This file is part of the pytextseg package.  This program is free
software; you can redistribute it and/or modify it under the terms of
either the GNU General Public License or the Artistic License, as
specified in the README file.
'''
import os
import re
import unittest
from textseg import LineBreak, LineBreakException, fill, fold, unfold
from textseg.Consts import eawZ, eawN, lbcID, sea_support, \
                           AMBIGUOUS_ALPHABETICS, KANA_NONSTARTERS

try:
    unicode, unichr
except NameError:
    unicode = str
    unichr = chr

def unistr(*list):
    return ''.join([unichr(c) for c in list])

LineBreak.DEFAULTS = {
    'charmax': 998,
    'eastasian_context': False,
    'eaw': { unistr(0x302E, 0x302F): eawZ },
    'format': 'SIMPLE',
    'hangul_as_al': False,
    'lbc': None,
    'legacy_cm': True,
    'minwidth': 0,
    'newline': "\n",
    'prep': None,
    'sizing': "UAX11",
    'urgent': None,
    'virama_as_joiner': True,
    'width': 76,
}

class LineBreakTest(unittest.TestCase):

    def readText(self, fn):
        fp = open(os.path.join('test-data', fn), 'rb')
        ret = unicode(fp.read(), 'utf-8')
        fp.close()
        return ret

    def doTest(self, pairs, **kwds):
        lb = LineBreak(**kwds)
        for infn, outfn in pairs:
            instring = self.readText(infn + '.in')
            b = lb.wrap(instring)
            broken = ''.join([unicode(x) for x in b])
            outstring = self.readText(outfn + '.out')
            self.assertEqual(broken, outstring)

    def test_00LineBreakTest(self):
        commentRe = re.compile(r'\s*#\s*')
        opRe = re.compile(r'\s*(?:' + unichr(0xF7) + '|' + unichr(0xD7) + r')\s*')

        try:
            fp = open(os.path.join('test-data', 'LineBreakTest.txt'), 'rb')
        except IOError:
            return

        eaw = {}
        for c in range(1, 0xFFFD):
            eaw[unichr(c)] = eawN
        lb = LineBreak(break_indent = False,
             width = 1,
             eaw = eaw,
             format = None,
             legacy_cm = False)

        print('')
        print(fp.readline().strip())
        print(fp.readline().strip())

        errs = 0
        tests = 0
        for l in fp.readlines():
            l = unicode(l, 'utf-8').rstrip()
            a = commentRe.split(l, 1)
            if len(a) > 1:
                desc = a[1]
            else:
                desc = ''
            l = a[0].strip()
            if not len(l):
                continue

            if l.startswith(unichr(0xD7)):      # ÷
                l = l[1:].lstrip()
            if l.endswith(unichr(0xF7)):        # ×
                l = l[:-1].rstrip()

            s = ''.join([unichr(int(c, 16))
                         for c in opRe.split(l)
                         if len(c) > 0])
            b = unistr(0x20, 0xF7, 0x20).join([unistr(0x20, 0xD7, 0x20).join(['%04X' % ord(c) for c in unicode(x)])
                                                for x in lb.wrap(s)])
            try:
                self.assertEqual(b, l)
            except AssertionError:
                import sys
                import traceback
                print('Failed: %s' % desc)
                traceback.print_exc(0)
                errs = errs + 1
            tests = tests + 1
        fp.close()

        if errs > 0:
            raise AssertionError("%d of %d subtests are failed." % (errs, tests))

    def test_01break(self):
        langs = ['ar', 'el', 'fr', 'he', 'ja', 'ja-a', 'ko', 'ru',
                 'vi', 'vi-decomp', 'zh']
        self.doTest([(x, x) for x in langs])

    def test_02hangul(self):
        self.doTest([('ko', 'ko.al')], hangul_as_al=True);
        self.doTest([('amitagyong', 'amitagyong')]);

    def test_03ns(self):
        self.doTest([('ja-k', 'ja-k')], width=72)
        self.doTest([('ja-k', 'ja-k.ns')],
                    lbc={ KANA_NONSTARTERS: lbcID }, width=72)

    def test_04fold(self):
        for lang in ('ja', 'fr', 'quotes'):
            instring = self.readText(lang + '.in')
            folded = {}
            for meth in ['plain', 'fixed', 'flowed']:
                folded[meth] = fold(instring, meth)
                outstring = self.readText(lang + '.' + meth + '.out')
                self.assertEqual(folded[meth], outstring)
            for meth in ['fixed', 'flowed']:
                if lang == 'quotes':
                    outstring = unfold(folded[meth], meth)
                    instring = self.readText(lang + '.' + 'norm.in')
                    self.assertEqual(outstring, instring)

    def test_05urgent(self):
        self.doTest([('ecclesiazusae', 'ecclesiazusae')]);
        self.doTest([('ecclesiazusae', 'ecclesiazusae.ColumnsMax')],
                    urgent='FORCE')
        self.doTest([('ecclesiazusae', 'ecclesiazusae.CharactersMax')],
                    charmax=79)
        self.doTest([('ecclesiazusae', 'ecclesiazusae.ColumnsMin')],
                    minwidth=7, width=66, urgent='FORCE')
        try:
            self.doTest([('ecclesiazusae', 'ecclesiazusae')], urgent='RAISE')
        except LineBreakException:
            self.assertEqual(True, True)
        else:
            self.assertEqual(True, False)

    def test_06context(self):
        self.doTest([('fr', 'fr.ea')], eastasian_context=True)
        self.doTest([('fr', 'fr')], eastasian_context=True,
                    eaw={ AMBIGUOUS_ALPHABETICS: eawN })

    def test_07sea(self):
        if sea_support is not None:
            print(('\n# SA word segmentation supported: %s' % sea_support))
        else:
            print('\n# SA word segmentation not supported.')
            return
        self.doTest([('th', 'th')], complex_breaking=True)

    def test_09uri(self):
        self.doTest([('uri', 'uri.break')], width=1, prep=['BREAKURI'])
        self.doTest([('uri', 'uri.nonbreak')], width=1, prep=['NONBREAKURI'])

    def test_11format(self):
        def format(self, state, s):
            if state.startswith('so'):
                return s * 0 + '    ' + state + '>' + s
            if state.startswith('eo'):
                return '<' + state + "\n"
            return None

        self.doTest([(x, x + '.format') for x in ['fr', 'ja']],
                    format = format)
        self.doTest([(x, x + '.newline') for x in ['fr', 'ko']],
                    format = 'NEWLINE')
        self.doTest([(x, x + '.newline') for x in ['fr', 'ko']],
                    format = 'TRIM')

    def test_12fill(self):
        for lang in ['ja', 'fr']:
            instring = self.readText(lang + '.in')
            folded = fill(instring, width = 76, initial_indent = ' ' * 8,
                          subsequent_indent = ' ' * 4) + "\n"
            outstring = self.readText(lang + '.wrap.out').expandtabs()
            self.assertEqual(folded, outstring)

    def test_13flowedsp(self):
        for lang in ['flowedsp']:
            instring = self.readText(lang + '.in')
            unfolded = unfold(instring, 'flowedsp');
            outstring = self.readText(lang + '.out')
            self.assertEqual(unfolded, outstring)

    def test_14sea_al(self):
        self.doTest([('th', 'th.al')], complex_breaking=False)

    def doTestArray(self, pairs, **kwds):
        for infn, outfn in pairs:
            instring = self.readText(infn + '.in')
            lb = LineBreak(**kwds)
            broken = [unicode(x) for x in lb.wrap(instring)]
            fp = open(os.path.join('test-data', outfn + '.out'), 'rb')
            outstrings = [unicode(x, 'utf-8') for x in fp.readlines()]
            fp.close()
            self.assertEqual(broken, outstrings);

    def test_15array(self):
        # break
        self.doTestArray([(x, x) for x in ['ar', 'el', 'fr', 'ja', 'ja-a',
                                           'ko', 'ru', 'zh']])
        # urgent
        self.doTestArray([('ecclesiazusae', 'ecclesiazusae')])
        self.doTestArray([('ecclesiazusae', 'ecclesiazusae.ColumnsMax')],
                         urgent='FORCE')
        self.doTestArray([('ecclesiazusae', 'ecclesiazusae.CharactersMax')],
                         charmax=79)
        self.doTestArray([('ecclesiazusae', 'ecclesiazusae.ColumnsMin')],
                         minwidth=7, width=66, urgent='FORCE')
        try:
            self.doTestArray([('ecclesiazusae', 'ecclesiazusae')],
                             urgent='RAISE')
        except:
            # unittest module of Python 2.3.x does not have assertTrue()
            self.assertEqual(True, True)
        else:
            self.assertEqual(True, False)

        # format
        def format(self, stat, s):
            if stat.startswith('so'):
                return s * 0 + '    ' + stat + '>' + s
            if stat.startswith('eo'):
                return '<' + stat + "\n"
            return None

        self.doTestArray([(x, x + '.format') for x in ['fr', 'ja']],
                         format = format)
        self.doTestArray([(x, x + '.newline') for x in ['fr', 'ko']],
                         format = "NEWLINE")
        self.doTestArray([(x, x + '.newline') for x in ['fr', 'ko']],
                         format = "TRIM")

    def test_16regex(self):
        # Regex matching most of URL-like strings.
        urire = re.compile(r'''\b(?:url:)?
        (?:[a-z][-0-9a-z+.]+://|news:|mailto:)
        [\x21-\x7E]+''', re.I + re.U + re.X)
        punctre = re.compile(r'\A[\".:;,>]+\Z', re.U)

        # Breaking URIs according to some CMoS rules.
        def breakURI(self, s):
            # 17.11 1.1: [/] ÷ [^/]
            # 17.11 2:   [-] ×
            # 6.17 2:   [.] ×
            # 17.11 1.2: ÷ [-~.,_?#%]
            # 17.11 1.3: ÷ [=&]
            # 17.11 1.3: [=&] ÷
            # Default:  ALL × ALL
            r = ''
            ret = []
            b = ''
            for c in s:
                if b == '':
                    r = c
                elif r.lower().endswith('url:'):
                    ret += [r]
                    r = c
                elif b in '/' and not c in '/' or \
                    not b in '-.' and c in '-~.,_?\#%=&' or \
                    b in '=&' or c in '=&':
                     if r != '':
                         ret += [r]
                     r = c
                else:
                    r += c
                b = c
            if r != '':
                ret += [r]

            # Won't break punctuations at end of matches.
            while 2 <= len(ret) and re.search(punctre, ret[-1]):
                c = ret[-1]
                ret = ret[0:-1]
                ret[-1] += c;
            return ret

        def nonBreak(self, s):
            return s

        # (REGEX, FUNC) pair
        self.doTest([('uri', 'uri.break')], width=1,
                    prep=[(urire, breakURI)])
        self.doTest([('uri', 'uri.nonbreak')], width=1,
                    prep=[(urire, nonBreak)])
        # [STRING, FUNC] pair
        self.doTest([('uri', 'uri.nonbreak')], width=1,
                     prep=[(urire.pattern, nonBreak, re.I + re.U + re.X)])
        # multiple patterns
        self.doTest([('uri', 'uri.break')], width=1,
                    prep=[(urire, breakURI),
                          (r'ftp://[\x21-\x7e]+', nonBreak)])
        self.doTest([('uri', 'uri.break.http')], width=1,
                    prep=[(r'ftp://[\x21-\x7e]+', nonBreak),
                          (urire, breakURI)])
        self.doTest([('uri', 'uri.nonbreak')], width=1,
                    prep=[(r'ftp://[\x21-\x7e]+', nonBreak),
                          (r'http://[\x21-\x7e]+', nonBreak),
                          (urire, breakURI)])


def suite():
    return unittest.makeSuite(LineBreakTest)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())

