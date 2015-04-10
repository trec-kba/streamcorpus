# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from streamcorpus import XpathRange


# Note that these tests are used inside of streamcorpus-pipeline. (See the
# tests for xpath offset transform.)
tests_roundtrip = [{
    'html': '<p>Foo</p>',
    'ranges': [(('/p[1]/text()[1]', 0), ('/p[1]/text()[1]', 3))],
    'expected': ['Foo'],
    'tokens': [(3, 6)],
}, {
    'html': '<p>Foo</p><p>Bar</p>',
    'ranges': [
        (('/p[1]/text()[1]', 0), ('/p[1]/text()[1]', 3)),
        (('/p[2]/text()[1]', 0), ('/p[2]/text()[1]', 3)),
    ],
    'expected': ['Foo', 'Bar'],
    'tokens': [(3, 6), (13, 16)],
}, {
    'html': '<p><a>Foo</a></p>',
    'ranges': [(('/p[1]/a[1]/text()[1]', 0), ('/p[1]/a[1]/text()[1]', 3))],
    'expected': ['Foo'],
    'tokens': [(6, 9)],
}, {
    'html': '<p>Homer <b>Jay</b> Simpson</p>',
    'ranges': [
        (('/p[1]/text()[1]', 0), ('/p[1]/text()[1]', 5)),
        (('/p[1]/b[1]/text()[1]', 0), ('/p[1]/b[1]/text()[1]', 3)),
        (('/p[1]/text()[2]', 1), ('/p[1]/text()[2]', 8)),
    ],
    'expected': ['Homer', 'Jay', 'Simpson'],
    'tokens': [(3, 8), (12, 15), (20, 27)],
}, {
    'html': '<b><i>a<u>b</u>c</i>d</b>',
    'ranges': [
        (('/b[1]/i[1]/text()[1]', 0), ('/b[1]/i[1]/text()[1]', 1)),
        (('/b[1]/i[1]/u[1]/text()[1]', 0), ('/b[1]/i[1]/u[1]/text()[1]', 1)),
        (('/b[1]/i[1]/text()[2]', 0), ('/b[1]/i[1]/text()[2]', 1)),
        (('/b[1]/text()[1]', 0), ('/b[1]/text()[1]', 1)),
    ],
    'expected': ['a', 'b', 'c', 'd'],
    'tokens': [(6, 7), (10, 11), (15, 16), (20, 21)],
}, {
    'html': '<b>AB</b>',
    'ranges': [
        (('/b[1]/text()[1]', 0), ('/b[1]/text()[1]', 1)),
        (('/b[1]/text()[1]', 1), ('/b[1]/text()[1]', 2)),
    ],
    'expected': ['A', 'B'],
    'tokens': [(3, 4), (4, 5)],
}, {
    'html': '<b>ABCD</b>',
    'ranges': [
        (('/b[1]/text()[1]', 0), ('/b[1]/text()[1]', 2)),
        (('/b[1]/text()[1]', 2), ('/b[1]/text()[1]', 4)),
    ],
    'expected': ['AB', 'CD'],
    'tokens': [(3, 5), (5, 7)],
}, {
    'html': '<b>b<i>a</i>r</b>',
    'ranges': [
        (('/b[1]/text()[1]', 0), ('/b[1]/text()[2]', 1)),
    ],
    'expected': ['bar'],
    'tokens': [(3, 13)],
}, {
    'html': '<b>Hello, Homer <i>Jay</i> Simpson. Press any key.</b>',
    'ranges': [
        (('/b[1]/text()[1]', 7), ('/b[1]/text()[2]', 8)),
    ],
    'expected': ['Homer Jay Simpson'],
    'tokens': [(10, 34)],
}, {
    'html': '<b>b<i>a</i>r</b>',
    'ranges': [
        (('/b[1]/text()[1]', 0), ('/b[1]/text()[1]', 1)),
        (('/b[1]/i[1]/text()[1]', 0), ('/b[1]/i[1]/text()[1]', 1)),
        (('/b[1]/text()[2]', 0), ('/b[1]/text()[2]', 1)),
    ],
    'expected': ['b', 'a', 'r'],
    'tokens': [(3, 4), (7, 8), (12, 13)],
}, {
    'html': u'<b>ΛΘΓΔα</b>',
    'ranges': [
        (('/b[1]/text()[1]', 1), ('/b[1]/text()[1]', 4)),
    ],
    'expected': [u'ΘΓΔ'],
    'tokens': [(4, 7)],
}, {
    'html': u'<b>1☃2☃3☃4☃</b>',
    'ranges': [
        (('/b[1]/text()[1]', 0), ('/b[1]/text()[1]', 1)),
        (('/b[1]/text()[1]', 1), ('/b[1]/text()[1]', 2)),
        (('/b[1]/text()[1]', 2), ('/b[1]/text()[1]', 6)),
        (('/b[1]/text()[1]', 6), ('/b[1]/text()[1]', 8)),
    ],
    'expected': [u'1', u'☃', u'2☃3☃', u'4☃'],
    'tokens': [(3, 4), (4, 5), (5, 9), (9, 11)],
# Getting these tests to pass will require a general tree traversal. ---AG
# }, {
    # 'html': '<b>b<i>ar</i></b>',
    # 'tokens': [(3, 8)],
    # 'expected': ['bar'],
# }, {
    # 'html': '<b>f<i>o</i>ob<u>a</u>r</b>',
    # 'tokens': [(3, 23)],
}]


def run_test(test):
    for ((x1, i1), (x2, i2)), expect in zip(test['ranges'], test['expected']):
        html = '<html><body>' + test['html'] + '</body></html>'
        xprange = XpathRange('/html/body' + x1, i1, '/html/body' + x2, i2)
        assert expect == xprange.from_html(html)

for i, test in enumerate(tests_roundtrip):
    globals()['test_roundtrip_%d' % i] = (lambda t: lambda: run_test(t))(test)
