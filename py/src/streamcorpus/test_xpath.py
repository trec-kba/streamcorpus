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
    'html': '<p>Foo</p>',
    'ranges': [
        None,
        None,
        (('/p[1]/text()[1]', 1), ('/p[1]/text()[1]', 2)),
        None,
    ],
    'expected': [None, None, 'o', None],
    'tokens': [(3, 3), (4, 4), (4, 5), (5, 5)],
}, {
    'html': '<div>Foo<br>Bar</div>',
    'ranges': [
        (('/div[1]/text()[1]', 0), ('/div[1]/text()[1]', 3)),
        (('/div[1]/text()[2]', 0), ('/div[1]/text()[2]', 3)),
    ],
    'expected': ['Foo', 'Bar'],
    'tokens': [(5, 8), (12, 15)],
}, {
    'html': '<div><p>a</p> or <p>b</p><br />c</div>',
    'ranges': [
        (('/div[1]/p[1]/text()[1]', 0), ('/div[1]/p[1]/text()[1]', 1)),
        (('/div[1]/p[2]/text()[1]', 0), ('/div[1]/p[2]/text()[1]', 1)),
        (('/div[1]/text()[2]', 0), ('/div[1]/text()[2]', 1)),
    ],
    'expected': ['a', 'b', 'c'],
    'tokens': [(8, 9), (20, 21), (31, 32)],
}, {
    'html': '<div><audio><source></source>Sorry, your browser.</audio></div>',
    'ranges': [
        (('/div[1]/audio[1]/text()[1]', 0), ('/div[1]/audio[1]/text()[1]', 5)),
    ],
    'expected': ['Sorry'],
    'tokens': [(29, 34)],
}, {
    'html': '<p>Cheech &amp; Chong</p>',
    'ranges': [
        (('/p[1]/text()[1]', 0), ('/p[1]/text()[1]', 18)),
    ],
    'expected': ['Cheech &amp; Chong'],
    'tokens': [(3, 21)],
}, {
    'html': '<p>Cheech &amp; Chong</p>',
    'ranges': [None],
    'expected': [None],
    'tokens': [(10, 14)],
}, {
    'html': '<p>Cheech &amp; Chong</p>',
    'ranges': [None, None],
    'expected': [None, None],
    'tokens': [(10, 14), (14, 15)],
}, {
    'html': '<p>Cheech &amp; Chong</p>',
    'ranges': [
        None,
        (('/p[1]/text()[1]', 13), ('/p[1]/text()[1]', 18)),
    ],
    'expected': [None, 'Chong'],
    'tokens': [(10, 14), (16, 21)],
}, {
    'html': '<p>Cheech & Chong</p>',
    'ranges': [None],
    'expected': [None],
    'tokens': [(10, 11)],
}, {
    'html': '<p>Cheech & Chong</p>',
    'ranges': [
        (('/p[1]/text()[1]', 7), ('/p[1]/text()[1]', 14)),
    ],
    'expected': ['& Chong'],
    'tokens': [(10, 17)],
}, {
    'html': '<p>&quot;hi&quot;</p>',
    'ranges': [
        (('/p[1]/text()[1]', 6), ('/p[1]/text()[1]', 8)),
    ],
    'expected': ['hi'],
    'tokens': [(9, 11)],
}, {
    'html': '<p>&#34;hi&#34;</p>',
    'ranges': [
        (('/p[1]/text()[1]', 5), ('/p[1]/text()[1]', 7)),
    ],
    'expected': ['hi'],
    'tokens': [(8, 10)],
}, {
    'html': '<p>&#x22;hi&#x22;</p>',
    'ranges': [
        (('/p[1]/text()[1]', 6), ('/p[1]/text()[1]', 8)),
    ],
    'expected': ['hi'],
    'tokens': [(9, 11)],
}, {
    'html': '<p><a>abc\na&gt;</a></p>',
    'ranges': [None],
    'expected': [None],
    'tokens': [(10, 14)],
}, {
    'html': '<p><a href="#CITEREFZhangYang2004">Zhang &amp; Yang (2004)</a></p>',
    'ranges': [
        (('/p[1]/a[1]/text()[1]', 0), ('/p[1]/a[1]/text()[1]', 5)),
        None,
        None,
        (('/p[1]/a[1]/text()[1]', 12), ('/p[1]/a[1]/text()[1]', 16)),
    ],
    'expected': ['Zhang', None, None, 'Yang'],
    'tokens': [(35, 40), (41, 45), (45, 46), (47, 51)],
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
# These require general tree traversal.
# i.e., Start and end in different DOM node. ---AG
}, {
    'html': '<b>b<i>ar</i></b>',
    'ranges': [
        (('/b[1]/text()[1]', 0), ('/b[1]/i[1]/text()[1]', 2)),
    ],
    'tokens': [(3, 9)],
    'expected': ['bar'],
}, {
    'html': '<b>f<i>o</i>ob<u>a</u>r</b>',
    'ranges': [
        (('/b[1]/text()[1]', 0), ('/b[1]/text()[3]', 1)),
    ],
    'tokens': [(3, 23)],
    'expected': ['foobar'],
}, {
    'html': '<div><p>##abc##</p>\n<p>!!mno!!</p>\n<p>@@xyz@@</p>\n</div>',
    'ranges': [
        (('/div[1]/p[1]/text()[1]', 2), ('/div[1]/p[3]/text()[1]', 5)),
    ],
    'tokens': [(10, 43)],
    'expected': ['abc##\n!!mno!!\n@@xyz'],
}, {
    'html':
        '<div>'
            '<p><a>!!!</a></p>\n'
            '<p><a>123</a></p>\n'
            '<p><a>456</a></p>\n'
            '<p><a>###</a></p>\n'
        '</div>',
    'ranges': [
        (('/div[1]/p[2]/a[1]/text()[1]', 0), ('/div[1]/p[3]/a[1]/text()[1]', 2)),
    ],
    'tokens': [(29, 49)],
    'expected': ['123\n45'],
}, {
    'html': '<p>running process*<br><strong>Jun 01 13:06:26</strong> &lt;neuron_&gt;     wait &lt;.&lt; derp<br></p>',
    'ranges': [None],
    'tokens': [(89, 90)],
    'expected': [None],
}, {
    'html': '<p><b>T</b>om <b>B</b>rady</p>',
    'ranges': [
        (('/p[1]/b[1]/text()[1]', 0), ('/p[1]/text()[1]', 2)),
        (('/p[1]/b[2]/text()[1]', 0), ('/p[1]/text()[2]', 4)),
    ],
    'tokens': [(6, 13), (17, 26)],
    'expected': ['Tom', 'Brady'],
}, {
    'html': '<p>a<b>a</b>a<b>a</b>a A<b>A</b>A a<b>a</b>a<b>a</b>a</p>',
    'ranges': [
        (('/p[1]/text()[3]', 2), ('/p[1]/text()[4]', 1)),
    ],
    'tokens': [(23, 33)],
    'expected': ['AAA'],
}, {
    'html': '<p><b>abc</b> <b>d<i>e</i>f <i>g</i>hij</b></p>',
    'ranges': [
        (('/p[1]/b[1]/text()[1]', 1), ('/p[1]/b[2]/text()[3]', 2)),
    ],
    'tokens': [(7, 38)],
    'expected': ['bc def ghi'],
}]


def run_test(test):
    for xoffsets, expect in zip(test['ranges'], test['expected']):
        if expect is None:
            assert xoffsets is None
        else:
            (x1, i1), (x2, i2) = xoffsets
            html = '<html><body>' + test['html'] + '</body></html>'
            xprange = XpathRange('/html/body' + x1, i1, '/html/body' + x2, i2)
            assert expect == xprange.slice_html(html)


for i, test in enumerate(tests_roundtrip):
    globals()['test_roundtrip_%d' % i] = (lambda t: lambda: run_test(t))(test)
