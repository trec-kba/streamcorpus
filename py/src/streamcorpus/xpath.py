from __future__ import absolute_import, division, print_function

import re

import lxml.html


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
    ]

    def __init__(self, start_xpath, start_offset, end_xpath, end_offset):
        '''Create a new ``XpathRange``.

        :param str start_xpath: Start xpath
        :param int start_offset: Start offset (where text begins in node)
        :param str end_xpath: End xpath
        :param int end_offset: End offset (where text ends in node)
        '''
        self.start_xpath = start_xpath
        self.start_offset = start_offset
        self.start_container_xpath = XpathRange.strip_text(self.start_xpath)
        self.start_text_index = XpathRange.text_index(self.start_xpath)
        self.end_xpath = end_xpath
        self.end_offset = end_offset
        self.end_container_xpath = XpathRange.strip_text(self.end_xpath)
        self.end_text_index = XpathRange.text_index(self.end_xpath)

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

    def from_html(self, html):
        '''Returns the text corresponding to this range in ``html``.'''
        if not isinstance(html, unicode):
            html = unicode(html, 'utf-8')
        return self.from_root_node(lxml.html.fromstring(html))

    def from_root_node(self, root):
        '''Returns the text corresponding to this range in ``root``.

        ``root`` should be a ``lxml.Element``.
        '''
        if self.same_node:
            t = XpathRange.one_node(root, self.start_xpath)
            return t[self.start_offset:self.end_offset]
        elif self.same_parent:
            # start = XpathRange.text_index(self.start_xpath)
            # end = XpathRange.text_index(self.end_xpath) + 1
            node = XpathRange.one_node(root, self.start_container_xpath)
            i = 0  # only counts direct child text nodes of `node`.
            parts = []
            for parent, text in XpathRange.text_node_tree(node):
                if self.start_text_index <= i <= self.end_text_index:
                    if node == parent and i == self.start_text_index:
                        parts.append(text[self.start_offset:])
                    elif node == parent and i == self.end_text_index:
                        parts.append(text[:self.end_offset])
                    else:
                        parts.append(text)
                if parent == node:
                    i += 1
                if i > self.end_text_index:
                    break
            return ''.join(parts)
        else:
            # TODO: In the general case, we need a full tree traversal. ---AG
            raise NotImplementedError

    @staticmethod
    def strip_text(xpath):
        return re.sub(r'/text\(\)\[\d+\]$', '', xpath)

    @staticmethod
    def one_node(root, xpath):
        node = root.xpath(xpath)
        assert len(node) == 1, xpath
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
