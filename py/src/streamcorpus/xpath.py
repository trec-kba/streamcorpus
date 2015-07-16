from __future__ import absolute_import, division, print_function

from itertools import ifilter
import re

import lxml.html

from streamcorpus.ttypes import OffsetType


class InvalidXpathError(Exception):
    '''Raises when an invalid Xpath is found.

    Technically, if an invalid xpath is found, then there is a bug in
    the code that maps char offsets to xpaths. However, HTML is vast,
    complex and full of corner cases. Therefore, it's a bug that one
    might want to gracefully recover from.

    An "invalid" Xpath is invalid with respect to the invariants
    defined in :class:`XpathRange` (not invalid with respect to the
    Xpath specification).
    '''
    pass


class XpathRange(object):
    '''Represents a range in HTML with xpaths.

    ``XpathRange`` is nearly isomorphic to Javascript's standard library
    ``Range`` object. Is it a bit more restrictive because it relies
    on the representation of xpath for node identity (rather than the
    DOM node itself). As a result, this assumes that there exists a
    *canonical* and *uniquely identifying* xpath for each DOM node in
    an HTML document.

    Once an ``XpathRange`` is created, it can be used to extract
    text from an HTML document (or DOM node).
    '''
    __slots__ = [
        'start_container_xpath', 'start_xpath', 'start_offset',
        'start_text_index',
        'end_container_xpath', 'end_xpath', 'end_offset',
        'end_text_index',
        'common_ancestor',
    ]

    def __init__(self, start_xpath, start_offset, end_xpath, end_offset):
        '''Create a new ``XpathRange``.

        If you have a :class:`streamcorpus.Offset`, then you can use
        the ``from_offset`` convenience constructor.

        :param str start_xpath: Start xpath
        :param int start_offset: Start offset (where text begins in node)
        :param str end_xpath: End xpath
        :param int end_offset: End offset (where text ends in node)
        :rtype: :class:`streamcorpus.XpathRange`
        '''
        self.start_xpath = start_xpath
        self.start_offset = start_offset
        self.start_container_xpath = XpathRange.strip_text(self.start_xpath)
        self.start_text_index = XpathRange.text_index(self.start_xpath)
        self.end_xpath = end_xpath
        self.end_offset = end_offset
        self.end_container_xpath = XpathRange.strip_text(self.end_xpath)
        self.end_text_index = XpathRange.text_index(self.end_xpath)
        self.common_ancestor = XpathRange.common_ancestor_xpath(
            self.start_xpath, self.end_xpath)

    @staticmethod
    def from_offset(offset):
        '''Creates a new ``XpathRange`` from a ``Offset``.

        :param offset: A offset
        :type offset: :class:`streamcorpus.Offset`
        :rtype: :class:`streamcorpus.XpathRange`
        '''
        assert offset.type == OffsetType.XPATH_CHARS
        return XpathRange(offset.xpath, offset.first,
                          offset.xpath_end, offset.xpath_end_offset)

    @staticmethod
    def common_ancestor_xpath(x1, x2):
        '''Return least common ancestor between ``x1` and ``x2``.

        Note that ``x1`` and ``x2`` must be canonical Xpaths as
        describe in this class' documentation.

        If there is no common ancestor, ``None`` is returned.
        Otherwise, a (canonical and unique) xpath to the common
        ancestor is returned.
        '''
        # This method is suspect. It doesn't just rely on canonicalization
        # and uniqueness. Instead, it relies on a particular canonicalization
        # so that splitting on `/` does the right thing. ---AG
        # Just return the longest common prefix.
        ancestor = []
        for p1, p2 in zip(x1.split('/'), x2.split('/')):
            if p1 != p2:
                break
            ancestor.append(p1)
        return '/'.join(ancestor) if len(ancestor) > 0 else None

    @staticmethod
    def html_node(html):
        '''Returns an ``lxml.Element`` suitable for ``slice_node``.'''
        if not isinstance(html, unicode):
            html = unicode(html, 'utf-8')
        # The catch here is that lxml's HTML parser replaces *some* HTML
        # entity/char escape sequences with their proper Unicode codepoint
        # (e.g., `&amp;` -> `&` and `&quot;` -> `"`).
        # But not all such entities are replaced (e.g., `&Hat;` -> `&Hat;`).
        # We can either special case the entities that lxml does replace
        # (no thanks), or just escape every `&` in the HTML, which starts
        # every entity/char escape sequence.
        #
        # We care about this because changing `&amp;` to `&` in the original
        # HTML will throw off indexing.
        return lxml.html.fromstring(html.replace(u'&', u'&amp;'))

    @property
    def same_parent(self):
        '''Returns true iff range starts and ends in same parent.'''
        return self.start_container_xpath == self.end_container_xpath

    @property
    def same_node(self):
        '''Returns true iff range starts and ends in same text node.'''
        return self.start_xpath == self.end_xpath

    def root_at(self, root_xpath):
        '''Returns a new ``XpathRange`` at the given root.'''
        return XpathRange(root_xpath + self.start_xpath, self.start_offset,
                          root_xpath + self.end_xpath, self.end_offset)

    def slice_stream_item(self, si, trimmed=False):
        '''Returns the text corresponding to this range.

        The text is sliced from the ``clean_html`` of the given
        stream item.
        '''
        return self.slice_html(si.body.clean_html, trimmed=trimmed)

    def slice_html(self, html, trimmed=False):
        '''Returns the text corresponding to this range in ``html``.'''
        return self.slice_node(XpathRange.html_node(html))

    def slice_node(self, root, trimmed=False):
        '''Returns the text corresponding to this range in ``root``.

        ``root`` should be a ``lxml.Element`` and **must** be produced
        by using :meth:`XpathRange.html_node`.

        If ``trimmed`` is true, then text nodes that are purely
        whitespace are dropped.
        '''
        if self.same_node:
            t = XpathRange.one_node(root, self.start_xpath)
            return t[self.start_offset:self.end_offset]
        else:
            ancestor = XpathRange.one_node(root, self.common_ancestor)
            start_node = XpathRange.one_node(root, self.start_container_xpath)
            end_node = XpathRange.one_node(root, self.end_container_xpath)
            starti = -1  # only count direct children of `start_node`
            endi = -1  # only count direct children of `end_node`
            parts = []
            for parent, text in XpathRange.text_node_tree(ancestor):
                if parent == start_node:
                    starti += 1
                if starti > -1 and parent == end_node:
                    endi += 1
                if starti > -1 and \
                        (self.start_text_index <= starti or
                         (endi > -1 and
                          self.end_text_index >= endi and
                          len(parts) > 0)):
                    if parent == start_node \
                            and starti == self.start_text_index:
                        parts.append(text[self.start_offset:])
                    elif parent == end_node and endi == self.end_text_index:
                        parts.append(text[:self.end_offset])
                        break
                    else:
                        parts.append(text)
            if trimmed:
                return ''.join(ifilter(lambda p: re.search('^\s+$', p) is None,
                                       parts))
            else:
                return ''.join(parts)

    @staticmethod
    def strip_text(xpath):
        return re.sub(r'/text\(\)\[\d+\]$', '', xpath)

    @staticmethod
    def one_node(root, xpath):
        node = root.xpath(xpath)
        if len(node) != 1:
            raise InvalidXpathError(
                'Xpath expected to address one node, '
                'but it found %d nodes: %r' % (len(node), xpath))
        return node[0]

    @staticmethod
    def text_index(xpath):
        m = re.search(r'/text\(\)\[(\d+)\]$', xpath)
        if m is None:
            raise ValueError('xpath has invalid text selector: %r' % xpath)
        return int(m.group(1)) - 1  # convert to zero based indexing

    @staticmethod
    def text_node_tree(node):
        '''Yield an iterator over text node children in ``node``.

        This will recursively descend the given node's children.

        ``node`` should be a ``lxml.Element``.

        This returns a generator that yields tuples of
        ``(parent_node, unicode)``.
        '''
        # TODO: Use an explicit stack because Python doesn't have TCO.
        if node.text is not None:
            yield node, node.text
        for child in node.iterchildren():
            for parent, text in XpathRange.text_node_tree(child):
                yield parent, text
            if child.tail is not None:
                yield node, child.tail

    def __eq__(self, other):
        return (
            self.start_offset == other.start_offset and
            self.end_offset == other.end_offset and
            self.start_xpath == other.start_xpath and
            self.end_xpath == other.end_xpath
        )

    def __str__(self):
        return '((%s, %d), (%s, %d))' % (self.start_xpath, self.start_offset,
                                         self.end_xpath, self.end_offset)

    def __repr__(self):
        tup = repr(((self.start_xpath, self.start_offset),
                    (self.end_xpath, self.end_offset)))
        return '%s(%s)' % (self.__class__.__name__, tup)
