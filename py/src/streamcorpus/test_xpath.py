from __future__ import absolute_import, division, print_function

from streamcorpus import XpathRange


tests_roundtrip = [{
    'html': '<p>Foo</p>',
    'ranges': [(('/p[1]/text()[1]', 0), ('/p[1]/text()[1]', 3))],
    'expected': ['Foo'],
}, {
    'html': '<p>Foo</p><p>Bar</p>',
    'ranges': [
        (('/p[1]/text()[1]', 0), ('/p[1]/text()[1]', 3)),
        (('/p[2]/text()[1]', 0), ('/p[2]/text()[1]', 3)),
    ],
    'expected': ['Foo', 'Bar'],
}, {
    'html': '<p><a>Foo</a></p>',
    'ranges': [(('/p[1]/a[1]/text()[1]', 0), ('/p[1]/a[1]/text()[1]', 3))],
    'expected': ['Foo'],
}, {
    'html': '<p>Homer <b>Jay</b> Simpson</p>',
    'ranges': [
        (('/p[1]/text()[1]', 0), ('/p[1]/text()[1]', 5)),
        (('/p[1]/b[1]/text()[1]', 0), ('/p[1]/b[1]/text()[1]', 3)),
        (('/p[1]/text()[2]', 1), ('/p[1]/text()[2]', 8)),
    ],
    'expected': ['Homer', 'Jay', 'Simpson'],
}, {
    'html': '<b><i>a<u>b</u>c</i>d</b>',
    'ranges': [
        (('/b[1]/i[1]/text()[1]', 0), ('/b[1]/i[1]/text()[1]', 1)),
        (('/b[1]/i[1]/u[1]/text()[1]', 0), ('/b[1]/i[1]/u[1]/text()[1]', 1)),
        (('/b[1]/i[1]/text()[2]', 0), ('/b[1]/i[1]/text()[2]', 1)),
        (('/b[1]/text()[1]', 0), ('/b[1]/text()[1]', 1)),
    ],
    'expected': ['a', 'b', 'c', 'd'],
}, {
    'html': '<b>AB</b>',
    'ranges': [
        (('/b[1]/text()[1]', 0), ('/b[1]/text()[1]', 1)),
        (('/b[1]/text()[1]', 1), ('/b[1]/text()[1]', 2)),
    ],
    'expected': ['A', 'B'],
}, {
    'html': '<b>ABCD</b>',
    'ranges': [
        (('/b[1]/text()[1]', 0), ('/b[1]/text()[1]', 2)),
        (('/b[1]/text()[1]', 2), ('/b[1]/text()[1]', 4)),
    ],
    'expected': ['AB', 'CD'],
}, {
    'html': '<b>b<i>a</i>r</b>',
    'ranges': [
        (('/b[1]/text()[1]', 0), ('/b[1]/text()[2]', 1)),
    ],
    'expected': ['bar'],
}, {
    'html': '<b>Hello, Homer <i>Jay</i> Simpson. Press any key.</b>',
    'ranges': [
        (('/b[1]/text()[1]', 7), ('/b[1]/text()[2]', 8)),
    ],
    'expected': ['Homer Jay Simpson'],
}, {
    'html': '<b>b<i>a</i>r</b>',
    'ranges': [
        (('/b[1]/text()[1]', 0), ('/b[1]/text()[1]', 1)),
        (('/b[1]/i[1]/text()[1]', 0), ('/b[1]/i[1]/text()[1]', 1)),
        (('/b[1]/text()[2]', 0), ('/b[1]/text()[2]', 1)),
    ],
    'expected': ['b', 'a', 'r'],
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
